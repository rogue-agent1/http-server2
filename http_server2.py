#!/usr/bin/env python3
"""http_server2 - Minimal HTTP server with routing."""
import sys, socket, json, datetime
class Router:
    def __init__(self): self.routes={}
    def route(self, method, path):
        def decorator(fn): self.routes[(method,path)]=fn; return fn
        return decorator
    def handle(self, method, path, body=""):
        handler=self.routes.get((method,path))
        if handler: return handler(body)
        return 404, "Not Found", "text/plain"
router=Router()
@router.route("GET","/")
def index(body): return 200, "<h1>Hello World</h1>", "text/html"
@router.route("GET","/api/time")
def api_time(body): return 200, json.dumps({"time":str(datetime.datetime.now())}), "application/json"
@router.route("GET","/api/echo")
def api_echo(body): return 200, json.dumps({"echo":body or "empty"}), "application/json"
def serve(host="127.0.0.1", port=8080):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((host,port)); s.listen(5); print(f"HTTP server on http://{host}:{port}")
    while True:
        conn,_=s.accept(); data=conn.recv(4096).decode()
        lines=data.split("\r\n"); method,path,_=lines[0].split(" ",2)
        body=lines[-1] if lines else ""
        status,content,ctype=router.handle(method,path,body)
        response=f"HTTP/1.1 {status} OK\r\nContent-Type: {ctype}\r\nContent-Length: {len(content)}\r\n\r\n{content}"
        conn.sendall(response.encode()); conn.close()
        print(f"{method} {path} -> {status}")
if __name__=="__main__":
    port=int(sys.argv[1]) if len(sys.argv)>1 else 8080
    serve(port=port)
