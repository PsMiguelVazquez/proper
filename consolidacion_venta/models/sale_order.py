# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    def view_consolidate_lines_wizard(self):
        sale_orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        order_lines = sale_orders.mapped('order_line')
        consolidacion_lines = []
        for line in order_lines:
            consolidacion_lines.append({
                'product_id': line.product_id.id
                ,'quantity': line.product_uom_qty
                , 'price_unit': line.price_unit
            })
        if len(sale_orders.mapped('partner_id')) > 1:
            raise UserError(_('No se puede  puede consolidar a diferentes clientes.'))
        for s_o in sale_orders:
            if s_o.invoice_ids.filtered(lambda x: x.state == 'posted'):
                raise UserError(_('No se puede  puede consolidar si la orden ya tiene una factura.'))
            if s_o.invoice_ids.filtered(lambda x: x.state == 'draft'):
                raise UserError(_('No se puede  puede consolidar si la orden si tiene borrador de factura o remisión'))
        if self.filtered(lambda x: x.state != 'sale'):
            raise UserError(_('No se puede consolidar si el pedido no esta en el estado "Orden de venta"'))
        w = self.env['consolidacion.wizard'].sudo().create({'sale_orders': sale_orders, 'orden_compra': sale_orders[0].x_studio_n_orden_de_compra})
        view = self.env.ref('consolidacion_venta.view_consolidacion_wizard_form')
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        context['view_no_maturity'] = False
        return {
            'name': _('Consolidar'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidacion.wizard',
            'view_mode': 'tree, form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    qty_invoiced_on_cons = fields.Float(string='Cantidad facturada en consolidación')