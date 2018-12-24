import functools
import json
import os
import pickle
from json import JSONDecodeError

from flask import flash
from flask_admin.babel import gettext
from flask_admin.model import BaseModelView
from google.protobuf.json_format import MessageToDict, ParseDict
from grpc import StatusCode
from wtforms import Form, StringField, IntegerField, BooleanField, validators

from node_launcher.node_set import NodeSet
from website.constants import cache_path

wtforms_type_map = {
    3: IntegerField,  # int64
    4: IntegerField,  # uint64
    5: IntegerField,  # int32
    8: BooleanField,  # bool
    9: StringField,  # string
    12: StringField,  # bytes
    13: IntegerField,  # uint32
}


def grpc_error_handling(func):
    @functools.wraps(func)
    def wrapper(*a, **kw):

        try:
            response = func(*a, **kw)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)), 'error')
            return False

        if hasattr(response, 'code') and response.code() == StatusCode.UNKNOWN:
            flash(gettext(response._state.details), 'error')
            return False
        elif hasattr(response, 'payment_error') and response.payment_error:
            flash(gettext(str(response.payment_error)), 'error')
            return False
        return response

    return wrapper


class LNDModelView(BaseModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    swagger_file_path = os.path.abspath(os.path.join(__file__,
                                                     '..', '..',
                                                     'rpc.swagger.json'))
    with open(swagger_file_path, 'r') as swagger_file:
        swagger = json.load(swagger_file)

    create_form_class = None
    get_query = None
    primary_key = None

    can_view_details = True
    details_modal = True
    create_modal = True
    can_delete = False
    can_edit = False
    column_display_actions = False

    list_template = 'admin/lnd_list.html'

    def get_one(self, record_id):
        record_count, records = self.get_list()
        return [r for r in records
                if str(getattr(r, self.primary_key)) == str(record_id)][0]

    def get_pk_value(self, model):
        return getattr(model, self.primary_key)

    def get_list(self, page=None, sort_field=None, sort_desc=False, search=None,
                 filters=None, page_size=None):
        node_set = NodeSet('mainnet')
        cache_file = os.path.join(cache_path, self.get_query + '.json')
        try:
            results = getattr(node_set.lnd_client, self.get_query)()
            with open(cache_file, 'w') as f:
                json.dump([MessageToDict(m) for m in results], f)
        except Exception as e:
            # todo add error logging
            print(e)
            try:
                with open(cache_file, 'r') as f:
                    results = json.load(f)
                    results = [r for r in results if not r.get('private', False)]
                    [r.pop('pending_htlcs', None) for r in results]
                    results = [ParseDict(m, self.model()) for m in results]
            except (FileNotFoundError, JSONDecodeError):
                results = []

        sort_field = sort_field or self.column_default_sort
        if isinstance(sort_field, tuple):
            sort_field, sort_desc = sort_field
        if hasattr(self.model(), 'capacity'):
            results.sort(key=lambda x: getattr(x, 'capacity'),
                         reverse=True)
        if hasattr(self.model(), 'active'):
            results.sort(key=lambda x: getattr(x, 'active'),
                         reverse=True)
        if sort_field is not None:
            results.sort(key=lambda x: getattr(x, sort_field),
                         reverse=sort_desc)

        return len(results), results

    def create_model(self, form):
        return NotImplementedError()

    def update_model(self, form, model):
        return NotImplementedError()

    def delete_model(self, model):
        return NotImplementedError()

    def scaffold_form(self):
        class NewForm(Form):
            pass

        if self.create_form_class is None:
            return NewForm

        for field in self.create_form_class.DESCRIPTOR.fields:

            if self.form_excluded_columns and field.name in self.form_excluded_columns:
                continue

            field_type = field.type

            if field_type == 11:  # Todo: handle "message" type, which is a nested object
                continue

            FormClass = wtforms_type_map[field_type]
            description = self.swagger['definitions'][
                'lnrpc' + self.create_form_class.__name__]['properties'][
                field.name]
            description = description.get('title') or description.get(
                'description')
            if description:
                description = description.replace('/ ', '')
            form_field = FormClass(field.name,
                                   default=field.default_value or None,
                                   description=description,
                                   validators=[validators.optional()]
                                   )
            setattr(NewForm, field.name, form_field)
        return NewForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def scaffold_list_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns

    def scaffold_sortable_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        self.column_descriptions = {
            c: self.swagger['definitions'][
                'lnrpc' + self.model.__name__]['properties'][c].get('title', '').replace('/ ', '')
            for c in columns
        }
        return columns

    def _create_ajax_loader(self, name, options):
        pass
