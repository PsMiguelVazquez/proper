# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuantClient(models.Model):
    _inherit = 'stock.quant'
    cliente_reporte = fields.Char(string='Cliente', compute="_compute_costo_cliente")
    costo_cliente = fields.Float(string='Costo por cliente',  compute="_compute_costo_cliente")
    margen_cliente = fields.Float(string='Margen del cliente', compute="_compute_costo_cliente")

    # MIGRACIÓN V19: `x_studio_costo_promedio` (en stock.quant), `x_fabricante`
    # (en product.product/template) y `x_nivel_cliente` (en res.partner) son
    # campos creados con Odoo Studio directamente en la base de datos de
    # producción de 15.0 -no existen como código de módulo-, por lo que no
    # viajan con esta migración. Se protege el cómputo con comprobaciones de
    # existencia para que las vistas de stock.quant no fallen en una base de
    # datos nueva donde esos campos de Studio todavía no se hayan recreado;
    # en la base de datos real (con los campos de Studio migrados aparte)
    # el cálculo funciona igual que en 15.0.
    @api.depends('product_id')
    def _compute_costo_cliente(self):
        wizard_client_id = self.env['change.client.wizard'].search(
            [('create_uid', '=', self.env.user.id)], limit=1, order='id desc'
        ).client_id
        for record in self:
            record.cliente_reporte = wizard_client_id.name if wizard_client_id else ''
            record.margen_cliente = 0.0
            record.costo_cliente = 0.0

            if not wizard_client_id or 'x_nivel_cliente' not in wizard_client_id._fields:
                continue
            nivel_cliente = wizard_client_id.x_nivel_cliente.x_name if wizard_client_id.x_nivel_cliente else False
            if not nivel_cliente:
                continue

            fabricante = record.product_id.x_fabricante if 'x_fabricante' in record.product_id._fields else False
            margen_field = 'x_studio_margen_' + nivel_cliente
            if not fabricante or margen_field not in fabricante._fields:
                continue
            margen = fabricante[margen_field]

            if 'x_studio_costo_promedio' not in record._fields:
                continue
            costo_promedio = record['x_studio_costo_promedio']

            record.margen_cliente = margen
            record.costo_cliente = costo_promedio / (1 - margen / 100) if margen != 100 else 0.0
