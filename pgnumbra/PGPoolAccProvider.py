import json
import threading

import logging

import requests

from pgnumbra.AccProvider import AccProvider
from pgnumbra.config import cfg_get
from pgnumbra.utils import pgpool_load_accounts

log = logging.getLogger(__name__)


class PGPoolAccProvider(AccProvider):

    def __init__(self):
        self.num_provided = 0
        self.done = False
        self.provided_accounts = []
        self.lck = threading.Lock()

    def get_num_accounts(self):
        return cfg_get('pgpool_num_accounts')

    def next(self):
        self.lck.acquire()

        acc = None
        try:
            if not self.done:
                accounts = pgpool_load_accounts(1)

                if not accounts:
                    log.warning("Got no further account back from PGPool.")
                    self.finish()
                else:
                    acc = accounts[0]
                    log.debug("Loaded account #{} ({}) from PGPool".format(self.num_provided, acc['username']))
                    if not (acc['username'] in self.provided_accounts):
                        self.provided_accounts.append(acc['username'])
                    else:
                        log.info("Loaded previously checked account. Round trip done.")
                        self.release(acc['username'])
                        acc = None
                        self.finish()

                    if acc:
                        self.num_provided += 1
                        if self.num_provided % 100 == 0:
                            log.info("Provided {} accounts so far...".format(self.num_provided))
                        if self.num_provided >= cfg_get('pgpool_num_accounts'):
                            self.finish()
            return acc
        finally:
            self.lck.release()

    def finish(self):
        self.done = True
        log.info("Finished providing accounts. Provided {} of {} accounts in total.".format(self.num_provided, cfg_get(
            'pgpool_num_accounts')))

    def release(self, username):
        url = '{}/account/release'.format(cfg_get('pgpool_url'))
        data = {
            'username': username
        }
        r = requests.post(url, data=json.dumps(data))
