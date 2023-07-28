# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class ConsolidacionWizard(models.Model):
    _name = 'consolidacion.wizard'
    _description = 'Muestra un wizard para el proceso consolidar líneas de pedido de ventas'
    lines = fields.Many2many('wizard.consolidation.line')
    sale_orders = fields.Many2many('sale.order', string='Pedidos')
    total = fields.Float(string='Total', compute='_compute_totals')
    subtotal = fields.Float(string='Subtotal',compute='_compute_totals')
    total_lines = fields.Float(string='Total Lineas', compute='_compute_totals')
    subtotal_lines = fields.Float(string='Subtotal Lineas',compute='_compute_totals')
    referencia = fields.Char(string='Referencia')
    orden_compra = fields.Char(string='Orden de compra')

    def _compute_totals(self):
        for record in self:
            record.total = round(sum(record.lines.mapped('total')),2)
            record.subtotal = round(sum(record.lines.mapped('subtotal')),2)
            record.total_lines = round(sum(record.sale_orders.mapped('amount_total')),2)
            record.subtotal_lines = round(sum(record.sale_orders.mapped('amount_untaxed')),2)


    def _compute_lines(self):
        for record in self:
            order_lines = self.sale_orders.mapped('order_line')
            productos = order_lines.mapped('product_id')
            lista_productos = []
            lista_productos_precios = [
                (
                    x.product_id,
                    x.price_unit,
                )
                for x in order_lines
            ]
            lista_productos_precios = list(set(lista_productos_precios))
            for elem in lista_productos_precios:
                lineas_a_consolidar = order_lines.filtered(lambda y: y.product_id == elem[0] and  y.price_unit == elem[1])
                suma_costos = 0.0
                costo_despejado = sum(lineas_a_consolidar.mapped('price_subtotal')) / sum(lineas_a_consolidar.mapped('product_uom_qty'))
                if elem[1] != costo_despejado:
                    up = costo_despejado
                else:
                    up = elem[1]
                lista_productos.append({
                    'product_id': lineas_a_consolidar.mapped('product_id.id')[0]
                    , 'quantity': sum(lineas_a_consolidar.mapped('product_uom_qty'))
                    , 'price_unit': up
                    , 'orden_compra': ', '.join(lineas_a_consolidar.filtered(lambda x: x.product_id == elem[0] and x.order_id.x_studio_n_orden_de_compra).mapped('order_id.x_studio_n_orden_de_compra'))
                    , 'sale_order_char': ', '.join(lineas_a_consolidar.filtered(lambda x: x.product_id == elem[0]).mapped('order_id.name'))
                    , 'sequence': 10
                    , 'wizard_id': record.id
                    , 'tax_id': lineas_a_consolidar.filtered(lambda x: x.product_id == elem[0]).mapped('tax_id')
                })
            lines = self.env['wizard.consolidation.line'].create(lista_productos)
            if lines:
                record['lines'] = lines
            else:
                record['lines'] = None

    def create(self, vals_list):
        r = super(ConsolidacionWizard, self).create(vals_list)
        if r:
            r._compute_lines()
        return r


    def done_consolidar(self):
        print(self)
        product_list = []
        for line in self.lines:
            if line.quantity > 0:
                product_dict = {
                    'sequence': line.sequence,
                    'name': line.product_id.name,
                    'quantity': line.quantity,
                    'product_id': line.product_id,
                    'price_unit': line.price_unit,
                    'tax_ids': line.tax_id,
                    'product_uom_id': line.product_id.uom_id.id
                }
                product_list.append(product_dict)

        partner = self.sale_orders[0].partner_id
        partner_shipping = self.sale_orders[0].partner_shipping_id
        invoice_origin_f = ', '.join(self.sale_orders.mapped('name'))
        if len(invoice_origin_f) > 45:
            invoice_origin_f = invoice_origin_f[:42] + '...'
        almacen = ', '.join(self.sale_orders.mapped('warehouse_id.name'))
        if len(almacen) > 45:
            almacen = almacen[:42] + '...'
        invoice_dict = {
            'ref': self.referencia,
            'x_referencia': self.referencia,
            'journal_id': 1,
            'move_type': 'out_invoice',
            'posted_before': False,
            'invoice_payment_term_id': partner.property_payment_term_id.id,
            'partner_id': partner.id,
            'l10n_mx_edi_payment_method_id': partner.x_studio_mtodo_de_pago,
            'l10n_mx_edi_payment_policy': partner.x_nombre_corto_tpago,
            'l10n_mx_edi_usage': partner.x_studio_uso_de_cfdi,
            'invoice_origin': invoice_origin_f,
            'invoice_line_ids': product_list,
            'partner_shipping_id': partner_shipping.id,
            'x_studio_orden_de_compra': self.orden_compra,
            'x_studio_almacn': almacen
        }
        invoice_id = self.env['account.move'].create(invoice_dict)
        if invoice_id:
            # invoice_id.sale_id.x_studio_n_orden_de_compra
            for sale_order_id in self.sale_orders:
                sale_order_id.invoice_ids |= invoice_id
                sale_order_dict = {
                    'invoice_ids': sale_order_id.invoice_ids,
                    'invoice_status': 'invoiced',
                }
                for sale_order_line_id in sale_order_id.order_line:
                    if sale_order_line_id.product_uom_qty > 0:
                        sale_order_line_id.write({'invoice_lines': invoice_id.line_ids.filtered(lambda x: x.product_id == sale_order_line_id.product_id)})
                        sale_order_line_id.write({'qty_invoiced_on_cons': sale_order_line_id.product_uom_qty})
                sale_order_id.write(sale_order_dict)
                invoice_msg = (
                                  "This invoice has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                                  sale_order_id.id, sale_order_id.name)
                invoice_id.message_post(body=invoice_msg, type="notification")
            return {
                'name': _('Factura'),
                'view_mode': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'res_id': invoice_id.id,
                'target': 'current',
            }
        return invoice_id

class ConsolidacionWizardLine(models.Model):
    _name= 'wizard.consolidation.line'
    _description = 'Líneas a consolidar'
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Producto')
    quantity = fields.Float(string='Cantidad')
    price_unit = fields.Float(string='Precio Unitario')
    wizard_id = fields.Many2one('consolidacion.wizard')
    sale_order = fields.Many2one('sale.order')
    sale_order_char = fields.Char(string='Órdenes de venta')
    orden_compra = fields.Char(string='Orden de compra')
    tax_id = fields.Many2many('account.tax', string='Impuestos')
    subtotal = fields.Float(string='Subtotal', compute='_compute_totals')
    taxes = fields.Float(string='Impuestos', compute='_compute_totals')
    total = fields.Float(string='Total', compute='_compute_totals')

    def _compute_totals(self):
        for record in self:
            record.subtotal = record.price_unit * record.quantity
            record.taxes = record.subtotal * 0.16
            record.total = record.subtotal + record.taxes