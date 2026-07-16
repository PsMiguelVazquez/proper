# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `pre_init_hook` en `__init__.py`, pero para el
caso de actualización (`-u`) en vez de instalación limpia. Ver la nota en
`res_partner_fields/migrations/0.0.0/pre-fix_studio_model_xmlids.py` para el
detalle de por qué `pre_init_hook` no alcanza.
"""
from odoo import api, SUPERUSER_ID

CUSTOM_MODELS = [
    'x_fabricante', 'x_familia', 'x_linea', 'x_grupo',
    'x_client_requirement', 'x_proposal_purchase',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrModel = env['ir.model']
    IrModelData = env['ir.model.data']
    for model_name in CUSTOM_MODELS:
        model = IrModel.search([('model', '=', model_name)], limit=1)
        if not model:
            continue
        xml_id = 'model_' + model_name
        exists = IrModelData.search([
            ('module', '=', 'sale_purchase_confirm'), ('name', '=', xml_id),
        ], limit=1)
        if not exists:
            IrModelData.create({
                'module': 'sale_purchase_confirm',
                'name': xml_id,
                'model': 'ir.model',
                'res_id': model.id,
                'noupdate': True,
            })
