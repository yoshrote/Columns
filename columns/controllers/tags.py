import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.lib import json
from columns.model import Tag, meta
from columns.model import article_tag_t, sql
from columns.model.form import CreateTag, UpdateTag

log = logging.getLogger(__name__)

class TagsController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('tag', 'tags')
	LOGGER = log
	MULTIPLE = 'tags'
	SINGLE = 'tag'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Tag,sql.func.count('*').label('counter')).join(article_tag_t).group_by(Tag.id).order_by('counter DESC')
		return query.limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			params = self._validate(json.loads(request.body), CreateTag, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Tag.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), CreateTag, 'new')
		else:
			raise UnacceptedFormat(format)
		
		item = Tag.from_dict(params)
		item.save()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = Tag()
		return item
	
	def _update(self, item, format):
		if format == 'json':
			params = self._validate(json.loads(request.body), UpdateTag, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Tag.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdateTag, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params)
		item.save()
		return item
	
	def _delete(self, item):
		item.delete()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Tag).get(id)
	

