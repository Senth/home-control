import logging

LOG_LOCATION = '/tmp/home-control.log'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', filename=LOG_LOCATION, level=LOG_LEVEL, datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger(__name__).addHandler(logging.StreamHandler())