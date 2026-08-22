# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_backfill_x_studio_almacn` en `__init__.py`
(llamada desde `post_init_hook`), pero para el caso de actualización -este
módulo ya estaba instalado antes de agregar este fix, así que
`post_init_hook` (que sólo corre en instalación limpia) nunca se
ejecutaría en el próximo deploy-. Va como migración `post-` (no `pre-`)
a propósito: el campo `x_studio_almacn` lo define este mismo módulo, así
que todavía no existe en el ORM cuando corren las migraciones `pre-`
-confirmado en local, revienta con "Invalid field account.move.
x_studio_almacn"-. Ver `__init__.py` de este módulo para el detalle
completo.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    moves = env['account.move'].search([
        ('sale_id.warehouse_id.code', '!=', False),
        ('x_studio_almacn', '=', False),
    ])
    moves._compute_x_studio_almacn()
