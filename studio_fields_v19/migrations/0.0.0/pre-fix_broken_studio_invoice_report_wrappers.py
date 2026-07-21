# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_studio_invoice_report_wrappers` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
import re

from odoo import api, SUPERUSER_ID

_L10N_MX_EDI_INVOICE_REPORT_NAME_RE = re.compile(
    r"_get_name_invoice_report\(\) == 'account\.report_invoice_document'"
)
_CORE_INVOICE_REPORT_KEYS = {'account.report_invoice', 'account.report_invoice_with_payments'}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        ('arch_db', 'like', "_get_name_invoice_report() == 'account.report_invoice_document'"),
    ])
    for view in views:
        if view.key in _CORE_INVOICE_REPORT_KEYS:
            continue
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _L10N_MX_EDI_INVOICE_REPORT_NAME_RE.sub(
            "_get_name_invoice_report() in ('account.report_invoice_document', 'l10n_mx_edi.report_invoice_document')",
            arch,
        )
        if new_arch != arch:
            view.write({'arch_db': new_arch})
