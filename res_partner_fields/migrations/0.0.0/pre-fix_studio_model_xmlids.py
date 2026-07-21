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

IMPORTANTE (encontrado al probar esto localmente, simulando el estado real
de producción): arreglar sólo el xmlid NO basta. Cuando estos modelos siguen
en `ir_model.state='manual'` (heredado de Studio) al momento de esta
actualización, Odoo los vuelve a registrar como modelos "manuales"
dinámicos (`_add_manual_models`, disparado por el `_setup_models__`
incremental que Odoo ya corrió ANTES de este script, al empezar a procesar
este módulo). Esa doble-registración dinámica deja "contaminado" el
`_module` del modelo para el resto de esta pasada, y cuando después se
reconcilian los campos (`_reflect_fields`), Odoo concluye que los campos
`x_razon_social`/`x_contacto`/etc. ya no pertenecen a ningún módulo y los
BORRA -- lo que además elimina la columna real de la tabla (pérdida de
datos), sin lanzar ningún error visible. Reproducido y confirmado en local.

El arreglo: además de crear el xmlid, esta migración voltea
`ir_model.state`/`ir_model_fields.state` a 'base' por SQL directo (sin pasar
por el ORM, que ya corrió tarde) y fuerza un `_setup_models__` adicional
ANTES de que este módulo cargue sus propias clases de Python. Con el estado
ya corregido en la base de datos, esa llamada extra limpia el registro
dinámico contaminado sin volver a crearlo, y cuando más adelante Odoo carga
las clases reales (`XRefComercial`, etc.), las registra limpias, como
modelos de código nuevos, sin arrastrar el `_module`/`_custom` erróneo.
"""
from odoo import api, SUPERUSER_ID

# Ver comentario en `__init__.py` (mismo fix, misma lista de modelos).
CUSTOM_MODELS = [
    'x_categoria_compania', 'x_niveles_de_cliente', 'x_grupo_cliente',
    'x_agente_de_venta', 'x_ref_banco', 'x_subcategia_compania',
    'x_clave_p', 'x_grupo_proveedor', 'x_ref_comercial',
]


def migrate(cr, version):
    cr.execute(
        "UPDATE ir_model SET state = 'base' WHERE model = ANY(%s) AND state = 'manual'",
        (CUSTOM_MODELS,),
    )
    cr.execute(
        "UPDATE ir_model_fields SET state = 'base' WHERE model = ANY(%s) AND state = 'manual'",
        (CUSTOM_MODELS,),
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    # Descarta cualquier registro dinámico "manual" ya contaminado para
    # estos modelos, ahora que la base de datos dice 'base' y no se van a
    # volver a crear como manuales.
    env.registry._setup_models__(cr, [])

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
