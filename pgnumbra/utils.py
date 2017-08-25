import json
import logging
import os
import sys

import requests

from pgnumbra.SingleLocationScanner import SingleLocationScanner
from pgnumbra.config import cfg_get, get_pgpool_system_id
from pgnumbra.proxy import get_new_proxy

log = logging.getLogger(__name__)


def get_pokemon_name(pokemon_id):
    fmt = cfg_get('pokemon_format')
    if fmt == 'id':
        return "{:3}".format(pokemon_id)

    if not hasattr(get_pokemon_name, 'pokemon'):
        file_path = os.path.join('pokemon.json')

        with open(file_path, 'r') as f:
            get_pokemon_name.pokemon = json.loads(f.read())
    name = get_pokemon_name.pokemon[str(pokemon_id)]

    return shorten(name) if fmt == 'short' else name


def shorten(s):
    # Remove vowels and return only 3 chars
    for ch in ['a', 'e', 'i', 'o', 'u']:
        if ch in s:
            s = s.replace(ch, '')
    return s[:3]


def load_accounts():
    accounts = []
    if cfg_get('accounts_file'):
        log.info("Loading accounts from file {}.".format(cfg_get('accounts_file')))
        with open(cfg_get('accounts_file'), 'r') as f:
            for num, line in enumerate(f, 1):
                fields = line.split(",")
                fields = map(str.strip, fields)
                accounts.append(
                    SingleLocationScanner(fields[0], fields[1], fields[2], cfg_get('latitude'), cfg_get('longitude'),
                                          cfg_get('hash_key'), get_new_proxy()))
    elif cfg_get('pgpool_url') and cfg_get('pgpool_num_accounts') > 0:
        log.info("Trying to load {} accounts from PGPool.".format(cfg_get('pgpool_num_accounts')))
        request = {
            'system_id': get_pgpool_system_id(),
            'count': cfg_get('pgpool_num_accounts'),
            'banned_or_new': True
        }

        r = requests.get("{}/account/request".format(cfg_get('pgpool_url')), params=request)

        acc_json = r.json()
        if isinstance(acc_json, dict):
            acc_json = [acc_json]

        if len(acc_json) > 0:
            log.info("Loaded {} accounts from PGPool.".format(len(acc_json)))
            for acc in acc_json:
                accounts.append(
                    SingleLocationScanner(acc['auth_service'], acc['username'], acc['password'], cfg_get('latitude'),
                                          cfg_get('longitude'), cfg_get('hash_key'), get_new_proxy()))

    if len(accounts) == 0:
        log.error("Could not load any accounts. Nothing to do. Exiting.")
        sys.exit(1)
    return accounts