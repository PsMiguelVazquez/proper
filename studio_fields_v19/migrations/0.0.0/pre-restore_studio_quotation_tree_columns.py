# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_restore_studio_quotation_tree_columns` en
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

    if root.find(".//xpath[@expr=\"//list[1]/field[@name='name']\"]") is None:
        xpath_node = etree.Element('xpath')
        xpath_node.set('expr', "//list[1]/field[@name='name']")
        xpath_node.set('position', 'after')
        field = etree.SubElement(xpath_node, 'field')
        field.set('name', 'x_studio_n_orden_de_compra')
        field.set('optional', 'show')
        root.insert(0, xpath_node)
        changed = True

    if root.find(".//field[@name='x_estado_compra']") is None:
        currency_xpath = root.find(".//xpath[@expr=\"//field[@name='currency_id']\"]")
        if currency_xpath is not None:
            field = etree.Element('field')
            field.set('name', 'x_estado_compra')
            comentarios = currency_xpath.find("field[@name='x_studio_comentarios']")
            if comentarios is not None:
                comentarios.addnext(field)
            else:
                currency_xpath.append(field)
            changed = True

    if changed:
        view.write({'arch_db': etree.tostring(root, encoding='unicode')})
