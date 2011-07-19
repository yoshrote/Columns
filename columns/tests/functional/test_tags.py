from columns.tests import *
from columns.lib import json

class TestTagsController(TestController):
	def setUp(self):
		from columns.model import Tag, meta
		try:
			meta.Session.add(Tag(label=u'test'))
			meta.Session.flush()
		except:
			pass
	
	def tearDown(self):
		from columns.model import Tag, meta
		meta.Session.query(Tag).delete()
		meta.Session.close()
	
	def test_index(self):
		response = self.app.get(url('tags'))
		self.assertEqual(response.status_int,200)
	
	def test_create(self):
		response = self.app.post(url('tags'), params={'label':u'TEST2'})
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test2').one()
		assert tmp.label == u'TEST2'
	
	def test_create_json(self):
		response = self.app.post(url('formatted_tags', format='json'), body=json.dumps({'label':u'TEST2'}), content_type='application/json')
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test2').one()
		assert tmp.label == u'TEST2'
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_tags', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_new(self):
		response = self.app.get(url('new_tag'))
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		response = self.app.put(url('tag', id='test'), params={'label':u'TEST2'})
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test2').one()
		assert tmp.label == u'TEST2'
	
	def test_update_json(self):
		response = self.app.put(url('formatted_tag', id='test', format='json'), content_type='application/json', extra_environ=self.extra_environ, body=json.dumps({'label':u'TEST2'}))
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test2').one()
		assert tmp.label == u'TEST2'
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_tag', id='test', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('tag', id='test'), params=dict(_method='put',label='TEST2'))
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test2').one()
		assert tmp.label == u'TEST2'
	
	def test_delete(self):
		response = self.app.delete(url('tag', id='test'))
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test').count()
		assert tmp == 0
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('tag', id='test'), params=dict(_method='delete'))
		from columns.model import Tag, meta
		tmp = meta.Session.query(Tag).filter(Tag.id == u'test').count()
		assert tmp == 0
	
	def test_show(self):
		response = self.app.get(url('tag', id='test'))
		self.assertEqual(response.status_int,200)
	
	def test_edit(self):
		response = self.app.get(url('edit_tag', id='test'))
		self.assertEqual(response.status_int,200)
	
