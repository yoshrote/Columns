from columns.lib.authorization.exceptions import *
from columns.lib.authorization.util import *
from formencode import validators, Invalid
from formencode.compound import All, Any

__all__ = [
	'MinimumPermission','ResourceOwner','LoggedIn','All','Any','GoodToGo','Restricted','ArticleOwner','ArticleOwnerLockout','IsUnpublished',
	'is_logged_in','is_allowed'
]

def is_logged_in(environ):
	try:
		LoggedIn().to_python(None,environ)
	except HTTPUnauthorized:
		return False
	else:
		return True

from paste.deploy.converters import asbool
def is_allowed(url=None,resource=None,action=None):
	from pylons import config, request
	if url is not None:
		route_dict = config['routes.map'].match(url)
	else:
		route_dict = {'controller':resource,'action':action}
	if not asbool(config.get('no_auth','false')) and route_dict is not None and 'columns.authorize.disabled' not in request.environ:
		try:
			controller = route_dict['controller']
			request.environ['columns.authorize.permissions'].authorize(request.environ, controller, **route_dict)
		except (AuthorizationException, HTTPUnauthorized):
			return False
	return True

class GoodToGo(validators.FancyValidator):
	def to_python(self, value, state):
		pass

class Restricted(validators.FancyValidator):
	def to_python(self, value, state):
		raise AuthorizationException
	

class MinimumPermission(validators.FancyValidator):
	permission = ''
	permission_set = {}
	def to_python(self, value, state):
		session = state['beaker.session']
		test = user_permission(session)
		if test is None:
			raise HTTPUnauthorized
		if test > self.permission_set[self.permission]:
			raise AuthorizationException
	

class LoggedIn(validators.FancyValidator):
	def to_python(self, value, state):
		session = state['beaker.session']
		if user_permission(session) is None or user_id(session) is None:
			raise HTTPUnauthorized
	

class ResourceOwner(validators.FancyValidator):
	messages = {'incompatable_controller': '%(name)s is not compatable with the ResourceOwner predicate',}
	
	def to_python(self, value, state):
		#app_globals = state.app_globals
		session = state['beaker.session']
		try:
			controller = value['controller']
			resource_id = value['id']
			resource_type = state['columns.authorize.resources'][controller]
			resource = resource_type.get_from_id(resource_id)
			#resource = getattr(app_globals.db[controller],resource_type.__name__).get_from_id(resource_id)
			user_id_chk = user_id(state['beaker.session'])
			if user_id_chk is None:
				raise HTTPUnauthorized
			elif user_id_chk != resource.owner():
				raise AuthorizationException
		except (KeyError,AttributeError), ex:
			raise validators.Invalid(self.message("incompatable_controller",state,name=ex),value,state)
	

class ArticleOwner(validators.FancyValidator):
	messages = {'incompatable_controller': '%(name)s is not compatable with the ResourceOwner predicate',}
	
	def to_python(self, value, state):
		#app_globals = state.app_globals
		session = state['beaker.session']
		try:
			controller = value['controller']
			resource_id = value['id']
			from pylons import app_globals
			resource = app_globals.get_cached_article_from_id(resource_id)
			#resource = getattr(app_globals.db[controller],resource_type.__name__).get_from_id(resource_id)
			user_id_chk = user_id(session)
			if user_id_chk is None:
				raise HTTPUnauthorized
			elif user_id_chk != resource.owner():
				raise AuthorizationException
		except (KeyError,AttributeError), ex:
			raise validators.Invalid(self.message("incompatable_controller",state,name=ex),value,state)
	

class IsUnpublished(validators.FancyValidator):
	messages = {'incompatable_controller': '%(name)s is not compatable with the ResourceOwner predicate',}
	
	def to_python(self, value, state):
		#app_globals = state.app_globals
		session = state['beaker.session']
		try:
			controller = value['controller']
			resource_id = value['id']
			from pylons import app_globals
			resource = app_globals.get_cached_article_from_id(resource_id)
			if resource.published is not None:
				raise AuthorizationException
		except (KeyError,AttributeError), ex:
			raise validators.Invalid(self.message("incompatable_controller",state,name=ex),value,state)
	

class ArticleOwnerLockout(validators.FancyValidator):
	messages = {'incompatable_controller': '%(name)s is not compatable with the ResourceOwner predicate',}
	
	def to_python(self, value, state):
		#app_globals = state.app_globals
		session = state['beaker.session']
		try:
			controller = value['controller']
			resource_id = value['id']
			from pylons import app_globals
			import datetime
			resource = app_globals.get_cached_article_from_id(resource_id)
			user_id_chk = user_id(session)
			if user_id_chk is None:
				raise HTTPUnauthorized
			elif user_id_chk != resource.owner():
				raise AuthorizationException
			elif resource.published is not None and resource.published + datetime.timedelta(days=1) < datetime.datetime.utcnow():
				raise AuthorizationException
		except (KeyError,AttributeError), ex:
			raise validators.Invalid(self.message("incompatable_controller",state,name=ex),value,state)
	
