# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_payment_receipt_post_time_ref` en
`__init__.py` (llamada desde `pre_init_hook`/el self-heal de
`_register_hook`), pero para el caso de actualización. Ver el comentario en
`__init__.py` para el detalle.
"""
import re

from odoo import api, SUPERUSER_ID

_PAYMENT_RECEIPT_MOVE_FIELD_RE = re.compile(r'\bo\.(serie|folio|l10n_mx_edi_usage|l10n_mx_edi_post_time)\b')


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|', '|', '|',
        ('arch_db', 'like', 'o.l10n_mx_edi_post_time'),
        ('arch_db', 'like', 'o.serie'),
        ('arch_db', 'like', 'o.folio'),
        ('arch_db', 'like', 'o.l10n_mx_edi_usage'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _PAYMENT_RECEIPT_MOVE_FIELD_RE.sub(r'o.move_id.\1', arch)
        if new_arch != arch:
            view.write({'arch_db': new_arch})
