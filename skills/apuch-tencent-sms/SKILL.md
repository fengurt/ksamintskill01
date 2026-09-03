---
name: apuch-tencent-sms
description: Operate and validate the APUCH Tencent Cloud SMS production setup using credentials stored in 1Password. Use when an agent needs to inspect SMS readiness, configure an application, send an explicitly authorized test or OTP message, diagnose Tencent SMS errors, rotate the dedicated CAM key, or inject the Promese01 SMS configuration without exposing secrets.
---

# APUCH Tencent SMS

Use 1Password item `iwyz7yrtu5l3ijp5f3k6wdr6te` in vault `Personal` as the source of
truth. It selects the verified `同泽科技` production signature. Never copy credentials
from a personal `tccli` profile into production.

Read [references/configuration.md](references/configuration.md) before changing credentials,
CAM permissions, application selection, signatures, templates, or production configuration.

## Safety rules

- Never print, log, paste, or commit `username` or `credential`; they are the CAM SecretId and
  SecretKey.
- Never run `tccli configure list`, because it prints credentials.
- Retrieve secrets into shell variables from 1Password and unset them immediately after use.
- Use the dedicated CAM user `promese01-sms-production`. Its policy permits `SendSms` plus the
  three non-mutating readiness calls only.
- Treat `SendSms` as an external side effect. Require an explicit target phone number and explicit
  authorization to send. If either is missing, run readiness checks only.
- Do not use a guessed, dummy, database-extracted, or unrelated phone number.
- Preserve the selected application, signature, and template unless the user explicitly requests
  a change and Tencent reports the replacement as usable.

## Readiness check

Run:

```bash
/Users/af/.codex/skills/apuch-tencent-sms/scripts/check-readiness.sh
```

The script reads the 1Password item, calls only Tencent read APIs, and prints a secret-free JSON
summary. Require:

- sign status `0`;
- template status `0`;
- a successful package-statistics query; treat `packageCount` as informational because the API
  counts packages created inside the query window, not the current available balance;
- `ready: true`.

## Read a field

Prefer the item UUID over its title:

```bash
op item get iwyz7yrtu5l3ijp5f3k6wdr6te --vault Personal --format json
```

Do not add `--reveal` unless the value is captured without being printed.

For an authorized Tencent CLI action:

```bash
sms_secret_id="$(op item get iwyz7yrtu5l3ijp5f3k6wdr6te \
  --vault Personal --fields username --reveal)"
sms_secret_key="$(op item get iwyz7yrtu5l3ijp5f3k6wdr6te \
  --vault Personal --fields credential --reveal)"

tccli sms <Action> \
  --secretId "$sms_secret_id" \
  --secretKey "$sms_secret_key" \
  <parameters>

unset sms_secret_id sms_secret_key
```

Never enable shell tracing around this sequence.

## Send an authorized test

1. Run the readiness check.
2. Normalize the user-supplied mainland number to E.164, such as `+8613800138000`.
3. Generate a six-digit test code. Do not use a production OTP stored in Redis.
4. Prefer the application's Tencent Node SDK for the test so its request shape matches production.
   If `tccli` is required, use `--cli-unfold-argument`; do not pass JSON strings to its array
   parameters.
5. Call `SendSms` once with the selected SDK AppID, sign, template, one template parameter, and the
   explicit phone number.
6. Record only Tencent's request ID, serial number, status code, and message. Do not repeat the full
   phone number in logs or the final response.
7. Query delivery status only when the user asks or delivery must be verified.

Use `TemplateParamSet` with exactly one value because template `1876280` contains only `{1}`.

## Inject Promese01 production

When the user authorizes a production configuration change:

1. Back up `/opt/promese01/.env`.
2. Read secrets from 1Password without printing them.
3. Set the five variables documented in
   [references/configuration.md](references/configuration.md) in the target `.env`; preserve every
   unrelated variable.
4. Restrict `.env` to mode `600`.
5. Recreate only the API service unless another service changed.
6. Verify the container health endpoint and the public `/v1/health` endpoint.
7. Run the readiness check again.

Do not store secrets in a repository, command transcript, generated document, or 1Password Document
item. The API Credential item is the only secret-bearing item.

## Rotate the CAM key

1. Create a second access key for CAM user UIN `100050986285`.
2. Update the API Credential item atomically.
3. Inject the new key into production and recreate the API.
4. Verify readiness and one explicitly authorized test.
5. Disable, then delete, the old key only after successful verification.

Never delete the only active key and never expose either key during comparison.
