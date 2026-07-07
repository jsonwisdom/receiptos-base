# Daily Briefing SMTP App Password Lane

Status: `SMTP_APP_PASSWORD_LANE_LOCKED`

This document replaces the high-friction Gmail OAuth path for the JayOps Daily Briefing delivery lane.

## Required secrets

```txt
SMTP_USER
SMTP_PASS
```

Current workflow sets these non-secret values directly:

```txt
DAILY_BRIEFING_TO=jaywisdom44@gmail.com
DAILY_BRIEFING_FROM=jaywisdom44@gmail.com
```

## Gmail setup

1. Open Google Account Security.
2. Enable 2-Step Verification.
3. Create an App Password.
4. Select Mail or name it `GitHub Actions`.
5. Copy the 16-character password.
6. Add it to GitHub Actions secrets as `SMTP_PASS`.
7. Add `SMTP_USER` as the Gmail sender address.

## GitHub secrets

```txt
SMTP_USER=jaywisdom44@gmail.com
SMTP_PASS=<16-character Google app password>
```

Do not store app passwords in source code, issues, comments, screenshots, or logs.

## Delivery behavior

The sender uses direct TLS SMTP:

```txt
host=smtp.gmail.com
port=465
```

If either `SMTP_USER` or `SMTP_PASS` is missing, the script renders the briefing and exits in dry-run mode:

```txt
DRY_RUN=true: SMTP_USER or SMTP_PASS missing; rendered briefing only.
```

On accepted SMTP delivery, the script emits:

```txt
EMAIL_DELIVERY_GREEN provider=smtp.gmail.com message_id=not_returned_by_smtp
```

SMTP does not return a Gmail API message ID. The inbox receipt is the delivery witness.

## Invariants

```txt
NO_TRUTH_CLAIMS
NO_SCORES
NO_RISK_SUMMARIES
WITNESS_OBJECTS_ONLY
AUTHORITY_FALSE
```
