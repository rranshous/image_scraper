

from os.path import abspath, dirname, join as path_join
from casconfig import CasConfig

base = dirname(here)
config_dir = path_join(base, 'config')

# TODO: cache
def get_config(debug, subtype=None):
    """
    returns a dictionary of the config for the specified
    subtype, development or production depending on debug log
    """

    config_type = 'production' if not debug else 'development'
    print 'reading config [%s]: %s' % (config_type, config_dir)
    config = CasConfig(config_path)
    config.setup(config_type, subtype)

