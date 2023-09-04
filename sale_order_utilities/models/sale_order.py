# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    edit_blocked = fields.Boolean('Bloqueado', default=False, compute='_compute_edit_blocked')
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('reverted', 'Nota de crédito aplicada'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_get_invoice_status', store=True)
    credit_notes = fields.Many2many('account.move', string='Notas de crédito relacionadas', compute='get_credit_notes')
    block_invoicing = fields.Boolean(compute='_compute_block_invoicing')
    invoice_approved = fields.Boolean(default=False)
    approve_invoicing_requested = fields.Boolean(default=False)

    def action_confirm_sale(self):
        lines = self.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra  - x.product_uom_qty) < 0 and x.x_validacion_precio == True)
        if lines:
            for l in lines:
                l.write({'cantidad_a_comprar': l.cantidad_faltante})
            msg_top = '<h3>Se solicita aprobar la orden parcial.</h3>'
            msg_bottom = ''
            lines_red = self.order_line.filtered(lambda x: x.check_price_reduce and not x.price_reduce_solicit)
            if lines_red:
                msg_bottom += '<h3>Se solicitará la aprobación de reducción de precio de los siguientes productos.</h3><table class="table" style="width: 100%"><thead>' \
                           '<tr style="width: 30% !important;"><th>Producto</th>' \
                           '<th style="width: 10%">Costo promedio</th>' \
                           '<th style="width: 10%">Precio unitario anterior</th>' \
                           '<th style="width: 10%">Margen anterior</th>' \
                           '<th style="width: 10%">Nuevo costo</th>' \
                           '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                           '<th style="width: 10%">Nuevo precio unitario</th>' \
                           '<th style="width: 10%">Nuevo margen</th>' \
                           '</tr></thead>' \
                           '<tbody>'
                for order_line in lines_red:
                    margen = order_line.product_id.x_fabricante[
                        'x_studio_margen_' + str(
                            order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                    msg_bottom += '<tr><td>' + order_line.name + '</td><td>' \
                               + str(order_line.product_id.standard_price) + '</td><td>' \
                               + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                               + str(margen) + '</td><td>' \
                               + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                               + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                               + str(round(order_line.price_unit)) + '</td><td>' \
                               + str(round((1 - (
                            order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                               + '</td></tr>'
            msg_bottom += '</tbody></table>'
            view = self.env.ref('sale_order_utilities.sale_purchase_order_alerta')
            wiz = self.env['sale.purchase.order.alerta'].create({'res_order_id': self.id, 'message_top': msg_top,
                                                                 'message_bottom': msg_bottom, 'lines': lines
                                                                 })
            return {
                'name': _('Alerta'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.purchase.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        return super(SaleOrder, self).action_confirm_sale()

    def show_confirm_sale_wizard(self):
        lines = self.order_line.filtered(lambda x: (
                        x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0
                        and x.x_validacion_precio == True)
        w = self.env['sale.purchase.order.alerta'].create({'res_order_id': self.id ,'message_top': '<h3>TOP</h3>', 'lines':lines, 'message_bottom': '<h3>BOTTOM</h3>'})
        view = self.env.ref('sale_order_utilities.sale_purchase_order_alerta')
        return {
            'name': _('Confirmar solicitud de compra'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.purchase.order.alerta',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }

    def request_approve_invoicing(self):
        self.approve_invoicing_requested = True

    def approve_invoicing(self):
        self.invoice_approved = not self.invoice_approved
        self.approve_invoicing_requested = False

    @api.depends('state')
    def _compute_block_invoicing(self):
        for record in self:
            record.block_invoicing = record.invoice_status != 'to_invoice' and record.es_orden_parcial and not record.invoice_approved

    @api.depends('state')
    def _compute_edit_blocked(self):
        for record in self:
            record.edit_blocked = record.state not in ['draft']
            # record.edit_blocked = False

    @api.depends('invoice_ids')
    def get_credit_notes(self):
        for record in self:
            record.credit_notes = record.invoice_ids.filtered(lambda x: x.move_type == 'out_refund')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    cantidad_faltante = fields.Integer('Cantidad faltante', compute='_compute_cantidad_faltante')
    atendido_por = fields.Many2one('res.users', compute='_on_change_x_solicitud_atendida', store=True)
    compra_confirmada = fields.Boolean(default=False)


    def _compute_cantidad_faltante(self):
        for record in self:
            record.cantidad_faltante = record.product_uom_qty - record.product_id.stock_quant_warehouse_zero


    @api.depends('x_solicitud_atendida')
    def _on_change_x_solicitud_atendida(self):
        for record in self:
            if record.x_solicitud_atendida == 'Atendido':
                record.atendido_por = self.env.uid
            else:
                record.atendido_por = None




