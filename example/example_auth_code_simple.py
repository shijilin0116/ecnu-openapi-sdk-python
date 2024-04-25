from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import webbrowser
from ecnuopenapi import auth
from ecnuopenapi import oauth_init

# 初始化OAuth客户端配置
config = oauth_init.OAuth2Config(
    client_id='client_id',
    client_secret='client_secret',
    redirect_url='http://localhost:8080/user',
)
oauth_init.initOAuth2AuthorizationCode(config)


class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/login'):
            state = auth.generateState()
            authorization_url = auth.getAuthorizationEndpoint(state)
            self.send_response(302)
            self.send_header('Location', authorization_url)
            self.end_headers()
        elif self.path.startswith('/user'):
            parsed_path = urlparse.urlparse(self.path)
            query = urlparse.parse_qs(parsed_path.query)
            code = query.get('code', [None])[0]
            state = query.get('state', [None])[0]

            token = auth.getToken(code, state)
            if not token:
                self._send_text('Failed to fetch token', 400)
                return

            user_info = auth.getUserInfo(token)
            if not user_info:
                self._send_text('Failed to fetch user info', 400)
                return

            self._send_text(f'User Info: {user_info}', 200)
        else:
            self._send_text('Not Found', 404)

    def _send_text(self, text, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(text.encode())


def run(server_class=HTTPServer, handler_class=SimpleServer, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
