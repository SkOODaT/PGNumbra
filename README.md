# PGNumbra Tools
Tools that help in identifying and analyzing shadowbanned POGO accounts.

# Support the Author [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/slop)
If you like PGNumbra Tools and feel the urgent need to thank me, just drop me one or more **level 30 accounts** or buy me a **[PokeHash key](https://talk.pogodev.org/d/51-api-hashing-service-by-pokefarmer)**. Seriously, that would be so awesome! :-D You can find me on various Pokémon related Discords as "sLoPPydrive".

# Disclaimer
PGNumbra Tools or its author takes no responsibility if your accounts get banned in any way. As with any other 3rd party software breaking the ToS there is absolutely no guarantee that your accounts stay safe. This software is purely for educational purpose.

## Tool 1: `compare_scans.py`

A specific location gets scanned (`GET_MAP_OBJECTS` request) over and over again and the number of found Pokémon get compared in a table view. This way you can determine if some accounts are seeing more than others and also *what* they see exactly. Of course you should have at least one account that is not shadowbanned to see the difference.

## Tool 2: `shadowcheck.py`

A tool for mass-checking accounts. For every account exactly one `GET_MAP_OBJECTS` call is made to determine what Pokémon the account can see. If there is any of the rare Pokémon (which shadowbanned accounts cannot see) in the wild or nearby list, the account is considered **good**, otherwise **blind**. The tool sorts the accounts to files `acc-good.csv`, `acc-blind.csv`, `acc-captcha.csv` and `acc-error.csv` (in case of bans or other errors). Note that these files will be **overwritten** with each new run.

Note: **You should use a location where you are sure that a "rare" Pokémon is nearby. A nest of rare Pokemon is recommended.**

## Common and Rare Pokemon

The following Pokemon are "**common**" and can be seen by every account. All others are called "**rare**" and can not be seen by shadowbanned accounts.

Generation 1 | Generation 2
------------ | ------------
Pidgey       | Sentret
Rattata      | Ledyba
Ekans        | Spinarak
Sandshrew    | Natu
Nidoran F    | Marill     
Nidoran M    | Hoppip   
Zubat        | Sunkern   
Oddish       | Wooper
Paras        | Murkrow
Meowth       | Snubbull
Psyduck      | Slugma
Poliwag      | 
Bellsprout   |
Tentacool    |
Geodude      |
Ponyta       |
Magnemite    |
Krabby       |
Goldeen      |
Staryu       |
Magikarp     |

## Installation
Do the regular `pip install -r requirements.txt` stuff. That's it.

## Configuration
Both tools use the same configuration file. Just copy&edit `config.ini.sample` to `config.ini` and either add some accounts and/or proxies to their respective files or configure PGPool. Then run `python <script name>`. You can also use the commandline to configure PGNumbra Tools. The arguments are:

```
optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Specify configuration file.
  -lat LATITUDE, --latitude LATITUDE
                        Latitude of location to scan.
  -lng LONGITUDE, --longitude LONGITUDE
                        Longitude of location to scan.
  -hk HASH_KEY, --hash-key HASH_KEY
                        Hash key to use.
  -p PROXIES_FILE, --proxies-file PROXIES_FILE
                        Load proxy list from text file (one proxy per line).
  -r SCAN_RETRIES, --scan-retries SCAN_RETRIES
                        Number of retries when scanning a location.
  -n, --include-nearby  Include nearby Pokemon in compare_scans.py - always
                        true for shadowcheck.py.
  -f {id,short,full}, --pokemon-format {id,short,full}
                        Format of Pokemons in compare_scans.py table overview.
  -t THREADS, --threads THREADS
                        Number of parallel threads to check accounts with
                        shadowcheck.py.
  -pgpu PGPOOL_URL, --pgpool-url PGPOOL_URL
                        Address of PGPool to load accounts from and/or update
                        their details.
  -pgpn PGPOOL_NUM_ACCOUNTS, --pgpool-num-accounts PGPOOL_NUM_ACCOUNTS
                        Load this many banned or new accounts from PGPool.
                        --pgpool-url required.
  -a ACCOUNTS_FILE, --accounts-file ACCOUNTS_FILE
                        Load accounts from CSV file containing
                        "auth_service,username,passwd" lines.
```

## PGPool Integration

There are basically 2 use cases for PGPool with PGNumbra:

1. Updating account details to PGPool as you use or check them. Accounts themselves will be read from a CSV file.
2. Requesting accounts from PGPool to check them for bans/shadowbans.

For both you will need to set the `--pgpool-url` to point to a running PGPool instance. For 2. you will also need to specify the number of accounts to request from PGPool via `--pgpool-num-accounts`.
In this case you must not specify a CSV file via `--accounts-file`. The accounts being requested from PGPool are currently not in use and either **new** and have unkonwn ban/shadowban status or they are **unusable** ()being banned or shadowbanned).

Because you don't have fine-grained control over which accounts get requested from PGPool you will usually only use it with `shadowcheck.py`. For `compare_scans.py` it is better to provide an `--accounts-file`.
