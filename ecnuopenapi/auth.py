import secrets
import requests
from requests_oauthlib import OAuth2Session
from ecnuopenapi.oauth_init import GetOpenAPIClient


def getAuthorizationEndpoint(state):
    c = GetOpenAPIClient()
    oauth2_session = OAuth2Session(c.client_id, redirect_uri=c.redirect_url, scope=c.scopes)
    authorization_url, state = oauth2_session.authorization_url(c.auth_url, state=state)
    return authorization_url


def generateState():
    return secrets.token_hex(16)


def getToken(code, state):
    c = GetOpenAPIClient()
    oauth2_session = OAuth2Session(c.client_id, redirect_uri=c.redirect_url, state=state)
    try:
        token = oauth2_session.fetch_token(c.token_url, client_secret=c.client_secret, code=code)
        return token
    except Exception as e:
        print("获取token失败:", e)
        return None


def getUserInfo(token):
    c = GetOpenAPIClient()
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    response = requests.get(c.user_info_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("获取用户信息失败")
        return None
