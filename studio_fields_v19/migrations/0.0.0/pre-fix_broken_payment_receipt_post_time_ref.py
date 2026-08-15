# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_payment_receipt_post_time_ref` en
`__init__.py` (llamada desde `pre_init_hook`/el self-heal de
`_register_hook`), pero para el caso de actualización. Ver el comentario en
`__init__.py` para el detalle -en particular, por qué esto se limita a dos
xmlids exactos en vez de buscar por contenido en todas las vistas qweb.
"""
import re

from odoo import api, SUPERUSER_ID

_PAYMENT_RECEIPT_MOVE_FIELD_RE = re.compile(
    r'\bo\.(serie|folio|l10n_mx_edi_usage|l10n_mx_edi_post_time'
    r'|l10n_mx_edi_cfdi_supplier_rfc|l10n_mx_edi_cfdi_customer_rfc)\b'
)

PAYMENT_RECEIPT_STUDIO_VIEW_XMLIDS = [
    'studio_customization.report_payment_recei_ddb786bf-f51e-484e-b163-2aa45af1a8c8',
    'studio_customization.odoo_studio_report_p_74cc6f4f-6ec6-4230-aaa5-d5c47e377cf4',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in PAYMENT_RECEIPT_STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if not view or view.type != 'qweb' or not view.arch_db:
            continue
        arch = view.arch_db
        new_arch = _PAYMENT_RECEIPT_MOVE_FIELD_RE.sub(r'o.move_id.\1', arch)
        new_arch = new_arch.replace('.Complemento.xpath(', '.xpath(')
        if new_arch != arch:
            view.write({'arch_db': new_arch})
