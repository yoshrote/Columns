import unittest
from columns.tests import TestController
from pylons import session
from beaker.session import Session
from columns.lib.authentication import make_oid_store, store_user, retrieve_user, create_user, AuthenticationAction, AuthenticationResponse, AuthenticationMiddleware

#278-289, 305-313, 316-327, 330-341, 344-435, 438-561, 604-613

class TestAuthenticationUtils(TestController):
	def __init__(self, *args, **kwargs):
		session._push_object(Session({}))
		TestController.__init__(self, *args, **kwargs)
	
	def setUp(self):
		from columns.model import User
		tmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		try:
			tmp.save()
		except:
			pass
	
	def tearDown(self):
		from columns.model import User, meta
		meta.Session.query(User).delete()
		meta.Session.close()
	
	def test_store_user(self):
		from columns.model import User
		tmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		store_user(session,tmp)
		self.assertEquals(session['user_id'], tmp.id)
		self.assertEquals(session['user_name'], tmp.name)
		self.assertEquals(session['user_type'], tmp.type)
		self.assertEquals(session['user_profile'], tmp.profile)
		self.assertEquals(session['user_openid'], tmp.open_id)
		self.assertEquals(session['user_fbid'], tmp.fb_id)
		self.assertEquals(session['user_twitterid'], tmp.twitter_id)
	
	def test_retrieve_user(self):
		from columns.model import User
		res = retrieve_user(session)
		self.assertEquals(res,None)
		
		tmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		store_user(session,tmp)
		res = retrieve_user(session)
		self.assertEquals(res['id'], tmp.id)
		self.assertEquals(res['name'], tmp.name)
		self.assertEquals(res['type'], tmp.type)
		self.assertEquals(res['profile'], tmp.profile)
		self.assertEquals(res['open_id'], tmp.open_id)
		self.assertEquals(res['fb_id'], tmp.fb_id)
		self.assertEquals(res['twitter_id'], tmp.twitter_id)
	
	def test_create_user(self):
		session['auth_type'] = 'facebook'
		session['auth_oid'] = '1234567890'
		session.save()
		
		res = create_user(session)
		self.assertNotEquals(res.id, None)
		self.assertEquals(res.name, None)
		self.assertEquals(res.type, 9)
		self.assertEquals(res.profile, None)
		self.assertEquals(res.open_id, None)
		self.assertEquals(res.fb_id, '1234567890')
		self.assertEquals(res.twitter_id, None)
		
		session.clear()
		session['auth_type'] = 'twitter'
		session['auth_oid'] = '1234567890'
		session.save()
		
		res = create_user(session)
		self.assertNotEquals(res.id, None)
		self.assertEquals(res.name, None)
		self.assertEquals(res.type, 9)
		self.assertEquals(res.profile, None)
		self.assertEquals(res.open_id, None)
		self.assertEquals(res.twitter_id, '1234567890')
		self.assertEquals(res.fb_id, None)
		
		session.clear()
		session['auth_type'] = 'openid'
		session['auth_oid'] = 'http://user.example.com'
		session.save()
		
		res = create_user(session)
		self.assertNotEquals(res.id, None)
		self.assertEquals(res.name, None)
		self.assertEquals(res.type, 9)
		self.assertEquals(res.profile, None)
		self.assertEquals(res.open_id, 'http://user.example.com')
		self.assertEquals(res.twitter_id, None)
		self.assertEquals(res.fb_id, None)
		
	


'''
def make_oid_store(pylons_obj):
	try:
		#return MongoStore(pylons_obj.app_globals.connection['openid'])
		from sqlalchemy.engine.url import make_url
		murl = make_url(pylons_obj.config['mongokit.url'])
		return MongoDBStore(host=murl.host, port=murl.port, db="openid", associations_collection="associations", nonces_collection="nonces")
	except KeyError: #AttributeError:
		from columns.model import meta
		drivername = meta.Session.bind.url.drivername
		if drivername == 'sqlite':
			from openid.store.sqlstore import SQLiteStore as SQLStore
		elif drivername == 'mysql':
			from openid.store.sqlstore import MySQLStore as SQLStore
		elif drivername == 'postgresql':
			from openid.store.sqlstore import PostgreSQLStore as SQLStore
		return SQLStore(meta.Session.connection().connection)

def AuthenticationAction(type_param='auth_type',id_param='auth_id',on_failure='login'):
	def _oauth_handler(pylons_obj, auth_type, auth_id):
		session = pylons_obj.session
		response = pylons_obj.response
		app_globals = pylons_obj.app_globals
		otwitter = oauthtwitter.OAuthApi(app_globals.settings(u'twitter_oauth_key', u'auth'), app_globals.settings(u'twitter_oauth_secret', u'auth'))
		request_token = otwitter.getRequestToken()
		session['oauth_request_token'] = request_token
		session.save()
		authorization_url = otwitter.getSigninURL(request_token)
		response.status_int = 302
		response.headers['location'] = authorization_url
		return ""
	
	def _facebook_handler(pylons_obj, auth_type, auth_id):
		app_globals = pylons_obj.app_globals
		response = pylons_obj.response
		url = pylons_obj.url
		args = {
			'client_id':app_globals.settings(u'facebook_api_key', u'auth'),
			'redirect_uri':url('verify',qualified=True)
		}
		response.status_int = 302
		response.headers['location'] = '?'.join(["https://graph.facebook.com/oauth/authorize",urllib.urlencode(args)])
		return ""
	
	def _openid_handler(pylons_obj, auth_type, auth_id):
		"Process login form to begin authentication process"
		url = pylons_obj.url
		session = pylons_obj.session
		response = pylons_obj.response
		
		oid_store = make_oid_store(pylons_obj)
		login_type = auth_type
		openid_url = auth_id
		
		if login_type == 'google':
			openid_url = 'https://www.google.com/accounts/o8/id'
		elif login_type == 'aol':
			openid_url = 'http://openid.aol.com/'
		elif login_type == 'yahoo':
			openid_url = 'yahoo.com'
		
		oid_consumer = consumer.Consumer(session, oid_store)
		trust_root = url("main", qualified=True)
		return_to = url('verify', qualified=True)
		try:
			req = oid_consumer.begin(openid_url)
		except consumer.DiscoveryFailure:
			helpers.flash(u"Error in discovery",'error')
			session.save()
			redirect(url(on_failure))
		else:
			if req is None:
				helpers.flash(u"No OpenID services found for %s" % openid_url,'error')
				session.save()
				redirect(url(on_failure))
			else:
				sreg_request = sreg.SRegRequest(required=['nickname'], optional=['fullname', 'email'])
				req.addExtension(sreg_request)
				pape_request = pape.Request([pape.AUTH_PHISHING_RESISTANT])
				req.addExtension(pape_request)
				if req.shouldSendRedirect():
					redirect_url = req.redirectURL(trust_root, return_to)
					response.status_int = 302
					response.headers['location'] = redirect_url
					return ""
				else:
					return req.htmlMarkup(realm=trust_root,return_to=return_to)
	
	def wrapper(func,self,*args,**kwargs):
		pylons_obj = self._py_object
		request_post = pylons_obj.request.POST
		session = pylons_obj.session
		url = pylons_obj.url
		try:
			auth_type = request_post[type_param]
			auth_id = request_post[id_param]
		except KeyError:
			redirect(url(on_failure))
		else:
			session['auth_type'] = auth_type
			session.save()
			if auth_type == 'twitter':
				return _oauth_handler(pylons_obj, auth_type, auth_id)
			elif auth_type == 'facebook':
				return _facebook_handler(pylons_obj, auth_type, auth_id)
			else:
				return _openid_handler(pylons_obj, auth_type, auth_id)
		# in case we find ourselves here for some reason
		return func(self,*arg,**kwargs)
	
	return decorator(wrapper)

def AuthenticationResponse():
	def _oauth_handler(pylons_obj):
		from columns.model import User
		session = pylons_obj.session
		url = pylons_obj.url
		app_globals = pylons_obj.app_globals
		
		request_token = session.pop('oauth_request_token')
		twitter_key, twitter_secret = app_globals.settings(u'twitter_oauth_key', u'auth'), app_globals.settings(u'twitter_oauth_secret', u'auth')
		twitter = oauthtwitter.OAuthApi(twitter_key, twitter_secret, request_token)
		access_token = twitter.getAccessToken()
		twitter = oauthtwitter.OAuthApi(twitter_key, twitter_secret, access_token)
		user = twitter.GetUserInfo()
		session['auth_type'] = 'twitter'
		session['auth_oid'] = user.id
		return User.fetch_one({'twitter_id':unicode(session['auth_oid'])})
	
	def _facebook_handler(pylons_obj):
		from columns.model import User
		session = pylons_obj.session
		url = pylons_obj.url
		app_globals = pylons_obj.app_globals
		request = pylons_obj.request
		
		try:
			fbcode = request.params.get("code")
		except KeyError:
			redirect(url("login"))
		args = {
		'client_id':app_globals.settings(u'facebook_api_key', u'auth'),
		'redirect_uri':url('verify',qualified=True),
		'client_secret':app_globals.settings(u'facebook_secret', u'auth'),
		'code':fbcode,
		}
		fb_response = cgi.parse_qs(urllib.urlopen(
			"https://graph.facebook.com/oauth/access_token?" +
			urllib.urlencode(args)).read())
		try:
			access_token = fb_response["access_token"][-1]
		except KeyError:
			redirect(url('challenge', auth_type='facebook'))
			#return fb_login(g, session, request, response, 'facebook', None)
		
		# Download the user profile and cache a local instance of the
		# basic profile info
		profile = json.load(urllib.urlopen(
			"https://graph.facebook.com/me?" +
			urllib.urlencode(dict(access_token=access_token))))
		session['auth_type'] = 'facebook'
		session['auth_oid'] = profile["id"]
		return User.fetch_one({'fb_id':unicode(session['auth_oid'])})
	
	def _openid_handler(pylons_obj):
		from columns.model import User
		session = pylons_obj.session
		url = pylons_obj.url
		g = pylons_obj.app_globals
		request = pylons_obj.request
		
		oid_store = make_oid_store(pylons_obj)
		oid_consumer = consumer.Consumer(session, oid_store)
		info = oid_consumer.complete(request.params, url('verify', qualified=True))
		
		sreg_resp = None
		pape_resp = None
		display_identifier = info.getDisplayIdentifier()
		
		if info.status == consumer.FAILURE and display_identifier:
			helpers.flash(u"Verification of %(display_identifier)s failed: %(message)s" % {'display_identifier':display_identifier,'message':info.message},'error')
		elif info.status == consumer.SUCCESS:
			sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)
			#pape_resp = pape.Response.fromSuccessResponse(info)
			if info.endpoint.canonicalID:
				session['auth_oid'] = info.endpoint.canonicalID
			else:
				session['auth_oid'] = display_identifier
			return User.fetch_one({'open_id':unicode(session['auth_oid'])})
		elif info.status == consumer.CANCEL:
			helpers.flash(u'Verification cancelled','error')
		elif info.status == consumer.SETUP_NEEDED:
			setup_url = info.setup_url
			if setup_url:
				helpers.flash(u'<a href=%s>Setup needed</a>' % helpers.literal(setup_url),'error')
			else:
				helpers.flash(u'Setup needed','error')
		else:
			helpers.flash(u'Verification failed.')
		redirect(url("login"))
	
	def wrapper(func,self,*args,**kwargs):
		pylons_obj = self._py_object
		session = pylons_obj.session
		url = pylons_obj.url
		try:
			auth_type = session['auth_type']
		except KeyError:
			auth_type = pylons_obj.request.params.get('auth_type')
		if auth_type == 'twitter':
			user = _oauth_handler(pylons_obj)
		elif auth_type == 'facebook':
			user = _facebook_handler(pylons_obj)
		else:
			user = _openid_handler(pylons_obj)
		
		if user is not None:
			store_user(pylons_obj.session, user)
		else:
			if 'return_to' in session and 'modifying' in session:
				#we are adding a new authentication method to an existing account
				return_to = session.pop('return_to')
				session.pop('modifying')
				redirect(url(**return_to))
			else:
				#we are making a new account
				#redirect(url("new_account"))
				user = create_user(session)
				store_user(pylons_obj.session, user)
		
		if 'return_to' in session:
			return_to = session.pop('return_to')
			redirect(url(**return_to))
		else:
			redirect(url("main"))
	
	return decorator(wrapper)

class AuthenticationMiddleware(object):
	"""Internally redirects a request based on status code
	
	StatusCodeRedirect watches the response of the app it wraps. If the 
	response is an error code in the errors sequence passed the request
	will be re-run with the path URL set to the path passed in.
	
	This operation is non-recursive and the output of the second 
	request will be used no matter what it is.
	
	Should an application wish to bypass the error response (ie, to 
	purposely return a 401), set 
	``environ['pylons.status_code_redirect'] = True`` in the application.
	
	"""
	def __init__(self, app, login_path='/login'):
		"""Initialize the ErrorRedirect
		
		``errors``
			A sequence (list, tuple) of error code integers that should
			be caught.
		``path``
			The path to set for the next request down to the 
			application. 
		
		"""
		self.app = app
		self.login_path = login_path
		
		# Transform errors to str for comparison
		self.errors = ['401']
	
	def __call__(self, environ, start_response):
		#this is from StatusCodeRedirect
		status, headers, app_iter, exc_info = call_wsgi_application(
			self.app, environ, catch_exc_info=True
		)
		if status[:3] in self.errors and 'ndbp.auth_redirect' not in environ and self.login_path:
			# Create a response object
			environ['pylons.original_response'] = Response(
				status=status, headerlist=headers, app_iter=app_iter
			)
			environ['pylons.original_request'] = Request(environ)
			
			# Create a new environ to avoid touching the original request data
			new_environ = environ.copy()
			new_environ['PATH_INFO'] = self.login_path
			
			newstatus, headers, app_iter, exc_info = call_wsgi_application(
				self.app, new_environ, catch_exc_info=True
			)
		start_response(status, headers, exc_info)
		return app_iter
	

'''