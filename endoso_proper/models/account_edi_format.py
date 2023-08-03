# -*- coding: utf-8 -*-

import logging
import re

from odoo import models, api
from odoo.tools.float_utils import float_round, float_is_zero

_logger = logging.getLogger(__name__)

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        if 'END/' in invoice.name and invoice.es_endoso:
            inv = self.env['endoso.move'].search([('move_id','=',invoice.id)]).origin_invoice
            return super(AccountEdiFormat, self)._l10n_mx_edi_get_invoice_cfdi_values(inv)
        return super(AccountEdiFormat, self)._l10n_mx_edi_get_invoice_cfdi_values(invoice)

    def _l10n_mx_edi_get_serie_and_folio(self, move):
        if 'END/' in move.name and move.es_endoso:
            print('END')
            inv = self.env['endoso.move'].search([('move_id','=',move.id)]).origin_invoice
            name_numbers = list(re.finditer('\d+', inv.name))
            serie_number = inv.name[:name_numbers[-1].start()]
            folio_number = name_numbers[-1].group().lstrip('0')
        else:
            name_numbers = list(re.finditer('\d+', move.name))
            serie_number = move.name[:name_numbers[-1].start()]
            folio_number = name_numbers[-1].group().lstrip('0')
        return {
            'serie_number': serie_number,
            'folio_number': folio_number,
        }