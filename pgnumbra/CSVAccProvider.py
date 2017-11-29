import logging
import threading

from pgnumbra.AccProvider import AccProvider
from pgnumbra.config import cfg_get
from pgnumbra.utils import load_accounts_file

log = logging.getLogger(__name__)


class CSVAccProvider(AccProvider):

    def __init__(self):
        self.num_provided = 0
        self.done = False
        self.lck = threading.Lock()
        self.accounts = load_accounts_file()

    def get_num_accounts(self):
        return len(self.accounts)

    def next(self):
        self.lck.acquire()

        acc = None
        try:
            if not self.done:
                if self.num_provided >= len(self.accounts):
                    self.finish()
                else:
                    acc = self.accounts[self.num_provided]
                    self.num_provided += 1
                    if self.num_provided % 100 == 0:
                        log.info("Provided {} accounts so far...".format(self.num_provided))
                    if self.num_provided >= len(self.accounts):
                        self.finish()
            return acc
        finally:
            self.lck.release()

    def finish(self):
        self.done = True
        log.info("Finished providing accounts. Provided {} of {} accounts in total.".format(self.num_provided,
                                                                                            len(self.accounts)))
