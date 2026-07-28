# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_studio_sale_order_tree_columns_scope` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

STUDIO_SALE_ORDER_TREE_COLUMNS_XMLID = 'studio_customization.odoo_studio_sale_ord_f72ed18a-41b5-433e-a8f1-73221ffd3c98'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref(STUDIO_SALE_ORDER_TREE_COLUMNS_XMLID, raise_if_not_found=False)
    order_tree = env.ref('sale.view_order_tree', raise_if_not_found=False)
    if not view or not order_tree:
        return
    if view.inherit_id.id != order_tree.id:
        view.write({'inherit_id': order_tree.id})
