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
_STOCK_PICKING_QTY_DONE_RE = re.compile(r'\b(?:qty_done|quantity_done)\b')
_STOCK_PICKING_MOVE_LINE_WITHOUT_PACKAGE_RE = re.compile(r'\bmove_line_ids_without_package\b')
_STOCK_PICKING_L10N_MX_EDI_STATUS_RE = re.compile(r'\bl10n_mx_edi_status\b')
_STOCK_PICKING_TRANSPORT_PERM_SCT_RE = re.compile(r'\btransport_perm_sct\b')


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|', '|', '|', '|', '|',
        ('arch_db', 'like', 'move_lines'),
        ('arch_db', 'like', 'move_ids_without_package'),
        ('arch_db', 'like', 'qty_done'),
        ('arch_db', 'like', 'quantity_done'),
        ('arch_db', 'like', 'l10n_mx_edi_status'),
        ('arch_db', 'like', 'transport_perm_sct'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _STOCK_PICKING_MOVE_LINE_WITHOUT_PACKAGE_RE.sub('move_line_ids', arch)
        new_arch = _STOCK_PICKING_MOVE_LINES_RE.sub('move_ids', new_arch)
        new_arch = _STOCK_PICKING_MOVE_WITHOUT_PACKAGE_RE.sub('move_ids', new_arch)
        new_arch = _STOCK_PICKING_QTY_DONE_RE.sub('quantity', new_arch)
        new_arch = _STOCK_PICKING_L10N_MX_EDI_STATUS_RE.sub('l10n_mx_edi_cfdi_state', new_arch)
        new_arch = _STOCK_PICKING_TRANSPORT_PERM_SCT_RE.sub('l10n_mx_transport_perm_sct', new_arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})
