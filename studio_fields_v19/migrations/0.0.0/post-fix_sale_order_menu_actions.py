# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_sale_order_menu_actions` en
`__init__.py` (llamada desde `post_init_hook`), pero para el caso de
actualización (`-u`) en vez de instalación limpia. Va como migración
`post-` (no `pre-`) a propósito: depende de que las acciones
`studio_fields_v19.sale_order_action_*` ya existan, y esas las crea este
mismo módulo vía `data/` -las migraciones `pre-` corren antes de que Odoo
cargue los `data` del módulo, así que en ese momento `env.ref(...)`
todavía no las encuentra-. Ver `__init__.py` de este módulo para el
detalle completo.
"""
from odoo import api, SUPERUSER_ID

SALE_ORDER_MENU_ACTIONS = {
    'studio_customization.contabilidad_cotizac_b7903b48-2807-4d8d-8bf6-1949a1d8fc97':
        'studio_fields_v19.sale_order_action_cotizaciones',
    'studio_customization.contabilidad_pedidos_5882ae4a-d4c7-490e-b8c2-0ac2e90862e1':
        'studio_fields_v19.sale_order_action_pedidos',
    'studio_customization.contabilidad_marketp_5f4c41a1-055a-4c7c-8479-64c1082dd7bb':
        'studio_fields_v19.sale_order_action_marketplace',
}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for menu_xmlid, action_xmlid in SALE_ORDER_MENU_ACTIONS.items():
        menu = env.ref(menu_xmlid, raise_if_not_found=False)
        action = env.ref(action_xmlid, raise_if_not_found=False)
        if not (menu and action):
            continue
        action_ref = 'ir.actions.act_window,%d' % action.id
        # Ver el comentario en `_fix_sale_order_menu_actions`
        # (`__init__.py`) sobre por qué se compara recordset contra
        # recordset en vez de contra el string `action_ref`.
        current_action = menu.action
        if not (current_action and current_action._name == action._name and current_action.id == action.id):
            menu.write({'action': action_ref})
        if not menu.active:
            menu.write({'active': True})
