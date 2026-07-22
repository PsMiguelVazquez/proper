# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_reactivate_studio_automations` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

STUDIO_AUTOMATION_NAMES = [
    'Send mail ventas',
    '*Notificar de aprobaciones pendientes al gerente de ventas Sandra',
    '*Notificar de aprobaciones pendientes al gerente de ventas Raúl',
    'validaciones',
    'Notificación a compras',
    'Quitar cliente de los seguidores',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    automations = env['base.automation'].with_context(active_test=False).search([
        ('name', 'in', STUDIO_AUTOMATION_NAMES),
        ('active', '=', False),
    ])
    if automations:
        automations.write({'active': True})
