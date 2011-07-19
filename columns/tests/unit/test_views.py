import unittest
import datetime
from columns.lib.views import rfc3339_formatted, jsonify, is_list, listify, dictify, localized_datetime_format, formfield

class TestViews(unittest.TestCase):
	def test_rfc3339_formatted(self):
		self.assertEquals(rfc3339_formatted(''),None)
	
	def test_jsonify(self):
		self.assertEquals(jsonify({'test':1}),'{"test": 1}')
	
	def test_is_list(self):
		self.assertEquals(is_list([]),True)
		self.assertEquals(is_list(1),False)
	
	def test_listify(self):
		self.assertEquals(listify([1]),[1])
		self.assertEquals(listify({'test':1}),[('test',1)])
		self.assertEquals(listify(None),[])
		self.assertEquals(listify(1),[1])
	
	def test_dictify(self):
		self.assertEquals(dictify({1:1}),{1:1})
		self.assertEquals(dictify(None),{})
		self.assertEquals(dictify([]),{})
		self.assertEquals(dictify([1]),{1:1})
		self.assertEquals(dictify([(1,2)]),{1:2})
		self.assertEquals(dictify(1),{1:1})
	
	def test_localized_datetime_format(self):
		self.assertEquals(localized_datetime_format(None),None)
	
	def test_formfield(self):
		self.assertEquals(formfield(None),'')
		self.assertEquals(formfield(1),u'1')
		self.assertEquals(formfield('hello'),u'hello')
	

