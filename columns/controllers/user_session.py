import logging

from pylons import response, session, url

from columns.lib.base import BaseController, render_jinja2, abort, redirect
from columns.lib.authentication import AuthenticationAction, AuthenticationResponse

log = logging.getLogger(__name__)

class UserSessionController(BaseController):
	def create(self):
		return render_jinja2('/blog/login.jinja')
	
	def delete(self):
		session.invalidate()
		redirect(url("main"))
	
	@AuthenticationAction()
	def challenge(self):
		redirect(url("login"))
	
	@AuthenticationResponse()
	def verify(self):
		redirect(url("login"))
	
	def xrds(self):
		response.content_type = 'application/xrds+xml'
		return render_jinja2('/xrds.jinja')
	

