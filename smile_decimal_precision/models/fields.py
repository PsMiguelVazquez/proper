# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Float
from odoo.fields import Monetary
from odoo import tools

from odoo.tools import (
    float_repr, float_round, float_compare, float_is_zero, html_sanitize, human_size,
    pg_varchar, ustr, OrderedSet, pycompat, sql, date_utils, unique, IterableGenerator,
    image_process, merge_sequences,
)


def new_float_convert_to_column(self, value, record, values=None, validate=True):
    precision = record.env.company.display_digits
    result = float(value or 0.0)
    if precision:
        precision, scale = (16, precision)
        result = float_repr(float_round(result, precision_digits=scale), precision_digits=scale)
    return result

def new_currency_convert_to_column(self, value, record, values=None, validate=True):
    precision = record.env.company.display_digits
    # retrieve currency from values or record
    currency_field_name = self.get_currency_field(record)
    currency_field = record._fields[currency_field_name]
    if values and currency_field_name in values:
        dummy = record.new({currency_field_name: values[currency_field_name]})
        currency = dummy[currency_field_name]
    elif values and currency_field.related and currency_field.related.split('.')[0] in values:
        related_field_name = currency_field.related.split('.')[0]
        dummy = record.new({related_field_name: values[related_field_name]})
        currency = dummy[currency_field_name]
    else:
        # Note: this is wrong if 'record' is several records with different
        # currencies, which is functional nonsense and should not happen
        # BEWARE: do not prefetch other fields, because 'value' may be in
        # cache, and would be overridden by the value read from database!
        currency = record[:1].with_context(prefetch_fields=False)[currency_field_name]

    value = float(value or 0.0)
    if currency:
        return float_repr(currency.round(value), precision)
    return value


def new_monetary_convert_to_cache(self, value, record, validate=True):
    # cache format: float
    value = float(value or 0.0)
    if value and validate:
        # FIXME @rco-odoo: currency may not be already initialized if it is
        # a function or related field!
        # BEWARE: do not prefetch other fields, because 'value' may be in
        # cache, and would be overridden by the value read from database!
        currency_field = self.get_currency_field(record)
        currency = record.sudo().with_context(prefetch_fields=False)[currency_field]
        if len(currency) > 1:
            raise ValueError("Got multiple currencies while assigning values of monetary field %s" % str(self))
        elif currency:
            value =  tools.float_round(value, precision_digits=2)
    return value

def new_float_convert_to_cache(self, value, record, validate=True):
    # apply rounding here, otherwise value in cache may be wrong!
    precision = record.env.company.display_digits
    value = float(value or 0.0)
    if not validate:
        return value
    #digits = self.get_digits(record.env)
    return float_round(value, precision_digits=precision) if precision else value


def new_monetary_convert_to_column(self, value, record, values=None, validate=True):
    # retrieve currency from values or record
    currency_field_name = self.get_currency_field(record)
    currency_field = record._fields[currency_field_name]
    precision = record.env.company.display_digits
    if values and currency_field_name in values:
        dummy = record.new({currency_field_name: values[currency_field_name]})
        currency = dummy[currency_field_name]
    elif values and currency_field.related and currency_field.related.split('.')[0] in values:
        related_field_name = currency_field.related.split('.')[0]
        dummy = record.new({related_field_name: values[related_field_name]})
        currency = dummy[currency_field_name]
    else:
        # Note: this is wrong if 'record' is several records with different
        # currencies, which is functional nonsense and should not happen
        # BEWARE: do not prefetch other fields, because 'value' may be in
        # cache, and would be overridden by the value read from database!
        currency = record[:1].with_context(prefetch_fields=False)[currency_field_name]

    value = float(value or 0.0)
    if currency:
        return float_repr(currency.round(value), precision)
    return value

Float.convert_to_cache = new_float_convert_to_cache
Float.convert_to_column = new_float_convert_to_column
Monetary.convert_to_column = new_monetary_convert_to_column
Monetary.convert_to_cache = new_monetary_convert_to_cache
