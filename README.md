# 📄 MD Viewer - Secure LAN Markdown Viewer for OpenClaw

A secure, LAN-accessible web viewer for Markdown files. Perfect for reviewing AI-generated documentation on your phone, tablet, or e-reader while working with AI agents.

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🌐 **LAN Access** - View from any device on same WiFi (opt-in)
- 📱 **E-ink Optimized** - Light theme, serif fonts, high contrast for e-readers
- 🔐 **Secure by Default** - Localhost only, no password in URL
- 🍪 **Cookie Auth** - Password saved to cookie (24h), no URL leakage
- 🛡️ **XSS Protection** - HTML sanitized with bleach library
- 📜 **History Tracking** - Optional, can be disabled for privacy
- 🔄 **No Caching** - Always shows latest file content on refresh

## 🔒 Security Features

### Secure by Default
- **Localhost only** - Binds to 127.0.0.1 by default
- **No password in URL** - Cookie-based authentication
- **Bleach sanitization** - Robust XSS protection
- **Blocked sensitive paths** - Cannot access /etc, ~/.ssh, etc.
- **No caching headers** - Files always refresh

### Security Best Practices

```bash
# SECURE: Localhost only (default)
python3 ~/.openclaw/skills/md-viewer/scripts/server.py

# LAN ACCESS: Use only on trusted networks
python3 ~/.openclaw/skills/md-viewer/scripts/server.py --host 0.0.0.0

# PRIVACY: Disable history tracking
python3 ~/.openclaw/skills/md-viewer/scripts/server.py --no-history
```

## 🚀 Quick Start

### Install

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/hoangcongst/md-viewer.git ~/.openclaw/skills/md-viewer

# Install dependencies
pip3 install markdown bleach
```

### Start Server

```bash
python3 ~/.openclaw/skills/md-viewer/scripts/server.py
```

Output:
```
============================================================
📄 MD Viewer Server Started
============================================================
Local:    http://localhost:8765
Network:  Disabled (localhost only)
------------------------------------------------------------
💡 Use --host 0.0.0.0 for LAN access
------------------------------------------------------------
🔐 Password: xk9mz2p7q4w8
   ⚠️  SAVE THIS PASSWORD - Required for login!
============================================================
```

### Use

1. Open `http://localhost:8765` in browser
2. Enter password
3. Password saved to cookie for 24 hours
4. View .md files freely

## 🔐 Authentication

### Cookie-Based Auth
- Password saved to HttpOnly cookie on login
- Cookie expires after 24 hours
- No password in URL (no log leakage)
- Wrong password clears cookie

### Why No Password in URL?
- URLs are logged by browsers, proxies, and servers
- URLs can be leaked via Referer header
- URLs can be shared accidentally
- Cookie-based auth is more secure

## 📖 E-ink Optimization

Perfect for Kindle, Kobo, and other e-readers:
- **Light theme** - White background, black text
- **Serif fonts** - Georgia for comfortable reading
- **High contrast** - Clear borders and text
- **No animations** - Saves battery life
- **Normal font sizes** - Comfortable reading

## 🛡️ Security Details

### Blocked Paths
```
❌ /etc/*, /proc/*, /sys/*, /dev/*, /var/log/*
❌ ~/.ssh/*, id_rsa, id_ed25519
❌ ~/.gnupg/*
❌ ~/.aws/*, ~/.gcp/*
❌ .netrc, .pgpass, .env
❌ *.pem, *.key, *.p12, *.pfx
```

### XSS Protection
- HTML sanitized with bleach library
- Only safe tags allowed
- Only safe attributes allowed
- JavaScript blocked

### No Caching
```
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Expires: 0
```

## 🔧 Configuration

```bash
python3 server.py [options]

Options:
  --host HOST          Host to bind (default: 127.0.0.1)
                       Use 0.0.0.0 for LAN access (caution!)
  --port PORT          Port (default: 8765)
  --password PASSWORD  Custom password (auto-generated if not set)
  --no-history         Disable history tracking for privacy
```

## 📦 Installation

### Requirements
- Python 3.8+
- `markdown` package (required)
- `bleach` package (recommended for XSS protection)

```bash
pip3 install markdown bleach
```

## 🤝 Integration with AI Agents

### For OpenClaw Users

The skill automatically triggers when you say:
- "cho tôi xem file md"
- "show me the file"
- "xem file này"
- "mở file"

The agent will start the server and provide a link.

### For Other AI Platforms

Add this to your AI's instructions:

```
When user wants to view a markdown file:
1. Start server: python3 ~/.openclaw/skills/md-viewer/scripts/server.py
2. Note the auto-generated password
3. Tell user to open http://localhost:8765 and enter password
4. User can then view files
```

## 📁 Project Structure

```
md-viewer/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
└── scripts/
    ├── server.py         # Web server
    └── md-link.py        # Link generator (legacy)
```

## 🔒 Security Notes

⚠️ **Important:**

1. **Default is secure** - localhost only, no LAN exposure
2. **Use --host 0.0.0.0 only on trusted networks**
3. **Password never in URL** - Cookie-based auth
4. **Install bleach** for robust XSS protection
5. **Use --no-history** if privacy is critical
6. **Stop server when not needed**: `pkill -f server.py`

## 🙏 Acknowledgments

- [markdown](https://github.com/Python-Markdown/markdown) - Python Markdown parser
- [bleach](https://github.com/mozilla/bleach) - HTML sanitization
- [highlight.js](https://highlightjs.org/) - Syntax highlighting
- [OpenClaw](https://openclaw.ai) - AI agent platform

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ for OpenClaw users