# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_partner_id_account_move_count = fields.Integer(
        string='Partner count', compute='_compute_x_partner_id_account_move_count')
    x_x_holding__res_partner_count = fields.Integer(
        string='Empresa count', compute='_compute_x_x_holding__res_partner_count')

    def _compute_x_partner_id_account_move_count(self):
        for record in self:
            record.x_partner_id_account_move_count = self.env['account.move'].search_count(
                [('partner_id', '=', record.id)])

    def _compute_x_x_holding__res_partner_count(self):
        # MIGRACIÓN V19: el original usaba `read_group` con la firma antigua
        # (diccionarios con clave `<campo>_count`); se reescribe con
        # `search_count`, más simple y compatible. `x_holding` es un campo
        # de Odoo Studio que puede no existir en todas las bases (ver
        # `common.py`); si no existe, el conteo queda en 0.
        if 'x_holding' not in self._fields:
            self.x_x_holding__res_partner_count = 0
            return
        for record in self:
            record.x_x_holding__res_partner_count = self.env['res.partner'].search_count(
                [('x_holding', '=', record.id)])
