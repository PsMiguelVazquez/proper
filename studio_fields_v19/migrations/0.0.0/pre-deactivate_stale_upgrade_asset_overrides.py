# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_deactivate_stale_upgrade_asset_overrides`
en `__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo para
el detalle completo (por qué la herramienta de upgrade de Odoo genera
este `ir.asset` roto y por qué rompe el bundle de JS del backend).
"""
from odoo import api, SUPERUSER_ID

STALE_UPGRADE_ASSET_PATHS = [
    'account_payment_widget_amount/static/src/js/account_payment_field.js',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    assets = env['ir.asset'].search([
        ('path', 'in', STALE_UPGRADE_ASSET_PATHS),
        ('active', '=', True),
    ])
    if assets:
        assets.write({'active': False})
