# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    sales_agent = fields.Many2one('res.users', string='Agente de ventas', store=True)
    codigo_uso_cfdi = fields.Char(string="Código Uso CFDi", compute='_compute_codigo_uso_cfdi', store=False)


    def _compute_codigo_uso_cfdi(self):
        for record in self:
            if record.x_studio_uso_de_cfdi:
                record.codigo_uso_cfdi = str(record.x_studio_uso_de_cfdi)
            else:
                record.codigo_uso_cfdi = ''

    @api.onchange('sales_agent')
    def _on_change_sales_agent(self):
        for record in self:
            self.x_nombre_agente_venta = record.sales_agent.name


    @api.onchange('x_nivel_cliente')
    def _compute_change_level(self):
        for record in self:
            partner = record.commercial_partner_id
            if record.x_nivel_cliente:
                message = "Se configuró el nivel de cliente " + record.x_nivel_cliente.x_name  +' para el usuario '+ record.name
                partner[0].message_post(body=message, type="notification")