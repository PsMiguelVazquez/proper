# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('consolidate', 'Consolidada'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def view_consolidate_purchase_wizard(self):
        purchase_orders = self.env['purchase.order'].browse(self.env.context.get('active_ids'))
        for po in purchase_orders:
            if len(po.order_line) == 0:
                raise UserError('Algunas órdenes de compra no tienen productos')
        if len(purchase_orders.mapped('partner_id')) > 1:
            raise UserError('No se pueden consolidar órdenes de diferentes proveedores')
        if len(purchase_orders) == 1:
            raise UserError('Se deben consolidar 2 o más órdenes')
        if len(list(set(purchase_orders.mapped('state')))) > 1:
            for state in purchase_orders.mapped('state'):
                if state not in ['draft', 'to approve']:
                    raise UserError('Sólo se pueden consolidar órdenes en estado borrador o en estado Para aprobar')
        partner = purchase_orders.mapped('partner_id')
        purchase_order_lines = purchase_orders.mapped('order_line')
        w = self.env['consolidacion.compras.wizard'].sudo().create(
            {'partner_id': partner.id, 'purchase_orders': purchase_orders, 'purchase_order_lines': purchase_order_lines.filtered(lambda x: x.product_qty > 0)})
        view = self.env.ref('consolidacion_compras.view_consolidacion_compra_wizard_form')
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        context['view_no_maturity'] = False
        return {
            'name': _('Consolidar'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidacion.compras.wizard',
            'view_mode': 'tree, form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }