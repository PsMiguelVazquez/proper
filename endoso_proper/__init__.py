# -*- coding: utf-8 -*-

from . import models
from . import wizard


def pre_init_hook(env):
    _fix_endoso_menu_parent(env)


# MIGRACIÓN V19: el menú "Endosos" (`account.menu_finance_receivables` como
# padre, declarado en `views/views.xml`) aparece sin padre (`parent_id`
# vacío) en la base real sin causa rastreable en el código -mismo fenómeno
# ya visto varias veces esta sesión con otros menús/vistas/automatizaciones
# de Studio-. Sin padre, el menú deja de aparecer bajo Contabilidad >
# Ventas aunque el registro siga existiendo. Se reasigna por código en
# cada actualización del módulo como red de seguridad.
def _fix_endoso_menu_parent(env):
    menu = env.ref('endoso_proper.endoso_menu', raise_if_not_found=False)
    parent = env.ref('account.menu_finance_receivables', raise_if_not_found=False)
    if menu and parent and menu.parent_id != parent:
        menu.write({'parent_id': parent.id})
