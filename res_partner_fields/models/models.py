# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    sales_agent = fields.Many2one('res.users', string='Agente de ventas', store=True)

    @api.onchange('sales_agent')
    def _on_change_sales_agent(self):
        for record in self:
            self.x_nombre_agente_venta = record.sales_agent.name
