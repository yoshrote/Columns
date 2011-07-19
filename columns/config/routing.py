"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from __future__ import with_statement
from routes import Mapper

def make_map(config):
	"""Create, configure and return the routes Mapper"""
	map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
	map.minimization = False
	map.explicit = False
	
	# The ErrorController route (handles 404/500 error pages); it should
	# likely stay at the top, ensuring it can always be resolved
	map.connect(None, '/error/{action}', controller='error')
	map.connect(None, '/error/{action}/{id}', controller='error')
	
	# Static routes
	map.connect("static", "%s{path}"%config['static_web_path'], _static=True)
	
	# Resource routes
	columns_routeset(map, 'article', 'articles', path_prefix='/atompub')
	columns_routeset(map, 'page', 'pages', path_prefix='/atompub')
	columns_routeset(map, 'picture', 'pictures', path_prefix='/atompub')
	columns_routeset(map, 'setting', 'settings', path_prefix='/atompub')
	columns_routeset(map, 'user', 'users', path_prefix='/atompub')
	columns_routeset(map, 'tag', 'tags', path_prefix='/atompub')
	columns_routeset(map, 'comment', 'comments', path_prefix='/atompub', parent='articles')
	
	# Administrative routes
	map.connect('admin-dashboard', '/admin', controller='admin', action='index')
	map.connect('formatted_admin-dashboard', '/admin.{format}', controller='admin', action='index')
	map.connect('admin-action', '/admin/{action}', controller='admin')
	
	# Analytics routes
	map.connect('analytics-dashboard', '/analytics', controller='analytics', action='index')
	map.connect('analytics-action', '/analytics/{action}', controller='analytics')
	
	# Account routes
	with map.submapper(path_prefix='/account', controller='accounts') as m:
		m.connect('accounts', '', action='create', conditions=dict(method=['POST']))
		m.connect(None, '', action='update', conditions=dict(method=['PUT']))
		m.connect(None, '', action='delete', conditions=dict(method=['DELETE']))
		#m.connect('account', '', action='show', conditions=dict(method=['GET']))
		#m.connect('formatted_account', '.{format}', action='show', conditions=dict(method=['GET']))
		m.connect('formatted_new_account', '/new.{format:html|atom|json|ajax}', action='new', conditions=dict(method=['GET']))
		m.connect('new_account', '/new', action='new', conditions=dict(method=['GET']))
		m.connect('formatted_edit_account', '/edit.{format:html|atom|json|ajax}', action='edit', conditions=dict(method=['GET']))
		m.connect('edit_account', '/edit', action='edit', conditions=dict(method=['GET']))
		#m.connect('add_link_accounts', '/add_link', action='add_link', conditions=dict(method=['POST']))
		m.connect('set_name_accounts', '/set_name', action='set_name', conditions=dict(method=['POST']))
		#m.connect('remove_link_accounts', '/remove_link', action='remove_link', conditions=dict(method=['POST']))
		m.connect('unique_account', '/unique_account', action='check_unique_name', conditions=dict(method=['GET']))
	
	# Authentcation routes
	with map.submapper(controller='user_session') as m:
		m.connect('xrds', '/xrds.xml', action='xrds')
		m.connect('login', '/login', action='create')
		m.connect('verify', '/verify', action='verify')
		m.connect('challenge', '/challenge', action='challenge')
		m.connect('logout', '/logout', action='delete')
	
	# Blog routes
	map.connect('search', '/search', controller='blog', action='search')
	map.connect('sitemap', '/sitemap', controller='blog', action='sitemap')
	map.connect('formatted_sitemap', '/sitemap.{format:html|xml}', controller='blog', action='sitemap')
	map.connect('story', '/story/{permalink}', controller='blog', action='story')
	map.connect('formatted_story', '/story/{permalink}.{format:html|atom|json|ajax}', controller='blog', action='story')
	
	# Pingback
	#map.connect('pingback', '/pingback', controller='pingback')
	
	with map.submapper(controller='blog', action='generate') as m:
		m.connect('main', '/')
		m.connect('formatted_feed', '/feed.{format:html|atom|json|ajax}')
		m.connect('tag_feed', '/tag/{name}', filter_='tag')
		m.connect('formatted_tag_feed', '/tag/{name}.{format:html|atom|json|ajax}', filter_='tag')
		m.connect('user_feed', '/user/{name}', filter_='user')
		m.connect('formatted_user_feed', '/user/{name}.{format:html|atom|json|ajax}', filter_='user')
		m.connect('page_feed', '/{page}')
		m.connect('formatted_page_feed', '/{page}.{format:html|atom|json|ajax}')
		m.connect('page_tag', '/{page}/tag/{name}', filter_='tag')
		m.connect('formatted_page_tag', '/{page}/tag/{name}.{format:html|atom|json|ajax}', filter_='tag')
		m.connect('page_user', '/{page}/user/{name}', filter_='user')
		m.connect('formatted_page_user', '/{page}/user/{name}.{format:html|atom|json|ajax}', filter_='user')
	
	return map

def columns_routeset(mapper, single, multiple, path_prefix='', parent=None):
	with mapper.submapper(path_prefix=path_prefix, controller=multiple) as m:
		parent_prefix = '' if parent is None else '/%s/{parent_id}'%parent
		m.connect('formatted_%s'%multiple, '%s/%s.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='index', conditions={'method':['GET']})
		m.connect(None, '%s/%s.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='create', conditions={'method':['POST']})
		m.connect('formatted_new_%s'%single, '%s/%s/new.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='new', conditions={'method':['GET']})
		m.connect('formatted_edit_%s'%single, '%s/%s/{id}/edit.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='edit', conditions={'method':['GET']})
		m.connect('formatted_%s'%single, '%s/%s/{id}.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='show', conditions={'method':['GET']})
		m.connect(None, '%s/%s/{id}.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='update', conditions={'method':['PUT']})
		m.connect(None, '%s/%s/{id}.{format:html|atom|json|ajax}'%(parent_prefix,multiple), action='delete', conditions={'method':['DELETE']})
		m.connect(multiple, '%s/%s'%(parent_prefix,multiple), action='index', conditions={'method':['GET']})
		m.connect(None, '%s/%s'%(parent_prefix,multiple), action='create', conditions={'method':['POST']})
		m.connect('new_%s'%single, '%s/%s/new'%(parent_prefix,multiple), action='new', conditions={'method':['GET']})
		m.connect(single, '%s/%s/{id}'%(parent_prefix,multiple), action='show', conditions={'method':['GET']})
		m.connect(None, '%s/%s/{id}'%(parent_prefix,multiple), action='update', conditions={'method':['PUT']})
		m.connect(None, '%s/%s/{id}'%(parent_prefix,multiple), action='delete', conditions={'method':['DELETE']})
		m.connect('edit_%s'%single, '%s/%s/{id}/edit'%(parent_prefix,multiple), action='edit', conditions={'method':['GET']})
