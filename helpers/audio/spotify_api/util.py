import logging
import errno
import json


LOGGER = logging.getLogger(__name__)


class CacheFileHandler:
    """
    Handles reading and writing cached Spotify authorization tokens
    as json files on disk.
    """

    def __init__(self, cache_path=None, username=None):
        """
        Parameters:
             * cache_path: May be supplied, will otherwise be generated
                           (takes precedence over `username`)
             * username: May be supplied or set as environment variable
                         (will set `cache_path` to `.cache-{username}`)
        """

        if cache_path:
            self.cache_path = cache_path
        else:
            cache_path = ".cache"
            username = username
            if username:
                cache_path += "-" + str(username)
            self.cache_path = cache_path

    def get_cached_token(self):
        token_info = None

        try:
            f = open(self.cache_path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)

        except IOError as error:
            if error.errno == errno.ENOENT:
                LOGGER.debug("cache does not exist at: %s", self.cache_path)
            else:
                LOGGER.warning("Couldn't read cache at: %s", self.cache_path)

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            f = open(self.cache_path, "w")
            f.write(json.dumps(token_info))
            f.close()
        except IOError:
            LOGGER.warning("Couldn't write token to cache at: %s", self.cache_path)
