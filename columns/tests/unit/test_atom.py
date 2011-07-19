import unittest
from webob import Request
from columns.lib import atom
from lxml import etree, objectify
from datetime import datetime

class TestAtom(unittest.TestCase):
	def test_slugify(self):
		test = atom.slugify("Yes're this is it!1_")
		self.assertEquals(test,"yesre-this-is-it1")
	
	def test_get_tag_uri(self):
		dt = datetime(year=2012,month=1,day=1)
		test = atom.get_tag_uri("http://diveintomark.org/archives/2004/05/28/howto-atom-id",dt,'tester')
		self.assertEquals(test,"tag:diveintomark.org,2012-01-01:tester")
	
	def test_ns(self):
		self.assertEquals(atom.ns('link'),"{http://www.w3.org/2005/Atom}link")
		self.assertEquals(atom.ns('link',None),"link")
	
	def test_from_request(self):
		expect = etree.tostring(objectify.fromstring("<div>testing</div>"))
		req = Request.blank("/", body="<div>testing</div>")
		reqstr = etree.tostring(atom.from_request(req))
		result = etree.tostring(objectify.fromstring(reqstr))
		self.assertEquals(expect, result)
	
