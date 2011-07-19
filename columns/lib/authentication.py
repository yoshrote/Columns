import urllib, cgi
from decorator import decorator
from pylons.controllers.util import redirect
from pylons.controllers.util import Response, Request
from columns.lib import helpers
#from columns.lib import oauthtwitter
import oauthtwitter
from columns.lib import json
from columns.lib.exc import NoResultFound
from openid.consumer import consumer
from openid.extensions import pape, sreg

import logging
log = logging.getLogger(__name__)


__all__ = ['make_oid_store','store_user','retrieve_user','AuthenticationAction','AuthenticationResponse','AuthenticationMiddleware']
'''
from openid.store.interface import OpenIDStore
from openid.association import Association
from openid.store import nonce
from pymongo.errors import OperationFailure
class MongoStore(OpenIDStore):
	"""\
	This is the interface for the store objects the OpenID library
	uses.  It is a single class that provides all of the persistence
	mechanisms that the OpenID library needs, for both servers and
	consumers.
	 
	@change: Version 2.0 removed the C{storeNonce}, C{getAuthKey}, and C{isDumb}
		methods, and changed the behavior of the C{L{useNonce}} method
		to support one-way nonces.	It added C{L{cleanupNonces}},
		C{L{cleanupAssociations}}, and C{L{cleanup}}.
		
	@sort: storeAssociation, getAssociation, removeAssociation,
		useNonce
	"""
	associations_table = 'associations'
	nonces_table = 'nonces'
	def __init__(self, conn, associations_table=None, nonces_table=None):
		"""
		This creates a new MongoStore instance.  It requires an
		established database connection be given to it, and it allows
		overriding the default collection names.
		
		@param conn: This must be an established connection to a
			MongoDB database.
			
		@type conn: A pymongo compatable connection
			object.
			
		@param associations_table: This is an optional parameter to
			specify the name of the collection used for storing
			associations.  The default value is specified in
			C{L{MongoStore.associations_table}}.
			
		@type associations_table: C{str}
		
		@param nonces_table: This is an optional parameter to specify
			the name of the collection used for storing nonces.	The
			default value is specified in C{L{MongoStore.nonces_table}}.
			
		@type nonces_table: C{str}
		"""
		self.conn = conn
		self._table_names = {
			'associations': associations_table or self.associations_table,
			'nonces': nonces_table or self.nonces_table,
		}
		self.max_nonce_age = 6 * 60 * 60 # Six hours, in seconds
	
	def storeAssociation(self, server_url, association):
		"""
		This method puts a C{L{Association
		<openid.association.Association>}} object into storage,
		retrievable by server URL and handle.
		
		@param server_url: The URL of the identity server that this
			association is with.  Because of the way the server
			portion of the library uses this interface, don't assume
			there are any limitations on the character set of the
			input string.  In particular, expect to see unescaped
			non-url-safe characters in the server_url field.
			
		@type server_url: C{str}
		
		@param association: The C{L{Association
			<openid.association.Association>}} to store.
			
		@type association: C{L{Association
			<openid.association.Association>}}
			
		@return: C{None}
		
		@rtype: C{NoneType}
		"""
		a = association
		self.conn[self._table_names['associations']].find_and_modify({
			'server_url':server_url,
			'handle':a.handle,
			'issued':a.issued,
			'lifetime':a.lifetime,
			'assoc_type':a.assoc_type,
			'secret':a.secret
		}, update=True, upsert=True)
	
	def getAssociation(self, server_url, handle=None):
		"""
		This method returns an C{L{Association
		<openid.association.Association>}} object from storage that
		matches the server URL and, if specified, handle. It returns
		C{None} if no such association is found or if the matching
		association is expired.
		
		If no handle is specified, the store may return any
		association which matches the server URL.  If multiple
		associations are valid, the recommended return value for this
		method is the one most recently issued.
		
		This method is allowed (and encouraged) to garbage collect
		expired associations when found. This method must not return
		expired associations.
		
		@param server_url: The URL of the identity server to get the
			association for.  Because of the way the server portion of
			the library uses this interface, don't assume there are
			any limitations on the character set of the input string.
			In particular, expect to see unescaped non-url-safe
			characters in the server_url field.
			
		@type server_url: C{str}
			
		@param handle: This optional parameter is the handle of the
			specific association to get.  If no specific handle is
			provided, any valid association matching the server URL is
			returned.
			
		@type handle: C{str} or C{NoneType}
		
		@return: The C{L{Association
			<openid.association.Association>}} for the given identity
			server.
			
		@rtype: C{L{Association <openid.association.Association>}} or
			C{NoneType}
		"""
		if handle is not None:
			rows = self.conn[self._table_names['associations']].find({'server_url':server_url, 'handle':handle})
		else:
			rows = self.conn[self._table_names['associations']].find({'server_url':server_url})
		
		if len(rows) == 0:
			return None
		else:
			associations = []
			for values in rows:
				assoc = Association(**values)
				if assoc.getExpiresIn() == 0:
					self.removeAssociation(server_url, assoc.handle)
				else:
					associations.append((assoc.issued, assoc))
			
			if associations:
				associations.sort()
				return associations[-1][1]
			else:
				return None
	
	def removeAssociation(self, server_url, handle):
		"""
		This method removes the matching association if it's found,
		and returns whether the association was removed or not.
		
		@param server_url: The URL of the identity server the
			association to remove belongs to.  Because of the way the
			server portion of the library uses this interface, don't
			assume there are any limitations on the character set of
			the input string.  In particular, expect to see unescaped
			non-url-safe characters in the server_url field.
			
		@type server_url: C{str}
			
		@param handle: This is the handle of the association to
			remove.	 If there isn't an association found that matches
			both the given URL and handle, then there was no matching
			handle found.
			
		@type handle: C{str}
			
		@return: Returns whether or not the given association existed.
			
		@rtype: C{bool} or C{int}
		"""
		tmp = self.conn[self._table_names['associations']].find_and_modify({'server_url':server_url, 'handle':handle},remove=True)
		return tmp is not None
	
	def useNonce(self, server_url, timestamp, salt):
		"""Called when using a nonce.
			
		This method should return C{True} if the nonce has not been
		used before, and store it for a while to make sure nobody
		tries to use the same value again.	If the nonce has already
		been used or the timestamp is not current, return C{False}.
			
		You may use L{openid.store.nonce.SKEW} for your timestamp window.
			
		@change: In earlier versions, round-trip nonces were used and
		   a nonce was only valid if it had been previously stored
		   with C{storeNonce}.	Version 2.0 uses one-way nonces,
		   requiring a different implementation here that does not
		   depend on a C{storeNonce} call.	(C{storeNonce} is no
		   longer part of the interface.)
			
		@param server_url: The URL of the server from which the nonce
			originated.
			
		@type server_url: C{str}
			
		@param timestamp: The time that the nonce was created (to the
			nearest second), in seconds since January 1 1970 UTC.
		@type timestamp: C{int}
			
		@param salt: A random string that makes two nonces from the
			same server issued during the same second unique.
		@type salt: str
			
		@return: Whether or not the nonce was valid.
			
		@rtype: C{bool}
		"""
		if abs(timestamp - time.time()) > nonce.SKEW:
			return False
			
		try:
			self.conn[self._table_names['nonces']].insert({'server_url':server_url, 'timestamp':timestamp, 'salt':salt}, safe=True)
		except OperationFailure:
			# The key uniqueness check failed
			return False
		else:
			# The nonce was successfully added
			return True
	
	def cleanupNonces(self):
		"""Remove expired nonces from the store.
			
		Discards any nonce from storage that is old enough that its
		timestamp would not pass L{useNonce}.
			
		This method is not called in the normal operation of the
		library.  It provides a way for store admins to keep
		their storage from filling up with expired data.
			
		@return: the number of nonces expired.
		@returntype: int
		"""
		tmp = self.conn[self._table_names['nonces']].find({'timestamp':{'$lt':int(time.time()) - nonce.SKEW}})
		ids = [x['_id'] for x in tmp]
		self.conn[self._table_names['nonces']].remove({'_id':{'$in':ids}})
		return len(ids)
	
	def cleanupAssociations(self):
		"""Remove expired associations from the store.
			
		This method is not called in the normal operation of the
		library.  It provides a way for store admins to keep
		their storage from filling up with expired data.
			
		@return: the number of associations expired.
		@returntype: int
		"""
		
		tmp = self.conn[self._table_names['associations']].find({'$where': "this.issued + this.lifetime < %s"%int(time.time())})
		ids = [x['_id'] for x in tmp]
		self.conn[self._table_names['associations']].remove({'_id':{'$in':ids}})
		return len(ids)
	

'''
def make_oid_store():
	#try:
	#	#return MongoStore(pylons_obj.app_globals.connection['openid'])
	#	from openidmongodb import MongoDBStore
	#	from sqlalchemy.engine.url import make_url
	#	murl = make_url(pylons_obj.config['mongokit.url'])
	#	return MongoDBStore(host=murl.host, port=murl.port, db="openid", associations_collection="associations", nonces_collection="nonces")
	#except KeyError:
	from columns.model import meta
	drivername = meta.Session.bind.url.drivername
	if drivername == 'sqlite':
		from openid.store.sqlstore import SQLiteStore as SQLStore
	elif drivername == 'mysql':
		from openid.store.sqlstore import MySQLStore as SQLStore
	elif drivername == 'postgresql':
		from openid.store.sqlstore import PostgreSQLStore as SQLStore
	return SQLStore(meta.Session.connection().connection)

'''
def store_user(pylons_obj, user):
	session = pylons_obj.session
	session['user_id'] = user['_id']
	session['user_name'] = user.name
	session['user_type'] = user.type
	session['user_profile'] = user.profile
	session['user_openid'] = user.open_id
	session['user_fbid'] = user.fb_id
	session['user_twitterid'] = user.twitter_id
	session.save()

'''
def store_user(session, user):
	session['user_id'] = user.id
	session['user_name'] = user.name
	session['user_type'] = user.type
	session['user_profile'] = user.profile
	session['user_openid'] = user.open_id
	session['user_fbid'] = user.fb_id
	session['user_twitterid'] = user.twitter_id
	session.save()

def retrieve_user(session):
	try:
	 	return {
			'id':session['user_id'],
			'name':session['user_name'],
			'type':session['user_type'],
			'profile':session['user_profile'],
			'open_id':session['user_openid'],
			'fb_id':session['user_fbid'],
			'twitter_id':session['user_twitterid'],
		}
	except KeyError:
		return None

def create_user(session):
	from columns.model import User
	from columns.config.authorization import INV_PERMISSIONS
	item = User()
	item.type = INV_PERMISSIONS['subscriber']
	if session.get('auth_type',None) == 'facebook':
		item.fb_id = session['auth_oid']
	elif session.get('auth_type',None) == 'twitter':
		item.twitter_id = session['auth_oid']
	else: #session.get('auth_type',None) == 'openid':
		item.open_id = session['auth_oid']
	item.save()
	return item

def AuthenticationAction(type_param='auth_type',id_param='auth_id',on_failure='login'):
	def _oauth_handler(pylons_obj, auth_type, auth_id):
		session = pylons_obj.session
		response = pylons_obj.response
		app_globals = pylons_obj.app_globals
		otwitter = oauthtwitter.OAuthApi(app_globals.settings(u'twitter_oauth_key', u'auth'), app_globals.settings(u'twitter_oauth_secret', u'auth'))
		request_token = otwitter.getRequestToken()
		session['oauth_request_token'] = request_token
		session.save()
		authorization_url = otwitter.getAuthorizationURL(request_token)#otwitter.getSigninURL(request_token)
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
		
		oid_store = make_oid_store()
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
		from columns.model import User, meta
		session = pylons_obj.session
		url = pylons_obj.url
		app_globals = pylons_obj.app_globals
		
		request_token = session.pop('oauth_request_token')
		twitter_key, twitter_secret = app_globals.settings(u'twitter_oauth_key', u'auth'), app_globals.settings(u'twitter_oauth_secret', u'auth')
		#twitter = oauthtwitter.OAuthApi(twitter_key, twitter_secret, request_token)
		twitter = oauthtwitter.OAuthApi(twitter_key, twitter_secret)
		#access_token = twitter.getAccessToken()
		access_token = twitter.getAccessToken(request_token)
		twitter = oauthtwitter.OAuthApi(twitter_key, twitter_secret, access_token)
		user = twitter.VerifyCredentials() #twitter.GetUserInfo()
		session['auth_type'] = 'twitter'
		#session['auth_oid'] = user.id
		session['auth_oid'] = user['id']
		try:
			return meta.Session.query(User).filter(User.twitter_id==unicode(session['auth_oid'])).one()
		except:
			return None
	
	def _facebook_handler(pylons_obj):
		from columns.model import User, meta
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
		try:
			return meta.Session.query(User).filter(User.fb_id==unicode(session['auth_oid'])).one()
		except:
			return None
	
	def _openid_handler(pylons_obj):
		from columns.model import User, meta
		session = pylons_obj.session
		url = pylons_obj.url
		g = pylons_obj.app_globals
		request = pylons_obj.request
		
		oid_store = make_oid_store()
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
			try:
				return meta.Session.query(User).filter(User.open_id==unicode(session['auth_oid'])).one()
			except:
				return None
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


from pylons.util import call_wsgi_application
class AuthenticationMiddleware(object):
	"""Internally redirects a request based on status code
	
	AuthenticationMiddleware watches the response of the app it wraps. If the 
	response is an error code in the errors sequence passed the request
	will be re-run with the path URL set to the path passed in.
	
	This operation is non-recursive and the output of the second 
	request will be used no matter what it is.
	
	Should an application wish to bypass the error response (to 
	purposely return a 401), set 
	``environ['columns.authentication_redirect'] = True`` in the application.
	
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
		if status[:3] in self.errors and 'columns.authentication_redirect' not in environ and self.login_path:
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
	

