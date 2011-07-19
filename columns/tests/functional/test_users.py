from columns.tests import *
from columns.lib import json

class TestUsersController(TestController):
	extra_environ = {'columns.authorize.disabled':True}
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
		#try:
		#	tmp = User.get_from_id(1)
		#	tmp.delete()
		#except:
		#	pass
	
	def test_index(self):
		response = self.app.get(url('users'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
		# Test response...
	
	def test_create(self):
		response = self.app.post(url('users'), extra_environ=self.extra_environ, params=dict(
			name=u'test_user12',
			open_id=u'http://myfake.openid.com',
			fb_id='',
			twitter_id='',
			type=1,
			profile=u'http://www.example.com',
		))
		from columns.model import User, meta
		tmp = meta.Session.query(User).filter(User.name == u'test_user12').one()
		assert tmp.name == u'test_user12'
		assert tmp.open_id == u'http://myfake.openid.com'
		assert tmp.fb_id == None
		assert tmp.twitter_id == None
		assert tmp.type == 1
		assert tmp.profile == u'http://www.example.com'
	
	def test_create_json(self):
		response = self.app.post(url('formatted_users', format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			name=u'test_user12',
			open_id=u'http://myfake.openid.com',
			fb_id='',
			twitter_id='',
			type=1,
			profile=u'http://www.example.com',
		)))
		from columns.model import User, meta
		tmp = meta.Session.query(User).filter(User.name == u'test_user12').one()
		assert tmp.name == u'test_user12'
		assert tmp.open_id == u'http://myfake.openid.com'
		assert tmp.fb_id == None
		assert tmp.twitter_id == None
		assert tmp.type == 1
		assert tmp.profile == u'http://www.example.com'
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_users', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_new(self):
		response = self.app.get(url('new_user'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		response = self.app.put(url('user', id=1), extra_environ=self.extra_environ, params=dict(
			name=u'test_user',
			open_id=u'http://myfake.openid.com',
			fb_id='',
			twitter_id='',
			type=1,
			profile=u'http://www.example.com/32',
		))
		from columns.model import User
		tmp = User.get_from_id(1)
		print tmp.to_dict()
		assert tmp.name == u'test_user'
		assert tmp.open_id == u'http://myfake.openid.com'
		assert tmp.fb_id == None
		assert tmp.twitter_id == None
		assert tmp.type == 1
		assert tmp.profile == u'http://www.example.com/32'
	
	def test_update_json(self):
		response = self.app.put(url('formatted_user', id=1, format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			name=u'test_user',
			open_id=u'http://myfake.openid.com',
			fb_id='',
			twitter_id='',
			type=1,
			profile=u'http://www.example.com/32',
		)))
		from columns.model import User
		tmp = User.get_from_id(1)
		print tmp.to_dict()
		assert tmp.name == u'test_user'
		assert tmp.open_id == u'http://myfake.openid.com'
		assert tmp.fb_id == None
		assert tmp.twitter_id == None
		assert tmp.type == 1
		assert tmp.profile == u'http://www.example.com/32'
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_user', id=1, format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('user', id=1), extra_environ=self.extra_environ, params=dict(
			_method='put',
			name=u'test_user',
			open_id=u'http://myfake.openid.com',
			fb_id='',
			twitter_id='',
			type=1,
			profile=u'http://www.example.com/dunno',
		))
		from columns.model import User
		tmp = User.get_from_id(1)
		assert tmp.name == u'test_user'
		assert tmp.open_id == u'http://myfake.openid.com'
		assert tmp.fb_id == None
		assert tmp.twitter_id == None
		assert tmp.type == 1
		assert tmp.profile == u'http://www.example.com/dunno'
	
	def test_delete(self):
		response = self.app.delete(url('user', id=1), extra_environ=self.extra_environ)
		from columns.model import User
		tmp = User.get_from_id(1)
		assert tmp == None
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('user', id=1), extra_environ=self.extra_environ, params=dict(_method='delete'))
		from columns.model import User
		tmp = User.get_from_id(1)
		assert tmp == None
	
	def test_show(self):
		response = self.app.get(url('user', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_show(self):
		response = self.app.get(url('user', id=1, p='a2'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_edit(self):
		response = self.app.get(url('edit_user', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
