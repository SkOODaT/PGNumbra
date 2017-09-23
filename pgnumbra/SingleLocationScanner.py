import logging
import random
import time

from mrmime.pogoaccount import POGOAccount

from pgnumbra.config import cfg_get

log = logging.getLogger(__name__)


class SingleLocationScanner(POGOAccount):
    def __init__(self, auth, username, password, latitude, longitude, hash_key_provider, proxy):
        super(SingleLocationScanner, self).__init__(auth, username, password,
                                                    hash_key_provider=hash_key_provider,
                                                    proxy_url=proxy)

        # Init API location
        self.latitude = latitude
        self.longitude = longitude
        self.set_position(self.latitude, self.longitude, random.randrange(3, 170))

        # The currently seen Pokemon
        self.seen_pokemon = {}

    def run(self):
        # Initial random delay to spread logins.
        time.sleep(random.randint(0, 10))
        while True:
            self.scan_once()
            time.sleep(15)

    def scan_once(self):
        if self.check_login():
            rareless_before = self.rareless_scans or 0
            self.scan_location()
            self.shadowbanned = self.rareless_scans > rareless_before

    def scan_location(self):
        tries = 0
        max_tries = cfg_get("scan_retries")
        while tries < max_tries:
            tries += 1
            self.log_info("Scanning {}, {} (try #{})".format(self.latitude,
                                                             self.longitude,
                                                             tries))
            try:
                responses = self.req_get_map_objects()
                self.count_pokemon(responses)
                if self.seen_pokemon:
                    self.log_info("Successfully scanned location")
                    return
                else:
                    self.log_warning("Emtpy scan (try #{})".format(tries))
            except Exception as e:
                self.log_error(
                    "Error on get_map_objects (try #{}): {}".format(tries,
                                                                    repr(e)))

        self.log_error("Failed {} times. Giving up.".format(max_tries))

    def count_pokemon(self, response):
        self.seen_pokemon = {}
        cells = response['GET_MAP_OBJECTS'].map_cells
        for cell in cells:
            for p in cell.wild_pokemons:
                pid = p.pokemon_data.pokemon_id
                self.seen_pokemon[pid] = self.seen_pokemon.get(pid, 0) + 1
            if cfg_get('include_nearby'):
                for p in cell.nearby_pokemons:
                    pid = p.pokemon_id
                    self.seen_pokemon[pid] = self.seen_pokemon.get(pid, 0) + 1
