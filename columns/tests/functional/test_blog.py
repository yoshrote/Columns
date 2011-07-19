from columns.tests import *
from datetime import datetime
dt = datetime.utcnow()

class TestBlogController(TestController):
	def setUp(self):
		from columns.model import Page, User, Article, Comment
		ptmp = Page.from_dict(dict(
			id=1,
			title=u'Main',slug=u'main',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=True,can_post=True,in_main=True,in_menu=False,
		))
		ptmp.save()
		p2tmp = Page.from_dict(dict(
			id=1,
			title=u'Test Page',slug=u'test-page',content=u'',template=u'/blog/stream',
			stream_comment_style=u'summary',story_comment_style=u'list',
			visible=True,can_post=True,in_main=True,in_menu=False,
		))
		p2tmp.save()
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
			links={},
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
		ctmp = Comment(**dict(
			id=1,
			updated=dt,
			atom_id=u'-'.join([dt.strftime("%Y-%m-%d"),u'test']),
			title=u'testcomment',
			content=u'this is a comment',
			published=dt,
			author_id=utmp.id,
			author={
				'name':u'test_user',
			},
			article_id=atmp.id,
		))
		ctmp.save()
	
	def tearDown(self):
		from columns.model import Article, Comment, Page, User, meta
		meta.Session.query(Comment).delete()
		meta.Session.query(Article).delete()
		meta.Session.query(User).delete()
		meta.Session.query(Page).delete()
		meta.Session.close()
	
	def test_generate_html(self):
		response = self.app.get(url(controller='blog', action='generate', format='html'))
		self.assertEqual(response.status_int,200)
	
	def test_generate_atom(self):
		response = self.app.get(url(controller='blog', action='generate', format='atom'))
		self.assertEqual(response.status_int,200)
	
	def test_generate_json(self):
		response = self.app.get(url(controller='blog', action='generate', format='json'), expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_hate_favicon(self):
		response = self.app.get(url(controller='blog', action='generate', page='favicon.ico'), expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_generate_page(self):
		response = self.app.get(url(controller='blog', action='generate', page='test-page'))
		self.assertEqual(response.status_int,200)
	
	def test_generate_tag(self):
		response = self.app.get(url(controller='blog', action='generate', filter_='tag', name='test'))
		self.assertEqual(response.status_int,200)
	
	def test_generate_user(self):
		response = self.app.get(url(controller='blog', action='generate', filter_='user', name='test_user'))
		self.assertEqual(response.status_int,200)
	
	def test_generate_bad_page(self):
		response = self.app.get(url(controller='blog', action='generate', page='qwertyuiop'), expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_story(self):
		response = self.app.get(url(controller='blog', action='story', permalink=u'-'.join([dt.strftime("%Y-%m-%d"),u'test'])))
		self.assertEqual(response.status_int,200)
	
	def test_bad_story(self):
		response = self.app.get(url(controller='blog', action='story', permalink='qwertyuiop'), expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_sitemap(self):
		response = self.app.get(url(controller='blog', action='sitemap'))
		self.assertEqual(response.status_int,200)
	
	def test_sitemap_xml(self):
		response = self.app.get(url(controller='blog', action='sitemap', format='xml'))
		self.assertEqual(response.status_int,200)
	
	def test_search(self):
		response = self.app.get(url(controller='blog', action='search', q='test'))
		self.assertEqual(response.status_int,200)
	
	def test_search_paged(self):
		response = self.app.get(url(controller='blog', action='search', q='test', pnum=2))
		self.assertEqual(response.status_int,200)
	
	def test_blank_search(self):
		response = self.app.get(url(controller='blog', action='search'))
		self.assertEqual(response.status_int,302)
	

