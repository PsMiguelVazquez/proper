# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_stock_picking_reports` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
import re

from odoo import api, SUPERUSER_ID

_STOCK_PICKING_MOVE_LINES_RE = re.compile(r'\bmove_lines\b')
_STOCK_PICKING_MOVE_WITHOUT_PACKAGE_RE = re.compile(r'\bmove_ids_without_package\b')


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|',
        ('arch_db', 'like', 'move_lines'),
        ('arch_db', 'like', 'move_ids_without_package'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _STOCK_PICKING_MOVE_LINES_RE.sub('move_ids', arch)
        new_arch = _STOCK_PICKING_MOVE_WITHOUT_PACKAGE_RE.sub('move_ids', new_arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})
