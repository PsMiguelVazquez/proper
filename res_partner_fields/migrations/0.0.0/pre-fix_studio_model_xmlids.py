# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `pre_init_hook` en `__init__.py`, pero para el
caso de actualización (`-u`) en vez de instalación limpia. `pre_init_hook`
sólo se ejecuta cuando el módulo se instala por primera vez
(`update_operation == 'install'`); si el módulo ya quedó registrado como
instalado en una base (aunque la instalación haya fallado a medio camino),
los despliegues siguientes pasan por la ruta de actualización, donde
`pre_init_hook` nunca se llama. Los scripts de migración en
`migrations/0.0.0/pre-*.py` sí corren en cada actualización cuya versión de
módulo suba, así que aquí se repite la misma reparación de xmlid.
"""
from odoo import api, SUPERUSER_ID

CUSTOM_MODELS = ['x_categoria_compania', 'x_niveles_de_cliente', 'x_grupo_cliente']


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
            ('module', '=', 'res_partner_fields'), ('name', '=', xml_id),
        ], limit=1)
        if not exists:
            IrModelData.create({
                'module': 'res_partner_fields',
                'name': xml_id,
                'model': 'ir.model',
                'res_id': model.id,
                'noupdate': True,
            })
