import logging
import time
from threading import Thread

from pgnumbra.SingleLocationScanner import SingleLocationScanner
from pgnumbra.config import cfg_get, cfg_init
from pgnumbra.console import print_status
from pgnumbra.proxy import init_proxies, get_new_proxy
from pgnumbra.utils import load_accounts

logging.basicConfig(filename="compare_scans.log", level=logging.INFO,
    format='%(asctime)s [%(threadName)16s][%(module)14s][%(levelname)8s] %(message)s')

log = logging.getLogger(__name__)

# Silence some loggers
logging.getLogger('pgoapi').setLevel(logging.WARNING)

scanners = []

# ===========================================================================

log.info("PGNumbra CompareScans starting up.")

cfg_init()

lat = cfg_get('latitude')
lng = cfg_get('longitude')

init_proxies()

accounts = load_accounts()

for acc in accounts:
    t = Thread(target=acc.run)
    t.daemon = True
    t.start()

# Start thread to print current status and get user input.
t = Thread(target=print_status,
           name='status_printer', args=(accounts,))
t.daemon = True
t.start()

# Dummy endless loop.
while True:
    time.sleep(1)
