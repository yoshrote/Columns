from __future__ import with_statement
from BeautifulSoup import BeautifulSoup
from xml.etree import ElementTree
from columns.model import meta, Tag, Page, User, Article, Comment, Upload, init_model
from columns.lib.atom import slugify
from sqlalchemy import create_engine, or_, orm
from ConfigParser import ConfigParser
from paste.script.command import Command
import re, datetime, os, traceback, urllib2, uuid

WORDPRESS_DT_FORMAT = "%Y-%m-%d %H:%M:%S"

def main(config, wp_file, static_path, base_wp_url, base_col_url):
	from columns.lib.app_globals import Globals	
	db_url =  config.get("app:main","sqlalchemy.url")
	engine = create_engine(db_url)
	init_model(engine)
	errors = []
	with open(wp_file) as f:
		xmlstr = f.read()
	dom = ElementTree.fromstring(xmlstr)
	
	
	#import tags
	for x in dom.findall('channel/{http://wordpress.org/export/1.0/}tag'):
		tk = x.findtext('{http://wordpress.org/export/1.0/}tag_slug')
		tv = x.findtext('{http://wordpress.org/export/1.0/}tag_name')
		try:
			meta.Session.merge(Tag(id=unicode(tk), name=unicode(tv)))
		except:
			pass
	meta.Session.flush()
	
	#import users
	authors = set([])
	for x in dom.findall('channel/item/{http://purl.org/dc/elements/1.1/}creator'):
		authors.add(x.text.lower())
	for x in authors:
		if meta.Session.query(User).filter(User.name==unicode(x)).count() == 0:
			meta.Session.add(User(name=unicode(x), type=3))
	meta.Session.flush()
	author_to_id = dict(meta.Session.query(User.name,User.id).all())
	
	#create 'main' page if it doesn't exist
	try:
		main_page = meta.Session.query(Page).filter(Page.slug==u'main').one()
	except orm.exc.NoResultFound:
		main_page = meta.Session.merge(
			Page(
				title = u'Main',
				slug = u'main',
				stream_comment_style = u'summary',
				story_comment_style = u'list',
				visible = True,
				can_post = True,
				tweet = True,
				content = None
			)
		)
		meta.Session.flush()
	
	#import pages
	for x in dom.findall('channel/item'):
		if x.findtext('{http://wordpress.org/export/1.0/}post_type') != 'page':
			continue
		title = unicode(x.findtext('title')).strip()
		slug = unicode(slugify(title))
		if slug == u'main':
			continue
		if meta.Session.query(Page).filter(Page.slug==slug).count() == 0:
			can_post = len(x.findall('{http://wordpress.org/export/1.0/}comment')) > 0
			soup = BeautifulSoup(x.findtext('{http://purl.org/rss/1.0/modules/content/}encoded'))
			t_page = meta.Session.merge(
				Page(
					title = title,
					slug = slug,
					stream_comment_style = u'summary',
					story_comment_style = u'list',
					visible = x.findtext('{http://wordpress.org/export/1.0/}status') == "publish",
					can_post = can_post,
					tweet = False,
					content = unicode(soup),
				)
			)	
		#add comments
		dummy_post = False
		t_post = None
		for comment in x.findall('{http://wordpress.org/export/1.0/}comment'):
			if dummy_post is False:
				t_post = Article(
					id=int(x.findtext('{http://wordpress.org/export/1.0/}post_id')),
					user_id=author_to_id.get(x.findtext('{http://purl.org/dc/elements/1.1/}creator').lower()),
					page_id=t_page.id,
					subject=unicode(t_page.title),
					date=datetime.datetime.strptime('2009-11-27 17:35:23',WORDPRESS_DT_FORMAT),
					published=True,
					permalink=None,
					can_comment=True,
					content=None,
					sticky=False
				)
				dummy_post = True
			author_name = comment.findtext('{http://wordpress.org/export/1.0/}comment_author')
			author_email = comment.findtext('{http://wordpress.org/export/1.0/}comment_author_email')
			author_url = comment.findtext('{http://wordpress.org/export/1.0/}comment_author_url')
			if author_name is None and author_email is None and author_url is None:
				continue
			try:
				userid = author_to_id.get(author_name.lower(), None)
				if userid is not None:
					user_t = meta.Session.get(userid)
					author_name = user_t.name
					author_url = user_t.profile
			except:
				pass
			soup = BeautifulSoup(comment.findtext('{http://wordpress.org/export/1.0/}comment_content'))
			try:
				t_post.comments.append(
					Comment(
						author_name = unicode(author_name) if author_name is not None else None,
						author_email = unicode(author_email) if author_email is not None else None,
						author_url = unicode(author_url) if author_url is not None else None,
						parent_comment = None,
						subject = u'',
						date = datetime.datetime.strptime(comment.findtext('{http://wordpress.org/export/1.0/}comment_date'),WORDPRESS_DT_FORMAT),
						content = unicode(soup),
					)
				)
			except:
				pass
		if t_post is not None:
			t_page.posts.append(t_post)
	meta.Session.flush()
	
	static_file_path = os.path.join(static_path,'uploaded')
	
	#import uploads
	upload_old_to_new = {}
	for x in dom.findall('channel/item'):
		if x.findtext('{http://wordpress.org/export/1.0/}post_type') != 'attachment':
			continue
		src = x.findtext('{http://wordpress.org/export/1.0/}attachment_url')
		re_match = re.match(r'^(?P<basepath>.*\/uploads)\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<file>.*)$',src)
		
		item = Upload()
		item.alt_text = unicode(x.findtext('{http://wordpress.org/export/1.0/}post_name'))
		item.description = None
		item.date = datetime.datetime(year=int(re_match.group('year')),month=int(re_match.group('month')),day=1)
		
		item.filepath = unicode(src.replace(re_match.group('basepath'),static_file_path))
		meta.Session.add(item)
	meta.Session.flush()
	
	caption_regex = re.compile(ur'\[caption .*? caption=\"(.*?)\"\](.*)\[\/caption\]')
	replace_str = ur'<div class=\"img-block\">\2<span class=\"img-caption\">\1</span></div>'
	#import posts
	for x in dom.findall('channel/item'):
		if x.findtext('{http://wordpress.org/export/1.0/}post_type') != 'post':
			continue
		user_fk = author_to_id.get(x.findtext('{http://purl.org/dc/elements/1.1/}creator').lower())
		page_fk = main_page.id
		post_pk = int(x.findtext('{http://wordpress.org/export/1.0/}post_id'))
		subject = x.findtext('title')
		published = x.findtext('{http://wordpress.org/export/1.0/}status') != "draft"
		date = None if not published else datetime.datetime.strptime(x.findtext('{http://wordpress.org/export/1.0/}post_date'),WORDPRESS_DT_FORMAT)
		permalink = None if not published else unicode(slugify('-'.join([date.date().strftime("%Y-%m-%d"),subject])))
		can_comment = True
		content = x.findtext('{http://purl.org/rss/1.0/modules/content/}encoded')
		content = content.replace(u'%s/wp-content/uploads/'%base_wp_url,u'%s/uploaded/'%base_col_url)
		soup = BeautifulSoup(content)
		soup = caption_regex.sub(replace_str ,unicode(soup))
		t_post = Article(
			id=post_pk,
			user_id=user_id,
			page_id=page_id,
			subject=unicode(subject),
			date=date,
			published=published,
			permalink=permalink,
			can_comment=can_comment,
			content=soup,
			sticky=False
		)
		for tag in x.findall('category'):
			if tag.attrib.get('domain','') == 'tag' and tag.attrib.get('nicename',None) is not None:
				t_post.tags.append(meta.Session.query(Tag).get(unicode(tag.attrib['nicename'])))
		#add comments
		for comment in x.findall('{http://wordpress.org/export/1.0/}comment'):
			author_name = comment.findtext('{http://wordpress.org/export/1.0/}comment_author')
			author_email = comment.findtext('{http://wordpress.org/export/1.0/}comment_author_email')
			author_url = comment.findtext('{http://wordpress.org/export/1.0/}comment_author_url')
			if author_name is None and author_email is None and author_url is None:
				continue
			try:
				userid = author_to_id.get(author_name.lower(), None)
				if userid is not None:
					user_t = meta.Session.get(userid)
					author_name = user_t.name
					author_url = user_t.profile
			except:
				pass
			soup = BeautifulSoup(comment.findtext('{http://wordpress.org/export/1.0/}comment_content'))
			t_post.comments.append(
				Comment(
					author_name = unicode(author_name) if author_name is not None else None,
					author_email = unicode(author_email) if author_email is not None else None,
					author_url = unicode(author_url) if author_url is not None else None,
					parent_comment = None,
					subject = u'',
					date = datetime.datetime.strptime(comment.findtext('{http://wordpress.org/export/1.0/}comment_date'),WORDPRESS_DT_FORMAT),
					content = unicode(soup),
				)
			)
		meta.Session.add(t_post)
	meta.Session.flush()
	return '\n'.join(errors)


class WordpressImporter(Command):
	# Parser configuration
	summary = "Import data from Wordpress XML"
	group_name = "columns"
	parser = Command.standard_parser(verbose=False)
	
	parser.set_defaults(config=os.path.join(os.path.dirname(__file__),'..','..',"production.ini"), here=os.path.join(os.path.dirname(__file__),'..','..'))
	parser.add_option("--config", metavar="CONFIG", action="store", dest="config", help="application config file [default: %default]")
	parser.add_option("--file", metavar="WPFILE", action="store", dest="wpfile", help="Wordpress xml file to import")
	parser.add_option("--here", metavar="HERE", action="store", dest="here", help="this directory")
	parser.add_option("--wpurl", metavar="WPURL", action="store", dest="wpurl", help="base url for the Wordpress instance")
	parser.add_option("--colurl", metavar="COLURL", action="store", dest="colurl", help="base url for the Columns instance")
	
	def command(self):
		try:
			config = ConfigParser({'here':self.options.here})
			config.read(self.options.config)
			return main(config, self.options.wpfile, self.options.here, self.options.wpurl, self.options.colurl)
		except:
			return traceback.format_exc()
