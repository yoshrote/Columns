from pylons.templating import render_jinja2, pylons_globals, cached_template
from jinja2 import Environment, PackageLoader, environmentfilter, Markup, escape
from webhelpers.html import literal

#def render_jinja2_block(template_name, block, extra_vars=None, cache_key=None, cache_type=None, cache_expire=None):
#	"""Render a template with Jinja2
#		
#	Accepts the cache options ``cache_key``, ``cache_type``, and
#	``cache_expire``.
#		
#	"""
#	# Create a render callable for the cache function
#	def render_template():
#		# Pull in extra vars if needed
#		globs = extra_vars or {}
#		
#		# Second, get the globals
#		globs.update(pylons_globals())
#		
#		# Grab a template reference
#		template = globs['app_globals'].jinja2_env.get_template(template_name)
#		render_func = template.blocks[block]
#		
#		return literal(template.render(**globs))
#	
#	return cached_template('^^^'.join([template_name,block]), render_template, cache_key=cache_key,
#						   cache_type=cache_type, cache_expire=cache_expire)


from columns.lib import rfc3339 
def rfc3339_formatted(value):
	try:
		return rfc3339.as_string(value)
	except AttributeError:
		return None

def localized_datetime_format(value, format='%Y-%m-%dT%H:%M:%S%z'):
	try:
		return rfc3339.localized(value).strftime(str(format))
	except AttributeError:
		return None

def upload_url(value):
	from pylons import config
	return '/'.join([config['static_web_path'],value.filepath])

def jsonify(value):
	from columns.lib import json
	return json.dumps(value)

from postmarkup import render_bbcode
from urllib import quote

from columns.lib.authorization import is_logged_in, is_allowed

def test_allowed(value):
	if isinstance(value,dict):
		return is_allowed(**value)
	else:
		return is_allowed(value)

def is_list(value):
	return isinstance(value, list)

def listify(value):
	if isinstance(value,list):
		return value
	elif isinstance(value,dict):
		return value.items()
	elif value is None:
		return []
	else:
		return [value]

def dictify(value):
	if isinstance(value,dict):
		return value
	elif value is None or isinstance(value,list) and len(value) == 0:
		return {}
	elif isinstance(value,list):
		if not isinstance(value[0],(tuple,list)):
			return dict(zip(value,value))
		else:
			return dict([(x[0],x[1]if len(x)>1 else x[0]) for x in value])
	else:
		return {value:value}
	

def formfield(value):
	if value is None:
		return ''
	else:
		return unicode(value)


def make_jinja_environment(config):
	env = Environment(
		loader=PackageLoader('columns', 'templates'),
		auto_reload=True,
	)
	env.filters['rfc3339'] = rfc3339_formatted
	env.filters['upload_url'] = upload_url
	env.filters['localized_datetime_format'] = localized_datetime_format
	env.filters['jsonify'] = jsonify
	env.filters['bbcode'] = render_bbcode
	env.filters['urlquote'] = quote
	env.filters['maximum'] = max
	env.filters['formfield'] = formfield
	env.tests['logged_in'] = is_logged_in
	env.tests['allowed'] = test_allowed
	env.tests['is_list'] = is_list
	return env

