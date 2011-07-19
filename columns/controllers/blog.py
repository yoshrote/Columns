import logging, re

from pylons import request, response, session, app_globals, url, config
from pylons.controllers.util import abort, redirect

from columns.lib.base import BaseController, render_jinja2
from columns.lib.exc import *
from columns.lib import json
from columns.model import Article, Page, Tag, User, meta
from sqlalchemy import sql, orm

log = logging.getLogger(__name__)

class BlogController(BaseController):
	def generate(self, page=None, filter_=None, name=None, format='html'):
		# i hate favicon
		if page == 'favicon.ico':
			abort(404)
		
		if page is None or page == 'main':
			page_obj = meta.Session.query(Page).filter(Page.slug=="main").filter(Page.visible==True).one()
			page_id = None
		else:
			try:
				page_obj = meta.Session.query(Page).filter(Page.slug==page).filter(Page.visible==True).one()
			except:
				abort(404)
			page_id = page_obj.id
		
		items_per_page = int(app_globals.settings(u'maximum_items','blog'))
		page_num = int(request.GET.get('p',1))
		first_item = (page_num - 1) * items_per_page
		
		query = meta.Session.query(Article).filter(Article.published != None)
		specs = {'published':{'$ne':None}}
		if page_id is None:
			query = query.filter(Article.page.has(Page.in_main==True))
			#specs['page.in_main'] = True
		else:
			query = query.filter(Article.page.has(Page.id==page_id))
			#specs['page.id'] = page_id
		
		if filter_ == 'user' and name is not None:
			query = query.filter(Article.author_rel.has(User.name==name))
			#specs['author_rel.name'] = name
		elif filter_ == 'tag' and name is not None:
			#specs['tags.id'] = name
			query = query.filter(Article.tags.any(Tag.id==name))
		
		items = query.order_by(Article.sticky.desc(),Article.published.asc()).limit(items_per_page).offset(first_item).options(orm.joinedload('tags')).all()
		#items = Article.fetch(
		#	specs,
		#	sort=[('sticky','DESCENDING'),('published','DESCENDING')],
		#	offset=first_item,limit=items_per_page,options=[orm.joinedload('tags')]
		#)
		
		if filter_ is not None:
			filter_ = (filter_,name)
		else:
			filter_ = None
		
		if format == 'atom':
			response.content_type = 'application/atom+xml'
			return render_jinja2("%s.atom.jinja"%page_obj.template)
		#elif format == 'json':
		#	response.content_type = 'application/json'
		#	return json.dumps({'data':[item.to_dict() for item in items],'page':page_obj})
		elif format == 'html':
			return render_jinja2("%s.jinja"%page_obj.template, extra_vars={'items':items, 'page_num':page_num, 'page':page_obj})
		else:
			abort(404)
	
	def story(self, permalink=None, format='html'):
		item = app_globals.get_article_from_permalink(permalink)
		#item = Article.fetch_one({'permalink':permalink,'published':{'$ne':None}})
		if item is None:
			abort(404)
		else:
			return render_jinja2('/blog/story.jinja', extra_vars={'item':item})
	
	def search(self):
		try:
			q = request.GET.getone("q")
			pnum = request.GET.get("pnum",None)
		except:
			redirect(url("main"))
		page_num = 1 if pnum is None else int(pnum)
		items_per_page = int(app_globals.settings(u'maximum_items','blog'))
		first_item = (page_num - 1) * items_per_page
		
		q_string = q.lower()
		res = meta.Session.query(Article).filter(
			sql.or_(
				Article.tags.any(sql.func.lower(Tag.label).contains(q_string)),
				sql.func.lower(Article.title).contains(q_string),
				sql.func.lower(Article.metacontent).contains(q_string)
			)
		).filter(Article.published!=None).filter(Article.page.has(Page.in_main==True)).\
		order_by(Article.published.desc()).limit(items_per_page).offset(first_item)
		items = res.all()
		
		return render_jinja2('/blog/stream.jinja', extra_vars={'items':items, 'page_num':page_num, 'page':None})
	
	def sitemap(self, format='html'):
		tags = meta.Session.query(Tag).order_by(Tag.label.asc()).all()
		users = meta.Session.query(User.name).filter(User.type <= self.permissions_map['probation']).order_by(User.name.asc()).all()
		pages = meta.Session.query(Page.title,Page.slug).filter(Page.visible == True).order_by(Page.title.asc()).all()
		return render_jinja2('/blog/sitemap.%s.jinja'%format, extra_vars={'tags':tags,'users':users,'pages':pages})
	

