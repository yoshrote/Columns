from lxml import etree
import re
__all__ = ['from_request', 'NSMAP', 'ns', 'slugify','get_tag_uri']

NSMAP = {
	None : "http://www.w3.org/2005/Atom",
	'atom' : "http://www.w3.org/2005/Atom",
	'dc' : "http://purl.org/dc/elements/1.1/",
	'dcterms' : "http://purl.org/dc/terms/",
	'thr' : "http://purl.org/syndication/thread/1.0",
}

re_slug = re.compile(r'[^a-z0-9\-]')
def slugify(string):
	tmp = string.lower().replace(' ','-')
	return unicode(re_slug.sub(u'',tmp))

def get_tag_uri(url, dt, name):
	"""Creates a TagURI. See http://diveintomark.org/archives/2004/05/28/howto-atom-id
	The middle fragment includes the time and final fragment is the author name
	"""
	tag = re.sub(r'^.*://', '', url)
	return ':'.join([
		'tag',
		','.join([tag.partition('/')[0],dt.strftime('%Y-%m-%d')]),
		name,
	])

def ns(tag,namespace='atom',nsmap=NSMAP):
	if namespace is None:
		return tag
	else:
		return ''.join(['{',nsmap[namespace],'}',tag])

def from_request(request):
	return etree.fromstring(request.body)

