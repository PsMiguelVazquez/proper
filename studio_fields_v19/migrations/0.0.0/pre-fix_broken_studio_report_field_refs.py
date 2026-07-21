# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_studio_report_field_refs` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', 'o.x_num_pro'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch.replace('o.x_num_pro', 'o.partner_id.x_num_pro')
        if new_arch != arch:
            view.write({'arch_db': new_arch})
