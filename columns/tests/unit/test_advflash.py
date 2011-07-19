import unittest
from columns.lib.advflash import Message, AdvFlash
from columns.tests import TestController
from pylons import session
from beaker.session import Session

class TestMessage(unittest.TestCase):
	def test_message(self):
		msg = Message('testing')
		self.assertEquals(repr(msg),'testing')
		self.assertEquals(str(msg),'testing')
		self.assertEquals(unicode(msg),u'testing')
	

class TestAdvFlash(TestController):
	def __init__(self, *args, **kwargs):
		session._push_object(Session({}))
		TestController.__init__(self, *args, **kwargs)
		
	def test_advflash(self):
		flash = AdvFlash()
		flash('test')
		flash.info('test2')
		res = flash.pop_messages()
		self.assert_(str(res[0]) in ['test','test2'])
		self.assert_(str(res[1]) in ['test','test2'])
	
