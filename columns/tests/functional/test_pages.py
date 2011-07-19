from columns.tests import *
from columns.lib import json

'''
	title = validators.UnicodeString(max=255, strip=True, not_empty=True)
	can_post = validators.StringBool(if_missing=False)
	content = HTMLValidator(if_empty=u'')
	template = validators.UnicodeString(if_empty=u'default')
	visible = validators.StringBool(if_missing=False)
	tweet = validators.StringBool(if_missing=False)
	in_main = validators.StringBool(if_missing=False)
	stream_comment_style = validators.UnicodeString(max=20, strip=True)
	story_comment_style = validators.UnicodeString(max=20, strip=True)
'''
class TestPagesController(TestController):
	def setUp(self):
		from columns.model import Page
		from sqlalchemy.exc import IntegrityError
		tmp = Page.from_dict(dict(
			id=1,
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=True,can_post=True,in_main=True,in_menu=False,
		))
		try:
			tmp.save()
		except IntegrityError:
			pass
	
	def tearDown(self):
		from columns.model import Page, meta
		meta.Session.query(Page).delete()
		meta.Session.close()
	
	def test_index(self):
		response = self.app.get(url('pages'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_create(self):
		response = self.app.post(url('pages'), extra_environ=self.extra_environ, params=dict(
			title=u'Test',content=u'',template=u'/blog/blank',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=False,can_post=True,in_main=True,#tweet=False,
		))
		from columns.model import Page, meta
		tmp = meta.Session.query(Page).filter(Page.slug == u'test').one()
		assert tmp.title == u'Test'
		assert tmp.content == u''
		assert tmp.template == u'/blog/blank'
		assert tmp.stream_comment_style == u'summary'
		assert tmp.story_comment_style == u'list'
		assert tmp.visible == False
		assert tmp.can_post == True
		assert tmp.in_main == True
		#assert tmp.tweet == False
		
	
	def test_create_json(self):
		response = self.app.post(url('formatted_pages', format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			title=u'Test',content=u'',template=u'/blog/blank',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=False,can_post=True,in_main=True,#tweet=False,
		)))
		from columns.model import Page, meta
		tmp = meta.Session.query(Page).filter(Page.slug == u'test').one()
		assert tmp.title == u'Test'
		assert tmp.content == u''
		assert tmp.template == u'/blog/blank'
		assert tmp.stream_comment_style == u'summary'
		assert tmp.story_comment_style == u'list'
		assert tmp.visible == False
		assert tmp.can_post == True
		assert tmp.in_main == True
		#assert tmp.tweet == False
		
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_pages', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_new(self):
		response = self.app.get(url('new_page'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		response = self.app.put(url('page', id=1), extra_environ=self.extra_environ, params=dict(
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=False,can_post=True,in_main=True,#tweet=False,
		))
		from columns.model import Page
		tmp = Page.get_from_id(1)
		assert tmp.title == u'Main'
		assert tmp.slug == u'main'
		assert tmp.content == u''
		assert tmp.template == u'/blog/stream'
		assert tmp.stream_comment_style == u'summary'
		assert tmp.story_comment_style == u'list'
		assert tmp.visible == False
		assert tmp.can_post == True
		assert tmp.in_main == True
		#assert tmp.tweet == False
	
	def test_update_json(self):
		response = self.app.put(url('formatted_page', format='json', id=1), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=False,can_post=True,in_main=True,#tweet=False,
		)))
		from columns.model import Page
		tmp = Page.get_from_id(1)
		assert tmp.title == u'Main'
		assert tmp.slug == u'main'
		assert tmp.content == u''
		assert tmp.template == u'/blog/stream'
		assert tmp.stream_comment_style == u'summary'
		assert tmp.story_comment_style == u'list'
		assert tmp.visible == False
		assert tmp.can_post == True
		assert tmp.in_main == True
		#assert tmp.tweet == False
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_page', id=1, format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('page', id=1), extra_environ=self.extra_environ, params=dict(
			_method='put',
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=True,can_post=True,in_main=False,#tweet=False,
		))
		from columns.model import Page
		tmp = Page.get_from_id(1)
		assert tmp.title == u'Main'
		assert tmp.slug == u'main'
		assert tmp.content == u''
		assert tmp.template == u'/blog/stream'
		assert tmp.stream_comment_style == u'summary'
		assert tmp.story_comment_style == u'list'
		assert tmp.visible == True
		assert tmp.can_post == True
		assert tmp.in_main == False
		#assert tmp.tweet == False
	
	def test_delete(self):
		from columns.model import Page
		tmp = Page.get_from_id(1)
		assert tmp != None
		response = self.app.delete(url('page', id=1), extra_environ=self.extra_environ)
		tmp = Page.get_from_id(1)
		assert tmp == None
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('page', id=1), extra_environ=self.extra_environ, params=dict(_method='delete'))
		from columns.model import Page
		tmp = Page.get_from_id(1)
		assert tmp == None
	
	def test_show(self):
		response = self.app.get(url('page', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_edit(self):
		response = self.app.get(url('edit_page', id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
