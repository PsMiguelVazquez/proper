# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_deactivate_old_pedido_mkp_menu` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
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
