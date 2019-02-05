from onegov.core.security import Public
from onegov.user import User
from onegov.user import UserCollection
from onegov.user import UserGroup
from onegov.wtfs import WtfsApp


class AddModel(object):
    """ The permission to add a given model. """


class AddModelUnrestricted(object):
    """ The permission to add given model without any restrictions. """


class EditModel(object):
    """ The permission to edit a given model. """


class EditModelUnrestricted(object):
    """ The permission to edit a given model without any restrictions. """


class DeleteModel(object):
    """ The permission to delete a given model. """


class ViewModel(object):
    """ The permission to view a given model. """


def same_group(model, identity):
    if model.group_id and identity.groupid:
        return model.group_id.hex == identity.groupid
    return False


@WtfsApp.setting_section(section="roles")
def get_roles_setting():
    return {
        'admin': set((
            AddModel,
            AddModelUnrestricted,
            EditModel,
            EditModelUnrestricted,
            DeleteModel,
            ViewModel,
            Public,
        )),
        'editor': set((
            Public,
        )),
        'member': set((
            Public,
        )),
        'anonymous': set((
            Public,
        )),
    }


@WtfsApp.permission_rule(model=UserGroup, permission=object)
def has_permission_user_group(app, identity, model, permission):
    # User groups linked to municipalities and users cannot be deleted
    if permission in {DeleteModel}:
        if model.municipality:
            return False
        if model.users.first():
            return False

    return permission in getattr(app.settings.roles, identity.role)


@WtfsApp.permission_rule(model=UserCollection, permission=object)
def has_permission_users(app, identity, model, permission):
    # Editors may view and add users
    if identity.role == 'editor':
        if permission in {ViewModel, AddModel}:
            return True

    return permission in getattr(app.settings.roles, identity.role)


@WtfsApp.permission_rule(model=User, permission=object)
def has_permission_user(app, identity, model, permission):
    # Admins can not be managed through the web
    if model.role == 'admin':
        if permission not in {Public}:
            return False

    # Editors may view, edit and delete members within the same group
    if identity.role == 'editor':
        if permission in {ViewModel, EditModel, DeleteModel}:
            if model.role == 'member':
                if same_group(model, identity):
                    return True

    return permission in getattr(app.settings.roles, identity.role)
