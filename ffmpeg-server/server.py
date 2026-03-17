#!/usr/bin/env python3
"""FFmpeg subtitle extraction server for Kodi addon.

Runs on a local server (Orange Pi, NAS, PC) and extracts subtitles
from streaming URLs using FFmpeg. Much faster than Python MKV parsing.

Usage:
    docker compose up -d
    # or: python3 server.py
"""

import subprocess
import tempfile
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger('ffmpeg-server')

PORT = int(os.environ.get('PORT', 7497))


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Health check."""
        if self.path == '/health':
            self._json_response({'status': 'ok'})
        else:
            self._json_response({'error': 'Use POST /extract'}, 400)

    def do_POST(self):
        if self.path != '/extract':
            self._json_response({'error': 'Not found'}, 404)
            return

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception:
            self._json_response({'error': 'Invalid JSON'}, 400)
            return

        url = body.get('url', '')
        stream_index = body.get('stream_index', 0)
        output_format = body.get('format', 'srt')

        if not url:
            self._json_response({'error': 'Missing url'}, 400)
            return

        log.info(f"Extracting stream {stream_index} from {url[:80]}...")

        try:
            result = extract_subtitles(url, stream_index, output_format)
            if result:
                log.info(f"Success: {len(result)} bytes")
                self._json_response({'subtitles': result, 'format': output_format})
            else:
                self._json_response({'error': 'No subtitles extracted'}, 404)
        except Exception as e:
            log.error(f"Extraction failed: {e}")
            self._json_response({'error': str(e)}, 500)

    def do_OPTIONS(self):
        """CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Suppress default access logs


def extract_subtitles(url, stream_index=0, output_format='srt'):
    """Extract subtitles using FFmpeg."""
    codec_map = {
        'srt': 'srt',
        'ass': 'ass',
        'ssa': 'ass',
        'vtt': 'webvtt',
    }
    codec = codec_map.get(output_format, 'srt')
    ext = output_format if output_format != 'ssa' else 'ass'

    with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', url,
            '-map', f'0:s:{stream_index}',
            '-c:s', codec,
            tmp_path
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            # Try to get useful error info
            err = result.stderr[-500:] if result.stderr else 'Unknown error'
            raise RuntimeError(f"FFmpeg failed (code {result.returncode}): {err}")

        with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if not content or len(content.strip()) < 10:
            return None

        return content

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def get_streams(url):
    """Get subtitle stream info using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        '-select_streams', 's',
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return []
    data = json.loads(result.stdout)
    return data.get('streams', [])


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    log.info(f"FFmpeg subtitle server running on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.shutdown()
