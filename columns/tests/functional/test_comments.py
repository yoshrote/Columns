from columns.tests import *
from columns.lib import json
import datetime
dt = datetime.datetime.now()

class TestCommentsController(TestController):
	def setUp(self):
		from columns.model import Page, User, Article, Comment
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
		u2tmp = User.from_dict(dict(
			id=2,
			name=None,
			open_id=None,
			fb_id=None,
			twitter_id=None,
			type=1,
			profile=None,
		))
		u2tmp.save()
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
	
	def test_index(self):
		response = self.app.get(url('comments', parent_id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_create(self):
		response = self.app.post(url('comments', parent_id=1), extra_environ=self.extra_environ, params=dict(
			title=u'bwahahaha',
			content = u'lol',
		))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'bwahahaha').one()
		assert tmp.content == u'lol'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 1
		assert tmp.article_id == 1
	
	def test_create_json(self):
		response = self.app.post(url('formatted_comments', parent_id=1, format='json'), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			title=u'bwahahaha',
			content = u'lol',
		)))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'bwahahaha').one()
		assert tmp.content == u'lol'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 1
		assert tmp.article_id == 1
	
	def test_create_atom(self):
		response = self.app.post(url('formatted_comments', parent_id=1, format='atom'), content_type='application/xml', extra_environ=self.extra_environ, body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_create_blank_user(self):
		extra_environ = {'test.session':{
			'user_id':2,
			'user_name':None,
			'user_type':9,
			'user_profile':u'http://www.example.com',
			'user_openid':u'http://tester.example.com',
			'user_fbid':None,
			'user_twitterid':None,
			'auth_type':u'open_id',
			'oid':u'http://tester.example.com'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('comments', parent_id=1), extra_environ=extra_environ, params=dict(
			title=u'bwahahaha',
			content = u'lol',
			name=u'test_user',
		))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'bwahahaha').one()
		assert tmp.content == u'lol'
		assert tmp.author['name'] == None
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 2
		assert tmp.article_id == 1
	
	def test_create_blank_user_unique(self):
		extra_environ = {'test.session':{
			'user_id':2,
			'user_name':None,
			'user_type':9,
			'user_profile':u'http://www.example.com',
			'user_openid':u'http://tester.example.com',
			'user_fbid':None,
			'user_twitterid':None,
			'auth_type':u'open_id',
			'oid':u'http://tester.example.com'
		},'columns.authorize.disabled':True}
		response = self.app.post(url('comments', parent_id=1), extra_environ=extra_environ, params=dict(
			title=u'bwahahaha',
			content = u'lol',
			name=u'test_use2r',
		))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'bwahahaha').one()
		assert tmp.content == u'lol'
		assert tmp.author['name'] == u'test_use2r'
		assert tmp.author['uri'] == u'http://www.example.com'
		assert tmp.author_id == 2
		assert tmp.article_id == 1
	
	def test_new(self):
		response = self.app.get(url('new_comment', parent_id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_update(self):
		response = self.app.put(url('comment', parent_id=1, id=1), extra_environ=self.extra_environ, params=dict(
			title=u'testcomment',
			content = u'this is a comment. lol',
		))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'testcomment').one()
		assert tmp.content == u'this is a comment. lol'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author_id == 1
		assert tmp.article_id == 1
	
	def test_update_json(self):
		response = self.app.put(url('formatted_comment', format='json', parent_id=1, id=1), extra_environ=self.extra_environ, content_type='application/json', body=json.dumps(dict(
			title=u'testcomment',
			content = u'this is a comment. lol',
		)))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'testcomment').one()
		assert tmp.content == u'this is a comment. lol'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author_id == 1
		assert tmp.article_id == 1
	
	def test_update_atom(self):
		response = self.app.put(url('formatted_comment', format='atom', parent_id=1, id=1), extra_environ=self.extra_environ, content_type='application/json', body="", expect_errors=True)
		self.assertEqual(response.status_int,415)
	
	def test_update_browser_fakeout(self):
		response = self.app.post(url('comment', parent_id=1, id=1), extra_environ=self.extra_environ, params=dict(
			_method='put',
			title=u'testcomment',
			content = u'this is a comment. lol',
		))
		from columns.model import Comment, meta
		tmp = meta.Session.query(Comment).filter(Comment.title == u'testcomment').one()
		assert tmp.content == u'this is a comment. lol'
		assert tmp.author['name'] == u'test_user'
		assert tmp.author_id == 1
		assert tmp.article_id == 1
	
	def test_delete(self):
		response = self.app.delete(url('comment', parent_id=1, id=1), extra_environ=self.extra_environ)
		from columns.model import Comment
		tmp = Comment.get_from_id(1)
		assert tmp is None
	
	def test_delete_browser_fakeout(self):
		response = self.app.post(url('comment', parent_id=1, id=1), extra_environ=self.extra_environ, params=dict(_method='delete'))
		from columns.model import Comment
		tmp = Comment.get_from_id(1)
		assert tmp is None
	
	def test_show(self):
		response = self.app.get(url('comment', parent_id=1, id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
	def test_edit(self):
		response = self.app.get(url('edit_comment', parent_id=1, id=1), extra_environ=self.extra_environ)
		self.assertEqual(response.status_int,200)
	
