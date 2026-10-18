"""No real credentials or network access are used by these tests."""

import base64
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import deepseek_consult as sender


class SenderTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(sender.os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.default_key = patch.object(sender, "DEFAULT_KEY_FILE", Path("/nonexistent/deepseek-test-api-key"))
        self.default_key.start()
        self.addCleanup(self.default_key.stop)

    def test_rejects_credential_forms(self):
        samples = [
            "sk-" + "a" * 32,
            '"api_key": "example-value"',
            "PASSWORD=example-value",
            "パスワード：example-value",
            "Authorization: Bearer example-value",
            "Cookie: session=example-value",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
            "https://user:example-value@example.com/db",
            "https://example.com/a?X-Amz-Signature=example-value",
            "https://example.com/a?token=example-value",
            "AKIA" + "A" * 16,
            "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.signature",
            "Read .env.production and /home/user/.codex/auth.json",
            "Read /home/user/key.txt",
            "ＡＰＩ＿ＫＥＹ＝example-value",
        ]
        for text in samples:
            with self.subTest(text=text), self.assertRaises(sender.UnsafeInput):
                sender.inspect_text(text)

    def test_rejects_exact_and_encoded_environment_credentials(self):
        secret = "arbitrary-sensitive-value-1234"
        with patch.dict(sender.os.environ, {"SERVICE_SECRET": secret}):
            for value in [secret, base64.b64encode(secret.encode()).decode(), secret.encode().hex()]:
                with self.subTest(value=value), self.assertRaises(sender.UnsafeInput):
                    sender.inspect_text("Context: " + value)

    def test_known_auth_key_never_enters_request_body(self):
        key = "arbitrary-auth-value-5678"
        with patch.object(sender.http.client, "HTTPSConnection") as connection:
            with self.assertRaises(sender.UnsafeInput):
                sender.send("Context: " + key, key)
            connection.assert_not_called()

    def test_network_and_auth_are_separate_from_the_model_input(self):
        key = "arbitrary-auth-value-5678"
        connection = Mock()
        response = connection.getresponse.return_value
        response.status = 200
        response.read.return_value = json.dumps({
            "status": "completed",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "公開例の設計は妥当です。"}]}],
            "usage": {"input_tokens": 10, "output_tokens": 5, "unexpected": key},
        }).encode()
        stderr = io.StringIO()
        with patch.object(sender.http.client, "HTTPSConnection", return_value=connection) as factory:
            with patch.dict(sender.os.environ, {"OTHER_SECRET": "other-sensitive-value", "HTTPS_PROXY": "https://proxy.invalid"}):
                with contextlib.redirect_stderr(stderr):
                    answer = sender.send("公開例の設計を検討してください。", key)
        self.assertEqual(answer, "公開例の設計は妥当です。")
        self.assertEqual(factory.call_args.args[:2], ("api.deepseek.com", 443))
        args, kwargs = connection.request.call_args
        self.assertEqual(args, ("POST", "/responses"))
        body = kwargs["body"].decode()
        payload = json.loads(body)
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer " + key)
        self.assertNotIn(key, body + stderr.getvalue())
        self.assertNotIn("other-sensitive-value", body)
        self.assertNotIn("proxy.invalid", body)
        self.assertNotIn("tools", payload)
        self.assertEqual(payload["input"], "公開例の設計を検討してください。")
        self.assertEqual(payload["model"], "deepseek-flash")
        self.assertFalse(payload["store"])
        connection.close.assert_called_once()

    def test_redirect_is_rejected_without_second_request(self):
        connection = Mock()
        connection.getresponse.return_value.status = 302
        with patch.object(sender.http.client, "HTTPSConnection", return_value=connection):
            with self.assertRaisesRegex(ValueError, "HTTP 302"):
                sender.send("公開例の設計を検討してください。", "auth-value")
        connection.request.assert_called_once()
        connection.getresponse.return_value.read.assert_not_called()

    def test_secret_input_stops_before_any_network_and_does_not_echo_it(self):
        with tempfile.TemporaryDirectory() as td:
            prompt = Path(td) / "prompt.md"
            secret = "sk-" + "q" * 32
            prompt.write_text(secret)
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(sender.http.client, "HTTPSConnection") as connection:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = sender.main(["--input", str(prompt), "--send"])
            self.assertEqual(code, 1)
            connection.assert_not_called()
            self.assertNotIn(secret, stdout.getvalue() + stderr.getvalue())

    def test_check_only_never_uses_network(self):
        with tempfile.TemporaryDirectory() as td:
            prompt = Path(td) / "prompt.md"
            prompt.write_text("公開例の設計を検討してください。")
            with patch.object(sender.http.client, "HTTPSConnection") as connection:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    code = sender.main(["--input", str(prompt)])
            self.assertEqual(code, 0)
            connection.assert_not_called()

    def test_key_file_is_used_for_auth_not_prompt(self):
        with tempfile.TemporaryDirectory() as td:
            key_file = Path(td) / "credential-file.txt"
            key = "local-auth-value-1234"
            key_file.write_text('export DEEPSEEK_API_KEY="' + key + '"\n')
            self.assertEqual(sender.read_api_key(str(key_file)), key)

    def test_default_key_file_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as td:
            key_file = Path(td) / "credential-file.txt"
            key_file.write_text("default-local-auth-value")
            with patch.object(sender, "DEFAULT_KEY_FILE", key_file):
                self.assertEqual(sender.read_api_key(None), "default-local-auth-value")
                with patch.dict(sender.os.environ, {"DEEPSEEK_API_KEY": "environment-auth-value"}):
                    self.assertEqual(sender.read_api_key(None), "environment-auth-value")

    def test_secret_path_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hidden = Path(td) / ".env"
            hidden.write_text("private business data")
            alias = Path(td) / "prompt.md"
            alias.symlink_to(hidden)
            with self.assertRaises(sender.UnsafeInput):
                sender.read_prompt(alias)

    def test_response_with_credential_is_not_printed(self):
        connection = Mock()
        response = connection.getresponse.return_value
        response.status = 200
        response.read.return_value = json.dumps({
            "status": "completed", "output": [{"type": "message", "content": [
                {"type": "output_text", "text": "sk-" + "r" * 32}
            ]}]
        }).encode()
        with patch.object(sender.http.client, "HTTPSConnection", return_value=connection):
            with self.assertRaises(sender.UnsafeInput):
                sender.send("公開例の設計を検討してください。", "local-auth-value")


if __name__ == "__main__":
    unittest.main()
