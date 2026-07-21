# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_l10n_mx_edi_reports` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización (`-u`) en vez de instalación limpia -este módulo ya estaba
instalado antes de agregar este fix, así que `pre_init_hook` nunca correría
en el próximo deploy-. Ver el comentario en `__init__.py` para el detalle de
qué reemplaza cada patrón y por qué (duplicado aquí en vez de importado: los
scripts de migración no se cargan como parte normal del paquete del módulo,
un `from .. import` falla con ImportError).
"""
import re

from odoo import api, SUPERUSER_ID

_L10N_MX_EDI_DECODE_CFDI_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_.]*)\._l10n_mx_edi_decode_cfdi\(\)')
_L10N_MX_EDI_SIGNED_DOC_RE = re.compile(r'bool\(([a-zA-Z_][a-zA-Z0-9_.]*)\._get_l10n_mx_edi_signed_edi_document\(\)\)')
_L10N_MX_EDI_CFDI_REQUEST_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_.]*\.l10n_mx_edi_cfdi_request\s*(?:in\s*\([^)]*\)|==\s*'[^']*')")


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([
        ('type', '=', 'qweb'),
        '|', '|',
        ('arch_db', 'like', '_l10n_mx_edi_decode_cfdi'),
        ('arch_db', 'like', '_get_l10n_mx_edi_signed_edi_document'),
        ('arch_db', 'like', 'l10n_mx_edi_origin'),
    ])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = _L10N_MX_EDI_DECODE_CFDI_RE.sub(
            lambda m: (
                f"{m.group(1)}.env['l10n_mx_edi.document']._decode_cfdi_attachment("
                f"{m.group(1)}.l10n_mx_edi_cfdi_attachment_id.raw)"
            ),
            arch,
        )
        new_arch = _L10N_MX_EDI_SIGNED_DOC_RE.sub(
            lambda m: f"({m.group(1)}.l10n_mx_edi_cfdi_state in ('sent', 'global_sent'))",
            new_arch,
        )
        new_arch = _L10N_MX_EDI_CFDI_REQUEST_RE.sub('True', new_arch)
        new_arch = new_arch.replace('l10n_mx_edi_origin', 'l10n_mx_edi_cfdi_origin')
        if new_arch != arch:
            view.write({'arch_db': new_arch})
