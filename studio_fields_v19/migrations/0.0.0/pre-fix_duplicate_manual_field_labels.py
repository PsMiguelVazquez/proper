# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_duplicate_manual_field_labels` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

_DUPLICATE_LABEL_FIELDS = [
    ('sale.order', 'x_productos_si', 'Productos (sí)'),
    ('sale.order', 'x_productos_no', 'Productos (no)'),
    ('stock.picking', 'x_studio_otros_documentos_1', 'Otros Documentos (2)'),
    ('x_wizard_proposal', 'x_proveedor_char', 'Nombre del proveedor'),
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrModelFields = env['ir.model.fields']
    for model, name, label in _DUPLICATE_LABEL_FIELDS:
        field = IrModelFields.search([
            ('model', '=', model), ('name', '=', name), ('state', '=', 'manual'),
        ], limit=1)
        if field and field.field_description != label:
            field.write({'field_description': label})
