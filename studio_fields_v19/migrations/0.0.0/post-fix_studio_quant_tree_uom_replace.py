# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_studio_quant_tree_uom_replace` en
`__init__.py` (llamada desde `post_init_hook`), pero para el caso de
actualización. Va como migración `post-` (no `pre-`) a propósito: al
reescribir el arch, Odoo valida la vista, y casi todos sus campos
(`x_studio_producto`, `x_studio_precio_de_venta`, ...) los define este
mismo módulo en `models/stock.py`; en una migración `pre-` todavía no
están cargados y la validación hacía fallar la actualización. Ver
`__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

_QUANT_UOM_REPLACE_XPATH = '<xpath expr="//field[@name=\'product_uom_id\']" position="replace">'
_QUANT_UOM_HIDE_AND_AFTER_XPATH = (
    '<xpath expr="//field[@name=\'product_uom_id\']" position="attributes">'
    '<attribute name="column_invisible">1</attribute>'
    '</xpath>'
    '<xpath expr="//field[@name=\'product_uom_id\']" position="after">'
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    parent = env.ref('stock.view_stock_quant_tree', raise_if_not_found=False)
    if not parent:
        return
    views = env['ir.ui.view'].search([
        ('model', '=', 'stock.quant'),
        ('inherit_id', '=', parent.id),
        ('arch_db', 'like', 'product_uom_id'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch or _QUANT_UOM_REPLACE_XPATH not in arch:
            continue
        view.write({'arch_db': arch.replace(_QUANT_UOM_REPLACE_XPATH, _QUANT_UOM_HIDE_AND_AFTER_XPATH)})
