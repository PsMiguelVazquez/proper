# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_studio_volumen_c_m = fields.Float(
        string='Volumen c-m', compute='_compute_x_studio_volumen_c_m', store=True)
    x_vol = fields.Float(
        string='Volumen', compute='_compute_x_vol', store=True)

    @api.depends('x_studio_alto_c_m', 'x_studio_ancho_c_m', 'x_studio_largo_c_m')
    def _compute_x_studio_volumen_c_m(self):
        for record in self:
            record.x_studio_volumen_c_m = (
                record.x_studio_alto_c_m * record.x_studio_ancho_c_m * record.x_studio_largo_c_m)

    @api.depends('x_Al', 'x_An', 'x_La')
    def _compute_x_vol(self):
        for record in self:
            record.x_vol = record.x_Al * record.x_An * record.x_La
