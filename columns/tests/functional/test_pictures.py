from columns.tests import *
from columns.lib import json
import datetime

class TestPicturesController(TestController):
	def setUp(self):
		from columns.model import Upload, User
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
		tmp = Upload(**dict(
			id=1,
			title=u'test',
			content=u'',
			filepath=u'',
			updated=datetime.datetime.utcnow(),
			published=datetime.datetime.utcnow(),
			author={'name':u'test_user'}
		))
		try:
			tmp.save()
		except Exception, ex:
			print ex
	
	def tearDown(self):
		from columns.model import Upload, User, Tag, meta
		meta.Session.query(Tag).delete()
		meta.Session.query(Upload).delete()
		meta.Session.query(User).delete()
		meta.Session.close()
		#try:
		#	tmp = Upload.get_from_id(1)
		#	tmp.delete()
		#except:
		#	pass
	
	def test_index(self):
		response = self.app.get(url('pictures'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_create(self):
		response = self.app.post(url('pictures'), extra_environ=self.extra_environ, params=dict(
			title=u'haha',
			content=u'aybabtu',
			tags=u'tag1,tag2',
		), upload_files=[('upload','test.txt','dummy crap')])
		from columns.model import Upload, meta
		tmp = meta.Session.query(Upload).filter(Upload.title == u'haha').one()
		assert tmp.title == u'haha'
		assert tmp.content == u'aybabtu'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 1
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_pictures', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	#def test_create_json(self):
	#	response = self.app.post(url('formatted_pictures', format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
	#		title=u'haha',
	#		content=u'aybabtu',
	#	)), upload_files=[('upload','test.txt','dummy crap')])
	#	from columns.model import Upload
	#	tmp = Upload.fetch_one({'title':u'haha'})
	#	assert tmp.title == u'haha'
	#	assert tmp.content == u'aybabtu'
	#	assert tmp.author['name'] == u'test_user'
	#	assert tmp.author['uri'] == u'http://www.example.com'
	#	assert tmp.author_id == 1
	
	def test_new(self):
		response = self.app.get(url('new_picture'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		response = self.app.put(url('picture', id=1), extra_environ=self.extra_environ, params=dict(
			title=u'blah',
			content=u'blah',
			tags=u'tag1,tag2',
		))
		from columns.model import Upload
		tmp = Upload.get_from_id(1)
		assert tmp.title == u'blah'
		assert tmp.content == u'blah'
	
	def test_update_json(self):
		response = self.app.put(url('formatted_picture', id=1, format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			title=u'blah',
			content=u'blah',
		)))
		from columns.model import Upload
		tmp = Upload.get_from_id(1)
		assert tmp.title == u'blah'
		assert tmp.content == u'blah'
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_picture', id=1, format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('picture', id=1), extra_environ=self.extra_environ, params=dict(
			_method='put',
			title=u'blah2',
			content=u'b2lah',
		))
		from columns.model import Upload
		tmp = Upload.get_from_id(1)
		assert tmp.title == u'blah2'
		assert tmp.content == u'b2lah'
	
	def test_delete(self):
		response = self.app.delete(url('picture', id=1), extra_environ=self.extra_environ)
		from columns.model import Upload
		tmp = Upload.get_from_id(1)
		assert tmp == None
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('picture', id=1), extra_environ=self.extra_environ, params=dict(_method='delete'))
		from columns.model import Upload
		tmp = Upload.get_from_id(1)
		assert tmp == None
	
	def test_show(self):
		response = self.app.get(url('picture', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_edit(self):
		response = self.app.get(url('edit_picture', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
