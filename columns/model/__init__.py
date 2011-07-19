"""The application's model objects"""
import logging, datetime, re, operator, os, shutil, time, copy, os.path
from StringIO import StringIO
from lxml import etree
from sqlalchemy import orm, sql, types
from sqlalchemy.schema import Table, Column, ForeignKeyConstraint, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, Boolean, Integer, DateTime, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from columns.lib import json
from columns.lib import rfc3339
from columns.lib.atom import ns, NSMAP, get_tag_uri, slugify
from columns.lib import html
from columns.lib.exc import *
from columns.model import meta
from columns.model.form import *
#from columns.model.base import RESTModelFactory

# The declarative Base
class RESTModel(object):
	skip_dict = []
	def _delete(self, dont_flush=False):
		meta.Session.delete(self)
		if dont_flush is False:
			meta.Session.flush()
	
	def _save(self, dont_flush=False):
		if meta.Session.object_session(self) is None:
			meta.Session.add(self)
		
		if dont_flush is False:
			meta.Session.flush()
	
	
	@classmethod
	def get_from_id(cls, id):
		"""
		return the document which has the id
		"""
		query = meta.Session.query(cls) #._init_query()
		res = query.autoflush(False).get(id)
		return res
	
	def save(self, uuid=False, validate=None, safe=True, *args, **kwargs):
		"""
		save the document into the db.
		"""
		#if validate is True:
		#	self.validate()
		self._save(kwargs.get('dont_flush',False))
	
	def delete(self):
		"""
		delete the document from the collection from his _id.
		"""
		self._delete()
	
	
	def to_dict(self):
		from copy import copy
		return copy(self)
	
	
	def set_defaults(self):
		pass
	
	@classmethod
	def from_dict(cls, dt):
		raise NotImplementedError
	
	@classmethod
	def parse_xml(cls, xml_doc):
		raise NotImplementedError
	
	def update_from_dict(self, dt):
		raise NotImplementedError
	
	def add_author_or_contributor(self, person):
		if getattr(self,'author',None) is None:
			self.author_id = person['id']
			self.author = person
		elif self.author_id == person['id']:
			return
		elif hasattr(self,'contributors') and not any([x['id'] == person['id'] for x in getattr(self,'contributors',[])]):
			self.contributors.append(person)
	

Base = declarative_base(metadata=meta.metadata,cls=RESTModel)

def init_model(config, app_globals):
	"""Call me before using any of the tables or classes in the model"""
	from sqlalchemy import engine_from_config
	engine = engine_from_config(config, 'sqlalchemy.')
	sm = orm.sessionmaker(autoflush=True, autocommit=True, bind=engine)
	
	meta.engine = engine
	meta.Session = orm.scoped_session(sm)

def merge_tags(target_tag, combined_tag):
	"""All posts with ``self.id`` tag will instead have ``target`` tag.
	``subject`` tag will then be deleted.
	"""
	for post in target_tag.articles:
		post.tags.add(combined_tag)
	meta.Session.flush()
	meta.Session.execute(article_tag_t.delete(article_tag_t.c.tag_id==target_tag.id))
	meta.Session.delete(target_tag)
	meta.Session.flush()


class AlwaysUnicode(TypeDecorator):
	impl = Unicode
	
	def process_bind_param(self, value, dialect):
		return unicode(value) if value is not None else None
	
	def process_result_value(self, value, dialect):
		return unicode(value) if value is not None else None
	
	def copy(self):
		return AlwaysUnicode(self.impl.length)
	

class AlwaysUnicodeText(TypeDecorator):
	impl = UnicodeText
	
	def process_bind_param(self, value, dialect):
		return unicode(value) if value is not None else None
	
	def process_result_value(self, value, dialect):
		return unicode(value) if value is not None else None
	
	def copy(self):
		return AlwaysUnicodeText(self.impl.length)
	

class JSONUnicode(TypeDecorator):
	impl = UnicodeText
	
	def process_bind_param(self, value, dialect):
		return unicode(json.dumps(value)) if value is not None else None
	
	def process_result_value(self, value, dialect):
		return json.loads(value) if value is not None else None
	
	def copy_value(self, value):
		return copy.deepcopy(value)
	


article_tag_t = Table(
	'article_tag', Base.metadata,
	Column('article_id', Integer(), ForeignKey('article.id'), index=True),
	Column('tag_id', AlwaysUnicode(length=45), ForeignKey('tag.id'), index=True),
)
upload_tag_t = Table(
	'upload_tag', Base.metadata,
	Column('upload_id', Integer(), ForeignKey('upload.id'), index=True),
	Column('tag_id', AlwaysUnicode(length=45), ForeignKey('tag.id'), index=True),
)
access_log_t = Table(
	'access_log', Base.metadata,
	Column('stamp', DateTime(), index=True),
	Column('remote_ip', AlwaysUnicode(length=45), index=True),
	Column('path_info', AlwaysUnicode(length=255)),
	Column('request_method', AlwaysUnicode(length=45)),
	Column('referer_uri', AlwaysUnicode(length=255)),
)

class Article(Base):
	__tablename__ = 'article'
	skip_dict = ['page','page_id','author_rel','reviewer']
	
	id				= Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	atom_id			= Column(AlwaysUnicode(length=255), nullable=True)
	title			= Column(AlwaysUnicode(length=255), nullable=False)
	published		= Column(DateTime(), nullable=True, index=True)
	updated			= Column(DateTime(), nullable=False, index=True)
	created			= Column(DateTime(), nullable=False, index=True)
	content			= Column(AlwaysUnicodeText(), nullable=False)
	summary			= Column(AlwaysUnicodeText(), nullable=True)
	links			= Column(JSONUnicode(), nullable=False)
	metatags		= Column(JSONUnicode(), nullable=False)
	author_id		= Column(Integer(), ForeignKey('user.id'), nullable=True)
	author			= Column(JSONUnicode(), nullable=False)
	contributors	= Column(JSONUnicode(), nullable=False)
	metacontent		= Column(AlwaysUnicodeText(), nullable=False)
	sticky			= Column(Boolean(), nullable=False)
	can_comment		= Column(Boolean(), nullable=False)
	editor_choice	= Column(Boolean(), nullable=False, default=False)
	reviewed_by		= Column(Integer(), ForeignKey('user.id'), nullable=True)
	permalink		= Column(AlwaysUnicode(length=255), nullable=True)
	page_id			= Column(Integer(),ForeignKey('page.id', ondelete='SET NULL'), nullable=True, index=True)
	tags			= orm.relationship(
						'Tag',
						secondary=article_tag_t,
						collection_class=set,
						cascade='all, delete',
						backref=orm.backref('articles', lazy='dynamic')
					)
	page			= orm.relationship('Page', backref=orm.backref('articles', lazy='dynamic'), single_parent=True)
	#author_rel		= orm.relationship('User', single_parent=True)
	#reviewer		= orm.relationship('User', single_parent=True)
	
	def __init__(self, *args, **kwargs):
		self.contributors = []
		Base.__init__(self, *args, **kwargs)
	
	def owner(self):
		return self.author_id
	
	@classmethod
	def from_dict(cls, dt, default_thumb=None):
		item = cls()
		item.title = dt.get('title',None)
		item.published = dt.get('published',None)
		item.content = dt.get('content',None)
		item.sticky = dt.get('sticky',None)
		item.can_comment = dt.get('can_comment',None)
		item.page_id = dt.get('page_id',None)
		
		item.contributors = []
		item.metacontent = html.striphtml(item.content)
		item.summary = html.stripobjects(item.content)
		media_data = html.get_metamedia_data(item.content, default_thumb)
		item.links = media_data.get('link',{})
		item.metatags = media_data.get('meta',{})
		
		for label in dt.get('tags',[]):
			tag = Tag.get_from_id(slugify(label)) or Tag(label=label)
			item.tags.add(tag)
		item.updated = rfc3339.now().replace(tzinfo=None)
		if item.created is None:
			item.created = item.updated
		return item
	
	def update_from_dict(self, dt, default_thumb=None):
		self.title = dt.get('title',None)
		self.published = dt.get('published',None)
		self.content = dt.get('content',None)
		self.sticky = dt.get('sticky',None)
		self.can_comment = dt.get('can_comment',None)
		self.page_id = dt.get('page_id',None)
		
		self.metacontent = html.striphtml(self.content)
		self.summary = html.stripobjects(self.content)
		media_data = html.get_metamedia_data(self.content, default_thumb)
		self.links = media_data.get('link',{})
		self.metatags = media_data.get('meta',{})
		
		self.tags.clear()
		for label in dt.get('tags',[]):
			tag = Tag.get_from_id(slugify(label)) or Tag(label=label)
			self.tags.add(tag)
		
		self.updated = rfc3339.now().replace(tzinfo=None)
	
	#@classmethod
	#def parse_xml(cls, xml_doc):
	#	params = {}
	#	tmp = xml_doc.find(ns('title'))
	#	if tmp is not None:
	#		params['title'] = tmp
	#	tmp = xml_doc.find(ns('content'))
	#	if tmp is not None:
	#		params['content'] = tmp
	#	params['tags'] = [t['label'] for t in xml_doc['tags']]
	#	for link in xml_doc.findall(ns('links')):
	#		params['links'].append({
	#			'rel':link.get('rel'),
	#			'href':link.get('href'),
	#			'type':link.get('type')
	#		})
	#	return params
	

class Comment(Base):
	__tablename__ = 'comment'
	
	id				= Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	atom_id			= Column(AlwaysUnicode(length=255), nullable=False)
	title			= Column(AlwaysUnicode(length=255), nullable=False)
	published		= Column(DateTime(), nullable=True, index=True)
	updated			= Column(DateTime(), nullable=False, index=True)
	is_pingback		= Column(Boolean(), nullable=False, default=False)
	content			= Column(AlwaysUnicodeText(), nullable=False)
	#links			= Column(JSONUnicode(), nullable=False)
	author_id		= Column(Integer(), ForeignKey('user.id'), nullable=True)
	author			= Column(JSONUnicode(), nullable=False)
	article_id		= Column(Integer(), ForeignKey('article.id'), nullable=False)
	article			= orm.relationship(
						'Article',
						single_parent=True,
						backref=orm.backref('comments', lazy='dynamic')
					)
	
	
	def owner(self):
		return self.author_id
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.title = dt.get('title',None)
		item.content = dt.get('content',None)
		item.article_id = dt.get('parent',None)
		item.updated = item.published = rfc3339.now().replace(tzinfo=None)
		return item
	
	def update_from_dict(self, dt):
		self.title = dt.get('title',None) or self.title
		self.content = dt.get('content',None) or self.content
		self.updated = rfc3339.now().replace(tzinfo=None)
		
	
	#@classmethod
	#def parse_xml(cls,xml_doc):
	#	item = cls()
	#	item['atom_id'] = xml_doc.findtext('id')
	#	item['title'] = xml_doc.findtext('title')
	#	try:
	#		item['published'] = rfc3339.from_string(xml_doc.findtext('published'))
	#	except TypeError:
	#		item['published'] = None
	#	try:
	#		item['updated'] = rfc3339.from_string(xml_doc.findtext('updated'))
	#	except TypeError:
	#		item['updated'] = None
	#	item['content'] = xml_doc.findtext('content')
	#	try:
	#		item['links'] = [{'rel':'related','type':"application/atom+xml", 'href':xml_doc.links[0].get('href')}]
	#	except IndexError:
	#		item['links'] = []
	#	item['author'] = {
	#		'name':xml_doc.findtext('author/name'),
	#		'email':xml_doc.findtext('author/email'),
	#		'uri':xml_doc.findtext('author/href')
	#	}
	#	
	#	return params
	

class Upload(Base):
	__tablename__ = 'upload'
	
	id				= Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	#atom_id			= Column(AlwaysUnicode(length=255), nullable=False)
	title			= Column(AlwaysUnicode(length=255), nullable=False)
	published		= Column(DateTime(), nullable=True, index=True)
	updated			= Column(DateTime(), nullable=False, index=True)
	content			= Column(AlwaysUnicodeText(), nullable=False)
	filepath		= Column(AlwaysUnicode(length=255), nullable=False)
	#links			= Column(JSONUnicode(), nullable=False)
	#metatags		= Column(JSONUnicode(), nullable=False)
	author_id		= Column(Integer(), ForeignKey('user.id'), nullable=True)
	author			= Column(JSONUnicode(), nullable=False)
	tags			= orm.relationship(
						'Tag',
						secondary=upload_tag_t,
						collection_class=set,
						cascade='all, delete',
						backref=orm.backref('uploads', lazy='dynamic')
					)
	
	
	def owner(self):
		return self.author_id
	
	
	def _upload_file(self, dt):
		from pylons import config
		static_file_path = config['static_file_path']
		upload_file = dt.get('upload')
		permanent_path = os.path.join(
			static_file_path, 'uploaded', str(self.published.year), str(self.published.month).zfill(2)
		)
		basename = '_'.join([str(int(time.time())),upload_file.filename.replace(os.sep,'_')])
		self.filepath = os.path.join(
			'uploaded', str(self.published.year), str(self.published.month).zfill(2), basename
		)
		if not os.path.exists(permanent_path):
			os.makedirs(permanent_path)
		permanent_path = os.path.join(permanent_path, basename)
		if os.path.exists(permanent_path):
			raise FileExistsError(permanent_path)
		permanent_file = open(permanent_path,'wb')
		shutil.copyfileobj(upload_file.file, permanent_file)
		upload_file.file.close()
		permanent_file.close()
		return basename
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.id = dt.get('id',None)
		#item.atom_id = dt.get('atom_id',None)
		item.title = dt.get('title',None)
		item.content = dt.get('content',None)
		
		for label in dt.get('tags',[]):
			tag = Tag.get_from_id(slugify(label)) or Tag(label=label)
			item.tags.add(tag)
		item.updated = item.published = rfc3339.now().replace(tzinfo=None)
		basename = item._upload_file(dt)
		item.title = basename if item.title is None else item.title
		#upload_url = url_gen('story',permalink=item.permalink)
		#item.atom_id = get_tag_uri(upload_url,item.published,basename)
		return item
	
	@classmethod
	def quick(cls, dt):
		item = cls()
		item.title = dt['upload'].filename
		item.content = dt.get('content',u'')
		
		item.updated = item.published = rfc3339.now().replace(tzinfo=None)
		item._upload_file(dt)
		#upload_url = url_gen('story',permalink=item.permalink)
		#item.atom_id = get_tag_uri(upload_url,item.published,basename)
		return item
	
	def update_from_dict(self, dt):
		#self.atom_id = dt.get('atom_id',None)
		self.title = dt.get('title',None)
		self.content = dt.get('content',None)
		
		self.tags.clear()
		for label in dt.get('tags',[]):
			tag = Tag.get_from_id(slugify(label)) or Tag(label=label)
			self.tags.add(tag)
		self.updated = rfc3339.now().replace(tzinfo=None)
	
	#@classmethod
	#def parse_xml(cls, xml_doc):
	#	params = {}
	#	params['atom_id'] = xml_doc.findtext('id')
	#	params['title'] = xml_doc.findtext('title')
	#	params['updated'] = tri(xml_doc,'updated_parsed',alt_key='updated')
	#	params['published'] = tri(xml_doc,'published_parsed',alt_key='published')
	#	params['content'] = xml_doc.findtext('content')
	#	params['tags'] = [t['label'] for t in xml_doc['tags']]
	#	params['rights'] = xml_doc.findtext('rights')
	#	author = xml_doc.find('author')
	#	params['author'] = {
	#		'name':author.findtext('name'),
	#		'email':author.findtext('email'),
	#		'uri':author.findtext('href')
	#	}
	#	params['links'] = []
	#	for link in dub(xml_doc,links,[]):
	#		params['links'].append({
	#			'rel':dub(link,'rel'),
	#			'href':dub(link,'href'),
	#			'type':dub(link,'type')
	#		})
	#	if xml_doc.find('source') is not None:
	#		source = xml_doc.find('source')
	#		params['source'] = {
	#			'icon': source.findtext('icon'),
	#			'atom_id': source.findtext('id'),
	#			'logo': source.findtext('logo'),
	#			'rights': source.findtext('rights'),
	#			'subtitle': source.findtext('subtitle'),
	#			'title': source.findtext('title'),
	#			'updated': tri(source,'updated_parsed',alt_key='updated'),
	#		}
	#		if source.find('author') is not None:
	#			s_author = source.find('author')
	#			source['author'] = {
	#				'name':dub(s_author,'name'),
	#				'email':dub(s_author,'email'),
	#				'uri':dub(s_author,'href')
	#			}
	#		if dub(source,'contributors') is not None:
	#			source['contributors'] = []
	#			for contrib in dub(source,'contributors'):
	#				source['contributors'].append({
	#					'name':contrib.findtext('name'),
	#					'email':contrib.findtext('email'),
	#					'uri':contrib.findtext('href')
	#				})
	#		if dub(source,'links') is not None:
	#			source['links'] = []
	#			for link in dub(source,'links'):
	#				source['links'].append({
	#					'rel':dub(link,'rel'),
	#					'href':dub(link,'href'),
	#					'type':dub(link,'type')
	#				})
	#	return params
	


class Setting(Base):
	__tablename__ = 'setting'
	
	module = Column(AlwaysUnicode(length=255), primary_key=True, nullable=False)
	values = Column(JSONUnicode(), nullable=False)
	@property
	def id(self):
		return self.module
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.module = dt.get('module')
		item.values = dt.get('values')
		return item
	
	def update_from_dict(self, dt):
		self.values = dt.get('values')
	
	#@classmethod
	#def parse_xml(cls, xml_doc):
	#	raise NotImplementedError
	


class Tag(Base):
	__tablename__ = 'tag'
	
	id = Column(AlwaysUnicode(length=255), primary_key=True, nullable=False)
	label = Column(AlwaysUnicode(length=255), nullable=False)
	
	def __init__(self,*args,**kwargs):
		Base.__init__(self,*args,**kwargs)
		if self.label is not None:
			self.label = self.label.strip()
			self.id = slugify(self.label)
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.label = dt.get('label')
		item.id = slugify(item.label)
		return item
	
	def update_from_dict(self, dt):
		target = meta.Session.query(self.__class__).get(slugify(dt.get('label')))
		if target is None:
			target = self.from_dict(dt)
			target.save()
		merge_tags(self, target)
	

class Page(Base):
	__tablename__ = 'page'
	_comment_styles = ['summary','list','none']
	id = Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	title = Column(AlwaysUnicode(length=255), nullable=False)
	slug = Column(AlwaysUnicode(length=255), nullable=False, unique=True)
	content = Column(AlwaysUnicodeText(), nullable=True)
	template = Column(AlwaysUnicode(length=255), nullable=False, default=u'/blog/blank')
	#settings, should be moved to a module with a value of Page.slug
	stream_comment_style = Column(AlwaysUnicode(length=20), nullable=False)
	story_comment_style = Column(AlwaysUnicode(length=20), nullable=False)
	visible = Column(Boolean(), nullable=False)
	can_post = Column(Boolean(), nullable=False)
	in_main = Column(Boolean(), nullable=False)
	in_menu = Column(Boolean(), default=False, nullable=False)
	
	@classmethod
	def styles_list(cls):
		return [(x,x.title()) for x in cls._comment_styles]
	
	def set_defaults(self):
		self.can_post = True
		self.visible = True
		self.in_main = True
		self.in_menu = False
		self.stream_comment_style = u'summary'
		self.story_comment_style = u'list'
		self.template = u'/blog/blank'
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.title = dt['title']
		item.slug = slugify(item.title)
		item.content = dt.get('content',None)
		item.template = dt.get('template',None)
		item.stream_comment_style = dt['stream_comment_style']
		item.story_comment_style = dt['story_comment_style']
		item.visible = dt['visible']
		item.can_post = dt['can_post']
		item.in_main = dt['in_main']
		item.in_menu = dt['in_menu']
		return item
	
	def update_from_dict(self, dt):
		self.title = dt['title']
		self.slug = slugify(self.title)
		self.content = dt.get('content',None)
		self.template = dt.get('template',None)
		#settings, should be moved to a module with a value of Page.slug
		self.stream_comment_style = dt['stream_comment_style']
		self.story_comment_style = dt['story_comment_style']
		self.visible = dt['visible']
		self.can_post = dt['can_post']
		self.in_main = dt['in_main']
		self.in_menu = dt['in_menu']
	
	#@classmethod
	#def parse_xml(cls, xml_doc):
	#	raise NotImplementedError
	


class User(Base):
	__tablename__ = 'user'
	skip_dict = ['articles','pictures','comments']
	
	id = Column(Integer(), autoincrement=True, primary_key=True, nullable=False)
	name = Column(AlwaysUnicode(length=255), nullable=True, unique=True)
	open_id = Column(AlwaysUnicode(length=255), nullable=True, index=True)
	fb_id = Column(AlwaysUnicode(length=255), nullable=True, index=True)
	twitter_id = Column(AlwaysUnicode(length=255), nullable=True, index=True)
	type = Column(Integer(), nullable=False)
	profile = Column(AlwaysUnicode(length=255), nullable=True)
	#articles = orm.relationship('Article')
	pictures = orm.relationship('Upload')
	comments = orm.relationship('Comment')
	
	@classmethod
	def is_unique(cls,name):
		return meta.Session.query(User).filter(sql.func.upper(User.name)==name.upper()).count() == 0
	
	def owner(self):
		return self.id
	
	@classmethod
	def set_defaults(self):
		from columns.config.authorization import INV_PERMISSIONS
		self.type = INV_PERMISSIONS['subscriber']
		
	
	@classmethod
	def from_dict(cls, dt):
		item = cls()
		item.id = dt.get('id',None)
		item.name = dt['name']
		item.open_id = dt.get('open_id',None)
		item.fb_id = dt.get('fb_id',None)
		item.twitter_id = dt.get('twitter_id',None)
		item.type = dt['type']
		item.profile = dt.get('profile',None)
		return item
	
	def update_from_dict(self, dt):
		self.name = dt['name']
		self.open_id = dt.get('open_id',None)
		self.fb_id = dt.get('fb_id',None)
		self.twitter_id = dt.get('twitter_id',None)
		self.type = dt['type']
		self.profile = dt.get('profile',None)
	
	#@classmethod
	#def parse_xml(cls, xml_doc):
	#	raise NotImplementedError
	#



Article.author_rel = orm.relationship(User, primaryjoin=Article.author_id==User.id, backref=orm.backref('articles'), single_parent=True)
Article.reviewer = orm.relationship(User, primaryjoin=Article.reviewed_by==User.id, single_parent=True)

def get_tag_frequencies(limit=None, offset=None):
	query = meta.Session.query(Tag,sql.func.count('*').label('counter')).join(article_tag_t).group_by(Tag.id).order_by('counter DESC')
	return query.limit(limit).offset(offset).all()


RESOURCE_MAP = {
	'articles':Article,
	'pictures':Upload,
	'settings':Setting,
	'pages':Page,
	'users':User,
	'tags':Tag,
	'comments':Comment,
}

def set_default_settings(conf):
	"""Inserts into the database  any settings and other fixtures that are 
	necessary for running this application and it's tests"""
	
	core_settings = Setting(module=u'core',values={
		u'date_format': u'%B %d, %Y at %I:%M %p',
		u'site_description': u'This is my test site.',
		u'site_name': u'Columns Test',
		u'site_rights': u'',
		u'site_subtitle': u"Isn't is awesome.",
		u'maximum_items': 20,
		u'summary_length': 200,
		u'tzinfo': u'EST'
	})
	core_settings.save()
	
	blog_settings = Setting(module=u'blog',values={
		u'maximum_items': 10,
		u'summary_length': 200,
		u'default_thumb': u'',
	})
	blog_settings.save()
	
	auth_settings = Setting(module=u'auth',values={
		u'facebook_api_key': None,
		u'facebook_secret': None,
		u'twitter_oauth_key': None,
		u'twitter_oauth_secret': None,
	})
	auth_settings.save()
	#main_page = Page(title=u'Main',slug=u'main',stream_comment_style=u'summary',template=u'/blog/stream',story_comment_style=u'list',visible=True,can_post=True,in_main=True)
	#main_page.save()

