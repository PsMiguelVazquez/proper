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

    def _compute_amount(self):
        super()._compute_amount()
        # MIGRACIÓN V19: `_compute_amount` (core) sólo acumula
        # `amount_residual` para líneas `display_type == 'payment_term'`
        # dentro de la rama que aplica cuando `move.is_invoice(True)` es
        # verdadero; para cualquier otro `move_type` (rama "Miscellaneous
        # journal entry") `amount_residual` queda fijo en 0.0, sin
        # excepción. `endoso.move` crea su `account.move` con
        # `move_type = 'entry'` (ver `endoso.create()`), así que cae
        # siempre en esa rama -esto ya era así en 15.0, pero antes
        # `amount_residual` no distinguía por `move_type` de esta forma-.
        # `endoso.move` lleva su propio tracking paralelo
        # (`amount`/`amount_paid`/`amount_residual`, ver
        # `_compute_amount_paid`) y trata de reflejarlo escribiendo
        # directo en `move_id.amount_residual`, pero como es un campo
        # `compute=`, ese valor se pierde cada vez que algo más dispara
        # un recompute de este mismo método (p.ej. una reconciliación),
        # dejando `account.move.amount_residual` de vuelta en 0.0 aunque
        # el endoso internamente sepa que tiene saldo pendiente -se
        # reprodujo en producción: el wizard de "Compensación"
        # (`factoraje_financiero`) lee este campo directo y lo mostraba
        # en 0 pese a que `endoso.move.amount_residual` sí tenía el
        # monto real-. Se reafirma aquí, después de `super()`, para que
        # sobreviva a cualquier recompute futuro. Se recalcula
        # `amount_paid` en línea (en vez de leer `endoso.amount_paid`)
        # para no disparar el propio compute de `endoso.move`, que
        # también escribe en este mismo campo -evita una recomputación
        # cruzada innecesaria en medio de este método-.
        endoso_moves = self.filtered(lambda m: m.es_endoso and m.move_type == 'entry')
        if not endoso_moves:
            return
        endosos = self.env['endoso.move'].search([('move_id', 'in', endoso_moves.ids)])
        endoso_by_move_id = {endoso.move_id.id: endoso for endoso in endosos}
        for move in endoso_moves:
            endoso = endoso_by_move_id.get(move.id)
            if not endoso:
                continue
            pay_rec_lines = move.line_ids.filtered(
                lambda line: line.account_type in ('asset_receivable', 'liability_payable')
            ).filtered(lambda line: line.partner_id == endoso.partner_id)
            amount_paid = sum(pay_rec_lines.mapped('matched_credit_ids.amount'))
            residual = endoso.amount - amount_paid
            move.amount_residual = residual
            move.amount_residual_signed = residual

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
