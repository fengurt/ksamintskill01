# Production configuration

## Source of truth

- 1Password vault: `Personal`
- API Credential item ID: `iwyz7yrtu5l3ijp5f3k6wdr6te`
- Item title: `Promese01 Tencent SMS Production`
- Dedicated CAM user: `promese01-sms-production`
- CAM user UIN: `100050986285`
- CAM policy: `Promese01SmsSend`
- CAM policy ID: `280290171`

The `username` field stores the CAM SecretId. The `credential` field stores the CAM SecretKey.
Never place either value in this file or any other documentation.

## Approved resources

| Purpose | Value |
| --- | --- |
| Qualification ID | `1203313` |
| Sign ID | `541989` |
| Sign name | `同泽科技` |
| Selected application | `apuch` |
| Selected SDK AppID | `1401087332` |
| Verification template ID | `1876280` |
| Template variables | `{1}` only |
| Alternative application | `EnchanteAI` / `1400842312` |
| Alternative application | Default application / `1400842064` |

Use the selected `apuch` application unless the user explicitly requests an alternative and the
replacement passes the same readiness checks.

## Production environment

```dotenv
TENCENT_SECRET_ID=<1Password username>
TENCENT_SECRET_KEY=<1Password credential>
TENCENT_SMS_SDK_APP_ID=1401087332
TENCENT_SMS_SIGN_NAME=同泽科技
TENCENT_SMS_TEMPLATE_ID=1876280
```

## CAM permissions

The dedicated custom policy should permit only:

- `name/sms:SendSms`
- `name/sms:DescribeSmsSignList`
- `name/sms:DescribeSmsTemplateList`
- `name/sms:SmsPackagesStatistics`
- `name/sms:PullSmsSendStatusByPhoneNumber` when delivery diagnosis is required.

All actions require resource `*` because Tencent server-side SMS APIs do not support resource-level
authorization.

## Expected readiness

- `DescribeSmsSignList`: sign `541989`, name `同泽科技`, status `0`.
- `DescribeSmsTemplateList`: template `1876280`, status `0`, one variable.
- `SmsPackagesStatistics`: the query succeeds for AppID `1401087332`. `packageCount` is
  informational because it counts packages created during the requested time window.
- `SendSms` with an empty phone array: `MissingParameter.EmptyPhoneNumberSet`. This is a
  non-delivery permission probe, not an end-to-end test.

## Error routing

- `UnauthorizedOperation`: inspect the CAM policy attachment and active key status.
- `InvalidAccessKeyId`: rotate/reinject the dedicated key from 1Password.
- `FailedOperation.SignatureIncorrectOrUnapproved`: recheck sign ID/name and carrier filing status.
- `FailedOperation.TemplateIncorrectOrUnapproved`: recheck template status and variable count.
- `InvalidParameterValue.TemplateParameter`: template `1876280` requires exactly one parameter.
- `MissingParameter.EmptyPhoneNumberSet`: credentials and `SendSms` authorization reached request
  validation; no SMS was sent.

Before changing requirements or policy syntax, verify against current official Tencent Cloud SMS
and CAM documentation.

## Verified delivery

On 2026-08-22, the production Node SDK sent with sign `同泽科技`, AppID `1401087332`, and
template `1876280`; Tencent returned `Ok` and the carrier receipt was `SUCCESS / DELIVRD`.
`APUCH / 542203` remains historical only after returning `FAIL / GB:0007` (number-portability
routing failure) for the authorized test destination.
