"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, redirect
from columns.lib.views import render_jinja2 #, render_jinja2_block 

class BaseController(WSGIController):
	def __call__(self, environ, start_response):
		"""Invoke the Controller"""
		# WSGIController.__call__ dispatches to the Controller method
		# the request is routed to. This routing information is
		# available in environ['pylons.routes_dict']
		return WSGIController.__call__(self, environ, start_response)
	
	def __before__(self):
		import columns.config.authorization
		self.permissions_map = columns.config.authorization.INV_PERMISSIONS
		session = self._py_object.session
		for k,v in self._py_object.request.environ.get('test.session',{}).items():
			session[k] = v
		session.save()
	
	def __after__(self):
		from columns.model import meta
		meta.Session.close()

'''
atom:link rel acceptable values
	a-zA-Z0-9!$&'()*+,;=
'''