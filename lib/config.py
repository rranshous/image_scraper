

from os.path import abspath, dirname, join as path_join
from casconfig import CasConfig

here = dirname(abspath(__file__))
base = dirname(here)
config_dir = path_join(base, 'config')

# TODO: cache
def get_config(debug, subtype=None):
    """
    returns a dictionary of the config for the specified
    subtype, development or production depending on debug log
    """

    config_type = 'production' if not debug else 'development'
    print 'reading config [%s|%s]: %s' % (
            config_type, subtype or '', config_dir)
    config = CasConfig(config_dir)
    config.setup(config_type, subtype)
    return config

