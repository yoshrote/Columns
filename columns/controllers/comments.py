import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect

from columns.lib.atompub_base import AtompubController, UnacceptedFormat, InvalidForm
from columns.lib.exc import *
from columns.lib import atom
from columns.lib import json
from columns.lib.helpers import user_from_session
from columns.model import Comment, Article, User, meta
from columns.model.form import CreateComment, UpdateComment

log = logging.getLogger(__name__)

class CommentsController(AtompubController):
	"""REST Controller styled on the Atom Publishing Protocol"""
	# To properly map this controller, ensure your config/routing.py
	# file has a resource setup:
	#     map.resource('comment', 'comments')
	LOGGER = log
	MULTIPLE = 'comments'
	SINGLE = 'comment'
	
	def _get_parent_attr(self):
		return 'article_id'
	
	def _index(self, parent_id=None, limit=None, offset=None):
		query = meta.Session.query(Comment)
		if parent_id is not None:
			query = query.filter(Comment.article_id == int(parent_id))
		return query.order_by(Comment.published.asc()).limit(limit).offset(offset).all()
	
	def _create(self, format, parent_id=None):
		if format == 'json':
			params = self._validate(json.loads(request.body), CreateComment, 'new')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Comment.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), CreateComment, 'new')
		else:
			raise UnacceptedFormat(format)
		
		params['parent'] = parent_id
		item = Comment.from_dict(params)
		item.add_author_or_contributor(user_from_session(session))
		if item.published is not None:
			user_id = item.author['name'] or str(session['user_id'])
			permalink = atom.slugify('-'.join([item.published.strftime("%Y-%m-%dT%H-%M-%S"),user_id]))
			story_permalink = meta.Session.query(Article).get(int(parent_id)).permalink
			story_url = url('story',permalink=story_permalink)
			item.atom_id = atom.get_tag_uri(story_url,item.published,user_id)
		item.save()
		app_globals.clear_count_comments()
		return item
	
	def _new(self, parent_id=None, with_defaults=True):
		item = Comment()
		if parent_id is not None:
			parent_attr = self._get_parent_attr()
			setattr(item,parent_attr,parent_id)
		if with_defaults is True:
			item.set_defaults()
		return item
	
	def _update(self, item, format):
		if format == 'json':
			params = self._validate(json.loads(request.body), UpdateComment, 'edit')
		#elif format == 'atom':
		#	from lxml import etree
		#	params = Comment.parse_xml(etree.fromstring(request.body))
		elif format == 'html':
			params = self._validate(request.POST.mixed(), UpdateComment, 'edit')
		else:
			raise UnacceptedFormat(format)
		
		already_published = item.published is not None
		item.update_from_dict(params)
		item.add_author_or_contributor(user_from_session(session))
		# All comments are published. This is unnessecary
		#if not already_published and item.published is not None:
		#	permalink = atom.slugify('-'.join([item.published.strftime("%Y-%m-%dT%H-%M-%S"),item.author['name']]))
		#	story_permalink = Article.get_from_id(item.article_id).permalink
		#	story_url = url('story',permalink=story_permalink)
		#	item.atom_id = atom.get_tag_uri(story_url,item.published,item.author['name'])
		item.save()
		app_globals.clear_count_comments()
		return item
	
	def _delete(self, item):
		item.delete()
		app_globals.clear_count_comments()
	
	def _get_from_id(self, id, parent_id=None):
		return meta.Session.query(Comment).get(int(id))
	
	def create(self, parent_id=None, format='html'):
		"""POST /``REST_Collection``: Create a new item"""
		if session['user_name'] is None:
			name = unicode(request.POST.get('name',u'').strip())
			if name != u'' and User.is_unique(name):
				user = meta.Session.query(User).get(int(session['user_id']))
				user.name = session['user_name'] = name
				user.save()
				session.save()
		try:
			item = self._create(format, parent_id)
		except UnacceptedFormat: 
			abort(415, detail='415 Unsupported Media Type')
		#except InvalidForm, ex:
		#	return ex.value
		
		if self.FORMAT_NEEDS_REDIRECT[format] is True:
			redirect(self._py_object.url('story',permalink=item.article.permalink))
		else:
			#if parent_id is None:
			#	abort(201, detail='201 Created', headers={'Location': self._py_object.url(self.SINGLE, id=item.id)})
			#else:
			abort(201, detail='201 Created', headers={'Location': self._py_object.url(self.SINGLE, parent_id=parent_id, id=item.id)})
	

