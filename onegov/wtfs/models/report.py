from cached_property import cached_property
from datetime import date
from onegov.wtfs.models.municipality import Municipality
from onegov.wtfs.models.scan_job import ScanJob
from sqlalchemy import func
from sqlalchemy.sql.expression import literal_column


def sum(table, attribute):
    result = func.coalesce(func.sum(getattr(table, attribute)), 0)
    return result.label(attribute)


def zero(attribute):
    return literal_column('0').label(attribute)


class Report(object):
    """ The base class for the reports.

    Aggregates the ``columns_in`` on the dispatch date and ``columns_out`` on
    the return date. Allows to filter by date range and scan job type.

    """

    def __init__(
        self, session, start=None, end=None, type=None, municipality=None
    ):
        self.session = session
        self.start = start or date.today()
        self.end = end or date.today()
        self.type = type
        self.municipality = municipality

    @cached_property
    def columns_in(self):
        return [
            'dispatch_boxes',
            'dispatch_cantonal_tax_office',
            'dispatch_cantonal_scan_center',
        ]

    @cached_property
    def columns_out(self):
        return ['return_boxes']

    @cached_property
    def columns(self):
        return self.columns_in + self.columns_out

    @property
    def query(self):
        # in / dispatch date
        query_in = self.session.query(ScanJob).join(Municipality)
        query_in = query_in.with_entities(
            Municipality.name.label('name'),
            *[sum(ScanJob, column) for column in self.columns_in],
            *[zero(column) for column in self.columns_out],
        )
        query_in = query_in.filter(
            ScanJob.dispatch_date >= self.start,
            ScanJob.dispatch_date <= self.end
        )
        if self.type in ('normal', 'express'):
            query_in = query_in.filter(ScanJob.type == self.type)
        if self.municipality:
            query_in = query_in.filter(Municipality.name == self.municipality)
        query_in = query_in.group_by(Municipality.name)

        # out / return date
        query_out = self.session.query(ScanJob).join(Municipality)
        query_out = query_out.with_entities(
            Municipality.name.label('name'),
            *[zero(column) for column in self.columns_in],
            *[sum(ScanJob, column) for column in self.columns_out],
        )
        query_out = query_out.filter(
            ScanJob.return_date >= self.start,
            ScanJob.return_date <= self.end
        )
        if self.type in ('normal', 'express'):
            query_out = query_out.filter(ScanJob.type == self.type)
        if self.municipality:
            query_out = query_out.filter(
                Municipality.name == self.municipality
            )
        query_out = query_out.group_by(Municipality.name)

        # join in / out
        union = query_in.union_all(query_out).subquery('union')
        query = self.session.query(
            union.c.name,
            *[sum(union.c, column) for column in self.columns]
        )
        query = query.group_by(union.c.name)
        query = query.order_by(union.c.name)
        return query

    @property
    def total(self):
        query = self.query.subquery()
        query = self.session.query(
            *[sum(query.c, column) for column in self.columns],
        )
        return query.one()


class ReportBoxes(Report):
    """ A Report containing all boxes of normal scan jobs. """

    def __init__(self, session, start=None, end=None):
        super().__init__(session, start, end, ['normal'])


class ReportBoxesAndForms(Report):
    """ A Report containing all boxes, tax forms and single documents. """

    @cached_property
    def columns_in(self):
        return [
            'dispatch_tax_forms_older',
            'dispatch_tax_forms_last_year',
            'dispatch_tax_forms_current_year',
            'dispatch_single_documents',
        ]


class ReportFormsByMunicipality(Report):
    """ A Report containing all tax forms of a single municipality. """

    @cached_property
    def columns_out(self):
        return []

    @cached_property
    def columns_in(self):
        return [
            'dispatch_tax_forms_older',
            'dispatch_tax_forms_last_year',
            'dispatch_tax_forms_current_year',
        ]