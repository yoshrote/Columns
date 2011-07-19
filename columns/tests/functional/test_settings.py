from columns.tests import *
from columns.lib import json

class TestSettingsController(TestController):
	def setUp(self):
		from columns.model import Setting
		tmp = Setting.from_dict(dict(
			module=u'test',
			values={'name':u'test_user'}
		))
		try:
			tmp.save()
		except Exception, ex:
			print ex
	
	def tearDown(self):
		from columns.model import meta, Setting
		meta.Session.query(Setting).delete()
		meta.Session.close()
	
	def test_index(self):
		response = self.app.get(url('settings'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
		# Test response...
	
	def test_create(self):
		response = self.app.post(url('settings'), extra_environ=self.extra_environ, params=dict(
			module='test2',
			values={'t1':1,'t2':'blah'}
		))
	
	def test_create_json(self):
		response = self.app.post(url('formatted_settings', format='json'), content_type='application/json', extra_environ=self.extra_environ, body=json.dumps(dict(
			module='test3',
			values={'t1':1,'t2':'blah'}
		)))
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_settings', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	#def test_new(self):
	#	response = self.app.get(url('new_setting'), extra_environ=self.extra_environ)
	#	self.assertEqual(response.status_int,200)
	#
	def test_update(self):
		response = self.app.put(url('setting', id='test'), extra_environ=self.extra_environ, params=dict(
			values={'t1':1,'t2':'blah'}
		))
	
	def test_update_json(self):
		response = self.app.put(url('formatted_setting', id='test', format='json'), content_type='application/json', extra_environ=self.extra_environ, body=json.dumps(dict(
			values={'t1':1,'t2':'blah'}
		)))
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_setting', id='test', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('setting', id='test'), extra_environ=self.extra_environ, params=dict(_method='put',values={'t1':1,'t2':'blah'}))
	
	def test_new(self):
		response = self.app.get(url('new_setting'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_delete(self):
		response = self.app.delete(url('setting', id='test'), extra_environ=self.extra_environ)
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('setting', id='test'), extra_environ=self.extra_environ, params=dict(_method='delete'))
	
	def test_show(self):
		response = self.app.get(url('setting', id='test'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_show_bad_format(self):
		response = self.app.get(url('formatted_setting', id='test', format='json'), extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_edit(self):
		response = self.app.get(url('edit_setting', id='test'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
