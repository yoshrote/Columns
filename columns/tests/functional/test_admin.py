from columns.tests import *
import datetime
dt = datetime.datetime.now()

class TestAdminController(TestController):
	def setUp(self):
		from columns.model import Page, User, Article, Upload
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
		tmp = Upload(**dict(
			id=1,
			title=u'test',
			content=u'',
			filepath=u'',
			updated=datetime.datetime.utcnow(),
			published=datetime.datetime.utcnow(),
			author={'name':u'test_user'}
		))
		tmp.save()
	
	def tearDown(self):
		from columns.model import Page, User, Article, Upload, meta
		meta.Session.query(Upload).delete()
		meta.Session.query(Article).delete()
		meta.Session.query(User).delete()
		meta.Session.query(Page).delete()
		meta.Session.close()
	
	def test_index(self):
		response = self.app.get(url(controller='admin', action='index'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_index_ajax(self):
		response = self.app.get(url(controller='admin', action='index', format='ajax'), extra_environ=self.extra_environ, expect_errors=True)
		self.assertEqual(response.status_int,404)
	
	def test_browse(self):
		response = self.app.get(url(controller='admin', action='browse', CKEditorFuncNum=12), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_browse_ajax(self):
		response = self.app.get(url(controller='admin', action='browse_ajax', offset=0, limit=10), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_tag_cloud(self):
		response = self.app.get(url(controller='admin', action='tag_cloud'), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_quick_upload(self):
		response = self.app.post(url(controller='admin', action='quick_upload'), extra_environ=self.extra_environ, params=dict(
			content=u'aybabtu',
		), upload_files=[('upload','test.txt','dummy crap')])
		from columns.model import Upload, meta
		tmp = meta.Session.query(Upload).filter(Upload.title == u'test.txt').one()
		assert tmp.title == u'test.txt'
		assert tmp.content == u'aybabtu'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 1
	
	def test_mark_reviewed(self):
		response = self.app.post(url(controller='admin', action='mark_reviewed'), extra_environ=self.extra_environ, params=dict(
			article_id=1
		))
		from columns.model import Article
		tmp = Article.get_from_id(1)
		assert tmp.reviewed_by == 1
	
