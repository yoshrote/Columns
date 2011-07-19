import cgi
import string

from columns.lib.base import BaseController
from pylons import url, request, config
error_template = string.Template("""
<html>
<head><title>${site_name}</title></head>
<body><a href="${link_path}"><img src="${img_path}" width="600" height="600"/></a></body>
</html>
""")
default_error_template = string.Template("""
<html>
<head><title>${site_name}</title></head>
<body><a href="${link_path}"></a></body>
</html>
""")

class ErrorController(BaseController):
	"""Generates error documents as and when they are required.
		
	The ErrorDocuments middleware forwards to ErrorController when error
	related status codes are returned from the application.
		
	This behaviour can be altered by changing the parameters to the
	ErrorDocuments middleware in your config/middleware.py file.
		
	"""
	def document(self):
		"""Render the error document"""
		resp = request.environ.get('pylons.original_response')
		error_code = str(request.GET.get('code', str(resp.status_int)))
		conf = config['app_conf']
		img_dict = dict([(k.replace('error_image.',''),v) for k,v in conf.items() if k.startswith('error_image')])
		error_title = conf.get('error_title',None)
		if error_code in img_dict:
			error_title = error_code if error_title is None else ' - '.join([error_title,error_code])
			return error_template.substitute(site_name=' - '.join([conf['error_title'],error_code]), link_path="/", img_path=url("static",path=img_dict[error_code]))
		else:
			error_title = 'Error' if error_title is None else ' - '.join([error_title,'Error'])
			try:
				return error_template.substitute(site_name=' - '.join([error_title,'Error']), link_path="/", img_path=url("static",path=img_dict['default']))
			except KeyError:
				return default_error_template.substitute(site_name=' - '.join([error_title,'Error']), link_path="/")
	
