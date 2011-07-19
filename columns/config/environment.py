"""Pylons environment configuration"""
import os

from pylons.configuration import PylonsConfig

import columns.lib.app_globals as app_globals
from columns.lib.views import make_jinja_environment
from columns.config.routing import make_map
from columns.model import init_model

def load_environment(global_conf, app_conf):
	"""Configure the Pylons environment via the ``pylons.config``
	object
	"""
	config = PylonsConfig()
	
	# Pylons paths
	root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	paths = dict(root=root,
				controllers=os.path.join(root, 'controllers'),
				static_files=os.path.join(root, 'public'),
				templates=[os.path.join(root, 'templates')])
	
	# Initialize config with the basic options
	config.init_app(global_conf, app_conf, package='columns', paths=paths)
	
	config['pylons.paths']['static_files'] = config['static_file_path']
	
	config['routes.map'] = make_map(config)
	import columns.lib.helpers
	config['pylons.app_globals'] = app_globals.Globals(config)
	config['pylons.h'] = columns.lib.helpers
	
	# Setup cache object as early as possible
	import pylons
	pylons.cache._push_object(config['pylons.app_globals'].cache)
	
	# Create the Jinja2 Environment
	config['pylons.app_globals'].jinja2_env = make_jinja_environment(config)
	config['pylons.strict_c'] = True
	
	# Setup the SQLAlchemy database engine
	init_model(config, config['pylons.app_globals'])
	
	# CONFIGURATION OPTIONS HERE (note: all config options will override
	# any Pylons config options)
	
	return config
