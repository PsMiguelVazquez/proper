# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_studio_quotation_tree_columns_anchor` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from lxml import etree

from odoo import api, SUPERUSER_ID

DUPLICATE_QUOTATION_TREE_VIEW_XMLID = 'studio_customization.odoo_studio_sale_ord_5540e2f3-8cc7-4a6b-800a-7db9408fe51d'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref(DUPLICATE_QUOTATION_TREE_VIEW_XMLID, raise_if_not_found=False)
    if not view or not view.arch_db:
        return
    try:
        root = etree.fromstring(view.arch_db.encode())
    except etree.XMLSyntaxError:
        return
    xpath_node = root.find(".//xpath[@expr=\"//field[@name='currency_id']\"]")
    if xpath_node is None:
        return
    xpath_node.set('expr', "//field[@name='invoice_status']")
    view.write({'arch_db': etree.tostring(root, encoding='unicode')})
