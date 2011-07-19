import unittest
from columns.lib.helpers import user_from_session, get_permissions, page_list, template_list, resource_counter

class TestHelpers(unittest.TestCase):
	def test_template_list(self):
		self.assertEquals(template_list(),[(u'/blog/blank',u'Blank'),(u'/blog/stream',u'Stream')])
	
	def test_user_from_session(self):
		self.assertEquals(user_from_session({'user_id':1,'user_name':'test','uri':None}),{'id':1,'name':'test','uri':None,'email':None})
	
	def test_get_permissions(self):
		from columns.config import authorization
		self.assertEquals(get_permissions(),authorization.PERMISSIONS)
	
	def test_resource_counter(self):
		self.assertEquals(resource_counter('articles'),0)
	
	def test_page_list(self):
		self.assertEquals(page_list(),[])
	

