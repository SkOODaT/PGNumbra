import logging
import os
import sys

import configargparse
from mrmime import init_mr_mime
from mrmime.cyclicresourceprovider import CyclicResourceProvider

log = logging.getLogger(__name__)
args = None


def cfg_get(key):
    global args
    return getattr(args, key)


def cfg_set(key, val):
    global args
    setattr(args, key, val)


def parse_args():
    global args
    defaultconfigfiles = []
    if '-c' not in sys.argv and '--config' not in sys.argv:
        defaultconfigfiles = ['config.ini']

    parser = configargparse.ArgParser(
        default_config_files=defaultconfigfiles)

    parser.add_argument('-c', '--config',
                        is_config_file=True, help='Specify configuration file.')

    parser.add_argument('-lat', '--latitude', type=float, required=True,
                        help='Latitude of location to scan.')

    parser.add_argument('-lng', '--longitude', type=float, required=True,
                        help='Longitude of location to scan.')

    parser.add_argument('-hk', '--hash-key', required=True, action='append',
                        help='Hash key to use.')

    parser.add_argument('-p', '--proxies-file',
                        help='Load proxy list from text file (one proxy per line).')

    parser.add_argument('-r', '--scan-retries', type=int, default=3,
                        help='Number of retries when scanning a location.')

    parser.add_argument('-i', '--include-nearby', action='store_true', default=False,
                        help="Include nearby Pokemon in compare_scans.py - always true for shadowcheck.py.")

    parser.add_argument('-f', '--pokemon-format', choices=['id', 'short', 'full'], default='full',
                        help="Format of Pokemons in compare_scans.py table overview.")

    parser.add_argument('-s', '--spin-below-level', type=int, default=2,
                        help="shadowcheck.py: Spin Pokestops in range for accounts below this level.")

    parser.add_argument('-m', '--max-spins', type=int, default=1,
                        help="shadowcheck.py: Spin at most this many Pokestops per account.")

    parser.add_argument('-t', '--threads', type=int, default=4,
                        help="Number of parallel threads to check accounts with shadowcheck.py.")

    parser.add_argument('-pgpmin', '--pgpool-min-level', type=int, default=1,
                        help="Minimum trainer level to request from PGPool")

    parser.add_argument('-pgpmax', '--pgpool-max-level', type=int, default=40,
                        help="Maximum trainer level to request from PGPool")

    parser.add_argument('-pgpu', '--pgpool-url',
                        help='Address of PGPool to load accounts from and/or update their details.')

    parser.add_argument('-mg', '--max-good', type=int, default=0,
                        help="Stop checking after this many 'GOOD' accounts have been found.")

    accs = parser.add_mutually_exclusive_group(required=True)
    accs.add_argument('-pgpn', '--pgpool-num-accounts', type=int, default=0,
                      help='Load this many banned or new accounts from PGPool. --pgpool-url required.')

    accs.add_argument('-a', '--accounts-file',
                      help='Load accounts from CSV file containing "auth_service,username,passwd" lines.')

    args = parser.parse_args()


def get_pgpool_system_id():
    return 'pgnumbra_' + str(os.getpid())


def cfg_init(shadowcheck=False):
    global args

    log.info("Loading PGNumbra configuration.")

    parse_args()

    # Provide hash keys
    args.hash_key_provider = CyclicResourceProvider()
    for hk in args.hash_key:
        args.hash_key_provider.add_resource(hk)

    mrmime_cfg = {
        'pgpool_system_id': get_pgpool_system_id()
    }

    if args.pgpool_url:
        mrmime_cfg['pgpool_url'] = args.pgpool_url
        log.info("Attaching to PGPool at {}".format(args.pgpool_url))

    if shadowcheck:
        # This test must include nearby Pokemon to work properly.
        args.include_nearby = True
        mrmime_cfg['pgpool_auto_update'] = False

    if cfg_get('pgpool_min_level') > 1 or cfg_get('pgpool_max_level') < 40:
        log.info("Only checking accounts with trainer level {} to {}.".format(cfg_get('pgpool_min_level'),
                                                                              cfg_get('pgpool_max_level')))

    if cfg_get('max_good'):
        log.info("Stopping after {} GOOD accounts.".format(cfg_get('max_good')))

    init_mr_mime(user_cfg=mrmime_cfg)
