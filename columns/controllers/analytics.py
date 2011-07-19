import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from columns.lib.base import BaseController, render_jinja2, abort
from columns.lib import json
from columns.model import access_log_t, meta
from sqlalchemy import sql
from datetime import datetime, timedelta
from collections import defaultdict
import urlparse
log = logging.getLogger(__name__)
dtformat = '%Y-%m-%d'
zero_formatted = datetime.fromtimestamp(0).strftime(dtformat)

class AnalyticsController(BaseController):
	def index(self):
		return render_jinja2('/analytics/base.jinja')
	
	def views_by_article(self):
		try:
			params = json.loads(request.body)
		except:
			abort(400, detail='400 Bad Request')
		start_time = datetime.strptime(params.get('start_time',zero_formatted),dtformat)
		end_time = datetime.strptime(params.get('end_time',datetime.utcnow().strftime(dtformat)),dtformat)
		hits = meta.Session.execute(
			sql.select([access_log_t.c.path_info, sql.func.count('*').label('hits')]).\
			where(access_log_t.c.stamp.between(start_time,end_time)).\
			group_by(access_log_t.c.path_info).\
			order_by(sql.text('hits DESC'))
		).fetchall()
		response.content_type = 'application/json'
		return json.dumps([dict(x.items()) for x in hits])
	
	def uniques_by_article(self):
		try:
			params = json.loads(request.body)
		except:
			abort(400, detail='400 Bad Request')
		start_time = datetime.strptime(params.get('start_time',zero_formatted),dtformat)
		end_time = datetime.strptime(params.get('end_time',datetime.utcnow().strftime(dtformat)),dtformat)
		hits = meta.Session.execute(
			sql.select([access_log_t.c.path_info, sql.func.count(access_log_t.c.remote_ip.distinct()).label('hits')]).\
			where(access_log_t.c.stamp.between(start_time,end_time)).\
			group_by(access_log_t.c.path_info).\
			order_by(sql.text('hits DESC'))
		).fetchall()
		response.content_type = 'application/json'
		return json.dumps([dict(x.items()) for x in hits])
	
	def referers(self):
		try:
			params = json.loads(request.body)
		except:
			abort(400, detail='400 Bad Request')
		start_time = datetime.strptime(params.get('start_time',zero_formatted),dtformat)
		end_time = datetime.strptime(params.get('end_time',datetime.utcnow().strftime(dtformat)),dtformat)
		referers_dict = defaultdict(int)
		for row in meta.Session.execute(access_log_t.select(access_log_t.c.stamp.between(start_time,end_time))).fetchall():
			try:
				row_url = urlparse.urlparse(row.referer_uri).host
			except:
				row_url = ''
			referers_dict[row_url] += 1
		referers = [{'referer':x,'hits':y} for x,y in referers_dict.items()]
		response.content_type = 'application/json'
		return json.dumps(referers)
	
