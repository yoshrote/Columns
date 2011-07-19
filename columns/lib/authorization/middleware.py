from columns.lib.authorization.exceptions import *
__all__ = ['AuthorizationMiddleware']
class AuthorizationMiddleware(object):
	"""Handles authorization based on a SitePermissions object.
	
	AuthorizationMiddleware expects requests to go through
	Beaker and Routes middleware before reaching it
	
	It can be disabled by adding 'columns.authorize.disabled' to the environment or setting it as disabled upon initialization
	"""
	def __init__(self, app, resource_map, permission_map, disabled=False):
		"""Initialize the ErrorRedirect
		
		``permission_map``
			The python path to a SitePermissions instance
		``resource_map``
			The python path to a dictionary mapping to the model
		``disabled``
			Boolean flag to disable middleware from config file
		
		"""
		self.app = app
		self.disabled = disabled
		resource_map, resource_obj = resource_map.rsplit('.',1)
		resource_module = __import__(resource_map,globals(),locals(),[resource_obj],0)
		self.resource_map = getattr(resource_module,resource_obj)
		
		permission_map, permission_obj = permission_map.rsplit('.',1)
		permission_module = __import__(permission_map,globals(),locals(),[permission_obj],0)
		self.permission_map = getattr(permission_module,permission_obj)
	
	def __call__(self, environ, start_response):
		environ['columns.authorize.resources'] = self.resource_map
		environ['columns.authorize.permissions'] = self.permission_map
		if self.disabled is not True and 'columns.authorize.disabled' not in environ:
			route_dict = environ['wsgiorg.routing_args'][1].copy()
			try:
				resource = route_dict.pop('controller')
				action = route_dict.pop('action')
			except KeyError:
				return self.app(environ, start_response)
			try:
				self.permission_map.authorize(environ,resource,action,**route_dict)
			except AuthorizationException:
				return HTTPForbidden()(environ, start_response)
			except HTTPUnauthorized:
				return HTTPUnauthorized()(environ, start_response)
		return self.app(environ, start_response)
	

