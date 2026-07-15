# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# MIGRACIÓN V19: este módulo ya estaba deshabilitado en 15.0 (el paquete
# `report` no se importaba desde el __init__.py raíz). Su lógica -forzar el
# `precision` de un campo Float en QWeb a partir de los `digits` propios del
# campo- fue absorbida por el core: `ir.qweb.field.float.record_to_html()`
# en 19.0 ya calcula `precision` desde `field.get_digits(record.env)` cuando
# no se pasa explícitamente en las opciones. Además, `FloatConverter` ya no
# existe como clase Python importable: los conversores QWeb ahora son
# AbstractModels (`ir.qweb.field.float`), por lo que este monkeypatch no
# sería ni siquiera cargable tal cual. Se conserva sin importar, solo como
# referencia histórica.

from odoo import api, models


class IrQwebFieldFloat(models.AbstractModel):
    _inherit = 'ir.qweb.field.float'

    @api.model
    def record_to_html(self, record, field_name, options):
        if 'precision' not in options and 'decimal_precision' not in options:
            _, precision = record._fields[field_name].get_digits(self.env) or (None, None)
            options = dict(options, precision=precision)
        return super().record_to_html(record, field_name, options)
