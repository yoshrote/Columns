import unittest
from columns.model.form import DateTimeValidator, UniqueUserName, StringListValidator, HTMLValidator, Invalid
import datetime, pytz
from columns.lib import rfc3339



class TestDateTimeValidator(unittest.TestCase):
	def test_from_python(self):
		v = DateTimeValidator(format=rfc3339.RFC3339_wo_Timezone)
		dt = datetime.datetime.now()
		self.assertEquals(v.from_python(dt,None),dt.strftime(rfc3339.RFC3339_wo_Timezone))
	
	def test_to_python(self):
		v = DateTimeValidator(format=rfc3339.RFC3339_wo_Timezone)
		dt = datetime.datetime.now()
		v.to_python(dt.strftime(rfc3339.RFC3339_wo_Timezone),None)
		self.assertRaises(Invalid,v.to_python,'iuytrewq',None)
	

class TestStringListValidator(unittest.TestCase):
	def test_from_python(self):
		v = StringListValidator()
		self.assertEquals(v.from_python(['1','2','3'],None),"1, 2, 3")
	
	def test_to_python(self):
		v = StringListValidator()
		self.assertEquals(v.to_python("1, 2, 3, ",None),['1','2','3'])
		self.assertRaises(Invalid,v.to_python,None,None)
	

class TestUniqueUserName(unittest.TestCase):
	def setUp(self):
		from columns.model import User
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
	
	def tearDown(self):
		from columns.model import User, meta
		meta.Session.query(User).delete()
		meta.Session.close()
	
	def test_to_python(self):
		v = UniqueUserName()
		self.assertEquals(v.to_python('test_user2',None),'test_user2')
		self.assertRaises(Invalid,v.to_python,'test_user',None)
	

class TestHTMLValidator(unittest.TestCase):
	def test_to_python(self):
		v = HTMLValidator()
		self.assertEquals(v.to_python('<p>test_user2</p>',None),'<p>test_user2</p>')
		self.assertEquals(v.to_python('<a>test_user2',None),'<a>test_user2</a>')
	
