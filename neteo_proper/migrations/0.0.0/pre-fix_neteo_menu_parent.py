# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_neteo_menu_parent` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu = env.ref('neteo_proper.neteo_menu', raise_if_not_found=False)
    parent = env.ref('account.menu_finance_receivables', raise_if_not_found=False)
    if menu and parent and menu.parent_id != parent:
        menu.write({'parent_id': parent.id})
