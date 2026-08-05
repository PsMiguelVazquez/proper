# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_activate_payment_method_otros` en
`__init__.py`, pero para el caso de actualización (`-u`) en vez de
instalación limpia -este módulo ya estaba instalado antes de agregar este
fix, así que `pre_init_hook` (que sólo corre en instalación limpia) nunca
se ejecutaría en el próximo deploy-. Ver `__init__.py` de este módulo
para el detalle completo (por qué se reactiva a pedido del cliente y por
qué no afecta ningún default/validación de timbrado).
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    payment_method = env.ref('l10n_mx_edi.payment_method_otros', raise_if_not_found=False)
    if payment_method and not payment_method.active:
        payment_method.write({'active': True})
