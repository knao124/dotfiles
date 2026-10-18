---
description: Strict workflow and reusable browser-console automation for registering monthly attendance corrections in TeamSpirit/Salesforce. Use when the user asks to automate, verify, or submit TeamSpirit/Teamsprit attendance, 勤怠表, 勤怠時刻修正申請, 承認申請, monthly part-time schedules, or console JavaScript for TeamSpirit.
license: MIT
metadata:
    github-path: skills/teamspirit-monthly-attendance
    github-ref: refs/heads/main
    github-repo: https://github.com/knao124/agent-skills
    github-tree-sha: 890e406e6063a2dfa39422775ca93bd8b59ebf55
name: teamspirit-monthly-attendance
---
# TeamSpirit Monthly Attendance

## Purpose

Register monthly TeamSpirit attendance correction applications from a weekday schedule with fail-stop checks, dry-run verification, and explicit confirmation before any submission.

Prefer the bundled console script when the available browser tool can execute it in the TeamSpirit Visualforce iframe. If evaluation is read-only or the old Chrome skill is unavailable, use supported browser UI actions instead; do not stop solely because `chrome:control-chrome` is missing. Read `references/browser-ui.md` for the UI workflow and multiple rest intervals. Manual DevTools Console paste remains an optional fallback.

- `scripts/teamspirit-monthly-console.js`: attendance correction helper. Edit only `CONFIG`; default output is compact.
- `scripts/teamspirit-work-ratio-console.js`: daily job work-ratio helper for the工数 dialog. Edit only `CONFIG`; default output is compact.
- `scripts/teamspirit-config.mjs`: locate, validate, and write the local private config file without echoing its contents.
- `references/configuration.md`: local config schema and first-run setup workflow. Read this whenever config is missing, invalid, or incomplete for the requested task.
- `references/config.example.json`: sanitized example config. Never put real workplace URLs, job names, or internal IDs in the repository copy.
- `references/observed-teamspirit-dom.md`: field IDs and selectors observed on the TeamSpirit attendance page. Read this only when the page/script behavior needs inspection or repair.

## Non-Negotiables

- Answer the user in Japanese.
- Treat TeamSpirit registration as transmission of workplace attendance data. Before clicking individual `承認申請`, show the exact target dates, start/end times,休憩, notes, and total hours, then get explicit approval unless the user has already approved that exact computed plan in the current turn.
- Never press the bottom monthly `承認申請` button unless the user separately and explicitly asks for monthly approval after individual applications are complete.
- Verify the active Chrome profile/account and URL are the intended workplace before running the script. If Chrome control sees a different profile/tab, stop and fix the target instead of operating that other page.
- When using manual DevTools Console fallback, verify the JavaScript context is the Visualforce attendance iframe, usually shown as `AtkWorkTimeView`. If `ttvApplyYYYY-MM-DD` or `dailyWorkCellYYYY-MM-DD` elements are missing, switch the Console context before doing anything else.
- Verify Japanese holidays/current company exclusions for the target month using a current source or user-provided exclusion dates. State absolute dates.
- Fail closed: if a target date has no plus button and it was not listed in `expectedExistingDates`, stop and inspect instead of silently skipping.
- For工数割合 registration, never modify `empWorkSeq*`; those hidden fields are TeamSpirit job row IDs. Use percent mode plus `empWorkSlider*` values only.
- For工数割合 registration, the script must run in the Visualforce page main world where `window.dijit` is available. Direct browser automation evaluation can run in an isolated context that sees `dailyWorkCell*` but cannot operate Dojo sliders.
- For bulk工数割合 registration, first run one sample target in dry-run or submit mode, reopen that sample date, and confirm the saved row times before running the full target list.
- Browser/Computer Use UI actions are allowed for attendance registration when direct script execution is unavailable. Use scoped DOM locators and compact checks; avoid repeated full accessibility-tree dumps or Console polling. Never use read-only evaluation to mutate the page or to run the console script.
- For a day with at least 8 hours (480 minutes) of actual work, require at least 1 hour (60 minutes) of total rest during that day, including exactly 8 hours of work. This is the user's operating rule. Compute work from the supplied segments and rest from the actual gaps; never invent a break, shift times, or deduct worked time to make the plan pass. If rest is insufficient, stop that date and ask for the actual break times.
- Check the company's day type in the attendance table. A specified date marked 所定休日 is not automatically excluded, nor may it be silently treated as a workday. Inspect available holiday-work/day-registration UI. A disabled 勤怠時刻修正申請 is not permission to bypass the UI. Do not create a 振替申請 or change another day without the user specifying and approving the corresponding dates; otherwise keep the date pending.
- Console scripts must keep compact output by default. Detailed payloads stay on `window.*_FINAL`; user-facing verification should read `window.*_SUMMARY` or compact marker logs first.
- Do not run the bundled sample `CONFIG` against a real workplace page. Build the run `CONFIG` from the local private config plus the current user request.
- Never commit, paste, or PR the local private config. Treat workplace URL/account hints, job names, client names, and job row matchers as private operational settings.

## Local Configuration

Before any real TeamSpirit browser or Console workflow, resolve the private local config:

1. Use `node scripts/teamspirit-config.mjs path` to get the default config path. It is `${CODEX_HOME:-~/.codex}/teamspirit-monthly-attendance/config.json`.
2. Run `node scripts/teamspirit-config.mjs validate`. If it succeeds and has the fields needed for the requested task, use it.
3. If the config file is missing, invalid, or incomplete, read `references/configuration.md` and ask the user for only the missing values before doing Chrome or Console work.
4. Write the answered config with `node scripts/teamspirit-config.mjs write` so the file is created with private permissions.
5. Use the config to replace placeholders:
   - `attendanceUrl` and `workplaceHint` drive Chrome tab selection.
   - `defaultWeekRules`, `defaultHolidays`, `defaultExcludeDates`, and `noteFormat` seed attendance plans unless the user overrides them.
   - `workRatio.jobs` provides real job labels and matchers for工数割合.
6. If a task needs工数割合 and `workRatio.jobs` is absent, ask for job labels/matchers and ratios, update the local config, then continue.

## Browser Control Policy

Use the lowest-token route that can operate the intended logged-in TeamSpirit page.

1. If the user only asks for calculation, script generation, or skill updates, do not open/control Chrome.
2. Use the available connected Chrome browser runtime to discover and claim the intended workplace tab/profile and verify its URL and account. A missing legacy Chrome skill or an empty tab list from a separate Playwright browser does not prove that the open Chrome tab is unavailable. Check the available Chrome inventory first. Execute the console script only when the tool explicitly supports mutating evaluation in the Visualforce iframe.
3. If the intended tab can be controlled but script execution is unavailable or read-only, follow `references/browser-ui.md` and register through normal UI controls. If the intended tab cannot be claimed, offer manual DevTools Console paste in `AtkWorkTimeView` or report the connection blocker; do not operate a different account.
4. For工数割合 only, if an automation route can evaluate JavaScript in the Visualforce document but `window.dijit` is unavailable, it is isolated from the page main world. Do not set hidden slider inputs manually. Either use DevTools Console in `AtkWorkTimeView`, or inject the edited script as a `<script>` element into the Visualforce document and bridge compact `window.TS_WORK_RATIO_SUMMARY` back through a DOM attribute.
5. Keep the work-ratio main-world/Dojo restrictions above even when using the attendance UI fallback. Attendance UI permission does not authorize hidden-field edits or script injection through read-only evaluation.
6. Never infer success from a different Chrome profile, a different Salesforce org, or the Lightning shell document outside the Visualforce iframe.

## Chrome Plugin Procedure

When `chrome:control-chrome` is available, load it first and follow its runtime instructions. Otherwise initialize the available browser tool and use its documented inventory and tab-claiming APIs. For the legacy Chrome runtime, follow this order:

1. Initialize the Chrome extension browser runtime once, then call `browser.user.openTabs()`.
2. Select the tab whose URL matches local config `attendanceUrl` and whose visible title/account context matches local config `workplaceHint`. Do not use a tab id that did not come from the current `openTabs()` result.
3. Claim that exact tab with `browser.user.claimTab(tab)` and reuse the returned `tab`.
4. Verify `await tab.url()` and a lightweight frame locator check for `iframe[id^="vfFrameId"]` or a frame containing `[id^="ttvApply"]` / `[id^="dailyWorkCell"]`.
5. If the API cannot execute the console script inside the Visualforce iframe, use the browser UI workflow in `references/browser-ui.md` or manual DevTools Console paste. Read-only evaluation may inspect DOM fields but must not mutate them.
6. After Chrome work, finalize the Chrome browser session and keep the claimed TeamSpirit tab only when the user needs to continue there.

## Token Budget Rules

- Never poll TeamSpirit with accessibility-tree dumps or repeated `get_app_state` calls.
- Do not paste full JSON payloads into chat. Summarize dates, statuses, total hours, and errors.
- Read `window.TS_MONTHLY_SUMMARY` or `window.TS_WORK_RATIO_SUMMARY` first. Read `window.TS_MONTHLY_FINAL` or `window.TS_WORK_RATIO_FINAL` only for a specific failed date.
- Use `copyResultToClipboard` only for compact summaries unless debugging a single failure.

## Workflow

1. Gather inputs:
   - local config from `scripts/teamspirit-config.mjs validate`
   - target year/month
   - weekday work segments from local config or user override
   - holidays/excluded dates from local config and current source/user override
   - existing submitted dates, if any
   - note format from local config, default `MM/DD`

2. Build the plan:
   - Convert multiple work segments into one TeamSpirit start/end plus休憩 gaps.
   - For recurring schedules, exclude Saturdays, Sundays, holidays, and `excludeDates`. For explicit worked dates, inspect the company day type and handle holidays separately instead of silently dropping the dates.
   - Compute total minutes from work segments only. Require at least 60 minutes of actual rest when work is at least 480 minutes; flag insufficient rest before requesting submission approval.
   - Preserve every gap as its own rest interval, including days with multiple gaps.
   - Use note `MM/DD` for every target date unless the user explicitly changes it.

3. Show a pre-submit summary:
   - target dates grouped or listed with weekday
   - start/end,休憩, note for each
   - expected existing/skipped dates
   - total hours
   - ask approval if the user has not already approved this exact plan

4. Open/verify TeamSpirit:
   - Follow the Browser Control Policy first.
   - URL path should be `/lightning/n/teamspirit__AtkWorkTimeTab`.
   - Displayed month must match the plan.
   - If using manual Console fallback, DevTools Console context must be the TeamSpirit Visualforce iframe (`AtkWorkTimeView`).

5. Dry-run (script path; for UI use the field verification in `references/browser-ui.md`):
   - Read `scripts/teamspirit-monthly-console.js`.
   - Edit only `CONFIG`.
   - Keep `submit: false`, `dryRun: true`.
   - Set `expectedTargetCount` and `expectedTotalHours` or `expectedTotalMinutes`.
   - Run it in Console.
   - Inspect `window.TS_MONTHLY_SUMMARY` first. Resolve any missing plus, wrong month, unexpected date, or total mismatch before submitting.

6. Submit:
   - Change `submit: true`, `dryRun: false`.
   - Set `confirmSubmit: "SUBMIT_TEAMSPIRIT_ATTENDANCE"`.
   - Keep `expectedTargetCount`, total expectation, `holidays`, and `expectedExistingDates`.
   - Run once. The script submits sequentially and stops on the first unexpected error.

7. Verify and report:
   - Read `window.TS_MONTHLY_SUMMARY`; use `window.TS_MONTHLY_FINAL` only if a specific date needs detail.
   - Confirm each new date is `submitted` and each pre-existing date is `existing`.
   - Confirm target dates no longer have the申請 plus button.
   - Tell the user what was submitted, what was skipped as already existing, total hours, and that monthly approval was not pressed.

## Work Ratio Workflow

Use this for the工数 column after the attendance times already exist.

1. Open/verify TeamSpirit:
   - Follow the Browser Control Policy first.
   - URL path should be `/lightning/n/teamspirit__AtkWorkTimeTab`.
   - Displayed month must match the intended month.
   - If using manual Console fallback, DevTools Console context must be the TeamSpirit Visualforce iframe (`AtkWorkTimeView`).

2. Sample run:
   - Read `scripts/teamspirit-work-ratio-console.js`.
   - Convert local config `workRatio.jobs[].matchText` to string matchers or `matchRegex` to JavaScript `RegExp` values in the script `CONFIG`.
   - Keep the default `targetDates: ["2026-01-05"]` or set exactly one requested sample date.
   - Keep `dryRun: true`, `submit: false`.
   - Run it once and inspect `window.TS_WORK_RATIO_SUMMARY`.
   - If the user asks to register the sample, set `dryRun: false`, `submit: true`, and `confirmSubmit: "SUBMIT_TEAMSPIRIT_WORK_RATIO"` for that single date only.

3. Verify sample persistence:
   - Reopen the same date's工数 dialog.
   - Confirm the expected job rows, slider values, row times, and total time remain saved.
   - For a `7:00` work day with sample ratios `Project A:1` and `Project B:4`, expected times are `1:24` and `5:36`, total `7:00`.

4. Full month:
   - Replace `targetDates` with the exact approved work dates, not a guessed weekday rule.
   - Set `expectedTargetCount`.
   - Run dry-run for the full list and confirm every target row has exactly the expected jobs.
   - Only after user approval, set `submit: true`, `dryRun: false`, and the required confirmation string.

5. Verify and report:
   - Read `window.TS_WORK_RATIO_SUMMARY`; use `window.TS_WORK_RATIO_FINAL` only for a failed date or detailed row audit.
   - Confirm every target date is `submitted`.
   - Reopen at least one representative date after submit and verify persisted times.

## Configuration Conventions

Use weekday keys compatible with JavaScript `Date#getDay()`:

- `1`: Monday
- `2`: Tuesday
- `3`: Wednesday
- `4`: Thursday
- `5`: Friday

Represent work as segments, not breaks:

```js
weekRules: {
  1: [["09:00", "12:00"], ["13:00", "17:00"]],
  3: [["10:00", "12:00"]],
  5: [["09:30", "12:00"], ["13:00", "16:30"]]
}
```

This becomes:

- Monday: start `09:00`, end `17:00`,休憩 `12:00-13:00`
- Wednesday: start `10:00`, end `12:00`,休憩なし
- Friday: start `09:30`, end `16:30`,休憩 `12:00-13:00`

Use `entries` only for one-off overrides:

```js
entries: {
  "2026-06-10": [["10:00", "12:00"]]
}
```

For local config JSON, store the same data under string keys:

```json
{
  "defaultWeekRules": {
    "1": [["09:00", "12:00"], ["13:00", "17:00"]],
    "3": [["10:00", "12:00"]]
  }
}
```

## Failure Handling

- Chrome target/profile not claimable: check the available Chrome inventory and intended account. If still unavailable, offer manual DevTools Console fallback. Do not continue in a different profile.
- 勤怠時刻修正申請 menu has `.empApplyMenuOff` or is otherwise disabled: inspect the date's holiday/workday status and available normal UI alternatives. Do not repeatedly click the disabled menu or infer that a hidden/API workaround is allowed. Keep the date pending if no permitted route exists.
- `Console context is not TeamSpirit...`: switch DevTools Console JavaScript context to the Visualforce iframe.
- `window.dijit is unavailable` or `Missing Dojo slider empWorkSlider*` while `dailyWorkCell*` exists: the script is running outside the page main world. Use DevTools Console in `AtkWorkTimeView` or inject the edited script as a page `<script>` element; do not write `empWorkSlider*` hidden inputs directly because the displayed row times will not recalculate.
- Month mismatch: navigate/select the correct month before running again.
- Unexpected no-plus date: inspect the row; if it is already `承認待ち`, add that date to `expectedExistingDates` and rerun. Otherwise stop.
- Rest input not found: read `references/observed-teamspirit-dom.md`, inspect the modal DOM, and update the script only after confirming the current field IDs.
- Any submit error: do not continue manually by guessing. Read the compact summary, inspect the affected date only, and report the exact status.
