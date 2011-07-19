"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	
	"""
	
	def __init__(self, config):
		"""One instance of Globals is created during application
		initialization and is available during requests via the
		'app_globals' variable
		
		"""
		self.static_file_path = config['static_file_path']
		self.static_web_path = config['static_web_path']
		self.cache = CacheManager(**parse_cache_config_options(config))
		
		self.clear_settings()
		self.clear_count_comments()
		self.clear_get_cached_article_from_id()
	
	def settings(self, key, mod=u'core'):
		values = self.rest_settings(mod)
		return values.get(key,None) if values is not None else None
	
	def rest_settings(self, rest_collection):
		@self.cache.region('query', 'settings_cache')
		def get_setting(r_col):
			from columns.model import Setting, meta
			res = meta.Session.query(Setting).get(unicode(r_col))
			return res.values if res is not None else {}
		
		return get_setting(rest_collection)
	
	def count_comments(self, article):
		@self.cache.region('query', 'comment_count')
		def get_count(art):
			return art.comments.count()
		
		return get_count(article)
	
	def get_cached_article_from_id(self, resource_id):
		@self.cache.region('query', 'article_cache')
		def get_resource(rsrc_id):
			from columns.model import Article, meta
			return meta.Session.query(Article).get(int(rsrc_id))
		
		return get_resource(resource_id)
	
	def get_article_from_permalink(self, permalink):
		from columns.model import Article, meta
		@self.cache.region('query', 'permalink_cache')
		def get_resource(perma):
			from sqlalchemy import orm
			try:
				return meta.Session.query(Article).filter(Article.permalink==perma).filter(Article.published != None).options(orm.joinedload(Article.tags),orm.joinedload(Article.page)).one()
			except:
				return None
		
		res = get_resource(permalink)
		if res is not None and res not in meta.Session:
			meta.Session.add(res)
		return res
	
	def clear_settings(self):
		self.cache.region_invalidate('settings_cache', 'query')
	
	def clear_count_comments(self):
		self.cache.region_invalidate('comment_count', 'query')
	
	def clear_get_cached_article_from_id(self):
		self.cache.region_invalidate('article_cache', 'query')
	
	def clear_get_article_from_permalink(self):
		self.cache.region_invalidate('permalink_cache', 'query')
	

