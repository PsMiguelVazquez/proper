# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_force_install_novu_modules` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

NOVU_MODULES_TO_FORCE_INSTALL = ['novu_sale_order', 'novu_purchase_order']


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules = env['ir.module.module'].search([
        ('name', 'in', NOVU_MODULES_TO_FORCE_INSTALL),
        ('state', '=', 'uninstalled'),
    ])
    if modules:
        modules.button_install()
