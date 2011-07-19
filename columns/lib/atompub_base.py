from columns.lib.base import BaseController, abort, redirect, render_jinja2 #, render_jinja2_block
from columns.lib.exc import UnacceptedFormat, InvalidForm, TemplateNotFound, AuthorizationException, NoParentException
from formencode import Invalid, htmlfill

class AtompubController(BaseController):
	FORMAT_NEEDS_REDIRECT = {'json':False,'atom':False,'html':True}
	RESOURCE_FORMATS = {'json':'application/json','atom':'application/atom+xml','html':'text/html','ajax':'text/html'}
	LOGGER = None
	SINGLE = None
	MULTIPLE = None
	
	def _validate(self, params, schema, form, dict_char='.', list_char='-', **htmlfill_kwargs):
		"""Reworked Pylons validate decorator into a usable form for helper classes"""
		request = self._py_object.request
		errors = {}
		
		# If they want post args only, use just the post args
		try:
			return schema.to_python(params, None)
		except Invalid, e:
			errors = e.unpack_errors(False, dict_char, list_char)
			request.environ['REQUEST_METHOD'] = 'GET'
			self._py_object.tmpl_context.form_errors = errors
		
			request.environ['pylons.routes_dict']['action'] = form
			resp = self._dispatch_call()
		
			# If the form_content is an exception response, return it
			if hasattr(resp, '_exception'):
				return resp
			
			htmlfill_kwargs2 = htmlfill_kwargs.copy()
			htmlfill_kwargs2.setdefault('encoding', request.charset)
			raise InvalidForm(htmlfill.render(resp, defaults=params, errors=errors, **htmlfill_kwargs2), errors)
	
	def _get_parent_attr(self):
		raise NoParentException
	
	def _index(self, parent_id=None, limit=None, offset=None):
		raise NotImplementedError
	
	def _create(self, format, parent_id=None):
		raise NotImplementedError
	
	def _new(self, parent_id=None, with_defaults=True):
		raise NotImplementedError
	
	def _update(self, item, format):
		raise NotImplementedError
	
	def _delete(self, item):
		raise NotImplementedError
	
	def _get_from_id(self, id, parent_id=None):
		raise NotImplementedError
	
	def _get_settings(self):
		return self._py_object.app_globals.rest_settings('core')
	
	def index(self, parent_id=None, format='html'):
		"""GET /``REST_Collection``: All items in the collection"""
		settings = self._get_settings()
		
		try:
			page_num = int(self._py_object.request.GET.get('p',1))
		except ValueError:
			page_num = 1
		try:
			limit = int(settings.get('maximum_items'))
		except (ValueError,TypeError):
		 	limit = 20
		offset = (page_num - 1) * limit
		
		items = self._index(parent_id=parent_id, limit=limit, offset=offset)
		
		try:
			self._py_object.response.content_type = self.RESOURCE_FORMATS[format]
			extra_vars={'settings':settings,'page_num':page_num,'items':items,'ctrl_name':self.MULTIPLE}
			#if format == 'ajax':
			#	return render_jinja2_block('/%s/index.html.jinja'%self.MULTIPLE, 'content', extra_vars=extra_vars)
			#else:
			return render_jinja2('/%s/index.%s.jinja'%(self.MULTIPLE,format), extra_vars=extra_vars)
		except TemplateNotFound, ex:
			self.LOGGER.error(ex)
			abort(415, detail='415 Unsupported Media Type')
	
	def create(self, parent_id=None, format='html'):
		"""POST /``REST_Collection``: Create a new item"""
		try:
			item = self._create(format, parent_id)
		except UnacceptedFormat: 
			abort(415, detail='415 Unsupported Media Type')
		except InvalidForm, ex:
			return ex.value
		
		if self.FORMAT_NEEDS_REDIRECT[format] is True:
			if parent_id is None:
				redirect(self._py_object.url(self.MULTIPLE))
			else:
				redirect(self._py_object.url(self.MULTIPLE, parent_id=parent_id))
		else:
			if parent_id is None:
				abort(201, detail='201 Created', headers={'Location': self._py_object.url(self.SINGLE, id=item.id)})
			else:
				abort(201, detail='201 Created', headers={'Location': self._py_object.url(self.SINGLE, parent_id=parent_id, id=item.id)})
	
	def new(self, parent_id=None, format='html'):
		"""GET /``REST_Collection``/new: Form to create a new item"""
		settings = self._get_settings()
		item = self._new(parent_id, with_defaults=True)
		try:
			extra_vars = {'item':item,'settings':settings,'ctrl_name':self.MULTIPLE}
			#if format == 'ajax':
			#	return render_jinja2_block('/%s/new.html.jinja'%self.MULTIPLE, 'content', extra_vars=extra_vars)
			#else:
			return render_jinja2('/%s/new.%s.jinja'%(self.MULTIPLE,format), extra_vars=extra_vars)
		except TemplateNotFound, ex:
			self.LOGGER.error(ex)
			abort(415, detail='415 Unsupported Media Type')
	
	def update(self, id, parent_id=None, format='html'):
		"""PUT /``REST_Collection``/id: Update an existing item"""
		try:
			item = self._get_from_id(id, parent_id)
			if item is None:
				abort(404, detail='404 Not Found')
			self._update(item, format)
		except UnacceptedFormat: 
			abort(415, detail='415 Unsupported Media Type')
		except InvalidForm, ex:
			return ex.value
		
		if self.FORMAT_NEEDS_REDIRECT[format] is True:
			if parent_id is None:
				redirect(self._py_object.url(self.MULTIPLE))
			else:
				redirect(self._py_object.url(self.MULTIPLE, parent_id=parent_id))
		else:
			abort(200, detail='200 OK')
	
	def delete(self, id, parent_id=None, format='html'):
		"""DELETE /``REST_Collection``/id: Delete an existing item"""
		item = self._get_from_id(id, parent_id)
		if item is None:
			abort(404, detail='404 Not Found')
		self._delete(item)
		
		if self.FORMAT_NEEDS_REDIRECT[format] is True:
			if parent_id is None:
				redirect(self._py_object.url(self.MULTIPLE))
			else:
				redirect(self._py_object.url(self.MULTIPLE, parent_id=parent_id))
		else:
			abort(200, detail='200 OK')
	
	def show(self, id, parent_id=None, format='html'):
		"""GET /``REST_Collection``/id: Show a specific item"""
		try:
			page_num = int(self._py_object.request.GET.get('p',1))
		except ValueError:
			#someone put something stupid as the value for page
			page_num = 1
		try:
			settings = self._get_settings()
			item = self._get_from_id(id, parent_id)
			if item is None:
				abort(404, detail='404 Not Found')
			settings = self._get_settings()
			self._py_object.response.content_type = self.RESOURCE_FORMATS[format]
			extra_vars = {'item':item,'settings':settings,'page_num':page_num,'ctrl_name':self.MULTIPLE}
			#if format == 'ajax':
			#	return render_jinja2_block('/%s/show.html.jinja'%self.MULTIPLE, 'content', extra_vars=extra_vars)
			#else:
			return render_jinja2('/%s/show.%s.jinja'%(self.MULTIPLE,format), extra_vars=extra_vars)
		except TemplateNotFound, ex:
			self.LOGGER.error(ex)
			abort(415, detail='415 Unsupported Media Type')
	
	def edit(self, id, parent_id=None, format='html'):
		"""GET /``REST_Collection``/id/edit: Form to edit an existing item"""
		settings = self._get_settings()
		item = self._get_from_id(id, parent_id)
		if item is None:
			abort(404, detail='404 Not Found')
		try:
			extra_vars = {'item':item,'settings':settings,'ctrl_name':self.MULTIPLE}
			#if format == 'ajax':
			#	return render_jinja2_block('/%s/edit.html.jinja'%self.MULTIPLE, 'content', extra_vars=extra_vars)
			#else:
			return render_jinja2('/%s/edit.%s.jinja'%(self.MULTIPLE,format), extra_vars=extra_vars)
		except TemplateNotFound, ex:
			self.LOGGER.error(ex)
			abort(415, detail='415 Unsupported Media Type')
	

