import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.controllers.xmlrpc import XMLRPCController 
from xmlrpclib import Fault
from columns.model import Article, Comment, meta
from urllib2 import urlopen, HTTPError, URLError
from urlparse import urlsplit
from BeautifulSoup import BeautifulSoup
from columns.lib import html

log = logging.getLogger(__name__)

class PingbackController(XMLRPCController):
	def pingback_ping(self, sourceURI, targetURI):
		try:
			doc = urlopen(sourceURI)
		except (HTTPError, URLError):
			return Fault(16, "The source URI does not exist.")
		
		# does the source refer to the target?
		soup = BeautifulSoup(doc.read())
		mylink = soup.find('a', attrs={'href': targetURI})
		if not mylink:
			return Fault(17, "The source URI does not contain a link to the target URI, and so cannot be used as a source.")
			
		# grab the title of the pingback source
		title = soup.find('title')
		if title:
			title = html.striphtml(unicode(title))
		else:
			title = 'Unknown title'
			
		# extract the text around the incoming link
		content = unicode(mylink.findParent())
		i = content.index(unicode(mylink))
		content = html.striphtml(content)
		max_length = config.get('PINGBACK_RESPONSE_LENGTH', 200)
		if len(content) > max_length:
			start = i - max_length/2
			if start < 0:
				start = 0
			end = i + len(unicode(mylink)) + max_length/2
			if end > len(content):
				end = len(content)
			content = content[start:end]
			
		scheme, server, path, query, fragment = urlsplit(targetURI)
		
		# check if the target is valid target
		if request.headers['SERVER_NAME'] not in [server, server.split(':')[0]]:
			return Fault(33, "The specified target URI cannot be used as a target. It either doesn't exist, or it is not a pingback-enabled resource.")
			
		route = config['routes.map'].match(path)
		try:
			article = meta.Session.query(Article).filter(Article.permalink == path).one()
		except:
			article = None
		if route is None or article is None:
			return Fault(32, "The specified target URI does not exist.")
			
		# Check if view accept pingbacks
		if route['controller'] not in ['blog']:
			return Fault(33, "The specified target URI cannot be used as a target. It either doesn't exist, or it is not a pingback-enabled resource.")
			
		pingbacks = meta.Session.query(Comment).filter(Comment.article_id == article.id).filter(Comment.is_pingback == True).all()
		if any([x.author['uri'] == sourceURI for x in pingbacks]):
			return Fault(48, "The pingback has already been registered.")
		
		pb = Comment.from_dict({
			'title':title.encode('utf-8'),
			'content':content.encode('utf-8'),
			'parent':article.id,
		})
		pb.author = {'uri':sourceURI,'name':'','email':None}
		pb.save()
		return 'pingback from %s to %s saved' % (sourceURI, targetURI)
	
	pingback_ping.signature = [ ['string','string','string'] ]

'''
	1. Alice posts to her blog. The post she's made includes a link to a post on Bob's blog.
	2. Alice's blogging system contacts Bob's blogging system and says "look, Alice made a post which linked to one of your posts".
	3. Bob's blogging system then includes a link back to Alice's post on his original post.
	4. Reader's of Bob's article can follow this link to Alice's post to read her opinion.
	
	source URI
		The address of the entry on the site containing the link.
	pingback client
		The software that establishes the connection to inform the server about the link from the source to the target. Typically, the source will be the client.
	pingback-enabled resource
		A document, image or other resource that advertises a pingback server using a pingback HTTP header or a pingback link element.
	pingback server
		The software that accepts XML-RPC connections. Typically, the target URI will be associated with the server (e.g. on the same host).
	pingback user agent
		A single system, which is both a pingback client and a pingback server.
	target URI
		The target of the link on the source site. This SHOULD be a pingback-enabled page.
		
	Parameters
		sourceURI of type string
			The absolute URI of the post on the source page containing the link to the target site.
		targetURI of type string
			The absolute URI of the target of the link, as given on the source page.
	Return Value
		A string, as described below.
	Faults
		If an error condition occurs, then the appropriate fault code from the following list should be used. Clients can quickly determine the kind of error from bits 5-8. 0×001x fault codes are used for problems with the source URI, 0×002x codes are for problems with the target URI, and 0×003x codes are used when the URIs are fine but the pingback cannot be acknowledged for some other reaon.
		0
			A generic fault code. Servers MAY use this error code instead of any of the others if they do not have a way of determining the correct fault code.
		0×0010 (16)
			The source URI does not exist.
		0×0011 (17)
			The source URI does not contain a link to the target URI, and so cannot be used as a source.
		0×0020 (32)
			The specified target URI does not exist. This MUST only be used when the target definitely does not exist, rather than when the target may exist but is not recognised. See the next error.
		0×0021 (33)
			The specified target URI cannot be used as a target. It either doesn't exist, or it is not a pingback-enabled resource. For example, on a blog, typically only permalinks are pingback-enabled, and trying to pingback the home page, or a set of posts, will fail with this error.
		0×0030 (48)
			The pingback has already been registered.
		0×0031 (49)
			Access denied.
		0×0032 (50)
			The server could not communicate with an upstream server, or received an error from an upstream server, and therefore could not complete the request. This is similar to HTTP's 402 Bad Gateway error. This error SHOULD be used by pingback proxies when propagating errors.
		In addition, [FaultCodes] defines some standard fault codes that servers MAY use to report higher level errors.
		
	Servers MUST respond to this function call either with a single string or with a fault code.
	If the pingback request is successful, then the return value MUST be a single string, containing as much information as the server deems useful. This string is only expected to be used for debugging purposes.
	If the result is unsuccessful, then the server MUST respond with an RPC fault value. The fault code should be either one of the codes listed above, or the generic fault code zero if the server cannot determine the correct fault code.
	Clients MAY ignore the return value, whether the request was successful or not. It is RECOMMENDED that clients do not show the result of successful requests to the user.
	Upon receiving a request, servers MAY do what they like. However, the following steps are RECOMMENDED:
	
	The server MAY attempt to fetch the source URI to verify that the source does indeed link to the target.
	The server MAY check its own data to ensure that the target exists and is a valid entry.
	The server MAY check that the pingback has not already been registered.
	The server MAY record the pingback.
	The server MAY regenerate the site's pages (if the pages are static).
	
	Here is a more detailed look at what could happen between Alice and Bob during the example described in the introduction.
	
	1. Alice posts to her blog. The post she's made includes a link to a post on Bob's blog. The permalink to Alice's new post is http://alice.example.org/#p123, and the URL of the link to Bob's blog is http://bob.example.net/#foo.
	2. Alice's blogging system parses all the external links out of Alice's post, and finds http://bob.example.net/#foo.
	3. It then requests the first 5 kilobytes of the page referred to by the link.
	4. It looks for an X-Pingback header, but fails to find one.
	5. It scans this page fragment for the pingback link tag, which it finds:
		<link rel="pingback" href="http://bob.example.net/xmlrpcserver">
	If this tag had not been contained in the page, then Bob's blog would not support pingback, so Alice's software would have given up here (moving on to the next link found in step 2).
	6. Next, since the link was there, it executes the the following XML-RPC call to http://bob.example.net/xmlrpcserver:
		pingback.ping('http://alice.example.org/#p123', 'http://bob.example.net/#foo')
	7.Alice's blogging system repeats step 3 to 6 for each external link that was found in the post.
	
	
	There ends the work undertaken by Alice's system. The rest of the work is performed by Bob's blog.
	1. Bob's blog receives a ping from Alice's blog (the ping sent in step 6 above), naming http://alice.example.org/#p123 (the site linking to Bob) and http://bob.example.net/#foo (the page Alice linked to).
	2. Bob's blog confirms that http://bob.example.net/#foo is in fact a post on this blog.
	3. It then requests the content of http://alice.example.org/#p123 and checks the Content-Type of the entity returned to make sure it is text of some sort.
	4. It verifies that this content does indeed contain a link to http://bob.example.net/#foo (to prevent spamming of pingbacks).
	5. Bob's blog also retrieves other data required from the content of Alice's new post, such as the page title, an extract of the page content surrounding the link to Bob's post, any attributes indicating which language the page is in, and so forth.
	6. Finally, Bob's post records the pingback in its database, and regenerates the static pages referring to Bob's post so that they mention the pingback.
'''
