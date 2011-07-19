from columns.tests import *

class TestAccountsController(TestController):
	extra_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'open_id',
		'oid':u'http://tester.example.com'
	},'columns.authorize.disabled':True}
	def setUp(self):
		from columns.model import User
		tmp = User.from_dict(dict(
			id=1,
			name=u'test_user',
			open_id=u'http://tester.example.com',
			fb_id=None,
			twitter_id=None,
			type=9,
			profile=u'http://www.example.com',
		))
		try:
			tmp.save()
		except:
			pass
		tmp2 = User.from_dict(dict(
			id=2,
			name=u'test_user2',
			open_id=u'http://tester2.example.com',
			fb_id=None,
			twitter_id=None,
			type=9,
			profile=u'http://www.example.com',
		))
		try:
			tmp2.save()
		except:
			pass
	
	def tearDown(self):
		from columns.model import User, meta
		meta.Session.query(User).delete()
		meta.Session.close()
	
	def test_create_facebook(self):
		tmp_environ = {'test.session':{
		'auth_type':u'facebook',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('accounts'), extra_environ=tmp_environ, params={'name':'qwerty_user'})
		sess = response.environ['beaker.session']
		from columns.model import User, meta
		tmp = meta.Session.query(User).filter(User.name=='qwerty_user').one()
		self.assertEquals(tmp.name,u'qwerty_user')
		self.assertEquals(sess['user_name'],u'qwerty_user')
		self.assertEquals(tmp.type,9)
		self.assertEquals(sess['user_type'],9)
		self.assertEquals(tmp.profile,None)
		self.assertEquals(sess['user_profile'],None)
		self.assertEquals(tmp.fb_id,u'1234567890')
	
	def test_create_twitter(self):
		tmp_environ = {'test.session':{
		'auth_type':u'twitter',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('accounts'), extra_environ=tmp_environ, params={'name':'qwerty_user'})
		sess = response.environ['beaker.session']
		from columns.model import User, meta
		tmp = meta.Session.query(User).filter(User.name=='qwerty_user').one()
		self.assertEquals(tmp.name,u'qwerty_user')
		self.assertEquals(sess['user_name'],u'qwerty_user')
		self.assertEquals(tmp.type,9)
		self.assertEquals(sess['user_type'],9)
		self.assertEquals(tmp.profile,None)
		self.assertEquals(sess['user_profile'],None)
		self.assertEquals(tmp.twitter_id,u'1234567890')
	
	def test_create_openid(self):
		tmp_environ = {'test.session':{
		'auth_type':u'openid',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('accounts'), extra_environ=tmp_environ, params={'name':'qwerty_user'})
		sess = response.environ['beaker.session']
		from columns.model import User, meta
		tmp = meta.Session.query(User).filter(User.name=='qwerty_user').one()
		self.assertEquals(tmp.name,u'qwerty_user')
		self.assertEquals(sess['user_name'],u'qwerty_user')
		self.assertEquals(tmp.type,9)
		self.assertEquals(sess['user_type'],9)
		self.assertEquals(tmp.profile,None)
		self.assertEquals(sess['user_profile'],None)
		self.assertEquals(tmp.open_id,u'1234567890')
	
	def test_new(self):
		response = self.app.get(url('new_account'))
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		tmp_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'facebook',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		
		response = self.app.put(url('accounts'), extra_environ=tmp_environ, params={'profile':'http://test.com'})
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.profile,u'http://test.com')
		self.assertEquals(sess['user_profile'],u'http://test.com')
		self.assertEquals(tmp.fb_id,u'1234567890')
	
	def test_update_2(self):
		tmp_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'openid',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		
		response = self.app.put(url('accounts'), extra_environ=tmp_environ, params={'profile':'http://test.com'})
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.profile,u'http://test.com')
		self.assertEquals(sess['user_profile'],u'http://test.com')
		self.assertEquals(tmp.open_id,u'1234567890')
	
	def test_update_nonexistant_user(self):
		tmp_environ = {'test.session':{
		'user_id':6,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'openid',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		
		response = self.app.put(url('accounts'), extra_environ=tmp_environ, params={'profile':'http://test.com'}, expect_errors=True)
		sess = response.environ['beaker.session']
		self.assertEqual(response.status_int,500)
		self.assertEquals(sess['user_profile'],u'http://www.example.com')
	
	def test_update_browser_fakeout(self):
		tmp_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'twitter',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		
		response = self.app.post(url('accounts'), extra_environ=tmp_environ, params={'_method':'put','profile':''})
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.profile,None)
		self.assertEquals(sess['user_profile'],None)
		self.assertEquals(tmp.twitter_id,u'1234567890')
	
	def test_delete(self):
		tmp_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'twitter',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		response = self.app.delete(url('accounts'), extra_environ=tmp_environ)
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp,None)
		self.assertEquals(sess.get('user_id',None),None)
	
	def test_delete_browser_fakeout(self):
		tmp_environ = {'test.session':{
		'user_id':1,
		'user_name':u'test_user',
		'user_type':9,
		'user_profile':u'http://www.example.com',
		'user_openid':u'http://tester.example.com',
		'user_fbid':None,
		'user_twitterid':None,
		'auth_type':u'twitter',
		'oid':u'1234567890'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('accounts'), extra_environ=tmp_environ, params=dict(_method='delete'))
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp,None)
		self.assertEquals(sess.get('user_id',None),None)
	
	#def test_show(self):
	#	response = self.app.get(url('account'), expect_errors=True)
	#	self.assertEqual(response.status_int,403)
	
	def test_edit(self):
		response = self.app.get(url('edit_account'), extra_environ=self.extra_environ, params={'profile':'http://test.com'})
		self.assertEqual(response.status_int,200)
	
	def test_check_unique_name_true(self):
		response = self.app.get(url('unique_account'), extra_environ=self.extra_environ, params={'name':'qwertyuiop'})
		self.assertEqual(response.body,"Not Taken")
	
	def test_check_unique_name_false(self):
		response = self.app.get(url('unique_account'), extra_environ=self.extra_environ, params={'name':'test_user'})
		self.assertEqual(response.body,"Already Taken")
	
	def test_check_unique_name_error(self):
		response = self.app.get(url('unique_account'), extra_environ=self.extra_environ)
		self.assertEqual(response.body,"Error")
	
	def test_set_name_true(self):
		response = self.app.post(url("set_name_accounts"), extra_environ=self.extra_environ, params={'name':'qwertyuiop'})
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.name,u"qwertyuiop")
		self.assertEquals(sess[u'user_name'],u"qwertyuiop")
	
	def test_set_name_false(self):
		response = self.app.post(url("set_name_accounts"), extra_environ=self.extra_environ, params={'name':'test_user2'})
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.name,u"test_user")
		self.assertEquals(sess[u'user_name'],u"test_user")
	
	def test_set_name_error(self):
		response = self.app.post(url("set_name_accounts"), extra_environ=self.extra_environ)
		sess = response.environ['beaker.session']
		from columns.model import User
		tmp = User.get_from_id(1)
		self.assertEquals(tmp.name,u"test_user")
		self.assertEquals(sess[u'user_name'],u"test_user")
	
