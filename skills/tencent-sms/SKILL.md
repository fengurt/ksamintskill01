---
name: tencent-sms
description: Operate, validate, diagnose, and safely configure Tencent Cloud SMS using runtime-only credentials. Use for SMS readiness, sign/template problems, application integration, authorized test sends, or dedicated CAM key rotation.
---

# Tencent SMS

Operate Tencent Cloud SMS without exposing credentials, identifiers, recipients, or OTP values.

## Safety boundary

- Treat credentials, application IDs, sign and template IDs, phone numbers, and message parameters as sensitive.
- Resolve secrets only at runtime from the project's established secret manager. Never place resolved values in source control, chat, logs, screenshots, shell history, or agent memory.
- With 1Password, prefer `op run` and an ignored temporary env file containing only `op://` references. Never use `op item get --reveal`, `set -x`, `env`, or another command that dumps the environment.
- Use a dedicated least-privilege CAM identity for SMS, never an owner or administrator identity.
- A real SMS is an external side effect. Require an explicit recipient and explicit authorization for each send. Default to one message.
- Redact phone numbers in reports, retaining only the country code and final four digits.

## Resolve the project contract

Read the application's existing provider interface, deployment documentation, and secret-injection mechanism before changing anything. Obtain the secret-manager item or references from the project or user; never guess them or substitute another application's values.

Resolve these logical values at runtime:

- Tencent Secret ID and Secret Key
- SMS SDK App ID
- approved sign name or sign ID
- approved template ID
- Tencent region when the SDK requires one

Preserve the application's established environment-variable names. If a required value is absent, stop and report only its logical label.

## Readiness inspection

1. Confirm the secret-manager session is available without revealing values.
2. Confirm the CAM identity is dedicated to SMS and has only the required API permissions.
3. Query Tencent SMS for the configured application's sign and template status.
4. Confirm both are approved, active, and belong to the configured application.
5. Confirm the requested parameters match the approved template's count and order.
6. Report redacted authentication, application, sign, template, and send-readiness results.

A read-only readiness check never authorizes a send.

## Application configuration

Map runtime values into the existing SMS provider interface and validate configuration shape before restart or rollout. Preserve unrelated configuration and restart only the affected service.

For local commands, prefer:

```sh
op run --env-file path/to/ignored-refs.env -- command-that-does-not-print-secrets
```

The references file contains only `op://` references, never resolved values.

## Authorized test send

Before sending, record the caller's authorization, redacted destination, approved template purpose, expected parameter count, and whether the message is a test or production OTP. Send exactly one message unless the caller authorizes a larger bounded test.

Capture Tencent's request ID and result code. Do not capture credentials, full phone numbers, message parameters, or OTP values. API acceptance is not delivery; check delivery status separately when required.

## Diagnosis

Classify the failure before changing configuration:

- authentication or CAM denial
- application, sign, or template mismatch
- template parameter mismatch
- recipient or regional restriction
- rate limit or risk-control rejection
- account balance, qualification, or compliance state
- provider timeout or network failure
- application-side configuration or retry bug

Use Tencent's request ID and official error code to select the smallest corrective action. Do not rotate credentials for template, parameter, or compliance errors.

## Credential rotation

Rotate only the dedicated SMS CAM key and only with explicit authorization. Create the replacement, update the approved secret-manager item, validate a read-only Tencent call, deploy through the existing secret-injection mechanism, perform one authorized smoke test, then disable the old key. Delete it only after successful verification and the agreed rollback window.

## Completion report

Report readiness, application/sign/template consistency, whether a send occurred, the redacted recipient and Tencent request ID when applicable, deployment or rotation outcome, and any remaining blocker and owner. Never include secrets, full phone numbers, OTP values, private server addresses, internal paths, or raw environment output.
