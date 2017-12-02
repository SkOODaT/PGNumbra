import codecs
import json
import logging
import os
import sys

import requests

from pgnumbra.config import cfg_get, get_pgpool_system_id

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


def load_accounts_file():
    accounts = []
    log.info("Loading accounts from file {}.".format(cfg_get('accounts_file')))
    with codecs.open(cfg_get('accounts_file'), mode='r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == "":
                continue
            fields = line.split(",")
            if len(fields) == 3:
                auth = fields[0].strip()
                usr = fields[1].strip()
                pwd = fields[2].strip()
            elif len(fields) == 2:
                auth = 'ptc'
                usr = fields[0].strip()
                pwd = fields[1].strip()
            elif len(fields) == 1:
                fields = line.split(":")
                auth = 'ptc'
                usr = fields[0].strip()
                pwd = fields[1].strip()
            accounts.append({
                'auth_service': auth,
                'username': usr,
                'password': pwd
            })
    if len(accounts) == 0:
        log.error("Could not load any accounts. Nothing to do. Exiting.")
        sys.exit(1)
    return accounts


def pgpool_load_accounts(num):
    request = {
        'system_id': get_pgpool_system_id(),
        'count': num,
        'banned_or_new': True
    }

    r = requests.get("{}/account/request".format(cfg_get('pgpool_url')), params=request)

    acc_json = r.json()
    if isinstance(acc_json, dict):
        acc_json = [acc_json]

    return acc_json
