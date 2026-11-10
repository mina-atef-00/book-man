# Camofox Browser Backend Setup

Camofox is the local browser backend Hermes uses for `browser_navigate`, `browser_click`, etc. It wraps Camoufox (a Firefox fork with fingerprint spoofing).

## Prerequisites

- `camofox-browser` npm global binary (`npm install -g @askjo/camofox-browser`)
- `Xvfb` for headless operation (Fedora: `sudo dnf install xorg-x11-server-Xvfb`)
- `CAMOFOX_URL` env var set per-profile (see below)

## Systemd User Service

Create `~/.config/systemd/user/camofox-browser.service`:

```ini
[Unit]
Description=Camofox browser automation server
After=network.target

[Service]
Type=simple
ExecStart=/home/linuxbrew/.linuxbrew/bin/camofox-browser
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Then:

```bash
systemctl --user daemon-reload
systemctl --user enable --now camofox-browser.service
```

## Verify

```bash
curl http://localhost:9377/health
# Should return 200
```

## Profile .env

`CAMOFOX_URL` must be in each profile's `.env` that needs browser tools.
Root `~/.hermes/.env` is NOT inherited by profiles.

- **Default profile:** `~/.hermes/.env` → `CAMOFOX_URL=http://localhost:9377`
- **book-man profile:** `~/.hermes/profiles/book-man/.env` → add `CAMOFOX_URL=http://localhost:9377`
