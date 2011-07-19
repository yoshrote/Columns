import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.lib.helpers import user_from_session
from columns.model import Upload, meta
from columns.model.form import CreateUpload, UpdateUpload

log = logging.getLogger(__name__)

class PicturesController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('picture', 'pictures')
	LOGGER = log
	MULTIPLE = 'pictures'
	SINGLE = 'picture'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Upload)
		return query.order_by(Upload.published.desc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		#if format == 'json':
		#	from columns.lib import json
		#	params = self._validate(json.loads(request.body), CreateUpload, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Upload.parse_xml(etree.fromstring(request.body))
		if format == 'html':
			params = self._validate(request.POST.mixed(), CreateUpload, 'new')
		else:
			raise UnacceptedFormat(format)
		
		item = Upload.from_dict(params)
		item.add_author_or_contributor(user_from_session(session))
		item.save()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = Upload()
		if with_defaults is True:
			item.set_defaults()
		return item
	
	def _update(self, item, format):
		if format == 'json':
			from columns.lib import json
			params = self._validate(json.loads(request.body), UpdateUpload, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Upload.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdateUpload, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params)
		item.add_author_or_contributor(user_from_session(session))
		item.save()
		return item
	
	def _delete(self, item):
		item.delete()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Upload).get(int(id))
	

