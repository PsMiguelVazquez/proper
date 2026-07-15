# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: campos de Odoo Studio en `product.template`/`product.product`
formalizados como código real (ver nota en `custom_models.py`).
"""

from odoo import models, fields, api


class ProductTemplateStudio(models.Model):
    _inherit = 'product.template'

    x_fabricante = fields.Many2one('x_fabricante', string='Marca')
    x_studio_ultimo_costo = fields.Monetary(string='Ultimo Costo', compute='_compute_x_studio_ultimo_costo', store=True)
    x_producto_propuesta = fields.Boolean(string='Por configurar')
    x_notas_propuestas = fields.Text(string='Notas de la propuesta')
    x_studio_many2one_field_0X3u9 = fields.Many2one('x_grupo', string='Grupo')
    x_studio_many2one_field_RWuq7 = fields.Many2one('x_familia', string='Familia')
    x_studio_many2one_field_LZOP8 = fields.Many2one('x_linea', string='Línea')

    # MIGRACIÓN V19: `stock.valuation.layer` (usado por la fórmula original de
    # Studio) fue reemplazado en este branch de 19.0 por `stock.move.value`/
    # `is_in` (ver `stock_account/models/stock_move.py`); no existe ya un
    # registro "capa de valoración" independiente con `unit_cost`. Se
    # recalcula el costo unitario de la última entrada valorada como
    # `value / quantity` del último `stock.move` de entrada (`is_in`) con
    # cantidad positiva.
    @api.depends('standard_price')
    def _compute_x_studio_ultimo_costo(self):
        for record in self:
            move = self.env['stock.move'].search(
                [('product_id', '=', record.product_variant_id.id), ('is_in', '=', True), ('quantity', '>', 0)],
                order='id desc', limit=1,
            )
            record.x_studio_ultimo_costo = (move.value / move.quantity) if move and move.quantity else 0.0


class ProductProductStudio(models.Model):
    _inherit = 'product.product'

    x_num_pro = fields.Char(string='Num Pro')
