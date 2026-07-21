# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_tax_totals_json` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle.
"""
import re

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrUiView = env['ir.ui.view']
    views = IrUiView.search([('arch_db', 'like', 'tax_totals_json')])
    external_ids = views.get_external_id()
    for view in views:
        xmlid = external_ids.get(view.id) or ''
        owner_module = xmlid.split('.')[0] if '.' in xmlid else ''
        if owner_module and owner_module != 'studio_customization':
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = re.sub(r'json\.loads\(([a-zA-Z_][a-zA-Z0-9_.]*)\.tax_totals_json\)', r'\1.tax_totals', arch)
        new_arch = new_arch.replace('tax_totals_json', 'tax_totals')
        if new_arch != arch:
            view.write({'arch_db': new_arch})
