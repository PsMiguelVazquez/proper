# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_quant_client(models.Model):
    _inherit = 'stock.quant'
    cliente_reporte = fields.Char(string='Cliente', compute="_compute_costo_cliente")
    costo_cliente = fields.Float(string='Costo por cliente',  compute="_compute_costo_cliente")
    margen_cliente = fields.Float(string='Margen del cliente', compute="_compute_costo_cliente")
    # client_id = fields.Many2one('res.partner', 'Cliente Id')

    @api.depends('margen_cliente', 'product_id')
    def _compute_costo_cliente(self):
        wizard_client_id = self.env['change.client.wizard'].search([],limit=1,order='id desc').client_id
        for record in self:
            nivel_cliente = wizard_client_id.x_nivel_cliente.x_name
            margen = record.product_id.x_fabricante['x_studio_margen_' + nivel_cliente] if nivel_cliente else 0
            record.costo_cliente = record.x_studio_costo_promedio / (1 - margen / 100)
            record.cliente_reporte = wizard_client_id.name
            record.margen_cliente = margen
