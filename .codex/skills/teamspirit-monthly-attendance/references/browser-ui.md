# Browser UI fallback for attendance

Use this when the intended logged-in Chrome tab is available but direct console-script execution is unavailable or evaluation is read-only. Use the browser tool's documented locators and UI input APIs; do not execute mutations through read-only evaluation or paste code into DevTools through Computer Use.

## Prepare

1. Resolve and validate the private local config before browser work. Discover Chrome tabs through the available runtime rather than assuming a separate Playwright browser shares the user's session. Claim the tab matching `attendanceUrl`; verify the visible account and selected year/month.
2. Inspect only the requested date rows. Check day type, existing applications, and the application icon's `title`. `承認待ち` confirms an existing application; absence of a plus by itself does not confirm success.
3. Present the exact dates, start/end, every rest interval, notes, and totals for approval under `SKILL.md`. Existing approval of that same complete plan remains valid unless the plan changes. Apply the 8-hour work / 1-hour rest rule before submission.

## Register one date at a time

1. Click the target date's application plus and inspect the current menu. Read `observed-teamspirit-dom.md` for field IDs. If the correction menu is disabled, inspect the holiday path below instead of repeatedly clicking it.
2. Open 勤怠時刻修正申請. Enter the approved start/end and move focus out so any field-triggered refresh finishes. Recheck the displayed date and values before continuing.
3. Enable 休憩時間修正 when the plan has breaks. Inspect the checkbox state after the click. Add rows with `dialogApplyReviseRestAdd1` until each approved rest interval has its own row; fill both endpoints. If extra rows exist, use their visible delete buttons and verify the resulting row count. Never combine gaps across actual work.
4. Enter the approved note, move focus out, and read back start/end, checkbox state, every rest input, and note from the rendered form. Verify the worked minutes and minimum-rest rule. If anything differs, correct it before submission.
5. Click only the individual `empApplyDone1` button after approval. Wait for the dialog to close and inspect the target date's application icon for `承認待ち` or another explicit submitted state. Page refresh may finish after the dialog closes; verify the next date's displayed menu before entering values. A timeout alone does not justify resubmitting: inspect the target date first to avoid duplicates.
6. Stop on an unexplained failure and inspect that date. Continue independent dates only after the failure is understood. Record skipped/pending dates separately.

## Holiday dates

Company 所定休日 and public holidays are separate classifications. When a user explicitly reports work on a company holiday, inspect the permitted UI for holiday work, daily attendance entry, or a day-type request; do not assume 振替 is the only option. Disabled fields/menus must not be enabled or bypassed through scripts, hidden fields, or APIs. A 振替申請 affects another date, so require the exact paired dates and approval before submitting it. If no supported path exists, leave the worked date pending and explain the visible blocker.

## Verify

Read the application status for every requested date. For a representative submitted date, reopen its application to verify saved start/end and all rest intervals without changing it. Report submitted and pending dates and their separate totals. Pending approval may leave the attendance table's actual start/end and monthly total blank or unchanged; do not describe those values as already approved. Save a screenshot of the resulting status and include it in the final response when the browser tool requires proof of work. Never click monthly approval as part of individual registration.
