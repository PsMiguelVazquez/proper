from . import models

# MIGRACIÓN V19: `x_wizard_rechcoti` era un modelo creado con Odoo Studio
# (`ir.model` con `state='manual'`), sin módulo dueño. Al formalizarlo aquí
# como modelo de código, si el modelo ya existía en la base de datos Odoo
# no crea el xmlid `novu_sale_order.model_x_wizard_rechcoti` que usa
# `security/ir.model.access.csv`, y la instalación falla con "No matching
# record found for external id 'model_x_wizard_rechcoti'" (mismo problema
# encontrado y corregido en `res_partner_fields`/`sale_purchase_confirm`).
# Además de crear el xmlid, hay que sacar el modelo y sus campos del
# estado 'manual' a mano: si no, un rebuild posterior del registro puede
# volver a tratarlo como dinámico y borrar filas de `ir_model_fields` ya
# declaradas en código.
CUSTOM_MODELS = ['x_wizard_rechcoti']


def pre_init_hook(env):
    IrModel = env['ir.model']
    IrModelData = env['ir.model.data']
    for model_name in CUSTOM_MODELS:
        model = IrModel.search([('model', '=', model_name)], limit=1)
        if not model:
            continue
        xml_id = 'model_' + model_name
        exists = IrModelData.search([
            ('module', '=', 'novu_sale_order'), ('name', '=', xml_id),
        ], limit=1)
        if not exists:
            IrModelData.create({
                'module': 'novu_sale_order',
                'name': xml_id,
                'model': 'ir.model',
                'res_id': model.id,
                'noupdate': True,
            })
        env.cr.execute(
            "UPDATE ir_model SET state = 'base' WHERE id = %s AND state = 'manual'",
            (model.id,),
        )
        env.cr.execute(
            "UPDATE ir_model_fields SET state = 'base' "
            "WHERE model = %s AND state = 'manual'",
            (model_name,),
        )
    _deactivate_old_pedido_mkp_menu(env)


# MIGRACIÓN V19: "Pedido de MKP" era un menú/acción creado con Odoo Studio
# (módulo fantasma `studio_customization`, sin dueño real), ya reemplazado
# por el menú "Pedidos MKP V18" (`menu_pedidos_mkp`/`action_pedidos_mkp`,
# formalizados en `views/sale_order_action_mkp.xml`, ahora renombrado a
# "Pedido de MKP" también). Se desactiva el menú viejo para no tener dos
# entradas duplicadas; se identifica por el dominio de su acción -no por el
# nombre, porque después de este cambio ambos comparten el mismo nombre- y
# excluyendo explícitamente nuestra propia acción formalizada.
def _deactivate_old_pedido_mkp_menu(env):
    our_action = env.ref('novu_sale_order.action_pedidos_mkp', raise_if_not_found=False)
    old_actions = env['ir.actions.act_window'].search([
        ('res_model', '=', 'sale.order'),
        ('domain', 'like', 'x_studio_venta_mostrador'),
    ])
    if our_action:
        old_actions -= our_action
    if not old_actions:
        return
    menus = env['ir.ui.menu'].search([
        ('action', 'in', ['ir.actions.act_window,%d' % a.id for a in old_actions]),
    ])
    menus.write({'active': False})