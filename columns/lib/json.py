import simplejson as refjson
from simplejson import JSONEncoder
from columns.lib import rfc3339
from decimal import Decimal
import datetime

__all__ = ['loads','dumps','load','dump']

class SuperJSONEncoder(refjson.encoder.JSONEncoder):
	def default(self, obj):
		return rfc3339.as_string(obj) if isinstance(obj, datetime.datetime) else refjson.JSONEncoder.default(self, obj)
	

def datetime_decoder(d):
	if isinstance(d, list):
		pairs = enumerate(d)
	elif isinstance(d, dict):
		pairs = d.items()
	result = []
	for k,v in pairs:
		if isinstance(v, basestring):
			try:
				v = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
			except ValueError:
				pass
		elif isinstance(v, (dict, list)):
			v = datetime_decoder(v)
		result.append((k, v))
	if isinstance(d, list):
		return [x[1] for x in result]
	elif isinstance(d, dict):
		return dict(result)


def loads(obj, **kw):
	kw['parse_float'] = Decimal
	kw['object_hook'] = datetime_decoder
	return refjson.loads(obj, **kw)

def dumps(obj, **kw):
	kw['cls'] = SuperJSONEncoder
	kw['use_decimal'] = True
	return refjson.dumps(obj, **kw)

def load(fp, **kw):
	kw['parse_float'] = Decimal
	kw['object_hook'] = datetime_decoder
	return refjson.load(fp, **kw)

def dump(obj, fp, **kw):
	kw['cls'] = SuperJSONEncoder
	kw['use_decimal'] = True
	return refjson.dump(obj, fp, **kw)

