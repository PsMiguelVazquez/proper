# -*- coding: utf-8 -*-

from odoo import models, fields, api
class ChangeClientWizard(models.TransientModel):
    _name = 'change.client.wizard'
    _description = 'Cambia el cliente del reporte'
    client_id= fields.Many2one('res.partner', 'Cliente')

    def change_report_client(self):
        report_lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        self.env['change.client.wizard'].browse(self._context.get('active_ids'))
        # for line in report_lines:
        #     line.client_id = self.client_id
        return True
        # report_lines = self.env['stock.quant'].browse(self._context.get('active_ids'))
        # nivel_cliente = self.client_id.x_nivel_cliente.x_name
        # nombre_cliente = self.client_id.name
        # for line in report_lines:
        #     # margen = line.product_id.x_fabricante['x_studio_margen_'+nivel_cliente] if nivel_cliente else 0
        #     line.margen_cliente = margen
        #     # line.costo_cliente = line.x_studio_costo_promedio/(1 - margen/100)
        #     # line.costo_cliente = line.x_studio_costo_promedio*(1 + margen/100)
        #     line.cliente_reporte = nombre_cliente


