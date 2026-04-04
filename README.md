# 📄 MD Viewer - LAN Markdown Viewer for OpenClaw

A secure, LAN-accessible web viewer for Markdown files. Perfect for reviewing AI-generated documentation on your phone, tablet, or e-reader while working with AI agents.

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🌐 **LAN Access** - View from any device on same WiFi (phone, tablet, e-reader)
- 📱 **E-ink Optimized** - Light theme, serif fonts, high contrast for e-readers
- 🔐 **Password Protected** - Auto-generated password saved to cookie for easy access
- 🛡️ **Security First** - Only `.md` files, blocked sensitive paths, XSS protection
- 📜 **History Tracking** - Quick access to recently viewed files
- 🎨 **Syntax Highlighting** - Code blocks rendered with highlight.js
- 🔄 **No Caching** - Always shows latest file content on refresh

## 🚀 Quick Start

### Install Skill

```bash
# Copy to OpenClaw skills directory
cp -r md-viewer ~/.openclaw/skills/
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
Network:  http://10.0.10.93:8765
------------------------------------------------------------
🔐 Password: 6mr9fgbisxwg
   ⚠️  SAVE THIS PASSWORD - Required for all links!
============================================================
```

### Generate Link

```bash
python3 ~/.openclaw/skills/md-viewer/scripts/md-link.py /path/to/file.md --password YOUR_PASSWORD
```

Output:
```
📄 Markdown Viewer Link:
   http://10.0.10.93:8765/view?path=/path/to/file.md&token=YOUR_PASSWORD

📁 File: README.md
🌐 LAN IP: 10.0.10.93
🔐 Password protected
```

### Open from Any Device

Just open the link from any device on the same WiFi network!

## 🔐 Authentication

### Cookie-Based Auth
- Password is saved to cookie on successful login
- No need to re-enter password for subsequent visits
- Cookie expires after 24 hours
- Invalid password clears the cookie

### Login Flow
1. First visit → Enter password
2. Password saved to cookie
3. Future visits → Automatic authentication
4. Wrong password → Cookie cleared, re-login required

## 🛡️ Security Features

### Only .md Files Allowed
```
❌ /view?path=/etc/passwd        → Blocked (not .md)
❌ /view?path=~/.ssh/id_rsa      → Blocked (sensitive path)
✅ /view?path=/project/README.md → Allowed
```

### Blocked Paths
- System: `/etc`, `/proc`, `/sys`, `/dev`
- SSH: `~/.ssh/`, `id_rsa`, `id_ed25519`
- GPG: `~/.gnupg/`
- Cloud: `~/.aws/`, `~/.gcp/`
- Passwords: `.netrc`, `.pgpass`, `.env`

### XSS Protection
- HTML sanitized
- Content Security Policy headers
- No raw HTML in markdown

## 📖 E-ink Optimization

Perfect for Kindle, Kobo, and other e-readers:
- **Light theme** - White background, black text
- **Serif fonts** - Georgia for comfortable reading
- **High contrast** - Clear borders and text
- **No animations** - Saves battery life
- **Normal font sizes** - Not too large, not too small

## 📖 Use Cases

### 1. AI Agent Integration
When working with AI agents (Claude, GPT, etc.) that create markdown files:

```
You: "Create a project plan"
Agent: "I've created plan.md. View at: http://10.0.10.93:8765/view?path=..."
```

### 2. Documentation Review
- View documentation on tablet while coding on laptop
- Read on e-reader (Kindle/Kobo) for comfortable reading
- Share meeting notes with team on same WiFi
- Review AI-generated plans on phone

### 3. E-reader Friendly
- Perfect for reading long documents on e-ink screens
- High contrast light theme
- Serif fonts for better readability

## 🔧 Configuration

```bash
python3 server.py [options]

Options:
  --port PORT          Port (default: 8765)
  --host HOST          Host (default: 0.0.0.0)
  --password PASSWORD  Custom password (auto-generated if not set)
  --history-file FILE  History file path
```

## 📦 Installation

### Requirements
- Python 3.8+
- `markdown` package

```bash
pip3 install markdown
```

### Install as OpenClaw Skill

```bash
# Method 1: Clone to skills directory
git clone https://github.com/hoangcongst/md-viewer.git ~/.openclaw/skills/md-viewer

# Method 2: Download and extract
curl -L https://github.com/hoangcongst/md-viewer/archive/main.zip -o md-viewer.zip
unzip md-viewer.zip -d ~/.openclaw/skills/
mv ~/.openclaw/skills/md-viewer-main ~/.openclaw/skills/md-viewer
```

## 🤝 Integration with AI Agents

### For OpenClaw Users

The skill automatically triggers when you say:
- "cho tôi xem file md"
- "show me the file"
- "xem file này"
- "mở file"

The agent will generate a LAN link instead of reading/summarizing.

### For Other AI Platforms

Add this to your AI's instructions:

```
When user wants to view a markdown file:
1. Start server: python3 ~/.openclaw/skills/md-viewer/scripts/server.py
2. Note the auto-generated password
3. Generate link: python3 md-link.py /path/to/file.md --password PASSWORD
4. Return the link to user
```

## 📁 Project Structure

```
md-viewer/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
└── scripts/
    ├── server.py         # Web server
    └── md-link.py        # Link generator
```

## 🔄 File Refresh

Files are always reloaded on page refresh:
- `Cache-Control: no-store` headers
- `Pragma: no-cache` headers
- No browser caching
- Always shows latest file content

## 🔒 Security Notes

⚠️ **Important:**
- Password is auto-generated on each server start
- Save the password immediately - it's required for all links
- Password saved in cookie for 24 hours
- Anyone on same WiFi can access if they have the password
- Stop server when not needed: `pkill -f server.py`
- Only use on trusted networks (home/office)

## 🙏 Acknowledgments

- [markdown](https://github.com/Python-Markdown/markdown) - Python Markdown parser
- [highlight.js](https://highlightjs.org/) - Syntax highlighting
- [OpenClaw](https://openclaw.ai) - AI agent platform

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ for OpenClaw users