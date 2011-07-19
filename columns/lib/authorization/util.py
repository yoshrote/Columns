from columns.lib.authorization.exceptions import *
from decorator import decorator

__all__ = ['retrieve_user','user_permission','user_id','SitePermissions'] #,'AuthorizeAction'
def retrieve_user(session):
	if session.get('user_id',None) is None:
		return None
	from columns.model import User, meta
	return meta.Session.query(User).get(int(session['user_id']))

def user_permission(session):
	return session.get('user_type',None)

def user_id(session):
	return session.get('user_id',None)


#def AuthorizeAction(permissions, fallback=None):
#	def wrapper(func, self, *args, **kwargs):
#		environ = self._py_object.request.environ
#		try:
#			permissions.to_python(kwargs, environ)
#		except Invalid:
#			from pylons.controllers.util import abort, redirect
#			if fallback is not None:
#				url_gen = environ['routes.url']
#				redirect(url_gen(fallback))
#			else:
#				abort(403)
#		return func(self,*args,**kwargs)
#	
#	return decorator(wrapper)


class SitePermissions(object):
	permission_sets = {}
	def __init__(self, permissions=None):
		if isinstance(permissions,dict):
			for k,v in permissions.items():
				self.add_permissions(k,v)
	
	def add_permissions(self, controller_or_resource, permissions):
		self.permission_sets[controller_or_resource] = permissions
	
	def authorize(self, environ, controller_or_resource=None, action=None,**kwargs):
		try:
			validator = self.permission_sets[controller_or_resource][action]
		except KeyError:
			return
		else:
			validator.to_python(kwargs, environ)
	
	#def auth_decorator(self, controller_or_resource, action):
	#	def wrapper(func,self,*args,**kwargs):
	#		environ = self._py_object.request.environ
	#		try:
	#			validator = self.permission_sets[controller_or_resource][action]
	#		except KeyError:
	#			pass
	#		else:
	#			validator.to_python(kwargs, environ)
	#		return func(self,*args,**kwargs)
	#	
	#	return decorator(wrapper)
	#

