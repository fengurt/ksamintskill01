# Deploying LLM Hub to a Tencent Cloud (AMD64) server

The container has **zero npm dependencies** and serves the gateway + dashboard on port `7878`.

## 0. Concepts — the access pair

Provider keys are **never shipped in plaintext**. Access requires **two halves**:

1. **The local PEM** (`secrets/llmhub_private.pem`) — decrypts the encrypted key store `secrets/keys.enc` (hybrid RSA-4096 + AES-256-GCM). Without it, `keys.enc` is useless ciphertext.
2. **A proxy API key** — what clients send to call the gateway. One **admin key** (manage) + any number of **user keys** (gateway only), stored in `gui/data/keys.json`.

So even if `keys.enc` leaks, an attacker can't read the provider keys; and even with the PEM, they can't call the gateway without a proxy key.

## 1. Prepare the encrypted store locally

The deploy **access pair** (private PEM + admin proxy key) is stored in 1Password — item **"LLM Hub Deploy"** (`op://Personal/LLM Hub Deploy`). Pull it, then seal the provider keys:

```bash
cd ~/.cursor/skills/llm-hub/gui
./scripts/pull-deploy-secrets.sh    # 1Password -> secrets/*.pem + deploy.env (LLMHUB_ADMIN_KEY)
./scripts/encrypt-keys.sh           # resolves every provider key from 1Password -> secrets/keys.enc
```

First-time setup (only if the keypair doesn't exist yet) — generate and store it:

```bash
./scripts/gen-keypair.sh            # -> secrets/llmhub_private.pem (SECRET) + llmhub_public.pem
#   optional passphrase: LLMHUB_PEM_PASSPHRASE=... ./scripts/gen-keypair.sh
# then save the PEMs + a strong admin key into 1Password ("LLM Hub Deploy")
```

To rotate provider keys later: update 1Password, re-run `encrypt-keys.sh`, re-ship `keys.enc`, restart.

## 2. Ship to the server

```bash
# Tencent server, Ubuntu/TencentOS, Docker installed (see step 4 if not).
rsync -av --exclude data ~/.cursor/skills/llm-hub/  user@SERVER:/opt/llm-hub/
# copies registry.tsv + gui/ including secrets/keys.enc, secrets/llmhub_private.pem, deploy.env
```

For stricter separation, ship the PEM out-of-band (not in the same rsync) and place it at `gui/secrets/llmhub_private.pem` on the server.

## 3. Run with Docker Compose (on the server)

```bash
cd /opt/llm-hub/gui
docker compose up -d --build
docker compose logs -f          # first run prints the admin key only if you didn't set one
```

Dashboard: `http://SERVER_IP:7878`  ·  Gateway: `http://SERVER_IP:7878/v1`

## 4. If Docker isn't installed

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
```

## 5. Tencent Cloud specifics

- **Security Group**: add an inbound rule for TCP `7878` (or, with the reverse proxy below, only `443`).
- **Public access**: use the instance's public IP / EIP.
- **HTTPS (recommended)** — put Caddy in front for automatic TLS:

```caddyfile
# /etc/caddy/Caddyfile   (point a domain's A record at the server first)
llm.yourdomain.com {
    reverse_proxy 127.0.0.1:7878
}
```

Then open `443` in the security group instead of exposing `7878` publicly.

## 6. Use the gateway (one key, all providers)

```bash
curl https://llm.yourdomain.com/v1/chat/completions \
  -H "Authorization: Bearer $LLMHUB_USER_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"deepseek:deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
```

- Model format: `provider:model` (e.g. `ali-tongyi:qwen3.7-max`, `openrouter:openai/gpt-4o-mini`).
- `GET /v1/models` lists all available models (prefixed by provider).
- Issue user keys in the dashboard → **⚿ API Keys**.

## 7. Cross-building the image from macOS (alternative to building on server)

```bash
cd ~/.cursor/skills/llm-hub
docker buildx build --platform linux/amd64 -f gui/Dockerfile -t llm-hub:latest --load .
docker save llm-hub:latest | gzip | ssh user@SERVER 'gunzip | docker load'
# then `docker compose up -d` on the server (it will reuse the image)
```

## Updating

```bash
cd /opt/llm-hub/gui && git pull 2>/dev/null; docker compose up -d --build
```

## Security notes

- Keep `deploy.env` and `secrets/` off git (already in `.gitignore`); the PEM is never in the Docker image (`.dockerignore`).
- `keys.enc` is encrypted at rest — safe to back up. The **private PEM** is the sensitive half; restrict it to `chmod 600` and the deploy host only.
- Always front with HTTPS in production; the admin key grants full control.
- Rotate the admin key by editing `deploy.env` and restarting; rotate provider keys via `encrypt-keys.sh`.
