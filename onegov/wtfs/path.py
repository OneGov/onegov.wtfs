from onegov.core.converters import extended_date_converter
from onegov.user import Auth
from onegov.user import User
from onegov.user import UserCollection
from onegov.user import UserGroup
from onegov.user import UserGroupCollection
from onegov.wtfs.app import WtfsApp
from onegov.wtfs.collections import MunicipalityCollection
from onegov.wtfs.collections import ScanJobCollection
from onegov.wtfs.models import DailyList
from onegov.wtfs.models import Municipality
from onegov.wtfs.models import Principal
from onegov.wtfs.models import Report
from onegov.wtfs.models import ReportBoxes
from onegov.wtfs.models import ReportBoxesAndForms
from onegov.wtfs.models import ReportFormsByMunicipality
from onegov.wtfs.models import ScanJob


@WtfsApp.path(
    model=Principal,
    path='/'
)
def get_principal(app):
    return app.principal


@WtfsApp.path(
    model=Auth,
    path='/auth'
)
def get_auth(request, to='/'):
    return Auth.from_request(request, to)


@WtfsApp.path(
    model=UserGroupCollection,
    path='/user-groups'
)
def get_user_groups(request):
    return UserGroupCollection(request.session)


@WtfsApp.path(
    model=UserGroup,
    path='/user-group/{id}'
)
def get_user_group(request, id):
    return UserGroupCollection(request.session).by_id(id)


@WtfsApp.path(
    model=UserCollection,
    path='/users'
)
def get_users(request):
    return UserCollection(request.session)


@WtfsApp.path(
    model=User,
    path='/user/{username}'
)
def get_user(request, username):
    return UserCollection(request.session).by_username(username)


@WtfsApp.path(
    model=MunicipalityCollection,
    path='/municipalities'
)
def get_municipalities(request):
    return MunicipalityCollection(request.session)


@WtfsApp.path(
    model=Municipality,
    path='/municipality/{id}'
)
def get_municipality(request, id):
    return MunicipalityCollection(request.session).by_id(id)


@WtfsApp.path(
    model=ScanJobCollection,
    path='/scan-jobs'
)
def get_scan_jobs(request):
    return ScanJobCollection(request.session)


@WtfsApp.path(
    model=ScanJob,
    path='/scan-job/{id}'
)
def get_scan_job(request, id):
    return ScanJobCollection(request.session).by_id(id)


@WtfsApp.path(
    model=DailyList,
    path='/daily-list/boxes/{date}',
    converters=dict(
        date=extended_date_converter,
    )
)
def get_daily_list(request, date):
    return DailyList(request.session, date)


@WtfsApp.path(
    model=Report,
    path='/report',
)
def get_report(request):
    return Report(request.session)


@WtfsApp.path(
    model=ReportBoxes,
    path='/report/boxes/{start}/{end}',
    converters=dict(
        start=extended_date_converter,
        end=extended_date_converter,
    )
)
def get_report_boxes(request, start, end):
    return ReportBoxes(request.session, start, end)


@WtfsApp.path(
    model=ReportBoxesAndForms,
    path='/report/boxes-and-forms/{start}/{end}/{type}',
    converters=dict(
        start=extended_date_converter,
        end=extended_date_converter,
    )
)
def get_report_boxes_and_forms(request, start, end, type):
    return ReportBoxesAndForms(request.session, start, end, type)


@WtfsApp.path(
    model=ReportFormsByMunicipality,
    path='/report/forms/{start}/{end}/{type}/{municipality}',
    converters=dict(
        start=extended_date_converter,
        end=extended_date_converter,
    )
)
def get_report_forms(request, start, end, type, municipality):
    return ReportFormsByMunicipality(
        request.session, start, end, type, municipality
    )
