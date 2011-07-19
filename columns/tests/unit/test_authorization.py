import unittest
from columns.lib.authorization.util import SitePermissions, retrieve_user, user_id, user_permission
from columns.lib.authorization.predicates import is_logged_in, GoodToGo, Restricted, MinimumPermission, LoggedIn, ResourceOwner, IsUnpublished, ArticleOwner, ArticleOwnerLockout
from columns.lib.authorization.exceptions import AuthorizationException, HTTPUnauthorized
from columns.lib.authorization.middleware import AuthorizationMiddleware
from columns.lib.exc import Invalid
from columns.model import User, Page, Article, meta
import datetime

dt = datetime.datetime.today()

class TestAuthorizationUtil(unittest.TestCase):
	def setUp(self):
		tmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		tmp.save()
	
	def tearDown(self):
		meta.Session.query(User).delete()
		meta.Session.close()
	
	def test_retreive_user(self):
		self.assertEquals(retrieve_user({}), None)
		self.assertNotEquals(retrieve_user({'user_id':1}), None)
	
	def test_user_id(self):
		self.assertEquals(user_id({'user_id':1,'user_type':9}),1)
		self.assertEquals(user_id({'user_type':9}),None)
	
	def test_user_permission(self):
		self.assertEquals(user_permission({'user_id':1,'user_type':9}),9)
		self.assertEquals(user_permission({'user_id':1}),None)
	
	def test_is_logged_in(self):
		self.assertEqual(is_logged_in({'beaker.session':{'user_id':1,'user_type':1}}),True)
		self.assertEqual(is_logged_in({'beaker.session':{}}),False)
	
	def test_is_allowed(self):
		pass

class TestAuthorizationPredicates(unittest.TestCase):
	def setUp(self):
		ptmp = Page.from_dict(dict(
			id=1,
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=True,can_post=True,in_main=True,in_menu=False,
		))
		ptmp.save()
		utmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		utmp.save()
		atmp = Article(**dict(
			id=1,
			created=dt,
			updated=dt,
			atom_id=u'-'.join([dt.strftime("%Y-%m-%d"),u'test']),
			title=u'test',
			content=u'',
			summary=u'',
			published=dt,
			links=[],
			author_id=utmp.id,
			author={
				'name':u'test_user',
			},
			contributors=[],
			metatags={},
			metacontent=u'',
			permalink=u'-'.join([dt.strftime("%Y-%m-%d"),u'test']),
			sticky=False,
			can_comment=True,
			page_id=ptmp.id,
		))
		atmp.save()
		a2tmp = Article(**dict(
			id=2,
			created=dt,
			updated=dt,
			atom_id=u'-'.join([dt.strftime("%Y-%m-%d"),u'test2']),
			title=u'test2',
			content=u'',
			summary=u'',
			published=None,
			links=[],
			author_id=utmp.id,
			author={
				'name':u'test_user',
			},
			contributors=[],
			metatags={},
			metacontent=u'',
			permalink=u'-'.join([dt.strftime("%Y-%m-%d"),u'test2']),
			sticky=False,
			can_comment=True,
			page_id=ptmp.id,
		))
		a2tmp.save()
		a3tmp = Article(**dict(
			id=3,
			created=datetime.datetime.fromtimestamp(0),
			updated=datetime.datetime.fromtimestamp(0),
			atom_id=u'-'.join([datetime.datetime.fromtimestamp(0).strftime("%Y-%m-%d"),u'test3']),
			title=u'test3',
			content=u'',
			summary=u'',
			published=datetime.datetime.fromtimestamp(0),
			links=[],
			author_id=utmp.id,
			author={
				'name':u'test_user',
			},
			contributors=[],
			metatags={},
			metacontent=u'',
			permalink=u'-'.join([datetime.datetime.fromtimestamp(0).strftime("%Y-%m-%d"),u'test3']),
			sticky=False,
			can_comment=True,
			page_id=ptmp.id,
		))
		a3tmp.save()
	
	def tearDown(self):
		meta.Session.query(Article).delete()
		meta.Session.query(User).delete()
		meta.Session.query(Page).delete()
		meta.Session.close()
	
	def test_restricted(self):
		res = Restricted()
		self.assertRaises(AuthorizationException, res.to_python, {}, {})
	
	def test_minimumpermission(self):
		res = MinimumPermission(permission_set={'super':1, 'admin':2, 'editor':3, 'author':4,'probation':8,'subscriber':9}, permission='editor')
		self.assertRaises(AuthorizationException, res.to_python, {}, {'beaker.session':{'user_type':9}})
		self.assertRaises(HTTPUnauthorized, res.to_python, {}, {'beaker.session':{}})
		res.to_python(None, {'beaker.session':{'user_type':1}})
	
	def test_resourceowner(self):
		res = ResourceOwner()
		res.to_python({'controller':'users','id':1},{'columns.authorize.resources':{'users':User},'beaker.session':{'user_id':1}})
		self.assertRaises(HTTPUnauthorized,res.to_python,{'controller':'users','id':1},{'columns.authorize.resources':{'users':User},'beaker.session':{}})
		self.assertRaises(AuthorizationException,res.to_python,{'controller':'users','id':1},{'columns.authorize.resources':{'users':User},'beaker.session':{'user_id':6}})
		self.assertRaises(Invalid,res.to_python,{'controller':'qwerty','id':1},{'columns.authorize.resources':{'users':User},'beaker.session':{'user_id':6}})
	
	def test_articleowner(self):
		res = ArticleOwner()
		res.to_python({'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
		self.assertRaises(HTTPUnauthorized,res.to_python,{'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{}})
		self.assertRaises(AuthorizationException,res.to_python,{'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':6}})
		self.assertRaises(Invalid,res.to_python,{'id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':6}})
	
	def test_isunpublished(self):
		res = IsUnpublished()
		res.to_python({'controller':'articles','id':2},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
		self.assertRaises(AuthorizationException,res.to_python,{'controller':'users','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
		self.assertRaises(Invalid,res.to_python,{'id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
	
	def test_articleownerlockout(self):
		res = ArticleOwnerLockout()
		res.to_python({'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
		self.assertRaises(HTTPUnauthorized,res.to_python,{'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{}})
		self.assertRaises(AuthorizationException,res.to_python,{'controller':'articles','id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':6}})
		self.assertRaises(AuthorizationException,res.to_python,{'controller':'articles','id':3},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':1}})
		self.assertRaises(Invalid,res.to_python,{'id':1},{'columns.authorize.resources':{'articles':Article},'beaker.session':{'user_id':6}})
	
	def test_loggedin(self):
		res = LoggedIn()
		res.to_python(None,{'beaker.session':{'user_id':1,'user_type':1}})
		self.assertRaises(HTTPUnauthorized,res.to_python,None,{'beaker.session':{}})
	

class TestSitePermissions(unittest.TestCase):
	def test_authorize(self):
		sp = SitePermissions({1:'super', 2:'admin', 3:'editor', 4:'author',8:'probation',9:'subscriber'})
		sp.authorize({})
		sp.add_permissions('test',{'index':GoodToGo()})
		sp.authorize({},'test','index')

class TestAuthorizationMiddleware(unittest.TestCase):
	def setUp(self):
		def simple_app(environ, start_response):
			"""Simplest possible application object"""
			status = '200 OK'
			response_headers = [('Content-type', 'text/plain')]
			start_response(status, response_headers)
			return ['Hello world!\n']
		
		def start_response(status, response_headers, exc_info=None):
			pass
		
		self.app = simple_app
		self.start_response = start_response
	
	def test_middleware(self):
		app = AuthorizationMiddleware(self.app, 'columns.model.RESOURCE_MAP', 'columns.config.authorization.AUTHORIZE_MAP', False)
		self.assertEquals(app({'wsgiorg.routing_args':(None,{})},self.start_response),['Hello world!\n'])
		self.assertEquals(app({'wsgiorg.routing_args':(None,{'controller':'articles','action':'index'})},self.start_response),['Hello world!\n'])
		res = app({'REQUEST_METHOD':'POST','wsgiorg.routing_args':(None,{'controller':'articles','action':'create'}),'beaker.session':{}},self.start_response)
		self.assert_(res[0].startswith('401 Unauthorized'))
		res = app({'REQUEST_METHOD':'POST','wsgiorg.routing_args':(None,{'controller':'articles','action':'create'}),'beaker.session':{'user_type':9}},self.start_response)
		self.assert_(res[0].startswith('403 Forbidden'))
		

