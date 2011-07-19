from columns.lib import json
from columns.lib import rfc3339
from decimal import Decimal
import unittest
from StringIO import StringIO
import datetime

class TestJson(unittest.TestCase):
	def test_load(self):
		fp = StringIO('{"test": 1}')
		res = json.load(fp)
		self.assertEquals(res['test'],1)
	
	def test_loads(self):
		fp = '{"test": 1}'
		res = json.loads(fp)
		self.assertEquals(res['test'],1)
	
	def test_dump(self):
		fp = StringIO()
		obj = {"test": 1}
		json.dump(obj, fp)
		fp.seek(0)
		self.assertEquals(fp.read(),'{"test": 1}')
	
	def test_dumps(self):
		obj = {"test": 1}
		res = json.dumps(obj)
		self.assertEquals(res,'{"test": 1}')
	
	def test_dumps_datetime(self):
		dt = datetime.datetime.now()
		obj = {'test':dt}
		res = json.dumps(obj)
		self.assertEquals(res,'{"test": "%s"}'%dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
	
	def test_dumps_decimal(self):
		test = {'test':2.2000000000000002}
		res = json.dumps(test)
		self.assertEquals(res,'{"test": 2.2000000000000002}')
	
	def test_loads_datetime(self):
		dt = datetime.datetime.now()
		test = '{"test": ["%s"]}'%dt.strftime('%Y-%m-%dT%H:%M:%SZ')
		res = json.loads(test)
		self.assertEquals(res['test'][0],dt.replace(microsecond=0))
	
	def test_loads_decimal(self):
		test = '{"test": 2.2000000000000002}'
		res = json.loads(test)
		self.assertEquals(res['test'],Decimal('2.2000000000000002'))
	
	def test_equvalency(self):
		test = '{"test": 2.2000000000000002}'
		res1 = json.loads(test)
		fin1 = json.dumps(res1)
		self.assertEquals(test,fin1)
		
		dt = datetime.datetime.now().replace(microsecond=0)
		test = {'test':dt}
		res2 = json.dumps(test)
		fin2 = json.loads(res2)
		self.assertEquals(test['test'],fin2['test'])
	
