from columns.tests import *
from columns.lib import json
class TestAnalyticsController(TestController):
	def setUp(self):
		from columns.model import access_log_t
		from columns.model import meta
		from datetime import datetime
		meta.Session.execute(access_log_t.insert(),{'stamp':datetime.fromtimestamp(14),'remote_ip':'127.0.0.1','path_info':'/test','request_method':'GET','referer_uri':None})
	
	def tearDown(self):
		from columns.model import access_log_t
		from columns.model import meta
		meta.Session.execute(access_log_t.delete())
	
	def test_index(self):
		response = self.app.get(url(controller='analytics', action='index'))
		self.assertEqual(response.status_int,200)
	
	def test_views_by_article(self):
		response = self.app.post(url(controller='analytics', action='views_by_article'), content_type='application/json', body=json.dumps({}))
		self.assertEqual(response.status_int,200)
	
	def test_uniques_by_article(self):
		response = self.app.post(url(controller='analytics', action='uniques_by_article'), content_type='application/json', body=json.dumps({}))
		self.assertEqual(response.status_int,200)
	
	def test_referers(self):
		response = self.app.post(url(controller='analytics', action='referers'), content_type='application/json', body=json.dumps({}))
		self.assertEqual(response.status_int,200)
	
	def test_views_by_article_bad_json(self):
		response = self.app.post(url(controller='analytics', action='views_by_article'), content_type='application/json', body="asd'd.dsa", expect_errors=True)
		self.assertEqual(response.status_int,400)
	
	def test_uniques_by_article_bad_json(self):
		response = self.app.post(url(controller='analytics', action='uniques_by_article'), content_type='application/json', body="asd'd.dsa", expect_errors=True)
		self.assertEqual(response.status_int,400)
	
	def test_referers_bad_json(self):
		response = self.app.post(url(controller='analytics', action='referers'), content_type='application/json', body="asd'd.dsa", expect_errors=True)
		self.assertEqual(response.status_int,400)
	

