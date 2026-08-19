#!/usr/bin/env bash
set -euo pipefail

item_id="${APUCH_SMS_OP_ITEM_ID:-iwyz7yrtu5l3ijp5f3k6wdr6te}"
vault="${APUCH_SMS_OP_VAULT:-Personal}"

for required_command in op tccli jq; do
  command -v "$required_command" >/dev/null || {
    printf 'Missing required command: %s\n' "$required_command" >&2
    exit 1
  }
done

item_json="$(op item get "$item_id" --vault "$vault" --format json --reveal)"

field_value() {
  local field_name="$1"
  printf '%s' "$item_json" |
    jq -er --arg field_name "$field_name" \
      '.fields[] | select(.id == $field_name or .label == $field_name) | .value' |
    head -n 1
}

secret_id="$(field_value username)"
secret_key="$(field_value credential)"
sign_id="$(field_value 'Sign ID')"
sign_name="$(field_value 'Sign Name')"
sdk_app_id="$(field_value 'SMS SDK AppID')"
template_id="$(field_value 'SMS Template ID')"

if begin_hour="$(date -u -v-29d +%Y%m%d%H 2>/dev/null)"; then
  end_hour="$(date -u -v-1H +%Y%m%d%H)"
else
  begin_hour="$(date -u -d '29 days ago' +%Y%m%d%H)"
  end_hour="$(date -u -d '1 hour ago' +%Y%m%d%H)"
fi

sign_json="$(
  tccli sms DescribeSmsSignList \
    --secretId "$secret_id" \
    --secretKey "$secret_key" \
    --SignIdSet "[$sign_id]" \
    --International 0
)"

template_json="$(
  tccli sms DescribeSmsTemplateList \
    --secretId "$secret_id" \
    --secretKey "$secret_key" \
    --International 0 \
    --TemplateIdSet "[$template_id]"
)"

packages_json="$(
  tccli sms SmsPackagesStatistics \
    --secretId "$secret_id" \
    --secretKey "$secret_key" \
    --SmsSdkAppId "$sdk_app_id" \
    --Limit 10 \
    --Offset 0 \
    --BeginTime "$begin_hour" \
    --EndTime "$end_hour"
)"

unset secret_id secret_key item_json

jq -n \
  --arg itemId "$item_id" \
  --arg sdkAppId "$sdk_app_id" \
  --arg signName "$sign_name" \
  --argjson sign "$sign_json" \
  --argjson template "$template_json" \
  --argjson packages "$packages_json" \
  '{
    itemId: $itemId,
    sdkAppId: $sdkAppId,
    sign: {
      id: ($sign.DescribeSignListStatusSet[0].SignId // null),
      name: ($sign.DescribeSignListStatusSet[0].SignName // $signName),
      status: ($sign.DescribeSignListStatusSet[0].StatusCode // null)
    },
    template: {
      id: ($template.DescribeTemplateStatusSet[0].TemplateId // null),
      name: ($template.DescribeTemplateStatusSet[0].TemplateName // null),
      status: ($template.DescribeTemplateStatusSet[0].StatusCode // null)
    },
    packageCount: ($packages.SmsPackagesStatisticsSet | length),
    ready: (
      $sign.DescribeSignListStatusSet[0].StatusCode == 0 and
      $template.DescribeTemplateStatusSet[0].StatusCode == 0
    )
  }'
