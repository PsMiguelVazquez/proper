# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_invoice_report_display_type` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', 'not line.display_type'),
        ('arch_db', 'like', 'invoice_line_ids'),
    ])
    for view in views:
        if view.key == 'account.report_invoice_document':
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace('not line.display_type', "line.display_type == 'product'")
        if new_arch != arch:
            view.write({'arch_db': new_arch})
