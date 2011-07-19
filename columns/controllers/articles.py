import logging, traceback

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.lib import atom
from columns.lib import json
from columns.lib.helpers import user_from_session
from columns.model import Article, meta
from columns.model.form import CreateArticle, UpdateArticle

log = logging.getLogger(__name__)

class ArticlesController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('article', 'articles')
	LOGGER = log
	MULTIPLE = 'articles'
	SINGLE = 'article'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Article)
		if request.GET.get('drafts',None) is not None:
			query.filter(Article.published == None)
		return query.order_by(Article.sticky.desc(),Article.published.desc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			params = self._validate(json.loads(request.body), CreateArticle, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Article.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), CreateArticle, 'new')
		else:
			raise UnacceptedFormat(format)
		
		item = Article.from_dict(params, default_thumb=app_globals.settings(u'default_thumb',u'blog'))
		item.add_author_or_contributor(user_from_session(session))
		if item.published is not None:
			item.atom_id = atom.get_tag_uri(url("story", permalink=str(item.permalink), qualified=True), item.published, item.title)
		item.save()
		app_globals.clear_get_cached_article_from_id()
		app_globals.clear_get_article_from_permalink()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = Article()
		if with_defaults is True:
			item.set_defaults()
		return item
	
	def _update(self, item, format):
		already_published = item.published is not None
		if format == 'json':
			params = self._validate(json.loads(request.body), UpdateArticle, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Article.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdateArticle, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params, default_thumb=app_globals.settings(u'default_thumb',u'blog'))
		item.add_author_or_contributor(user_from_session(session))
		if not already_published and item.published is not None:
			item.atom_id = atom.get_tag_uri(url("story", permalink=str(item.permalink), qualified=True), item.published, item.title)
		item.save()
		app_globals.clear_get_cached_article_from_id()
		app_globals.clear_get_article_from_permalink()
		return item
	
	def _delete(self, item):
		item.delete()
		app_globals.clear_get_cached_article_from_id()
		app_globals.clear_get_article_from_permalink()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Article).get(int(id))
	

