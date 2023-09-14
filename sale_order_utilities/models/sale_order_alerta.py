# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderAlerta(models.TransientModel):
    _inherit = 'sale.order.alerta'

    def confirmar_validacion(self):
        r = super(SaleOrderAlerta, self).confirmar_validacion()
        order_lines = self.sale_id.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero
                                                                  + x.x_cantidad_disponible_compra
                                                                  - x.product_uom_qty) < 0)
        if order_lines:
            for line in order_lines:
                data_validate = self.env['data.validate'].search([('order_line_id', '=', line.id)])
                if not data_validate:
                    self.env['data.validate'].create({
                        'order_line_id': line.id,
                        'product_qty_purchases': line.x_cantidad_disponible_compra,
                        'new_cost': line.x_studio_nuevo_costo,
                        'delivery_time': line.x_tiempo_entrega_compra,
                        'note': line.x_obse_comprador,
                        'request_answered': line.x_solicitud_atendida,
                    })
                else:
                    data_validate.write({'request_answered': False})
        return r