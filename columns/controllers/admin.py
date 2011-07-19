import logging
from pylons import request, response, session, tmpl_context as c, url, config

from columns.lib.base import BaseController, render_jinja2, abort, redirect
from columns.lib.exc import *
from columns.lib import json
from columns.lib.helpers import user_from_session
from columns.model import Upload, Article, Tag, meta, get_tag_frequencies

log = logging.getLogger(__name__)

class AdminController(BaseController):
	def index(self, format='html'):
		# Dashboard for admin
		if format == 'html':
			return render_jinja2('/admin/dashboard.jinja')
		else:
			abort(404)
	
	def quick_upload(self):
		import os.path
		ckedit_num = request.GET.get('CKEditorFuncNum')
		message = None
		filepath = 'null'
		try:
			item = Upload.quick(request.POST.mixed())
			item.add_author_or_contributor(user_from_session(session))
			item.save()
			static_web_path = config['static_web_path']
			filepath = os.path.join(static_web_path,item.filepath)
		except FileExistsError, ex:
			message = "Sorry. Could not upload file with that name."
			filepath = ex
		if message is None:
			return "<script type='text/javascript'>window.parent.CKEDITOR.tools.callFunction(%(num)s, '%(url)s')</script>" % {'num':ckedit_num,'url':filepath}
		else:
			return "<script type='text/javascript'>window.parent.CKEDITOR.tools.callFunction(%(num)s, '%(url)s', '%(msg)s')</script>" % {'num':ckedit_num,'msg':message,'url':filepath}
	
	def browse(self):
		"this template uses ajax to page through and sort thumbs of all media"
		"once a thumbnail is selected, the form goes to quick_upload"
		ckedit_num = request.GET.get('CKEditorFuncNum',None)
		return render_jinja2('/admin/browse.html.jinja', extra_vars={'ckedit_num':ckedit_num})
	
	def browse_ajax(self):
		"this action returns some thumbnails based on a sort param and offset"
		response.content_type = 'application/json'
		sort_type = request.params.get('sort',None)
		offset = int(request.params.get('offset','0'))
		limit = int(request.params.get('limit','20'))
		query = meta.Session.query(Upload).order_by(Upload.updated.desc()).offset(offset).limit(limit).all()
		json_temp = []
		for item in query:
			json_temp.append({
				'filepath':'/'.join([config['static_web_path'],item.filepath]),
				'date':item.updated.isoformat(),
				'alt':item.title or ''
			})
		return json.dumps(json_temp)
	
	def tag_cloud(self):
		response.content_type = 'application/json'
		maximum = request.params.get('max',None)
		maximum = int(maximum) if maximum is not None else None
		result = [{'id':tag.id,'name':tag.label,'count':count} for tag, count in get_tag_frequencies(limit=maximum)]
		return json.dumps(result)
	
	def mark_reviewed(self):
		article_id = request.POST.get('article_id')
		item = meta.Session.query(Article).get(int(article_id))
		item.reviewed_by = session['user_id']
		item.save()
