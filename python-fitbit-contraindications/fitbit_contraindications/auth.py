import requests
from requests_oauthlib import OAuth2Session
from compliance import fitbit_compliance_fix

class FitbitOAuth2Client:
    """Use this to authorize the user and obtain initial access and refresh tokens."""

    AUTHORIZATION_BASE_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_BASE_URL = "https://api.fitbit.com/oauth2/token"
    SCOPE = [
        "activity", "nutrition", "heartrate",
        "location", "nutrition", "profile",
        "settings", "sleep", "social", "weight"
    ]

    def __init__(self, client_id, client_secret):
        """
        Initialize the client for the OAuth flow.

        :param client_id: The client ID provided by Fitbit.
        :type client_id: str
        :param client_secret: The client secret provided by Fitbit.
        :type client_secret: str
        """
        self.client_id = client_id
        self.client_secret = client_secret

        self.session = OAuth2Session(
            client_id,
            auto_refresh_url=self.TOKEN_BASE_URL
        )

    def authorize_endpoint(self, scope=None, redirect_uri=None, **kwargs):
        """
        Build the authorization URL for the user to visit.

        :param scope: The scopes to request from the user. Defaults to self.SCOPE
        :type scope: list
        :param redirect_uri: The URL to redirect the user to after user grants access
        :type redirect_uri: str
        """
        self.session.scope = scope or self.SCOPE
        if redirect_uri:
            self.session.redirect_uri = redirect_uri
        return self.session.authorization_url(self.AUTHORIZATION_BASE_URL, **kwargs)

    def fetch_access_token(self, code):
        """
        Exchange the authorization code for an access and refresh token.

        :param code: The authorization code received from the user's authorization.
        :type code: str
        """
        return self.session.fetch_token(
            self.TOKEN_BASE_URL, code=code, client_secret=self.client_secret

        )

class OAuthRequestHandler:
    TOKEN_BASE_URL = "https://api.fitbit.com/oauth2/token"
    TOKEN_REVOKE_URL = "https://api.fitbit.com/oauth2/revoke"

    def __init__(
            self,
            client_id,
            client_secret=None,
            access_token=None,
            refresh_token=None,
            refresh_callback=None
    ):

        self.client_id = client_id
        self.client_secret = client_secret

        token = {}
        if access_token:
            token['access_token'] = access_token
        if refresh_token:
            token['refresh_token'] = refresh_token


        self._session = fitbit_compliance_fix(OAuth2Session(
            client_id,
            auto_refresh_url=self.TOKEN_BASE_URL,
            token_updater=refresh_callback,
            token=token
        ))

    def make_request(self, url, method='GET'):
        """
        Make a request to the Fitbit API.

        :param url: The URL to make the request to.
        :type url: str
        :param method: The HTTP method to use for the request.
        :type method: str
        """
        response = self._session.request(method, url)
        if response.status_code == 401:
            self._refresh_token()
            response = self._session.request(method, url)
        return response

    def make_request_v2(self, url, method="GET"):
        """
        Make a request to the Fitbit API.

        :param url: The URL to make the request to.
        :type url: str
        :param method: The HTTP method to use for the request.
        :type method: str
        """
        return self.make_request(url, method)

    def _refresh_token(self):
        token = self._session.refresh_token(
            self.TOKEN_BASE_URL,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        if self._session.token_updater:
            self._session.token_updater(token)

        return token

    def revoke_token(self):
        return self._session.request("POST", self.TOKEN_REVOKE_URL)