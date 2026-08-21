# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_missing_work_location_address` en
`__init__.py`, pero para el caso de actualización. Ver el comentario en
`__init__.py` para el detalle -incluyendo por qué este fix sólo hace
efecto a partir del siguiente arranque completo, no en el mismo en el
que se despliega-.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    locations = env['hr.work.location'].with_context(active_test=False).search([
        ('address_id', '=', False),
    ])
    for location in locations:
        if location.company_id.partner_id:
            location.write({'address_id': location.company_id.partner_id.id})
