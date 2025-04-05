import yt_dlp.YoutubeDL
import yt_dlp.extractor.youtube
from cachetools import cached, TTLCache
from logger import logger
import time

import const

UPDATE_AFTER = 60 * 60 * 4  # 4 hours
CACHE_TTL = 60 * 10  # 10 minutes

class Player:
    def __init__(self):
        ie = yt_dlp.extractor.YoutubeIE()
        ydl = yt_dlp.YoutubeDL({})
        ydl.add_info_extractor(ie)

        self._latest_update = time.time()
        self._ie = ie
        self._player_url = None
        self._update_player_id()

    def get_player_id(self):
        """ extract player ID from the player URL 
        return f'https://www.youtube.com/s/player/{player_version}/player_ias.vflset/en_US/base.js'
        """
        try:
            player_id = self._player_url.replace('https://www.youtube.com/s/player/', '')
            player_id = player_id.split('/')[0]

            # convert to int (from hexa) (player_id is aabb88cc)
            player_id = int(player_id, 16)
        except (IndexError, ValueError) as e:
            logger.error(f"Error extracting player ID: {e}")
            logger.exception(e)
            player_id = 1
        logger.debug(f"Player ID: {player_id}")
        return player_id

    def get_player_update_timestamp(self):
        return int(self._latest_update)

    @cached(cache=TTLCache(maxsize=2048, ttl=CACHE_TTL))
    def decode_nsig(self, signature):
        self._update_player_url_if_needed()

        try:
            decrypted_nsig = self._ie._decrypt_nsig(signature, const.VIDEO_ID, self._player_url)
        except Exception as e:
            decrypted_nsig = b""
            logger.error(f"Error decrypting non-signature: {e}")
            logger.exception(e)
        logger.debug(f"Decrypted non-signature: {decrypted_nsig} for {signature}")
        return decrypted_nsig
    
    @cached(cache=TTLCache(maxsize=2048, ttl=CACHE_TTL))
    def decode_sig(self, signature):
        self._update_player_url_if_needed()

        try:
            decrypted_sig = self._ie._decrypt_signature(signature, const.VIDEO_ID, self._player_url)
        except Exception as e:
            decrypted_sig = b""
            logger.error(f"Error decrypting signature: {e}")
            logger.exception(e)
        logger.debug(f"Decrypted signature: {decrypted_sig} for {signature}")
        return decrypted_sig

    @cached(cache=TTLCache(maxsize=2048, ttl=CACHE_TTL))
    def get_signature_timestamp(self):
        self._update_player_url_if_needed()

        timestamp = self._ie._extract_signature_timestamp(const.VIDEO_ID, self._player_url)
        logger.debug(f"Signature timestamp: {timestamp}")
        return timestamp
    
    def _update_player_id(self):
        try:
            self._player_url = self._ie._download_player_url(const.VIDEO_ID)
        except Exception as e:
            logger.error(f"Error updating player URL: {e}")
            logger.exception(e)
            if not self._player_url:
                raise
            return
        self._latest_update = time.time()

        # clear the cache
        self.decode_sig.cache_clear()
        self.decode_nsig.cache_clear()
        self.get_signature_timestamp.cache_clear()

        logger.info(f"Updated player URL: {self._player_url}")

    def _update_player_url_if_needed(self):
        if time.time() - self._latest_update > UPDATE_AFTER \
            or not self._player_url \
            or time.time() < self._latest_update:

            self._update_player_id()
