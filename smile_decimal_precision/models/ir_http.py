# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# MIGRACIÓN V19: este override ya estaba deshabilitado en el módulo original
# (no se importaba desde models/__init__.py) porque referenciaba
# `res.currency.display_decimal_places`, un campo que nunca llegó a
# implementarse (ver res_currency.py, donde quedó comentado). Además, en
# 19.0 `ir.http.get_currencies()` está deprecado en favor de
# `res.currency.get_all_currencies()`. Se conserva el archivo sin importar,
# tal como estaba en producción en 15.0, para no reintroducir código roto.

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def get_currencies(self):
        res = super().get_currencies()
        currency_ids = list(res.keys())
        for currency in self.env['res.currency'].browse(currency_ids):
            res[currency.id]['digits'][1] = currency.display_decimal_places
        return res
