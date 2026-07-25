# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class Endoso(models.Model):
    _name = 'endoso.move'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Endosos"

    # MIGRACIÓN V19: desde 19.0, `_inherits` exige declarar explícitamente
    # el campo Many2one de delegación (antes se creaba implícitamente).
    move_id = fields.Many2one('account.move', required=True, ondelete='cascade')
    origin_invoice = fields.Many2one('account.move', string='Factura endosada')
    origin_partner_id = fields.Many2one('res.partner', string="Cliente de la factura")
    amount = fields.Monetary(currency_field='currency_id')
    amount_residual = fields.Monetary('Monto restante')
    amount_paid = fields.Monetary('Monto pagado', compute='_compute_amount_paid')
    origin_invoice_sale_id = fields.Many2one('sale.order', compute='_compute_invoice_fields', string='Venta')
    origin_invoice_date = fields.Date(compute='_compute_invoice_fields', string='Fecha de la factura')
    origin_invoice_payment_term_id = fields.Many2one('account.payment.term', compute='_compute_invoice_fields', string='Términos de pago de la factura')
    origin_invoice_warehouse_id = fields.Char(compute='_compute_invoice_fields', string='Almacén')
    origin_invoice_orden_compra = fields.Char(compute='_compute_invoice_fields', string='Orden de compra')
    origin_invoice_referencia = fields.Char(compute='_compute_invoice_fields', string='Referencia')
    origin_invoice_cfdi_uuid = fields.Char(string='Folio fiscal de la factura', related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio fiscal',related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    # MIGRACIÓN V19: `l10n_mx_edi_origin` -> `l10n_mx_edi_cfdi_origin`.
    l10n_mx_edi_origin = fields.Char(string='CFDI de origen',related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    # MIGRACIÓN V19: `l10n_mx_edi_cfdi_request` (campo + compute) fue
    # eliminado por completo: pertenecía al viejo mecanismo de seguimiento
    # de solicitudes de timbrado ligado a `account_edi`, reemplazado por la
    # máquina de estados `l10n_mx_edi_cfdi_state`. Ni `account.move` ni
    # ningún modelo de `l10n_mx_edi` en 19.0 tienen ya este campo.
    # `edi_document_ids` también se elimina: `account_edi` (el módulo que
    # define `account.move.edi_document_ids`) no es dependencia de
    # `l10n_mx_edi` en 19.0 y no está instalado en este stack -el campo
    # `related` simplemente no existe si `account_edi` no está presente-.
    invoice_date = fields.Date(string='Fecha de factura',related='origin_invoice.invoice_date')
    payment_state = fields.Selection(string='Estado de pago', selection=[('not_paid','not_paid'),('paid','paid'), ('partial','partial')], default='not_paid', compute='_compute_payment_state')

    def _compute_amount_paid(self):
        for record in self:
            # MIGRACIÓN V19: `account_internal_type` -> `account_type`.
            pay_rec_lines = record.line_ids.filtered(
                lambda line: line.account_type in ('asset_receivable', 'liability_payable')).filtered(lambda y: y.partner_id == record.partner_id)
            record.amount_paid = sum(pay_rec_lines.mapped('matched_credit_ids.amount'))
            record.move_id.amount_residual = record.amount - record.amount_paid
            record.move_id.amount_residual_signed = record.amount - record.amount_paid

    @api.depends('amount_paid')
    def _compute_payment_state(self):
        for record in self:
            if record.amount_paid == 0.00:
                record.payment_state = 'not_paid'
                record.move_id.payment_state = 'not_paid'
            elif record.amount - record.amount_paid > 0.00:
                record.payment_state = 'partial'
                record.move_id.payment_state = 'partial'
            elif record.amount ==  record.amount_paid:
                record.payment_state = 'paid'
                record.move_id.payment_state = 'paid'
            record.amount_residual = record.amount - record.amount_paid
            record.move_id.payment_state = record.payment_state

    def _compute_invoice_fields(self):
        for record in self:
            origin = record.origin_invoice
            record.origin_invoice_sale_id = origin.sale_id
            record.origin_invoice_date = origin.invoice_date
            record.origin_invoice_payment_term_id = origin.invoice_payment_term_id
            # MIGRACIÓN V19: `x_studio_almacn`, `x_studio_n_orden_de_compra`
            # y `x_referencia` se formalizaron como campos reales en
            # `account_move_proper`/`sale_purchase_confirm`.
            record.origin_invoice_warehouse_id = origin.x_studio_almacn
            record.origin_invoice_orden_compra = origin.x_studio_n_orden_de_compra
            record.origin_invoice_referencia = origin.x_referencia

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['move_type'] = 'entry'
            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
        endosos = super().create(vals_list)
        inv_ori = endosos.origin_invoice
        endosos.move_id.invoice_date = endosos.invoice_date
        endosos.amount_residual = endosos.amount - endosos.amount_paid
        write_vals = {
            'amount_untaxed': inv_ori.amount_untaxed,
            'amount_tax': inv_ori.amount_tax,
            'amount_total': inv_ori.amount_total,
            'amount_residual': inv_ori.amount_total,
            'amount_untaxed_signed': inv_ori.amount_untaxed_signed,
            'amount_tax_signed': inv_ori.amount_tax_signed,
            'amount_total_signed': inv_ori.amount_total_signed,
            'amount_residual_signed': inv_ori.amount_total,
            'payment_state': 'not_paid',
            'es_endoso': True,
        }
        # MIGRACIÓN V19: `porcent_assign` es un campo real de
        # `add_invoice_to_paid`, pero ese módulo depende de `endoso.move`
        # (este modelo) para su propia lógica -declarar aquí una
        # dependencia real hacia `add_invoice_to_paid` crearía una
        # dependencia circular-. Se mantiene el guard defensivo: solo se
        # inicializa si el campo existe (es decir, si `add_invoice_to_paid`
        # está instalado en el mismo stack, como ocurre en producción).
        if 'porcent_assign' in endosos.move_id._fields:
            write_vals['porcent_assign'] = 0.0
        endosos.move_id.write(write_vals)
        return endosos

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        return res

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        self.move_id.write({'auto_post': False, 'state': 'cancel'})

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    # MIGRACIÓN V19: `name_get()` fue removido del core; el equivalente es
    # sobreescribir `_compute_display_name`.
    @api.depends('move_id.name')
    def _compute_display_name(self):
        for endoso in self:
            endoso.display_name = endoso.move_id.name != '/' and endoso.move_id.name or _('Borrador de endoso')

    # MIGRACIÓN V19: el botón inteligente nunca tuvo una implementación real
    # -en todo el historial del módulo solo hacía `print(self)`, sin
    # devolver ninguna acción, así que el clic no navegaba a ningún lado-.
    # Se implementa para abrir la factura endosada (`origin_invoice`), que
    # es el documento relacionado que el ícono/posición del botón sugieren.
    def button_open_invoices(self):
        self.ensure_one()
        return {
            'name': _('Factura endosada'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.origin_invoice.id,
            'target': 'current',
        }
