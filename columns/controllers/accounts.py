import logging, traceback

from pylons import request, response, session, app_globals, url

from columns.lib.base import BaseController, abort, redirect, render_jinja2
from columns.lib.authorization import is_logged_in
from columns.model import User, meta

log = logging.getLogger(__name__)

class AccountsController(BaseController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	def create(self):
		"""POST /accounts: Create a new item"""
		# url('accounts')
		from columns.config.authorization import INV_PERMISSIONS
		item = User()
		item.name = request.POST.get('name',None)
		item.profile = request.POST.get('profile',None)
		item.type = INV_PERMISSIONS['subscriber']
		if session.get('auth_type',None) == 'facebook':
			item.fb_id = session['oid']
		elif session.get('auth_type',None) == 'twitter':
			item.twitter_id = session['oid']
		elif session.get('auth_type',None) == 'openid':
			item.open_id = session['oid']
		session['user_name'] = item.name
		session['user_type'] = item.type
		session['user_profile'] = item.profile
		session.save()
		item.save(session, app_globals)
		redirect(url("main"))
	
	def new(self, format='html'):
		"""GET /accounts/new: Form to create a new item
		this is a super simple form to quickly create new user accounts
		when someone initially logs in with openid, oauth or facebook"""
		# url('new_account')
		return render_jinja2("/accounts/new.html.jinja")
	
	def update(self):
		"""PUT /accounts: Update an existing item"""
		# url('account')
		try:
			item = meta.Session.query(User).get(int(session['user_id']))
			#add any other update stuff
			#item = self.update_from_format(ctrl_obj, item, format, request, session, app_globals, parent_id)
			if session.get('auth_type',None) == 'facebook':
				item.fb_id = session['oid']
			elif session.get('auth_type',None) == 'twitter':
				item.twitter_id = session['oid']
			elif session.get('auth_type',None) == 'openid':
				item.open_id = session['oid']
			item.profile = request.POST.get('profile',u'').strip()
			if item.profile == u'':
				item.profile = None
			#session['user_name'] = item.name
			session['user_profile'] = item.profile
			session.save()
			item.save(session, app_globals)
		except:
			log.error(traceback.format_exc())
			abort(500)
		redirect(url("edit_account"))
	
	def delete(self):
		"""DELETE /accounts: Delete an existing item"""
		# url('account')
		user = meta.Session.query(User).get(int(session['user_id']))
		user.delete()
		session.invalidate()
		session.save()
		redirect(url("main"))
	
	#def show(self, format='html'):
	#	"""GET /accounts: Show a specific item"""
	#	# url('account')
	#	item = User.get_from_id(session['user_id'])
	#	return render_jinja2("/accounts/show.html.jinja")
	
	def edit(self, format='html'):
		"""GET /accounts/edit: Form to edit an existing item"""
		# url('edit_account')
		item = meta.Session.query(User).get(int(session['user_id']))
		return render_jinja2("/accounts/edit.html.jinja", extra_vars={'item':item})
	
	def check_unique_name(self):
		try:
			user_name = request.params.getone("name")
			if User.is_unique(user_name):
				return "Not Taken"
			else:
				return "Already Taken"
		except Exception, ex:
			log.error(traceback.format_exc())
			return "Error"
	
	#def add_link(self):
	#	account_type = request.GET.getone('type')
	#
	def set_name(self):
		try:
			user_name = request.POST.getone("name")
			if User.is_unique(user_name):
				user = meta.Session.query(User).get(int(session['user_id']))
				user.name = session['user_name'] = user_name
				user.save()
				session.save()
		except Exception, ex:
			log.error(traceback.format_exc())
		redirect(url("edit_account"))
	
	#def remove_link(self):
	#	account_type = request.GET.getone('type')
	#
