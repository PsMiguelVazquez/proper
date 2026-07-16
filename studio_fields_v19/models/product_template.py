# -*- coding: utf-8 -*-
from odoo import models, fields

from .common import studio_get


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_studio_volumen_c_m = fields.Float(
        string='Volumen c-m', compute='_compute_x_studio_volumen_c_m', store=True)
    x_vol = fields.Float(
        string='Volumen', compute='_compute_x_vol', store=True)

    # MIGRACIÓN V19: sin `@api.depends` a propósito, ver `common.py`
    # (`x_studio_alto_c_m`/`x_studio_ancho_c_m`/`x_studio_largo_c_m` no
    # existen en todas las bases).
    def _compute_x_studio_volumen_c_m(self):
        for record in self:
            record.x_studio_volumen_c_m = (
                studio_get(record, 'x_studio_alto_c_m') * studio_get(record, 'x_studio_ancho_c_m')
                * studio_get(record, 'x_studio_largo_c_m'))

    # MIGRACIÓN V19: sin `@api.depends` a propósito, ver `common.py`
    # (`x_Al`/`x_An`/`x_La` no existen en todas las bases).
    def _compute_x_vol(self):
        for record in self:
            record.x_vol = studio_get(record, 'x_Al') * studio_get(record, 'x_An') * studio_get(record, 'x_La')
