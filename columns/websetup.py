"""Setup the columns application"""
import logging, os

import pylons.test

from columns.config.environment import load_environment
from columns.model import set_default_settings, meta

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
	"""Place any commands to setup columns here"""
	# Don't reload the app if it was loaded under the testing environment
	if not pylons.test.pylonsapp:
		env = load_environment(conf.global_conf, conf.local_conf)
	else:
		# Create a fresh database
		meta.metadata.drop_all(bind=meta.engine, checkfirst=True)
	
	# Create the tables if they aren't there already
	meta.metadata.create_all(bind=meta.engine, checkfirst=True)
	
	# initialize settings with default values
	set_default_settings(conf)
