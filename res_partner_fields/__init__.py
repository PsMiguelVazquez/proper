# -*- coding: utf-8 -*-

from . import models

# MIGRACIÓN V19: `x_categoria_compania`, `x_niveles_de_cliente` y
# `x_grupo_cliente` eran modelos creados por Odoo Studio (`ir.model` con
# `state='manual'`), sin módulo dueño. Al formalizarlos aquí como modelos de
# código con el mismo `_name`, Odoo debería re-registrar ese `ir.model` como
# `state='base'` perteneciente a este módulo -y con eso crear el xmlid
# `res_partner_fields.model_x_categoria_compania` que usa
# `security/ir.model.access.csv`-, pero en la práctica, cuando el modelo ya
# existe en la base de datos, ese xmlid termina sin crearse (el registro se
# actualiza pero queda sin `ir.model.data` propio) y la instalación falla
# con "No matching record found for external id 'model_x_categoria_compania'".
# Este hook crea ese `ir.model.data` a mano, antes de que se procesen los
# modelos del módulo, para que el CSV de accesos siempre lo encuentre, tanto
# si el modelo ya existía (viene de Studio) como si es la primera vez que se
# instala (no existe todavía; en ese caso no hay nada que hacer aquí, Odoo
# lo crea normalmente).
# `x_agente_de_venta`, `x_ref_banco`, `x_subcategia_compania`, `x_clave_p`,
# `x_grupo_proveedor` y `x_ref_comercial` son el mismo caso: también eran
# modelos de Studio ya existentes en la base antes de formalizarse aquí como
# código, así que necesitan el mismo arreglo.
CUSTOM_MODELS = [
    'x_categoria_compania', 'x_niveles_de_cliente', 'x_grupo_cliente',
    'x_agente_de_venta', 'x_ref_banco', 'x_subcategia_compania',
    'x_clave_p', 'x_grupo_proveedor', 'x_ref_comercial',
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
