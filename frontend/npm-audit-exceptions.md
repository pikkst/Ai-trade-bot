# Frontend npm Audit Policy

No frontend vulnerability exceptions are currently approved.

CI runs `npm audit --audit-level=moderate` without unconditional success handling, so any new advisory at moderate severity or above fails the security job. A future exception requires a machine-readable policy keyed by advisory and package, with an owner, justification, approval date, and expiry date, plus CI enforcement that rejects unknown or expired advisories.
