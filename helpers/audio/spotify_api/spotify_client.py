import aiohttp
import json
import logging


logger = logging.getLogger(__name__)


class Spotify(object):
    """
    Example usage::

        import spotipy

        urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
        sp = spotipy.Spotify()

        artist = sp.artist(urn)
        print(artist)

        user = sp.user('plamere')
        print(user)
    """

    max_retries = 3
    default_retry_codes = (429, 500, 502, 503, 504)
    country_codes = [
        "AD",
        "AR",
        "AU",
        "AT",
        "BE",
        "BO",
        "BR",
        "BG",
        "CA",
        "CL",
        "CO",
        "CR",
        "CY",
        "CZ",
        "DK",
        "DO",
        "EC",
        "SV",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "GT",
        "HN",
        "HK",
        "HU",
        "IS",
        "ID",
        "IE",
        "IT",
        "JP",
        "LV",
        "LI",
        "LT",
        "LU",
        "MY",
        "MT",
        "MX",
        "MC",
        "NL",
        "NZ",
        "NI",
        "NO",
        "PA",
        "PY",
        "PE",
        "PH",
        "PL",
        "PT",
        "SG",
        "ES",
        "SK",
        "SE",
        "CH",
        "TW",
        "TR",
        "GB",
        "US",
        "UY",
    ]

    def __init__(
        self,
        event_loop=None,
        auth_manager=None,
        proxies=None,
        requests_timeout=5,
        status_forcelist=None,
        retries=max_retries,
        status_retries=max_retries,
        backoff_factor=0.3,
        language=None,
    ):
        """
        Creates a Spotify API client.

        :param auth: An access token (optional)
        :param requests_session:
            A Requests session object or a truthy value to create one.
            A falsy value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons (connection pooling).
        :param client_credentials_manager:
            SpotifyClientCredentials object
        :param oauth_manager:
            SpotifyOAuth object
        :param auth_manager:
            SpotifyOauth, SpotifyClientCredentials,
            or SpotifyImplicitGrant object
        :param proxies:
            Definition of proxies (optional).
            See Requests doc https://2.python-requests.org/en/master/user/advanced/#proxies
        :param requests_timeout:
            Tell Requests to stop waiting for a response after a given
            number of seconds
        :param status_forcelist:
            Tell requests what type of status codes retries should occur on
        :param retries:
            Total number of retries to allow
        :param status_retries:
            Number of times to retry on bad status codes
        :param backoff_factor:
            A backoff factor to apply between attempts after the second try
            See urllib3 https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
        :param language:
            The language parameter advertises what language the user prefers to see.
            See ISO-639 language code: https://www.loc.gov/standards/iso639-2/php/code_list.php
        """
        self.prefix = "https://api.spotify.com/v1/"
        # self._auth = auth
        self.event_loop = event_loop
        self.auth_manager = auth_manager
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.backoff_factor = backoff_factor
        self.retries = retries
        self.status_retries = status_retries
        self.language = language

        """
        if isinstance(requests_session, aiohttp.ClientSession):
            self._session = requests_session
        else:
            self._session = aiohttp.ClientSession(loop=self.event_loop) #new client session
        """

    # def set_auth(self, auth):
    # self._auth = auth

    @property
    def auth_manager(self):
        return self._auth_manager

    @auth_manager.setter
    def auth_manager(self, auth_manager):
        if auth_manager is not None:
            self._auth_manager = auth_manager

    async def _auth_headers(self):
        # if self._auth:
        # return {"Authorization": "Bearer {0}".format(self._auth)}
        if not self.auth_manager:
            return {}
        try:
            token = await self.auth_manager.get_access_token(as_dict=False)
        except TypeError:
            token = await self.auth_manager.get_access_token()

        return {"Authorization": "Bearer {0}".format(token)}

    async def _internal_call(self, method, url, payload, params):

        # cant have none parameter while doing session.get() with aiohttp
        if params["market"] is None:
            del params["market"]

        args = dict(params=params)
        # print(f"internal url - {url}")
        if not url.startswith("http"):
            url = self.prefix + url
        # print(url)
        headers = await self._auth_headers()

        if "content_type" in args["params"]:
            headers["Content-Type"] = args["params"]["content_type"]
            del args["params"]["content_type"]
            if payload:
                args["data"] = payload
        else:
            headers["Content-Type"] = "application/json"
            if payload:
                args["data"] = json.dumps(payload)

        # print(args)
        # print(headers)

        if self.language is not None:
            headers["Accept-Language"] = self.language

        logger.debug(
            "Sending %s to %s with Params: %s Headers: %s and Body: %r ",
            method,
            url,
            args.get("params"),
            headers,
            args.get("data"),
        )

        # i'm retarded didn't pass args hahhhhhah
        async with aiohttp.ClientSession(
            loop=self.event_loop
        ) as session:  # i'm seriously retarded for doing this
            # print(args)
            # test = {'q': 'weezer', 'limit': 20, 'offset': 0, 'type': 'track', 'market':None}
            async with session.get(url, headers=headers, **args) as response:
                # print("Status:", response.status)
                results = await response.json()
                # print(results)
                # results = json.loads(results)

        logger.debug("RESULTS: %s", results)
        return results

    async def _get(self, url, args=None, payload=None, **kwargs):
        # print(url)
        if args:
            kwargs.update(args)

        return await self._internal_call("GET", url, payload, kwargs)

    async def _get_id(self, type, id):
        fields = id.split(":")
        if len(fields) >= 3:
            if type != fields[-2]:
                logger.warning(
                    "Expected id of type %s but found type %s %s", type, fields[-2], id
                )
            return fields[-1]
        fields = id.split("/")
        if len(fields) >= 3:
            itype = fields[-2]
            if type != itype:
                logger.warning(
                    "Expected id of type %s but found type %s %s", type, itype, id
                )
            return fields[-1].split("?")[0]
        return id

    async def search(self, q, limit=10, offset=0, type="track", market=None):
        """searches for an item

        Parameters:
            - q - the search query (see how to write a query in the
                  official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
            - limit - the number of items to return (min = 1, default = 10, max = 50). The limit is applied
                      within each type, not on the total response.
            - offset - the index of the first item to return
            - type - the types of items to return. One or more of 'artist', 'album',
                     'track', 'playlist', 'show', and 'episode'.  If multiple types are desired,
                     pass in a comma separated string; e.g., 'track,album,episode'.
            - market - An ISO 3166-1 alpha-2 country code or the string
                       from_token.
        """

        return await self._get(
            "search", q=q, limit=limit, offset=offset, type=type, market=market
        )

    async def playlist_items(
        self,
        playlist_id,
        fields=None,
        limit=100,
        offset=0,
        market=None,
        additional_types=("track", "episode"),
    ):
        """Get full details of the tracks and episodes of a playlist.

        Parameters:
            - playlist_id - the id of the playlist
            - fields - which fields to return
            - limit - the maximum number of tracks to return
            - offset - the index of the first track to return
            - market - an ISO 3166-1 alpha-2 country code.
            - additional_types - list of item types to return.
                                 valid types are: track and episode
        """
        plid = await self._get_id("playlist", playlist_id)
        return await self._get(
            "playlists/%s/tracks" % (plid),
            limit=limit,
            offset=offset,
            fields=fields,
            market=market,
            additional_types=",".join(additional_types),
        )

    async def track(self, track_id, market=None):
        """returns a single track given the track's ID, URI or URL

        Parameters:
            - track_id - a spotify URI, URL or ID
            - market - an ISO 3166-1 alpha-2 country code.
        """

        trid = await self._get_id("track", track_id)
        return await self._get("tracks/" + trid, market=market)

    async def album_tracks(self, album_id, limit=50, offset=0, market=None):
        """Get Spotify catalog information about an album's tracks

        Parameters:
            - album_id - the album ID, URI or URL
            - limit  - the number of items to return
            - offset - the index of the first item to return
            - market - an ISO 3166-1 alpha-2 country code.

        """

        trid = await self._get_id("album", album_id)
        return await self._get(
            "albums/" + trid + "/tracks/", limit=limit, offset=offset, market=market
        )
