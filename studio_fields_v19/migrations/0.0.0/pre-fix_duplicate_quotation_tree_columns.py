# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_duplicate_quotation_tree_columns` en
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
    changed = False
    for xpath_node in root.findall(".//xpath[@expr=\"//list[1]/field[@name='name']\"]"):
        field = xpath_node.find("field[@name='x_studio_n_orden_de_compra']")
        if field is not None and len(xpath_node) == 1:
            root.remove(xpath_node)
            changed = True
    for field in root.findall(".//field[@name='x_estado_compra']"):
        parent = field.getparent()
        if parent is not None:
            parent.remove(field)
            changed = True
    if changed:
        view.write({'arch_db': etree.tostring(root, encoding='unicode')})
