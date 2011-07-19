import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.model import Page, meta
from columns.model.form import CreatePage, UpdatePage

log = logging.getLogger(__name__)

class PagesController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('page', 'pages')
	LOGGER = log
	MULTIPLE = 'pages'
	SINGLE = 'page'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Page)
		return query.order_by(Page.title.desc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			from columns.lib import json
			params = self._validate(json.loads(request.body), CreatePage, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Page.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), CreatePage, 'new')
		else:
			raise UnacceptedFormat(format)
		
		item = Page.from_dict(params)
		item.save()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = Page()
		if with_defaults is True:
			item.set_defaults()
		return item
	
	def _update(self, item, format):
		if format == 'json':
			from columns.lib import json
			params = self._validate(json.loads(request.body), UpdatePage, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Page.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdatePage, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params)
		item.save()
		return item
	
	def _delete(self, item):
		item.delete()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Page).get(int(id))
	

