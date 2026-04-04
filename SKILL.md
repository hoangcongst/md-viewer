---
name: md-viewer
description: Secure LAN-accessible web viewer for Markdown files optimized for e-readers. TRIGGER when user says "cho tôi xem", "show me", "mở file", "view file", "xem md", "xem file này", or wants to review a .md file. Instead of reading/summarizing, generate a LAN link for user to view directly in browser from any device on WiFi.
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
- ✅ **Password protection** - Auto-generated password with cookie auth
- ✅ **XSS protection** - HTML sanitized with bleach library
- ✅ **CSP headers** - Content Security Policy enforced
- ✅ **Localhost default** - Binds to 127.0.0.1 by default (secure)
- ✅ **No password in URL** - Cookie-based auth, no token leakage
- ✅ **No caching** - Files always refresh on page reload

## Workflow

### Step 1: Start Server (Auto-generates password)

```bash
python3 ~/.openclaw/skills/md-viewer/scripts/server.py
```

Output:
```
📄 MD Viewer Server Started
============================================================
Local:    http://localhost:8765
Network:  Disabled (localhost only)
------------------------------------------------------------
💡 Use --host 0.0.0.0 for LAN access
------------------------------------------------------------
🔐 Password: a1b2c3d4e5f6
   ⚠️  SAVE THIS PASSWORD - Required for login!
============================================================
```

### Step 2: Open in Browser

1. Open `http://localhost:8765` in browser
2. Enter password
3. Password saved to cookie (24 hours)
4. View files freely

### Step 3: Enable LAN Access (Optional)

```bash
python3 ~/.openclaw/skills/md-viewer/scripts/server.py --host 0.0.0.0
```

⚠️ **Warning**: Anyone on same WiFi can access!

## Server Options

```bash
python3 ~/.openclaw/skills/md-viewer/scripts/server.py [options]

Options:
  --host HOST          Host (default: 127.0.0.1, use 0.0.0.0 for LAN)
  --port PORT          Port (default: 8765)
  --password PASSWORD  Custom password (auto-generated if not set)
  --no-history         Disable history tracking for privacy
```

## Security Best Practices

1. **Default is localhost only** - Secure by default
2. **Use --host 0.0.0.0 only on trusted networks**
3. **Password stored in cookie, not URL** - No leakage via logs
4. **Install bleach for robust XSS protection**: `pip3 install bleach`
5. **Use --no-history** if privacy is critical

## Blocked Paths

Automatically blocked:
- System: `/etc`, `/proc`, `/sys`, `/dev`, `/var/log`
- SSH: `~/.ssh/`, `id_rsa`, `id_dsa`, etc.
- GPG: `~/.gnupg/`
- Cloud: `~/.aws/`, `~/.gcp/`
- Passwords: `.netrc`, `.pgpass`, `.env`
- Certs: `.pem`, `.key`, `.p12`, `.pfx`

## Features

- Light theme (e-ink optimized)
- Serif fonts for comfortable reading
- High contrast for e-readers
- Syntax highlighting
- Mobile-friendly UI
- History tracking (50 files, optional)
- Cookie-based authentication
- XSS protection with bleach

## Dependencies

```bash
pip3 install markdown bleach
```

## Resources

### scripts/

- `server.py` - Web server with security features
- `md-link.py` - Link generator helper