# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_banner_route` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle -incluyendo por qué se quita
sólo la etiqueta `<attribute name="banner_route">` en vez de todo el
bloque `<xpath expr="//tree" ...>`-.
"""
import re

from odoo import api, SUPERUSER_ID

_BANNER_ROUTE_ATTR_RE = re.compile(
    r'<attribute name="banner_route">[^<]*</attribute>\s*'
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([('arch_db', 'like', 'banner_route')])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _BANNER_ROUTE_ATTR_RE.sub('', arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})
