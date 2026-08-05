# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_customer_invoice_menu_action` en
`__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo para
el detalle de por qué hace falta un `write()` por código en vez de un
`<record>` en un XML de datos (el menú ya tiene `noupdate=True`, puesto
por Studio).
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('account.menu_action_move_out_invoice_type', raise_if_not_found=False)
    action = env.ref('account.action_move_out_invoice', raise_if_not_found=False)
    if not (menu and action):
        return
    action_ref = 'ir.actions.act_window,%d' % action.id
    if menu.action != action_ref:
        menu.write({'action': action_ref})
