# -*- coding: utf-8 -*-

from . import models
from . import wizard


def pre_init_hook(env):
    _fix_neteo_menu_parent(env)


# MIGRACIÓN V19: mismo fix que `_fix_endoso_menu_parent` en
# `endoso_proper/__init__.py` -el menú "Neteos" aparece sin padre
# (`parent_id` vacío) en la base real sin causa rastreable en el código-.
def _fix_neteo_menu_parent(env):
    menu = env.ref('neteo_proper.neteo_menu', raise_if_not_found=False)
    parent = env.ref('account.menu_finance_receivables', raise_if_not_found=False)
    if menu and parent and menu.parent_id != parent:
        menu.write({'parent_id': parent.id})
