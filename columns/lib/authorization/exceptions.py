from webob.exc import HTTPUnauthorized, HTTPForbidden
from formencode import Invalid

class AuthorizationException(Exception):
	message = "The user is not authorized for this action."
	def __str__(self):
		return self.message
	
