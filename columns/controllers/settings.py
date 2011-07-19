import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.lib import json
from columns.model import Setting, meta
from columns.model.form import CreateSetting, UpdateSetting

log = logging.getLogger(__name__)

class SettingsController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('setting', 'settings')
	LOGGER = log
	MULTIPLE = 'settings'
	SINGLE = 'setting'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Setting)
		return query.order_by(Setting.module.desc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			params = json.loads(request.body)
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Setting.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			from formencode import NestedVariables
			params = NestedVariables.to_python(request.POST.mixed())
		else:
			raise UnacceptedFormat(format)
		
		item = Setting.from_dict(params)
		item.save()
		app_globals.clear_settings()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		abort(200)
		#item = Setting()
		#if parent_id is not None:
		#	parent_attr = self._get_parent_attr()
		#	setattr(item,parent_attr,parent_id)
		#if with_defaults is True:
		#	item.set_defaults()
		#return item
	
	def _update(self, item, format):
		if format == 'json':
			params = json.loads(request.body)
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Setting.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			from formencode import NestedVariables
			params = NestedVariables.to_python(request.POST.mixed())
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params)
		item.save()
		app_globals.clear_settings()
		return item
	
	def _delete(self, item):
		item.delete()
		app_globals.clear_settings()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Setting).get(id)
	

