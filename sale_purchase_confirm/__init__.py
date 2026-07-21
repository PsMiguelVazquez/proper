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
    # MIGRACIÓN V19: mismo problema, modelos formalizados en
    # `custom_models.py` que hasta ahora nunca se habían declarado en esta
    # lista (fallaban con "No matching record found for external id
    # 'model_x_...'" al procesar `security/ir.model.access.csv`).
    'x_caracteristica_1', 'x_color', 'x_sublinea', 'x_modelo_del_producto',
    'x_numero_de_serie_arti', 'x_numero_de_serie_moto', 'x_marca',
    'x_largo', 'x_marca_del_producto', 'x_estado_del_producto',
    'x_conceptos_de_baja', 'x_conceptos_basicos_de', 'x_segmento',
    'x_wizard_partner', 'x_temporadas',
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
        # MIGRACIÓN V19: crear el xmlid del modelo no basta. Mientras
        # `ir_model.state`/`ir_model_fields.state` sigan en 'manual', un
        # rebuild posterior del registro (disparado por CUALQUIER otro
        # módulo que se cargue después) puede volver a tratar el modelo
        # como dinámico/manual, y `_process_end()` termina borrando las
        # filas de `ir_model_fields` de los campos ya declarados en código
        # -rompiendo cualquier `related=` de otro módulo que apunte a ellos
        # (ej. `crm_lead.x_studio_descripcin_de_segmento` -> `x_segmento.
        # x_descripcion` en `studio_fields_v19`)-, en un loop de crash que
        # se repite en cada intento. Forzamos el estado a 'base' a mano.
        env.cr.execute(
            "UPDATE ir_model SET state = 'base' WHERE id = %s AND state = 'manual'",
            (model.id,),
        )
        env.cr.execute(
            "UPDATE ir_model_fields SET state = 'base' "
            "WHERE model = %s AND state = 'manual'",
            (model_name,),
        )
