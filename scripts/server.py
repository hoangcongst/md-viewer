#!/usr/bin/env python3
"""
MD Viewer Server - Local web server for viewing Markdown files (SECURE VERSION)

Usage:
    python3 server.py [--port PORT] [--host HOST] [--history-file FILE] [--password PASSWORD]

Examples:
    python3 server.py --password mysecret
"""

import argparse
import fcntl
import json
import os
import re
import secrets
import sys
import threading
from datetime import datetime
from html import escape
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import markdown

# Configuration
DEFAULT_PORT = 8765
DEFAULT_HOST = "0.0.0.0"
DEFAULT_HISTORY_FILE = str(Path.home() / ".md-viewer-history.json")

# History lock for thread safety
_history_lock = threading.Lock()

# Security: Blocked paths and patterns
BLOCKED_PATHS = [
    '/etc', '/proc', '/sys', '/dev', '/var/log',
    '/.ssh', '/.gnupg', '/.aws', '/.docker',
]

BLOCKED_PATTERNS = [
    'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
    '.ssh/', '.gnupg/', '.aws/', '.docker/',
    '.env', '.netrc', '.pgpass', '.pypirc',
    'credentials', 'secret', 'private',
    '.key', '.pem', '.p12', '.pfx',
    '.htaccess', '.htpasswd',
    'shadow', 'passwd', 'master.passwd',
]

# Global state (set at runtime)
_config = {
    'history_file': DEFAULT_HISTORY_FILE,
    'password': None,
}


def is_path_allowed(file_path: str) -> tuple[bool, str]:
    """Check if path is allowed to be read. Returns (allowed, reason)"""
    path_lower = file_path.lower()
    
    # Only allow .md files
    if not file_path.endswith('.md'):
        return False, "Only .md files are allowed"
    
    # Check blocked absolute paths
    for blocked in BLOCKED_PATHS:
        if path_lower.startswith(blocked):
            return False, f"Access to system directory denied: {blocked}"
    
    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in path_lower:
            return False, f"Access to sensitive file denied"
    
    return True, ""


def sanitize_html_content(html: str) -> str:
    """Sanitize HTML to prevent XSS"""
    # Remove script tags and event handlers
    # This is a basic sanitizer - for production, use bleach library
    import re
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<script[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Remove event handlers (onerror, onclick, etc.)
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
    
    # Remove data: URLs that could execute code
    html = re.sub(r'data:text/html[^"\']*', '', html, flags=re.IGNORECASE)
    
    return html


# HTML Template for rendering
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown-dark.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data: https:;">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; min-height: 100vh; font-size: 16px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 16px; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 12px 16px; position: sticky; top: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
        .header h1 {{ color: #c9d1d9; font-size: 16px; font-weight: 600; }}
        .header-actions {{ display: flex; gap: 8px; }}
        .btn {{ background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-height: 44px; }}
        .btn:hover {{ background: #2ea043; }}
        .btn-secondary {{ background: #21262d; border: 1px solid #30363d; padding: 8px 16px; }}
        .btn-secondary:hover {{ background: #30363d; }}
        .content {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; margin-top: 16px; padding: 20px; }}
        .markdown-body {{ color: #c9d1d9; font-size: 16px; line-height: 1.6; }}
        .markdown-body h1 {{ font-size: 1.5em; border-bottom: 1px solid #30363d; padding-bottom: 0.3em; }}
        .markdown-body h2 {{ font-size: 1.3em; border-bottom: 1px solid #30363d; padding-bottom: 0.3em; }}
        .markdown-body h3 {{ font-size: 1.1em; }}
        .markdown-body code {{ background: #0d1117; padding: 0.2em 0.4em; border-radius: 4px; }}
        .markdown-body pre {{ background: #0d1117; border: 1px solid #30363d; border-radius: 8px; overflow-x: auto; }}
        .markdown-body pre code {{ background: transparent; }}
        .markdown-body a {{ color: #58a6ff; }}
        .markdown-body a:hover {{ text-decoration: underline; }}
        .markdown-body blockquote {{ border-left: 4px solid #3fb950; background: #0d1117; padding: 16px; border-radius: 0 8px 8px 0; }}
        .markdown-body table {{ border-collapse: collapse; width: 100%; overflow-x: auto; display: block; }}
        .markdown-body th, .markdown-body td {{ border: 1px solid #30363d; padding: 8px 12px; }}
        .markdown-body th {{ background: #0d1117; }}
        .history-list {{ list-style: none; padding: 0; }}
        .history-item {{ background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px; }}
        .history-item:hover {{ border-color: #58a6ff; }}
        .history-title {{ color: #58a6ff; font-weight: 600; font-size: 16px; word-break: break-word; }}
        .history-path {{ color: #8b949e; font-size: 12px; font-family: monospace; word-break: break-all; }}
        .history-time {{ color: #6e7681; font-size: 12px; }}
        .history-actions {{ margin-top: 8px; }}
        .empty-state {{ text-align: center; padding: 40px 20px; color: #8b949e; }}
        .file-path-form {{ display: flex; flex-direction: column; gap: 10px; }}
        .file-path-input {{ width: 100%; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 12px 16px; border-radius: 8px; font-size: 16px; min-height: 44px; }}
        .file-path-input:focus {{ outline: none; border-color: #58a6ff; }}
        .submit-btn {{ width: 100%; }}
        .error-message {{ background: #da3633; color: white; padding: 16px; border-radius: 8px; margin: 20px 0; word-break: break-word; }}
        .back-link {{ color: #58a6ff; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; margin-bottom: 16px; font-size: 16px; }}
        .back-link:hover {{ text-decoration: underline; }}
        .login-form {{ max-width: 400px; margin: 40px auto; }}
        .login-form input {{ width: 100%; margin-bottom: 12px; }}
        @media (max-width: 600px) {{ .container {{ padding: 8px; }} .content {{ padding: 12px; }} .btn {{ padding: 10px 16px; font-size: 14px; }} .markdown-body {{ font-size: 15px; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 MD Viewer</h1>
        <div class="header-actions">
            <a href="/" class="btn btn-secondary">🏠 Home</a>
            <a href="/history" class="btn btn-secondary">📜 History</a>
        </div>
    </div>
    <div class="container">
        {content}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
</body>
</html>
"""


class MDViewerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MD Viewer"""
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")
    
    def _check_auth(self, query) -> bool:
        """Check if request is authenticated"""
        password = _config.get('password')
        if not password:
            return True
        provided = query.get('token', [''])[0]
        return provided == password
    
    def _get_auth_param(self) -> str:
        """Get auth parameter for URLs"""
        password = _config.get('password')
        return f"&token={quote(password)}" if password else ""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # Check authentication
        if not self._check_auth(query):
            self._serve_login()
            return
        
        try:
            if path == '/':
                self._serve_home(query)
            elif path == '/history':
                self._serve_history(query)
            elif path == '/view':
                file_path = query.get('path', [''])[0]
                if file_path:
                    self._serve_markdown(unquote(file_path), query)
                else:
                    self._serve_home(query)
            elif path == '/api/history':
                self._serve_history_json(query)
            else:
                self._serve_404(query)
        except Exception as e:
            self._serve_error(str(e), query)
    
    def do_POST(self):
        """Handle POST for login"""
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            password = params.get('password', [''])[0]
            if password == _config.get('password'):
                # Redirect to home with token
                self.send_response(302)
                self.send_header('Location', f'/?token={quote(password)}')
                self.end_headers()
            else:
                self._serve_login(error="Invalid password")
        else:
            self._serve_404({})
    
    def _serve_login(self, error=None):
        """Serve login page"""
        error_html = f'<div class="error-message">{escape(error)}</div>' if error else ''
        content = f'''
        <div class="content login-form">
            <h2 style="color: #c9d1d9; margin-bottom: 20px; text-align: center;">🔐 Login Required</h2>
            {error_html}
            <form method="POST" action="/login">
                <input type="password" name="password" class="file-path-input" placeholder="Enter password" required />
                <button type="submit" class="btn submit-btn">Login</button>
            </form>
        </div>
        '''
        self._send_html(HTML_TEMPLATE.format(title="Login - MD Viewer", content=content))
    
    def _serve_home(self, query):
        auth_param = self._get_auth_param()
        content = f'''
        <div class="content">
            <h2 style="color: #c9d1d9; margin-bottom: 16px;">📂 Open Markdown File</h2>
            <form class="file-path-form" onsubmit="return openFile()">
                <input type="text" id="filePath" class="file-path-input" placeholder="Enter absolute path to .md file" />
                <button type="submit" class="btn submit-btn">📖 View File</button>
            </form>
            <p style="color: #8b949e; font-size: 14px; margin-top: 16px;">
                💡 Only .md files allowed. Sensitive paths blocked.
            </p>
        </div>
        <script>
            function openFile() {{
                const path = document.getElementById('filePath').value;
                if (path) {{
                    window.location.href = '/view?path=' + encodeURIComponent(path) + '{auth_param}';
                }}
                return false;
            }}
        </script>
        '''
        self._send_html(HTML_TEMPLATE.format(title="MD Viewer", content=content))
    
    def _serve_markdown(self, file_path, query):
        # Security: Check if path is allowed
        allowed, reason = is_path_allowed(file_path)
        if not allowed:
            self._serve_error(f"Access denied: {escape(reason)}", query)
            return
        
        path = Path(file_path).resolve()
        
        # Verify it's actually a .md file
        if path.suffix.lower() != '.md':
            self._serve_error("Only .md files are allowed", query)
            return
        
        if not path.exists():
            self._serve_error(f"File not found: {escape(file_path)}", query)
            return
        
        if not path.is_file():
            self._serve_error("Not a file", query)
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        except Exception as e:
            self._serve_error(f"Cannot read file: {escape(str(e))}", query)
            return
        
        # Convert markdown to HTML (without 'extra' extension to reduce XSS risk)
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
        ])
        html_content = md.convert(md_content)
        
        # Sanitize HTML to prevent XSS
        html_content = sanitize_html_content(html_content)
        
        # Add to history
        self._add_to_history(str(path), path.name)
        
        content = f'''
        <a href="/{self._get_auth_param()}" class="back-link">← Back</a>
        <div class="content">
            <article class="markdown-body">
                {html_content}
            </article>
        </div>
        '''
        self._send_html(HTML_TEMPLATE.format(title=f"{escape(path.name)} - MD Viewer", content=content))
    
    def _serve_history(self, query):
        history = self._load_history()
        auth_param = self._get_auth_param()
        
        if not history:
            content = '''
            <div class="content">
                <div class="empty-state">
                    <h2>📭 No history yet</h2>
                    <p>Files you view will appear here.</p>
                </div>
            </div>
            '''
        else:
            items = []
            for item in history:
                safe_path = quote(item.get('path', ''))
                items.append(f'''
                <li class="history-item">
                    <div class="history-info">
                        <div class="history-title">{escape(item.get('name', 'Unknown'))}</div>
                        <div class="history-path">{escape(item.get('path', ''))}</div>
                        <div class="history-time">{escape(item.get('timestamp', ''))}</div>
                    </div>
                    <div class="history-actions">
                        <a href="/view?path={safe_path}{auth_param}" class="btn">📖 Open</a>
                    </div>
                </li>
                ''')
            
            content = f'''
            <div class="content">
                <h2 style="color: #c9d1d9; margin-bottom: 16px;">📜 View History</h2>
                <ul class="history-list">
                    {''.join(items)}
                </ul>
            </div>
            '''
        
        self._send_html(HTML_TEMPLATE.format(title="History - MD Viewer", content=content))
    
    def _serve_history_json(self, query):
        if not self._check_auth(query):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode('utf-8'))
            return
        
        history = self._load_history()
        self._send_json(history)
    
    def _serve_404(self, query):
        content = '''
        <div class="content">
            <div class="empty-state">
                <h2>❌ 404 Not Found</h2>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/" class="btn" style="margin-top: 20px;">Go Home</a>
            </div>
        </div>
        '''
        self._send_html(HTML_TEMPLATE.format(title="404 - MD Viewer", content=content), 404)
    
    def _serve_error(self, message, query):
        content = f'''
        <a href="/{self._get_auth_param()}" class="back-link">← Back</a>
        <div class="error-message">
            <strong>❌ Error:</strong> {message}
        </div>
        '''
        self._send_html(HTML_TEMPLATE.format(title="Error - MD Viewer", content=content), 500)
    
    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _load_history(self):
        """Load history with file locking"""
        history_file = Path(_config['history_file'])
        
        with _history_lock:
            try:
                if history_file.exists():
                    with open(history_file, 'r', encoding='utf-8') as f:
                        # Use file lock for reading
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        try:
                            data = json.load(f)
                        finally:
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        return data
            except json.JSONDecodeError as e:
                print(f"History file corrupted, resetting: {e}")
                # Reset corrupted file
                self._init_history_file()
                return []
            except Exception as e:
                print(f"Error loading history: {e}")
        return []
    
    def _init_history_file(self):
        """Initialize history file if not exists"""
        history_file = Path(_config['history_file'])
        
        with _history_lock:
            try:
                history_file.parent.mkdir(parents=True, exist_ok=True)
                with open(history_file, 'w', encoding='utf-8') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump([], f)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception as e:
                print(f"Error initializing history file: {e}")
    
    def _add_to_history(self, path, name):
        """Add to history with file locking"""
        history_file = Path(_config['history_file'])
        
        with _history_lock:
            try:
                # Ensure file exists
                if not history_file.exists():
                    self._init_history_file()
                
                # Read current history
                history = []
                with open(history_file, 'r', encoding='utf-8') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    try:
                        history = json.load(f)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
                # Update history
                history = [h for h in history if h.get('path') != path]
                history.insert(0, {
                    'path': path,
                    'name': name,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                history = history[:50]
                
                # Write back with exclusive lock
                with open(history_file, 'w', encoding='utf-8') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    try:
                        json.dump(history, f, indent=2)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        
            except Exception as e:
                print(f"Error saving history: {e}")


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_password(length=12):
    """Generate a random password"""
    import string
    import random
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description="MD Viewer Server - Secure local web server for Markdown files")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--history-file", default=str(DEFAULT_HISTORY_FILE))
    parser.add_argument("--password", default=None, help="Custom password (auto-generated if not set)")
    
    args = parser.parse_args()
    
    # Auto-generate password if not provided
    password = args.password or generate_password()
    
    _config['history_file'] = args.history_file
    _config['password'] = password
    
    # Initialize history file on startup
    history_file = Path(_config['history_file'])
    if not history_file.exists():
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    else:
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    local_ip = get_local_ip()
    
    print("\n" + "=" * 60, flush=True)
    print("📄 MD Viewer Server Started", flush=True)
    print("=" * 60, flush=True)
    print(f"Local:    http://localhost:{args.port}", flush=True)
    print(f"Network:  http://{local_ip}:{args.port}", flush=True)
    print("-" * 60, flush=True)
    print(f"🔐 Password: {password}", flush=True)
    print("   ⚠️  SAVE THIS PASSWORD - Required for all links!", flush=True)
    print("=" * 60, flush=True)
    print("Press Ctrl+C to stop", flush=True)
    print(flush=True)
    
    server = HTTPServer((args.host, args.port), MDViewerHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()