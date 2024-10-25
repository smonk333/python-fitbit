import json
from urllib.parse import urlencode

import exceptions
from auth import OAuthRequestHandler

class FitbitClient:

    def __init__(
            self,
            client_id=None,
            client_secret=None,
            access_token=None,
            refresh_token=None,
            refresh_callback=None
    ):
        """
        :param client_id: The client id - identifies your application.
        :type client_id: str

        :param client_secret: The client secret. Required for auto refresh.
        :type client_secret: str

        :param access_token: Access token.
        :type access_token: str

        :param refresh_token: Use this to renew tokens when they expire
        :type refresh_token: str

        :param refresh_callback: Callback to handle token response
        :type refresh_callback: callable
        """

        if client_id is not None:
            self._auth_handler = OAuthRequestHandler(
                client_id, client_secret, access_token, refresh_token, refresh_callback
            )

    def _make_request