# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_reactivate_carta_porte_views` en
`__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo
para el detalle completo (por qué `carta_porte.view_picking_carta_porte`
queda inactiva sin causa rastreable).
"""
from odoo import api, SUPERUSER_ID

CARTA_PORTE_VIEW_XMLIDS = [
    'carta_porte.view_picking_carta_porte',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in CARTA_PORTE_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view and not view.active:
            view.write({'active': True})
