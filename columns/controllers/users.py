import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController
from columns.lib.exc import *
from columns.lib import json
from columns.model import User, meta
from columns.model.form import CreateUser, UpdateUser

log = logging.getLogger(__name__)

class UsersController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('user', 'users')
	LOGGER = log
	MULTIPLE = 'users'
	SINGLE = 'user'
	
	def _index(self, parent_id=None, limit=None, offset=None, sort=None):
		query = meta.Session.query(User)
		return query.order_by(User.type.asc(),User.name.desc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			params = self._validate(json.loads(request.body), CreateUser, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = User.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), CreateUser, 'new')
		else:
			raise UnacceptedFormat(format)
		
		item = User.from_dict(params)
		item.save()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = User()
		if with_defaults is True:
			item.set_defaults()
		return item
	
	def _update(self, item, format):
		if format == 'json':
			params = self._validate(json.loads(request.body), UpdateUser, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = User.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdateUser, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		item.update_from_dict(params)
		item.save()
		return item
	
	def _delete(self, item):
		item.delete()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(User).get(int(id))
	

