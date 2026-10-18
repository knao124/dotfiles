import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

// Exercise the actual planner in an isolated dry-run; no browser or live submission.
const source = await readFile(new URL("./teamspirit-monthly-console.js", import.meta.url), "utf8");
const sandbox = {
  window: {},
  document: {
    querySelector: () => ({}),
    getElementById: () => null,
    body: { innerText: "2026年01月" }
  },
  console: { log() {}, error() {} }
};
await vm.runInNewContext(source.replace("  window.TS_MONTHLY_RUNNING = true;", "  window.testBuildPlan = buildPlan;\n  window.TS_MONTHLY_RUNNING = true;"), sandbox);
const build = (segments) => sandbox.window.testBuildPlan({
  year: 2026, month: 2, weekRules: {}, entries: { "2026-02-06": segments }
});

test("less than 8 hours does not trigger the one-hour rule", () => {
  assert.equal(build([["08:00", "15:59"]]).totalMinutes, 479);
});

test("exactly 8 hours without rest fails", () => {
  assert.throws(() => build([["08:00", "16:00"]]), /at least 1 hour of actual rest/);
});

test("exactly 8 hours with only 59 minutes of rest fails", () => {
  assert.throws(() => build([["08:00", "12:00"], ["12:59", "16:59"]]), /at least 1 hour of actual rest/);
});

test("exactly 8 hours with 60 minutes of rest passes", () => {
  assert.equal(build([["08:00", "12:00"], ["13:00", "17:00"]]).totalMinutes, 480);
});

test("several actual breaks count toward the one-hour minimum", () => {
  const plan = build([["08:00", "11:00"], ["11:30", "14:30"], ["15:00", "17:00"]]);
  assert.equal(plan.totalMinutes, 480);
  assert.equal(JSON.stringify(plan.plan[0].rest), JSON.stringify([["11:00", "11:30"], ["14:30", "15:00"]]));
});

test("more than 8 hours with too little rest fails", () => {
  assert.throws(() => build([["07:00", "12:00"], ["12:30", "17:30"]]), /at least 1 hour of actual rest/);
});

test("three gaps preserve the actual four hours of work", () => {
  const plan = build([["08:30", "10:00"], ["10:30", "11:00"], ["13:00", "14:00"], ["19:00", "20:00"]]);
  assert.equal(plan.totalMinutes, 240);
  assert.equal(JSON.stringify(plan.plan[0].rest), JSON.stringify([["10:00", "10:30"], ["11:00", "13:00"], ["14:00", "19:00"]]));
});

test("several dates validate both count and total", () => {
  const entries = {
    "2026-02-02": [["08:00", "12:00"], ["13:00", "17:00"]],
    "2026-02-03": [["09:00", "13:00"]],
    "2026-02-04": [["08:00", "12:00"], ["13:00", "18:00"]]
  };
  const plan = sandbox.window.testBuildPlan({ year: 2026, month: 2, entries, weekRules: {}, expectedTargetCount: 3, expectedTotalMinutes: 1260 });
  assert.equal(plan.totalHours, "21:00");
  assert.throws(() => sandbox.window.testBuildPlan({ year: 2026, month: 2, entries, weekRules: {}, expectedTotalMinutes: 1200 }), /Total mismatch/);
});
