import datetime
from oauthlib.oauth2 import BackendApplicationClient
from requests import Session
from requests_oauthlib import OAuth2Session

DEFAULT_SCOPE = "ECNU-Basic"
DEFAULT_BASE_URL = "https://api.ecnu.edu.cn"
DEFAULT_TIMEOUT = 10
DEFAULT_USER_INFO_URL = "https://api.ecnu.edu.cn/oauth2/userinfo"
DEFAULT_AUTH_URL = "https://api.ecnu.edu.cn/oauth2/authorize"
DEFAULT_TOKEN_URL = "https://api.ecnu.edu.cn/oauth2/token"

open_api_client = None


class OAuth2Config:
    def __init__(self, client_id, client_secret, redirect_url=None, base_url=DEFAULT_BASE_URL, scopes=[DEFAULT_SCOPE],
                 timeout=DEFAULT_TIMEOUT, auth_url=DEFAULT_AUTH_URL, token_url=DEFAULT_TOKEN_URL,
                 user_info_url=DEFAULT_USER_INFO_URL, debug=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.scopes = scopes
        self.timeout = timeout
        self.debug = debug

        self.redirect_url = redirect_url
        self.auth_url = auth_url
        self.token_url = token_url
        self.user_info_url = user_info_url


class OAuth2Client:
    def __init__(self, config):
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.token_url if config.base_url is None else config.base_url + "/oauth2/token"
        self.base_url = config.base_url
        self.token_expiration = None
        self.oauth2_session = self.createOauth2Session()
        self.debug = config.debug
        self.RetryCount = 0

        self.auth_url = config.auth_url
        self.auth_url = config.auth_url
        self.user_info_url = config.user_info_url
        self.redirect_url = config.redirect_url
        self.scopes = config.scopes

    def createOauth2Session(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth2_session = OAuth2Session(client=client)
        return oauth2_session

    def getAccessToken(self):
        if self.token_expiration is None:
            token = self.oauth2_session.fetch_token(self.token_url, client_id=self.client_id,
                                                    client_secret=self.client_secret)
            self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=token.get("expires_in", 3600))
        # 小于600秒刷新---
        if (self.token_expiration - datetime.datetime.now()).total_seconds() <= 600:
            token = self.oauth2_session.fetch_token(self.token_url, client_id=self.client_id,
                                                    client_secret=self.client_secret)
        return self.oauth2_session.access_token

    def refreshAccessToken(self):
        token = self.oauth2_session.fetch_token(self.token_url, client_id=self.client_id,
                                                client_secret=self.client_secret)
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=token.get("expires_in", 3600))

    def retryAdd(self):
        self.RetryCount += 1

    def retryReset(self):
        self.RetryCount = 0


def initOauth2ClientCredentials(config):
    global open_api_client
    open_api_client = OAuth2Client(config)


def initOAuth2AuthorizationCode(config):
    global open_api_client
    open_api_client = OAuth2Client(config)


def GetOpenAPIClient():
    return open_api_client
