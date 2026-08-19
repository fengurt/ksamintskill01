# Never touch (denylist)

Do not delete, trash, or `--apply` these without an explicit per-path user instruction naming the exact path.

## System and identity

- `/System`, `/usr`, `/bin`, `/sbin`, `/private/var/db`
- `~/Library/Keychains`, `/Library/Keychains`
- `~/Library/Mobile Documents/` (iCloud Drive)
- Any `*.photoslibrary` bundle
- `~/Library/Application Support/MobileSync/Backup` (iOS backups) unless named
- `~/Library/Messages/Attachments`
- Provisioning profiles / `_CodeSignature/` inside `.app` bundles
- `com.apple.*` LaunchAgents / LaunchDaemons / Preferences

## Password / VPN / security

- 1Password, Bitwarden, LastPass, KeePassXC vaults and support dirs
- VPN / proxy configs: Clash*, Surge, Shadowsocks, V2Ray, Tailscale, WireGuard, OpenVPN
- SSH private keys: `~/.ssh/` (never bulk-delete)

## AI / agent tool state (protect by default)

- Cursor, Claude, ChatGPT, Codex, Ollama app data under Application Support
  (caches under `~/Library/Caches` for those apps may be Safe-tier after quit)

## User media (UserData — never batch)

- WhatsApp / WeChat Group Containers (guide in-app storage managers)
- Mail Downloads / Mail attachments
- Photos, Music, Movies libraries

## Risky vendor roots (low confidence orphans)

Treat as UserData / skip unless the parent app is confirmed uninstalled:

- `~/Library/Application Support/Google`
- `~/Library/Application Support/Adobe`
- `~/Library/Application Support/Microsoft`
- `~/Library/Application Support/JetBrains`
- `~/Library/Group Containers/*` matching the above
