from columns.lib.authorization.util import SitePermissions
from columns.lib.authorization.predicates import *
from functools import partial
"super: control site functions, manage pages, posts, and users"
"admin: manage posts, pages, and users"
"editor: manage posts from anyone"
"author: manage own posts"
"probation: can create posts and upload pics"
"subscriber: can comment"

PERMISSIONS = {1:'super', 2:'admin', 3:'editor', 4:'author',8:'probation',9:'subscriber'}
INV_PERMISSIONS = dict([(v,k) for k,v in PERMISSIONS.items()])

MinimumPermission = partial(MinimumPermission, permission_set=INV_PERMISSIONS)
AUTHORIZE_MAP = SitePermissions({
	'tags': dict(
		index = GoodToGo(),
		show = GoodToGo(),
		new = MinimumPermission(permission='probation'),
		create = MinimumPermission(permission='probation'),
		edit = MinimumPermission(permission='editor'),
		update = MinimumPermission(permission='editor'),
		delete = MinimumPermission(permission='editor'),
	),
	'comments': dict(
		index = GoodToGo(),
		show = GoodToGo(),
		new = LoggedIn(),
		create = LoggedIn(),
		edit = MinimumPermission(permission='editor'),
		update = MinimumPermission(permission='editor'),
		delete = MinimumPermission(permission='editor'),
	),
	'pictures': dict(
		index = GoodToGo(),
		show = GoodToGo(),
		new = MinimumPermission(permission='probation'),
		create = MinimumPermission(permission='probation'),
		edit = MinimumPermission(permission='probation'),
		update = MinimumPermission(permission='probation'),
		delete = MinimumPermission(permission='editor'),
	),
	'pages': dict(
		index = GoodToGo(),
		show = GoodToGo(),
		new = MinimumPermission(permission='admin'),
		create = MinimumPermission(permission='admin'),
		edit = MinimumPermission(permission='admin'),
		update = MinimumPermission(permission='admin'),
		delete = MinimumPermission(permission='admin'),
	),
	'users': dict(
		index = MinimumPermission(permission='admin'),
		show = MinimumPermission(permission='admin'),
		new = MinimumPermission(permission='admin'),
		create = MinimumPermission(permission='admin'),
		edit = MinimumPermission(permission='admin'),
		update = MinimumPermission(permission='admin'),
		delete = MinimumPermission(permission='admin'),
	),
	'settings': dict(
		index = MinimumPermission(permission='super'),
		show = MinimumPermission(permission='super'),
		new = MinimumPermission(permission='super'),
		create = MinimumPermission(permission='super'),
		edit = MinimumPermission(permission='super'),
		update = MinimumPermission(permission='super'),
		delete = MinimumPermission(permission='super'),
	),
	'articles': dict(
		index = GoodToGo(),
		show = GoodToGo(),
		new = MinimumPermission(permission='probation'),
		create = MinimumPermission(permission='probation'),
		edit = Any(MinimumPermission(permission='editor'),ArticleOwnerLockout()),
		update = Any(MinimumPermission(permission='editor'),ArticleOwnerLockout()),
		delete = Any(MinimumPermission(permission='editor'),IsUnpublished()),
		publish = MinimumPermission(permission='author'),
	),
	'admin': dict(
		index = MinimumPermission(permission='probation'),
		settings = MinimumPermission(permission='super'),
		save_setting = MinimumPermission(permission='super'),
		quick_upload = MinimumPermission(permission='probation'),
		browse = MinimumPermission(permission='probation'),
		browse_ajax = MinimumPermission(permission='probation'),
		tag_cloud = MinimumPermission(permission='probation'),
		preview = MinimumPermission(permission='probation'),
		mark_reviewed = MinimumPermission(permission='editor'),
	),
	'accounts': dict(
		show = Restricted(), #LoggedIn(),
		new = GoodToGo(),
		create = GoodToGo(),
		edit = Restricted(), #LoggedIn(),
		set_name = Restricted(), #LoggedIn(),
		update = Restricted(), #LoggedIn(),
		delete = Restricted(), #LoggedIn(),
	),
	None: dict(
		see_reviewer = MinimumPermission(permission='editor'),
	)
})
