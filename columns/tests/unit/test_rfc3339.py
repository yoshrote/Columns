import datetime
from columns.lib import rfc3339
import unittest

class TestRFC3339(unittest.TestCase):
	def test_now(self):
		res = rfc3339.now()
		self.assertEquals(res.tzinfo,rfc3339.UTC)
	
	def test_UTCDateTime(self):
		res = datetime.datetime.now()
		res2 = rfc3339.UTC.localize(res)
		x1 = rfc3339.UTFDateTime(res)
		x2 = rfc3339.UTFDateTime(res2)
		self.assertEquals(res2,x1)
		self.assertEquals(res2,x2)
	
	def test_as_string(self):
		res = datetime.datetime.now()
		dt_w_tz = rfc3339.UTFDateTime(res)
		self.assertEquals(rfc3339.as_string(None),None)
		self.assertEquals(rfc3339.as_string(res),res.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEquals(rfc3339.as_string(res),res.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEquals(rfc3339.as_string(dt_w_tz),dt_w_tz.strftime('%Y-%m-%dT%H:%M:%S%z'))
	
	def test_from_string(self):
		test = rfc3339.UTFDateTime(datetime.datetime.now()).replace(microsecond=0)
		t1 = test.strftime('%Y-%m-%dT%H:%M:%SZ')
		self.assertEquals(test,rfc3339.from_string(t1))
	
	def test_localized(self):
		res = datetime.datetime.utcnow()
		local_dt = rfc3339.localized(res)
		self.assertEquals(local_dt.tzinfo,rfc3339.LOCAL)
		testing_dt = local_dt - local_dt.tzinfo.utcoffset(local_dt)
		self.assertEquals(testing_dt.replace(tzinfo=None),res.replace(tzinfo=None))
	

