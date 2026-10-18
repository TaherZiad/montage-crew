"""The one guarded web fetcher of montage-crew (brand.py --site, learn.py link checks). Standard library only.

  check_url(url, allow_http=False)  -> url, or SystemExit with the reason
  get(url, cap, allow_http=False)   -> (bytes, final_url, content_type)
  python net.py --selftest

Rules: https only (http only when the user typed an http link); no user:pass@, no IP literals, no localhost / *.local /
*.localhost / *.internal; every address the host resolves to must be public (ipaddress.is_global, v4 + v6);
the same check on every redirect (max 5, https only); 20 s timeout; size cap per call; no cookies; honest UA.
The bytes are data: nothing fetched is ever executed.
"""
import ipaddress, socket, sys, urllib.error, urllib.request
from urllib.parse import urlparse

UA = "montage-crew/2.0"
TIMEOUT = 20
MAX_REDIRECTS = 5
BLOCKED_SUFFIX = (".local", ".localhost", ".internal", ".lan", ".home.arpa")


def check_url(url, allow_http=False):
    u = urlparse(url if isinstance(url, str) else "")
    schemes = ("https", "http") if allow_http else ("https",)
    if u.scheme not in schemes:
        raise SystemExit(f"refused link (only {' or '.join(schemes)}): {url!r}")
    host = (u.hostname or "").rstrip(".").lower()
    if not host or u.username or u.password or any(c in url for c in "\r\n\t \\"):
        raise SystemExit(f"refused link: {url!r}")
    try:
        ipaddress.ip_address(host)
        raise SystemExit(f"refused link (an IP address, not a site name): {url!r}")
    except ValueError:
        pass
    if host == "localhost" or host.endswith(BLOCKED_SUFFIX) or "." not in host:
        raise SystemExit(f"refused link (local/private host): {url!r}")
    try:
        port = u.port or (443 if u.scheme == "https" else 80)
        addrs = {ai[4][0] for ai in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)}
    except (OSError, ValueError) as e:
        raise SystemExit(f"cannot resolve {host}: {e}")
    for a in addrs:
        ip = ipaddress.ip_address(a.split("%")[0])
        if not ip.is_global or ip.is_multicast:
            raise SystemExit(f"refused link ({host} points to a private/local address)")
    # ponytail: resolve-then-connect leaves a DNS-rebinding window; pin the checked IP in a custom HTTPSConnection if needed
    return url


class _Redirect(urllib.request.HTTPRedirectHandler):
    max_redirections = MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)  # https only after the first hop
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _build():
    """explicit handler list: no FileHandler / FTPHandler / DataHandler, no cookie processor."""
    o = urllib.request.OpenerDirector()
    for h in (urllib.request.ProxyHandler(), urllib.request.HTTPHandler(), urllib.request.HTTPSHandler(),
              urllib.request.HTTPDefaultErrorHandler(), _Redirect(), urllib.request.HTTPErrorProcessor()):
        o.add_handler(h)
    return o


def get(url, cap, allow_http=False):
    check_url(url, allow_http)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with _build().open(req, timeout=TIMEOUT) as r:
            n = r.headers.get("Content-Length")
            if n and n.isdigit() and int(n) > cap:
                raise SystemExit(f"too large ({int(n) // 1024} KB > {cap // 1024} KB): {url}")
            data = r.read(cap + 1)
            if len(data) > cap:
                raise SystemExit(f"too large (> {cap // 1024} KB): {url}")
            return data, r.geturl(), (r.headers.get_content_type() or "")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} for {url}")
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit(f"cannot fetch {url}: {getattr(e, 'reason', e)}")


def selftest():
    refused = ["http://127.0.0.1/", "https://127.0.0.1/", "http://[::1]/", "https://[::1]:8443/", "http://169.254.169.254/latest",
               "http://10.0.0.1/", "https://192.168.1.1/", "file:///C:/x", "file://server/share/x", "ftp://example.com/x",
               "https://localhost/", "https://printer.local/", "https://user:pw@example.com/", "https://2130706433/",
               "https://0x7f.0.0.1/", "javascript:alert(1)", "https://", "\\\\server\\share", "https://exa mple.com/"]
    for u in refused:
        for http in (False, True):
            try:
                check_url(u, http); raise AssertionError(u)
            except SystemExit:
                pass
    try:
        check_url("http://example.com/"); raise AssertionError("http without allow_http")
    except SystemExit:
        pass
    real = socket.getaddrinfo
    fake = {"public.example": "93.184.216.34", "evil.example": "10.0.0.5", "evil6.example": "fd00::1",
            "meta.example": "169.254.169.254", "cgnat.example": "100.64.0.1"}
    socket.getaddrinfo = lambda h, *a, **k: [(0, 0, 0, "", (fake[h], 0))] if h in fake else real(h, *a, **k)
    try:
        assert check_url("https://public.example/x") and check_url("http://public.example/", allow_http=True)
        for h in ("evil", "evil6", "meta", "cgnat"):
            try:
                check_url(f"https://{h}.example/"); raise AssertionError(h)
            except SystemExit as e:
                assert "private" in str(e), e
        rd = _Redirect()
        req = urllib.request.Request("https://public.example/")
        for to in ("http://127.0.0.1/", "https://evil.example/", "file:///etc/passwd", "http://public.example/"):
            try:
                rd.redirect_request(req, None, 302, "Found", {}, to); raise AssertionError(to)
            except SystemExit:
                pass
        assert rd.redirect_request(req, None, 302, "Found", {}, "https://public.example/b") is not None
    finally:
        socket.getaddrinfo = real
    names = {type(h).__name__ for h in _build().handlers}
    assert not names & {"FileHandler", "FTPHandler", "DataHandler", "HTTPCookieProcessor"}, names
    print("selftest ok")


if __name__ == "__main__":
    selftest() if len(sys.argv) < 2 or sys.argv[1] == "--selftest" else sys.exit(__doc__)
