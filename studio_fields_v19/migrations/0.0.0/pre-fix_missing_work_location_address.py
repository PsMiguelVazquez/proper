# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_missing_work_location_address` en
`__init__.py`, pero para el caso de actualización. Ver el comentario en
`__init__.py` para el detalle -incluyendo por qué hace falta poner la
constraint por SQL directo en vez de esperar a que `hr` la reintente
solo-.
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

    env.cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'hr_work_location' AND column_name = 'address_id'
           AND is_nullable = 'YES'
    """)
    if not env.cr.fetchone():
        return
    env.cr.execute("SELECT COUNT(*) FROM hr_work_location WHERE address_id IS NULL")
    if env.cr.fetchone()[0]:
        return
    env.cr.execute("ALTER TABLE hr_work_location ALTER COLUMN address_id SET NOT NULL")
