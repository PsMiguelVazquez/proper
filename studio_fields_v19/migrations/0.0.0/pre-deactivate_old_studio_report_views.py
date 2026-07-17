# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `pre_init_hook` en `__init__.py`, pero para el
caso de actualización (`-u`) en vez de instalación limpia -este módulo ya
estaba instalado antes de agregar este fix, así que `pre_init_hook` (que
sólo corre en instalación limpia) nunca se ejecutaría en el próximo
deploy-. Ver la nota en `res_partner_fields/migrations/0.0.0/pre-fix_studio_model_xmlids.py`
para el detalle de por qué `pre_init_hook` no alcanza, y `__init__.py` de
este módulo para el detalle de qué hace esta función (duplicada aquí en
vez de importada: los scripts de migración no se cargan como parte normal
del paquete del módulo, un `from .. import` falla con ImportError).
"""
from odoo import api, SUPERUSER_ID

OLD_STUDIO_VIEW_XMLIDS = [
    'studio_customization.report_saleorder_doc_67c4399c-f382-4d8e-932e-e820104b7fd',
    'studio_customization.odoo_studio_report_s_07964ef2-b734-4ddc-8a9a-88137e048216',
    'studio_customization.document_tax_totals_32e1fed0-21e9-4ea0-8b41-ceb2b094f137',
    'studio_customization.report_saleorder_pro_be1a584c-a8ce-4ab7-944a-7283f77025c0',
    'studio_customization.report_saleorder_pro_19c7eaa3-bc03-42de-9f78-0863b2efaea8',
]

OWN_VIEW_KEYS = [
    'sale.report_saleorder_document_copy_3',
    'sale.report_saleorder_document_copy_3_copy_1',
    'account.document_tax_totals_copy_1',
    'account.document_tax_totals_copy_1_copy_1',
    'sale.report_saleorder_pro_forma_copy_1',
    'sale.report_saleorder_pro_forma_copy_1_copy_1',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrUiView = env['ir.ui.view']
    to_deactivate = env['ir.ui.view']

    for xmlid in OLD_STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view:
            to_deactivate |= view

    own_views = IrUiView.with_context(active_test=False).search([
        ('key', 'in', OWN_VIEW_KEYS),
        ('id', 'not in', to_deactivate.ids or [0]),
    ])
    for view in own_views:
        if not (view.get_external_id().get(view.id, '') or '').startswith('studio_fields_v19.'):
            to_deactivate |= view

    if to_deactivate:
        to_deactivate.write({'active': False})
