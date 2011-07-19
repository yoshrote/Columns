from columns.tests import *
from columns.lib import json
from columns.model import Article, meta
import datetime

dt = datetime.datetime.today()
'''	id				= Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	atom_id			= Column(AlwaysUnicode(length=255), nullable=True)
	title			= Column(AlwaysUnicode(length=255), nullable=False)
	published		= Column(DateTime(), nullable=True, index=True)
	updated			= Column(DateTime(), nullable=False, index=True)
	created			= Column(DateTime(), nullable=False, index=True)
	content			= Column(AlwaysUnicodeText(), nullable=False)
	summary			= Column(AlwaysUnicodeText(), nullable=True)
	links			= Column(JSONUnicode(), nullable=False)
	metatags		= Column(JSONUnicode(), nullable=False)
	author_id		= Column(Integer(), ForeignKey('user.id'), nullable=True)
	author			= Column(JSONUnicode(), nullable=False)
	contributors	= Column(JSONUnicode(), nullable=False)
	metacontent		= Column(AlwaysUnicodeText(), nullable=False)
	sticky			= Column(Boolean(), nullable=False)
	can_comment		= Column(Boolean(), nullable=False)
	permalink		= Column(AlwaysUnicode(length=255), nullable=True)
	page_id			= Column(Integer(),ForeignKey('page.id', ondelete='SET NULL'), nullable=True, index=True)
'''

'''	title = validators.UnicodeString(max=255, strip=True, not_empty=True)
	page_id = validators.Int(if_empty=None)
	can_comment = validators.StringBool(if_missing=False)
	sticky = validators.StringBool(if_missing=False)
	published = DateTimeValidator(format=rfc3339.RFC3339_wo_Timezone, if_empty=None)
	content = HTMLValidator()
	tags = StringListValidator()
'''
class TestArticlesController(TestController):
	def setUp(self):
		from columns.model import Page, User, Article
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
			published=None,#dt,
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
	
	def tearDown(self):
		from columns.model import Article, Page, User, meta
		meta.Session.query(Article).delete()
		meta.Session.query(User).delete()
		meta.Session.query(Page).delete()
		meta.Session.close()
	
	def test_index(self):
		response = self.app.get(url('articles'),extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_index_bad_p(self):
		response = self.app.get(url('articles',p='hs'),extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_index_bad_format(self):
		response = self.app.get(url('formatted_articles',format='json'),extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_index_drafts(self):
		response = self.app.get(url('articles'),extra_environ=self.extra_environ, params={'drafts':1})
		self.assertEqual(response.status_int,200)
	
	def test_create(self):
		response = self.app.post(url('articles'),extra_environ=self.extra_environ, params=dict(
			page_id=1,
			title=u'testsadfsg',
			content=u'',
			sticky=True,
			published=dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
			can_comment=True,
			tags=u'tag1,tag2',
		))
	
	def test_create_json(self):
		response = self.app.post(url('formatted_articles', format='json'), content_type='application/json',extra_environ=self.extra_environ, body=json.dumps(dict(
			page_id=1,
			title=u'testsadfsg',
			content=u'',
			sticky=True,
			published=dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
			can_comment=True,
			tags=u'tag1,tag2',
		)))
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_articles', format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_new(self):
		response = self.app.get(url('new_article'),extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_new_bad_format(self):
		response = self.app.get(url('formatted_new_article',format='json'),extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update(self):
		response = self.app.put(url('article', id=1),extra_environ=self.extra_environ,params=dict(
			page_id=1,
			title=u'test',
			content=u'',
			sticky=True,
			published=dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
			can_comment=True,
			tags=u'tag4,tag2',
		))
	
	def test_update_json(self):
		response = self.app.put(url('formatted_article', format='json', id=1), content_type='application/json',extra_environ=self.extra_environ, body=json.dumps(dict(
			page_id=1,
			title=u'test',
			content=u'',
			sticky=True,
			published=dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
			can_comment=True,
			tags=u'tag4,tag2',
		)))
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_article', format='atom', id=1), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('article', id=1),extra_environ=self.extra_environ, params=dict(
			_method='put',
			page_id=1,
			title=u'test',
			content=u'',
			sticky=True,
			published=dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
			can_comment=True,
			tags=u"tag3,tag6",
		))
	
	def test_update_nonexistent(self):
		response = self.app.put(url('article', id=10), extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_delete(self):
		response = self.app.delete(url('article', id=1),extra_environ=self.extra_environ)
		from columns.model import Article
		tmp = Article.get_from_id(1)
		assert tmp == None
	
	def test_delete_json(self):
		response = self.app.delete(url('formatted_article', id=1, format='json'),extra_environ=self.extra_environ)
		from columns.model import Article
		tmp = Article.get_from_id(1)
		assert tmp == None
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('article', id=1),extra_environ=self.extra_environ, params=dict(_method='delete'))
		from columns.model import Article
		tmp = Article.get_from_id(1)
		assert tmp == None
	
	def test_delete_nonexistent(self):
		response = self.app.delete(url('article', id=10), extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_show(self):
		response = self.app.get(url('article', id=1),extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_show_nonexistent(self):
		response = self.app.get(url('article', id=10),extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_edit(self):
		response = self.app.get(url('edit_article', id=1),extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_edit_bad_format(self):
		response = self.app.get(url('formatted_edit_article', id=1, format='json'),extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_edit_nonexistent(self):
		response = self.app.get(url('edit_article', id=10),extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,404)
	
