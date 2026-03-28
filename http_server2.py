#!/usr/bin/env python3
"""http_server2 - HTTP/1.1 server from raw sockets."""
import argparse, socket, os, mimetypes, datetime

MIME = {'.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
        '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
        '.gif': 'image/gif', '.txt': 'text/plain', '.svg': 'image/svg+xml'}

def handle_request(conn, root):
    data = conn.recv(8192).decode(errors='replace')
    if not data: return
    lines = data.split('\r\n')
    method, path, _ = lines[0].split(' ', 2)
    path = path.split('?')[0]
    if path == '/': path = '/index.html'
    filepath = os.path.join(root, path.lstrip('/'))
    filepath = os.path.realpath(filepath)
    if not filepath.startswith(os.path.realpath(root)):
        send_response(conn, 403, "Forbidden", b"403 Forbidden")
        return
    if os.path.isfile(filepath):
        ext = os.path.splitext(filepath)[1]
        ct = MIME.get(ext, 'application/octet-stream')
        body = open(filepath, 'rb').read()
        send_response(conn, 200, "OK", body, ct)
    else:
        send_response(conn, 404, "Not Found", b"404 Not Found")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = 200 if os.path.isfile(filepath) else 404
    print(f"[{now}] {method} {path} -> {status}")

def send_response(conn, code, reason, body, content_type='text/plain'):
    headers = f"HTTP/1.1 {code} {reason}\r\nContent-Type: {content_type}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
    conn.sendall(headers.encode() + body)

def main():
    p = argparse.ArgumentParser(description="Minimal HTTP server")
    p.add_argument("-p", "--port", type=int, default=8080)
    p.add_argument("-d", "--directory", default=".")
    args = p.parse_args()
    root = os.path.realpath(args.directory)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', args.port)); sock.listen(5)
    print(f"Serving {root} on port {args.port}")
    try:
        while True:
            conn, addr = sock.accept()
            try: handle_request(conn, root)
            finally: conn.close()
    except KeyboardInterrupt: pass
    finally: sock.close()

if __name__ == "__main__":
    main()
