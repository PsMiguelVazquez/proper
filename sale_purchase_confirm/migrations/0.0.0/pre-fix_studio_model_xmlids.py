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
        # MIGRACIÓN V19: ver la nota en `pre_init_hook` (`__init__.py`) -
        # crear el xmlid del modelo no basta, también hay que sacar el
        # modelo y sus campos del estado 'manual' para que ningún rebuild
        # posterior del registro (durante la carga del resto de módulos)
        # los vuelva a tratar como dinámicos y termine borrando filas de
        # `ir_model_fields` ya declaradas en código.
        cr.execute(
            "UPDATE ir_model SET state = 'base' WHERE id = %s AND state = 'manual'",
            (model.id,),
        )
        cr.execute(
            "UPDATE ir_model_fields SET state = 'base' "
            "WHERE model = %s AND state = 'manual'",
            (model_name,),
        )
