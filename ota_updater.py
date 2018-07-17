import usocket
import os


class OTAUpdater:

    def __init__(self):
        self.http_client = HttpClient()
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        print("Checking version... ")
        print("\tCurrent version: ", current_version)
        print("\tLatest version: ", latest_version)
        if latest_version > current_version:
            print("Updating...")
            os.mkdir("next")
            self.download_all_files()

    def get_current_version(self):
        f = open('current/showerloop.version')
        version = f.read()
        f.close()
        return version

    def get_latest_version(self):
        latest_release = self.http_client.get('https://api.github.com/repos/rdehuyss/showerloop/releases/latest')
        version = latest_release.json()['tag_name']
        latest_release.close()
        return version

    def download_all_files(self, version):
        file_list = self.http_client.get('https://api.github.com/repos/rdehuyss/showerloop/contents/main?ref=refs/tags/' + version)
        for file in file_list.json():
            if file['type'] == 'file':
                download_url = file['download_url']
                download_path = 'next/' + file['path'].replace('main/', '')
                self.download_file(download_url.replace('refs/tags/', ''), download_path)
            elif file['type'] == 'dir':
                path = 'next/' + file['path'].replace('main/', '')
                os.mkdir(path)
        file_list.close()

    def download_file(self, url, path):
        with open(path, 'w') as outfile:
            try:
                response = self.http_client.get(url)
                outfile.write(response.text)
                response.close()
            finally:
                response.close()
                outfile.close()


class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


class HttpClient:

    def request(self, method, url, data=None, json=None, headers={}, stream=None):
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        elif proto == "https:":
            import ussl
            port = 443
        else:
            raise ValueError("Unsupported protocol: " + proto)

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]

        s = usocket.socket(ai[0], ai[1], ai[2])
        try:
            s.connect(ai[-1])
            if proto == "https:":
                s = ussl.wrap_socket(s, server_hostname=host)
            s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
            if not "Host" in headers:
                s.write(b"Host: %s\r\n" % host)
            # Iterate over keys to avoid tuple alloc
            for k in headers:
                s.write(k)
                s.write(b": ")
                s.write(headers[k])
                s.write(b"\r\n")
            # add user agent
            s.write('User-Agent')
            s.write(b": ")
            s.write('ShowerLoop')
            s.write(b"\r\n")
            if json is not None:
                assert data is None
                import ujson
                data = ujson.dumps(json)
                s.write(b"Content-Type: application/json\r\n")
            if data:
                s.write(b"Content-Length: %d\r\n" % len(data))
            s.write(b"\r\n")
            if data:
                s.write(data)

            l = s.readline()
            # print(l)
            l = l.split(None, 2)
            status = int(l[1])
            reason = ""
            if len(l) > 2:
                reason = l[2].rstrip()
            while True:
                l = s.readline()
                if not l or l == b"\r\n":
                    break
                # print(l)
                if l.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in l:
                        raise ValueError("Unsupported " + l)
                elif l.startswith(b"Location:") and not 200 <= status <= 299:
                    raise NotImplementedError("Redirects not yet supported")
        except OSError:
            s.close()
            raise

        resp = Response(s)
        resp.status_code = status
        resp.reason = reason
        return resp

    def head(self, url, **kw):
        return self.request("HEAD", url, **kw)

    def get(self, url, **kw):
        return self.request("GET", url, **kw)

    def post(self, url, **kw):
        return self.request("POST", url, **kw)

    def put(self, url, **kw):
        return self.request("PUT", url, **kw)

    def patch(self, url, **kw):
        return self.request("PATCH", url, **kw)

    def delete(self, url, **kw):
        return self.request("DELETE", url, **kw)
