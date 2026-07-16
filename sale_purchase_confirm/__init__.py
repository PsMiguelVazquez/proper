# -*- coding: utf-8 -*-

from . import models
from . import controller
from . import extensions

# MIGRACIÓN V19: `x_fabricante`, `x_familia`, `x_linea`, `x_grupo`,
# `x_client_requirement` y `x_proposal_purchase` eran modelos creados por
# Odoo Studio (`ir.model` con `state='manual'`), sin módulo dueño. Al
# formalizarlos aquí como modelos de código con el mismo `_name`, si el
# modelo ya existía en la base de datos (viene de Studio) Odoo no crea el
# xmlid `sale_purchase_confirm.model_x_...` que usa
# `security/ir.model.access.csv`, y la instalación falla con "No matching
# record found for external id 'model_x_...'" (mismo problema que se
# encontró y corrigió en `res_partner_fields`). Este hook crea ese
# `ir.model.data` a mano antes de que se procesen los modelos del módulo.
CUSTOM_MODELS = [
    'x_fabricante', 'x_familia', 'x_linea', 'x_grupo',
    'x_client_requirement', 'x_proposal_purchase',
]


def pre_init_hook(env):
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
