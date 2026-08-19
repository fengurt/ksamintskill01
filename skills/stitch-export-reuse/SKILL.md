---
name: stitch-export-reuse
description: Export Stitch project screen images and HTML code with OAuth, then download via curl -L for reuse across projects.
---

# Stitch Export Reuse Skill

## Purpose

Batch export Stitch screens by `projectId` + `screenId` list, then download:
- Screenshot image URL
- HTML/code URL

The output is a local folder with `.png`, `.html`, and `manifest.json`.

## Security Baseline (Mandatory)

- Never hardcode API keys, OAuth tokens, or secrets into skill files.
- Always pass credentials through environment variables.
- Rotate any credential that was pasted in plain text.

Required runtime env:

```bash
export STITCH_ACCESS_TOKEN="<oauth_access_token>"
export GOOGLE_CLOUD_PROJECT="<gcp_project_id_with_stitch_api_enabled>"
```

## One-Time Prerequisites

1. Enable Stitch API on your selected GCP project:

```bash
gcloud services enable stitch.googleapis.com --project "$GOOGLE_CLOUD_PROJECT"
```

2. Configure ADC quota project:

```bash
gcloud config set project "$GOOGLE_CLOUD_PROJECT"
gcloud auth application-default set-quota-project "$GOOGLE_CLOUD_PROJECT"
```

3. Get OAuth token:

```bash
gcloud auth application-default login
gcloud auth application-default print-access-token
```

## Install SDK

```bash
npm init -y
npm install @google/stitch-sdk
```

## Export Script Template

Create `export_and_download.mjs`:

```js
import fs from "fs/promises";
import path from "path";
import { StitchToolClient, Stitch } from "@google/stitch-sdk";

const accessToken = process.env.STITCH_ACCESS_TOKEN;
const cloudProjectId = process.env.GOOGLE_CLOUD_PROJECT;
const projectId = "<stitch_project_id>";
const screens = [
  { id: "<screen_id_1>", title: "<slug_1>" },
  { id: "<screen_id_2>", title: "<slug_2>" },
];

if (!accessToken || !cloudProjectId) {
  throw new Error("Missing STITCH_ACCESS_TOKEN or GOOGLE_CLOUD_PROJECT");
}

const outDir = path.resolve("downloads");
await fs.mkdir(outDir, { recursive: true });

const client = new StitchToolClient({ accessToken, projectId: cloudProjectId });
const stitch = new Stitch(client);
const project = stitch.project(projectId);

const manifest = [];
for (const entry of screens) {
  const screen = await project.getScreen(entry.id);
  const imageUrl = await screen.getImage();
  const htmlUrl = await screen.getHtml();
  manifest.push({ ...entry, imageUrl, htmlUrl });
}

await fs.writeFile(path.join(outDir, "manifest.json"), JSON.stringify(manifest, null, 2));
await client.close();
console.log("manifest-ready");
```

Run:

```bash
node export_and_download.mjs
```

## Download via curl -L

```bash
python3 - <<'PY'
import json, subprocess
from pathlib import Path

base = Path("downloads")
manifest = json.loads((base / "manifest.json").read_text())

for item in manifest:
    png_path = base / f"{item['title']}_{item['id']}.png"
    html_path = base / f"{item['title']}_{item['id']}.html"
    subprocess.run(["curl", "-L", item["imageUrl"], "-o", str(png_path)], check=True)
    subprocess.run(["curl", "-L", item["htmlUrl"], "-o", str(html_path)], check=True)

print(f"downloaded {len(manifest)} screens")
PY
```

## Common Failures

- `API keys are not supported`: use OAuth `STITCH_ACCESS_TOKEN`, not API key.
- `Stitch API has not been used`: enable `stitch.googleapis.com` on quota project.
- `serviceusage.services.use` permission error: quota project IAM is missing.
