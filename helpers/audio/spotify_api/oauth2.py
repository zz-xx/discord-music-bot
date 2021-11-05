import aiohttp
import base64
import logging
import time

import six

from helpers.audio.spotify_api.util import CacheFileHandler
from helpers.audio.spotify_api.exceptions import SpotifyOauthError

logger = logging.getLogger(__name__)

class SpotifyAuthBase(object):
    
    def __init__(self):
        pass
    
    def _ensure_value(self, value):
        _val = value 
        if _val is None:
            msg = "No credentials. Pass it."
            raise SpotifyOauthError(msg)
        return _val

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, val):
        self._client_id = self._ensure_value(val)

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val):
        self._client_secret = self._ensure_value(val)

    @staticmethod
    def is_token_expired(token_info):
        now = int(time.time())
        return token_info["expires_at"] - now < 60


class SpotifyClientCredentials(SpotifyAuthBase):
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id=None,
        client_secret=None,
    ):
        """
        Creates a Client Credentials Flow Manager.

        The Client Credentials flow is used in server-to-server authentication.
        Only endpoints that do not access user information can be accessed.
        This means that endpoints that require authorization scopes cannot be accessed.
        The advantage, however, of this authorization flow is that it does not require any
        user interaction

        You can either provide a client_id and client_secret to the
        constructor or set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
        environment variables

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * proxies: Optional, proxy for the requests library to route through
             * requests_session: A Requests session
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
             * cache_handler: An instance of the `CacheHandler` class to handle
                              getting and saving cached authorization tokens.
                              Optional, will otherwise use `CacheFileHandler`.
                              (takes precedence over `cache_path` and `username`)

        """

        super(SpotifyClientCredentials, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache_handler = CacheFileHandler()
    
    async def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        return token_info
    

    async def _make_authorization_headers(self, client_id, client_secret):
        auth_header = base64.b64encode(
            six.text_type(client_id + ":" + client_secret).encode("ascii")
        )
        return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

    
    async def _request_access_token(self):
        """Gets client credentials access token """
        payload = {"grant_type": "client_credentials"}

        headers = await self._make_authorization_headers(
            self.client_id, self.client_secret
        )

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        '''response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
        ) '''

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=True)) as session: #i'm seriously retarded for doing this
            
            async with session.post(self.OAUTH_TOKEN_URL, data=payload, headers=headers) as response:
                #print("Status:", response.status)
                token_info = await response.json()
                #print(results)

        return token_info

    async def get_access_token(self, as_dict=True, check_cache=False):
        """
        If a valid access token is in memory, returns it
        Else feches a new token and returns it

            Parameters:
            - as_dict - a boolean indicating if returning the access token
                as a token_info dictionary, otherwise it will be returned
                as a string.
        """

        if check_cache:
            
            token_info = self.cache_handler.get_cached_token()
            if token_info and not self.is_token_expired(token_info):
                return token_info if as_dict else token_info["access_token"]

        token_info = await self._request_access_token()
        token_info = await self._add_custom_values_to_token_info(token_info)
        self.cache_handler.save_token_to_cache(token_info)
        
        return token_info if as_dict else token_info["access_token"]
