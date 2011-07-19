from sqlalchemy import engine_from_config
from webob.exc import HTTPInternalServerError
from columns.model import access_log_t, meta
from pylons.util import call_wsgi_application
import logging
import datetime
import operator

log = logging.getLogger(__name__)

class AnalyticsMiddleware(object):
	"""Gathers user information for statistical purposes
	It can be disabled by adding 'columns.analytics.disabled' to the environment
	"""
	def __init__(self, app, config, engine_prefix='analytics.', disabled=False):
		"""Initialize the ErrorRedirect
		
		``permission_map``
			The python path to a SitePermissions instance
		``engine_prefix``
			The prefix to be passed to engine_from_config. Default: 'analytics.'
		``disabled``
			Boolean flag to disable middleware from config file. Default: False
		
		"""
		self.app = app
		self.disabled = disabled
		self.engine = engine_from_config(config, engine_prefix)
	
	def __call__(self, environ, start_response):
		if self.disabled is True:
			return self.app(environ, start_response)
		
		access_log_t.create(bind=meta.engine,checkfirst=True)
		def wrapper_app(status, headers, exc_info=None):
			REMOTE_ADDR = environ.get('REMOTE_ADDR',None)	# '10.200.1.160'
			HTTP_REFERER = environ.get('HTTP_REFERER',None)	# '/frontend/domains'
			REQUEST_METHOD = environ['REQUEST_METHOD']		# 'GET'
			PATH_INFO = environ['PATH_INFO']				# '/frontend/references/registrations'
			route_dict = environ['wsgiorg.routing_args'][1]
			if route_dict.get('controller',None) == 'blog':
				meta.engine.execute(
					access_log_t.insert(),
					{'remote_ip':REMOTE_ADDR,
					'path_info':PATH_INFO,
					'request_method':REQUEST_METHOD,
					'referer_uri':HTTP_REFERER,
					'stamp':datetime.datetime.utcnow(),
				})
			return start_response(status, headers, exc_info)
		
		return self.app(environ,wrapper_app)
	

