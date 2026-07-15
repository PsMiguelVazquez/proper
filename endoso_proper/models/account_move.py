# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'
    ocultar_endoso = fields.Boolean(string='Ocultar endoso',
                                    help='Oculta el botón Endosar factura si ya está endosada',
                                    compute='_compute_ocultar_endoso')
    es_endoso = fields.Boolean(string='Es endoso')

    def is_inbound(self, include_receipts=True):
        # MIGRACIÓN V19: `self.name` puede ser `False` (no solo `'/'`) para
        # registros nuevos/en onchange antes de asignarse una secuencia;
        # `'END/' in False` lanza TypeError. Se agrega el guard `self.name`.
        if self.name and 'END/' in self.name and self.es_endoso:
            return True
        return self.move_type in self.get_inbound_types(include_receipts)

    def _compute_ocultar_endoso(self):
        for record in self:
            # MIGRACIÓN V19: se usaba `self.amount_residual`/`self.l10n_mx_edi_cfdi_uuid`
            # dentro del bucle (bug preexistente, solo correcto para un
            # único registro); se corrige a `record.*`. También se evita
            # `search()` con un `NewId` (registro virtual de un Form/onchange
            # sin guardar aún), que Odoo 19 ya no tolera silenciosamente
            # (warning "Domains don't support NewId").
            has_active_endoso = (
                isinstance(record.id, int)
                and bool(self.env['endoso.move'].search([('origin_invoice', '=', record.id)]).filtered(lambda x: x.state != 'cancel'))
            )
            if has_active_endoso or record.amount_residual == 0.0 or not record.l10n_mx_edi_cfdi_uuid:
                record['ocultar_endoso'] = True
            else:
                record['ocultar_endoso'] = False

    def endosar_factura(self):
        w = self.env['endoso.wizard'].sudo().create({'factura': self.id})
        view = self.env.ref('endoso_proper.view_endoso_wizard_form')
        return {
            'name': _('Endosar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'endoso.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }
