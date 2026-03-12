gcloud_repo() {
  emulate -L zsh
  setopt pipefail

  local repo_root git_common_dir repo_name hash config_base config_dir account project

  repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    print -u2 -- "gcloud_repo: git repo の中で実行してください"
    return 1
  }

  git_common_dir=$(git rev-parse --git-common-dir 2>/dev/null) || {
    print -u2 -- "gcloud_repo: git-common-dir を取得できません"
    return 1
  }

  [[ "$git_common_dir" = /* ]] || git_common_dir="${repo_root}/${git_common_dir}"
  git_common_dir=$(cd "$git_common_dir" 2>/dev/null && pwd -P) || {
    print -u2 -- "gcloud_repo: git-common-dir を解決できません: $git_common_dir"
    return 1
  }

  if (( $+commands[shasum] )); then
    hash=$(printf '%s' "$git_common_dir" | shasum -a 256 | awk '{print substr($1,1,12)}')
  elif (( $+commands[sha256sum] )); then
    hash=$(printf '%s' "$git_common_dir" | sha256sum | awk '{print substr($1,1,12)}')
  else
    print -u2 -- "gcloud_repo: shasum か sha256sum が必要です"
    return 1
  fi

  repo_name=${repo_root:t}
  config_base="${HOME}/.config/gcloud-repos"
  config_dir="${config_base}/${repo_name}-${hash}"

  mkdir -p "$config_dir" || {
    print -u2 -- "gcloud_repo: ディレクトリを作れません: $config_dir"
    return 1
  }

  export CLOUDSDK_CONFIG="$config_dir"

  if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    print -u2 -- "warning: GOOGLE_APPLICATION_CREDENTIALS が設定されています"
    print -u2 -- "         ADC 分離よりこちらが優先されます"
  fi

  if (( $+commands[gcloud] )); then
    account=$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | head -n 1)
    project=$(gcloud config get-value project 2>/dev/null | tail -n 1)
    [[ "$project" == "(unset)" ]] && project=""
  fi

  print -- "repo:            $repo_root"
  print -- "CLOUDSDK_CONFIG: $CLOUDSDK_CONFIG"
  print -- "account:         ${account:-"(none)"}"
  print -- "project:         ${project:-"(unset)"}"
}

gcloud_project() {
  emulate -L zsh
  setopt pipefail

  local project="$1"
  if [[ -z "$project" ]]; then
    print -u2 -- "usage: gcloud_project <project-id>"
    return 1
  fi

  gcloud config set project "$project" >/dev/null || return 1

  if ! gcloud auth application-default set-quota-project "$project" >/dev/null 2>&1; then
    print -u2 -- "warning: ADC の quota project は更新できませんでした"
    print -u2 -- "         必要なら: gcloud auth application-default login"
  fi

  export CLOUDSDK_CORE_PROJECT="$project"
  export GOOGLE_CLOUD_PROJECT="$project"

  print -- "project:       $project"
  print -- "quota project: $project"
}

gcloud_default() {
  unset CLOUDSDK_CONFIG
  unset CLOUDSDK_CORE_PROJECT
  unset GOOGLE_CLOUD_PROJECT
  print -- "gcloud の repo 固有設定を解除しました"
}

