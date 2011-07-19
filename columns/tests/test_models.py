import unittest
import re
import os
import copy
import datetime
from columns.model import meta, User, Article, Comment, Page, Upload, Tag, merge_tags
from columns.model import RESTModel


'''
73, 75, 79, 81, 83, 87   , 172-173, 210, 226
class RESTModel(object):
	skip_dict = []
	
	def __getitem__(self,key):
		return getattr(self,key)
	
	def __setitem__(self, key, value):
		setattr(self,key,value)
	
	def __copy__(self):
		from copy import copy
		value = {}
		for p in self.__mapper__.iterate_properties:
			if issubclass(getattr(self,p.key).__class__,Base) and key not in self.skip_dict:
				value[p.key] = copy(getattr(self,p.key))
			else:
				value[p.key] = getattr(self,p.key)
		return value
	
	@classmethod
	def _init_query(cls, fields=None, options=None):
		#from columns.model import meta
		query = None
		if fields is None:
			query = meta.Session.query(cls)
		else:
			actual_fields = [getattr(cls,field) for field in fields if isinstance(getattr(cls,field),orm.attributes.InstrumentedAttribute)]
			query = meta.Session.query(*actual_fields)
		
		if options is not None:
			query = query.options(*options)
		
		return query
	
	@classmethod
	def _spec_builder(cls, query, spec={}):
		for spec_key, spec_val in spec.items():
			if not isinstance(spec_val,dict):
				#attempt to figure deep query
				if spec_key.find('.') != -1:
					prop, tmp, subprop = spec_key.partition('.')
					qprop = cls.__mapper__.get_property(prop)
					qclass = qprop.mapper.class_
					if qprop.single_parent is True:
						query = query.filter(getattr(cls,prop).has(getattr(qclass,subprop)==spec_val))
					else:
						query = query.filter(getattr(cls,prop).any(getattr(qclass,subprop)==spec_val))
				else:
					query = query.filter(getattr(cls,spec_key)==spec_val)
			else:
				for key, value in spec_val.items():
					if key == "$in":
						query = query.filter(getattr(cls,spec_key).in_(value))
					elif key == "$nin":
						query = query.filter(sql.not_(getattr(cls,spec_key).in_(value)))
					elif key == "$ne":
						query = query.filter(getattr(cls,spec_key) != value)
					elif key == "$gt":
						query = query.filter(getattr(cls,spec_key) > value)
					elif key == "$lt":
						query = query.filter(getattr(cls,spec_key) < value)
					elif key == "$gte":
						query = query.filter(getattr(cls,spec_key) >= value)
					elif key == "$lte":
						query = query.filter(getattr(cls,spec_key) <= value)
					else:
						raise UnknownOperatorError(key)
		return query
	
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
		query = cls._init_query()
		res = query.autoflush(False).get(id)
		return res
	
	@classmethod
	def find(cls, spec=None, fields=None, sort=None, offset=None, limit=None, count=False, options=None, return_query=False):
		"""\
		Query the database.
		
		The `spec` argument is a prototype document that all results must
		match. For example if self si called MyDoc:
		
		>>> mydocs = MyDoc.find({"hello": "world"})
		
		only matches documents that have a key "hello" with value "world".
		Matches can have other keys *in addition* to "hello". The `fields`
		argument is used to specify a subset of fields that should be included
		in the result documents. By limiting results to a certain subset of
		fields you can cut down on network traffic and decoding time.
		
		`mydocs` is a cursor which yield MyDoc object instances.
		
		See pymongo's documentation for more details on arguments.
		"""
		query = cls._init_query(fields=fields,options=options)
		
		if spec is not None:
			query = cls._spec_builder(query,spec)
		if sort is not None:
			phrases = []
			for tup in sort:
				key, val = tup
				if val == 'DESCENDING':
					phrases.append(getattr(cls,key).desc())
				else:
					phrases.append(getattr(cls,key).asc())
			query = query.order_by(*phrases)
		
		if offset is not None:
			query = query.offset(offset)
		if limit is not None:
			query = query.limit(limit)
		
		if return_query is True:
			return query
		elif count is True:
			return query.count()
		else:
			return query.all()
	
	@classmethod
	def one(cls, spec, fields=None, options=None, invalidate=False):
		"""
		`one()` act like `find()` but will raise a
		`mongokit.MultipleResultsFound` exception if there is more than one
		result.
		
		If no document is found, `one()` returns `None`
		"""
		query = cls.find(spec=spec, fields=fields, options=options, return_query=True)
		try:
			res = query.one()
		except NoResultFound:
			res = None
		except SQLA_MultipleResultsFound:
			raise MultipleResultsFound
		
		return res
	
	@classmethod
	def fetch(self, spec=None, *args, **kwargs):
		"""
		return all document wich match the structure of the object
		`fetch()` takes the same arguments than the the pymongo.collection.find method.
		
		The query is launch against the db and collection of the object.
		"""
		return self.find(spec, *args, **kwargs)
	
	@classmethod
	def fetch_one(self, spec=None, *args, **kwargs):
		"""
		return one document wich match the structure of the object
		`fetch_one()` takes the same arguments than the the pymongo.collection.find method.
		
		If multiple documents are found, raise a MultipleResultsFound exception.
		If no document is found, return None
		
		The query is launch against the db and collection of the object.
		"""
		return self.one(spec, *args, **kwargs)
	
	
	def reload(self):
		"""\
		allow to refresh the document, so after using update(), it could reload
		its value from the database.
	 	
		Be carrefull : reload() will erase all unsaved values.
	 	
		If no _id is set in the document, a KeyError is raised.
		"""
		meta.Session.refresh(self)
	
	def save(self, uuid=False, validate=None, safe=True, *args, **kwargs):
		"""
		save the document into the db.
		
		if uuid is True, a uuid4 will be automatiquely generated
		else, the pymongo.ObjectId will be used.
		
		If validate is True, the `validate` method will be called before
		saving. Not that the `validate` method will be called *before* the
		uuid is generated.
		
		`save()` follow the pymongo.collection.save arguments
		"""
		if uuid is True:
			self.id = uuid4()
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
		value = cls()
		from sqlalchemy.orm import properties
		for k,v in dt.items():
			prop = getattr(getattr(cls,k),'property')
			if issubclass(prop.__class__,properties.ColumnProperty):
				setattr(value,k,v)
			elif issubclass(prop.__class__,properties.RelationshipProperty):
				if prop.single_parent is True:
					val = prop.mapper.class_.from_dict(v)
					setattr(value,k,val)
				elif prop.collection_class is None or prop.collection_class is list:
					setattr(value,k,[])
					for sv in v:
						getattr(value,k).append(prop.mapper.class_.from_dict(sv))
				elif prop.collection_class is set:
					setattr(value,k,set([]))
					for sv in v:
						getattr(value,k).add(prop.mapper.class_.from_dict(sv))
		return value
	
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
	

'''
class TestRESTModel(unittest.TestCase):
	def test_update_from_dict(self):
		rest = RESTModel()
		self.assertRaises(NotImplementedError, rest.update_from_dict,{})
	
	def test_parse_xml(self):
		self.assertRaises(NotImplementedError, RESTModel.parse_xml,"")
	
	def test_from_dict(self):
		self.assertRaises(NotImplementedError, RESTModel.from_dict,{})
	

class TestArticle(unittest.TestCase):
	def test_add_author_and_contributor(self):
		article = Article()
		self.assertEquals(article.author_id,None)
		self.assertEquals(article.author,None)
		self.assertEquals(article.contributors,[])
		
		article.add_author_or_contributor({'id':1,'name':'test1','uri':None,'email':None})
		self.assertEquals(article.author_id,1)
		self.assertEquals(article.author['name'],'test1')
		self.assertEquals(article.author['uri'],None)
		self.assertEquals(article.author['email'],None)
		self.assertEquals(article.author['id'],1)
		self.assertEquals(article.contributors,[])
		
		article.add_author_or_contributor({'id':1,'name':'test1','uri':None,'email':None})
		self.assertEquals(article.author_id,1)
		self.assertEquals(article.author['name'],'test1')
		self.assertEquals(article.author['uri'],None)
		self.assertEquals(article.author['email'],None)
		self.assertEquals(article.author['id'],1)
		self.assertEquals(article.contributors,[])
		
		article.add_author_or_contributor({'id':2,'name':'test2','uri':None,'email':None})
		self.assertEquals(article.author_id,1)
		self.assertEquals(article.author['name'],'test1')
		self.assertEquals(article.author['uri'],None)
		self.assertEquals(article.author['email'],None)
		self.assertEquals(article.author['id'],1)
		self.assertEquals(len(article.contributors),1)
		self.assertEquals(article.contributors[0]['name'],'test2')
		self.assertEquals(article.contributors[0]['uri'],None)
		self.assertEquals(article.contributors[0]['email'],None)
		self.assertEquals(article.contributors[0]['id'],2)
	

class TestComment(unittest.TestCase):
	def test_getowner(self):
		comment = Comment()
		comment.author_id = 1
		self.assertEquals(1,comment.owner())
	

class TestUpload(unittest.TestCase):
	def test_getowner(self):
		upload = Upload()
		upload.author_id = 1
		self.assertEquals(1,upload.owner())
	
	def test_from_dict(self):
		pass
	
	def test_update_from_dict(self):
		pass

class TestTag(unittest.TestCase):
	def setUp(self):
		dt = datetime.datetime.utcnow()
		meta.Session.query(Article).delete()
		meta.Session.query(Tag).delete()
		meta.Session.flush()
		atmp = Article.from_dict(dict(
			title=u'test',
			content=u'',
			summary=u'',
			published=dt,
			sticky=False,
			can_comment=True,
			tags=['tag1','tag2'],
		))
		atmp.author = {}
		atmp.save()
		a2tmp = Article.from_dict(dict(
			title=u'test2',
			content=u'',
			summary=u'',
			published=dt,
			sticky=False,
			can_comment=True,
			tags=['tag2','tag3']
		))
		a2tmp.author = {}
		a2tmp.save()
		meta.Session.flush()
	
	def tearDown(self):
		meta.Session.query(Article).delete()
		meta.Session.query(Tag).delete()
		meta.Session.close()
		
	def test_merge(self):
		t2 = meta.Session.query(Tag).get('tag2')
		t1 = meta.Session.query(Tag).get('tag1')
		merge_tags(t2,t1)
		for art in meta.Session.query(Article).all():
			if art.title == u'test':
				labels = [t.id for t in art.tags]
				self.assert_('tag1' in labels)
				self.assertEquals(len(art.tags),1)
			elif art.title == u'test2':
				labels = [t.id for t in art.tags]
				self.assert_('tag1' in labels)
				self.assert_('tag3' in labels)
				self.assertEquals(len(art.tags),2)
			else:
				print art.title,art.content,art.author
				raise Exception("WTF")
	


'''
from unittest import TestCase

class UserModelTest(TestCase):
	def test_create_from_dict(self):
		original = User.from_dict(dict(id=1,name=u'test1',type=9))
		original.save()
		stored = User.get_from_id(1)
		self.assertEqual(original.id,stored.id)
		self.assertEqual(original.name,stored.name)
		self.assertEqual(original.open_id,stored.open_id)
		self.assertEqual(original.fb_id,stored.fb_id)
		self.assertEqual(original.twitter_id,stored.twitter_id)
		self.assertEqual(original.type,stored.type)
		self.assertEqual(original.profile,stored.profile)
	
	def tearDown(self):
		User.get_from_id(1).delete()
	
	def test_is_unique(self):
		

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
	articles = orm.relationship('Article')
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
	
	@classmethod
	def parse_xml(cls, xml_doc):
		raise NotImplementedError
	

'''
