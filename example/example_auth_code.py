from functools import wraps

from flask import Flask, redirect, request, jsonify
import urllib.parse as urlparse
import webbrowser
from ecnuopenapi import auth
from ecnuopenapi import oauth_init

app = Flask(__name__)
# 初始化OAuth客户端配置
config = oauth_init.OAuth2Config(
    client_id='client_id',
    client_secret='client_secret',
    redirect_url='http://localhost:8080/user',
)
oauth_init.initOAuth2AuthorizationCode(config)


def oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        code = request.args.get('code')
        state = request.args.get('state')

        token = auth.getToken(code, state)
        if not token:
            return jsonify({'error': 'Failed to fetch token.'}), 500

        user_info = auth.getUserInfo(token)
        if not user_info:
            return jsonify({'error': 'Failed to fetch user info.'}), 500

        kwargs['user_info'] = user_info
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login')
def login():
    state = auth.generateState()
    auth_url = auth.getAuthorizationEndpoint(state)
    return redirect(auth_url)


@app.route('/user')
@oauth_required
def user_info(user_info):
    return jsonify(user_info)


if __name__ == '__main__':
    app.run(port=8080)
