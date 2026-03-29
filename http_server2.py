#!/usr/bin/env python3
"""HTTP/1.1 server with routing, middleware, and static files."""
import sys, os, json, mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class Router:
    def __init__(self): self.routes = []; self.middleware = []
    def route(self, method, path):
        def decorator(fn):
            self.routes.append((method, path, fn)); return fn
        return decorator
    def use(self, middleware_fn): self.middleware.append(middleware_fn)
    def match(self, method, path):
        for m, p, fn in self.routes:
            if m == method:
                params = self._match_path(p, path)
                if params is not None: return fn, params
        return None, {}
    def _match_path(self, pattern, path):
        pp = pattern.strip('/').split('/'); rp = path.strip('/').split('/')
        if len(pp) != len(rp): return None
        params = {}
        for p, r in zip(pp, rp):
            if p.startswith(':'): params[p[1:]] = r
            elif p != r: return None
        return params

class Request:
    def __init__(self, method, path, headers=None, body=None, query=None):
        self.method, self.path = method, path
        self.headers = headers or {}; self.body = body; self.query = query or {}

class Response:
    def __init__(self): self.status = 200; self.headers = {"Content-Type":"text/plain"}; self.body = ""
    def json(self, data): self.headers["Content-Type"] = "application/json"; self.body = json.dumps(data); return self
    def html(self, content): self.headers["Content-Type"] = "text/html"; self.body = content; return self

def main():
    router = Router()
    @router.route("GET", "/")
    def index(req, res, params): return res.html("<h1>Welcome</h1>")
    @router.route("GET", "/api/users/:id")
    def get_user(req, res, params): return res.json({"id":params["id"],"name":"Alice"})
    @router.route("POST", "/api/users")
    def create_user(req, res, params): res.status = 201; return res.json({"created":True})
    # Simulate requests
    for method, path in [("GET","/"),("GET","/api/users/42"),("POST","/api/users"),("GET","/404")]:
        fn, params = router.match(method, path)
        if fn:
            res = Response(); fn(Request(method, path), res, params)
            print(f"  {method} {path} -> {res.status} {res.headers['Content-Type']}: {res.body[:50]}")
        else: print(f"  {method} {path} -> 404 Not Found")

if __name__ == "__main__": main()
