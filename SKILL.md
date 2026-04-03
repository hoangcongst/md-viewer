---
name: md-viewer
description: LAN-accessible web viewer for Markdown files with security features. TRIGGER when user says "cho tôi xem", "show me", "mở file", "view file", "xem md", "xem file này", or wants to review a .md file. Instead of reading/summarizing, generate a LAN link for user to view directly in browser from any device on WiFi.
---

# MD Viewer

## Key Principle

**When user says "show me the file", "view this file":**
- ❌ DO NOT read and summarize the content
- ✅ DO generate LAN link for user to view directly

User wants to VIEW the file themselves, not hear a summary.

## Security Features

- ✅ **Only .md files** - Blocks all other file types
- ✅ **Blocked paths** - Cannot access /etc, ~/.ssh, ~/.gnupg, etc.
- ✅ **Password protection** - Auto-generated password on first run
- ✅ **XSS protection** - Sanitizes HTML output
- ✅ **CSP headers** - Content Security Policy enforced

## Workflow

### Step 1: Start Server (Auto-generates password)

```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/md-viewer/scripts/server.py
```

Output:
```
📄 MD Viewer Server Started
============================================================
Local:    http://localhost:8765
Network:  http://10.0.10.93:8765
Password: a1b2c3d4e5f6  ← SAVE THIS!
============================================================
```

**Password is auto-generated. Save it!**

### Step 2: Generate Link with Password

```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/md-viewer/scripts/md-link.py /path/to/file.md --password YOUR_PASSWORD
```

Output:
```
📄 Markdown Viewer Link:
   http://10.0.10.93:8765/view?path=/path/to/file.md&token=YOUR_PASSWORD

🔐 Password protected
```

### Step 3: Share Link

Provide the full link including token:
```
http://10.0.10.93:8765/view?path=/path/to/file.md&token=PASSWORD
```

## Direct URL Format

```
http://<LAN-IP>:8765/view?path=/path/to/file.md&token=PASSWORD
```

## Get LAN IP

```bash
ipconfig getifaddr en0  # macOS
hostname -I | awk '{print $1}'  # Linux
```

## Blocked Paths

Automatically blocked:
- System: `/etc`, `/proc`, `/sys`, `/dev`, `/var/log`
- SSH: `~/.ssh/`, `id_rsa`, `id_dsa`, etc.
- GPG: `~/.gnupg/`
- AWS: `~/.aws/`
- Passwords: `.netrc`, `.pgpass`, `.env`
- Certs: `.pem`, `.key`, `.p12`, `.pfx`

## Features

- Dark theme (GitHub style)
- Syntax highlighting
- Mobile-friendly UI
- History tracking (50 files)
- Password authentication (required)
- XSS protection

## Server Options

```bash
python3 server.py [options]

Options:
  --port PORT          Port (default: 8765)
  --host HOST          Host (default: 0.0.0.0)
  --password PASSWORD  Use custom password (auto-generated if not set)
  --history-file FILE  History file path
```

## Resources

### scripts/

- `server.py` - Web server with security
- `md-link.py` - Link generator

### Dependencies

```bash
pip3 install markdown
```