# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_duplicate_product_default_codes` en
`__init__.py`, pero para el caso de actualización. Ver el comentario en
`__init__.py` para el detalle -y ver `carta_porte/migrations/19.0.1.0.1/
pre-fix_duplicate_product_default_codes.py` para el fix "primario" que
corre antes de que se intente crear el índice único; este es sólo la
red de seguridad idempotente para duplicados nuevos-.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("""
        SELECT default_code,
               array_agg(id) FILTER (WHERE active) AS active_ids,
               array_agg(id) FILTER (WHERE NOT active) AS archived_ids
          FROM product_product
         WHERE default_code IS NOT NULL AND default_code != ''
      GROUP BY default_code
        HAVING count(*) > 1
    """)
    for default_code, active_ids, archived_ids in env.cr.fetchall():
        if len(active_ids or []) != 1 or not archived_ids:
            continue
        for product_id in archived_ids:
            new_code = '%s-ARCH%d' % (default_code, product_id)
            env.cr.execute(
                "UPDATE product_product SET default_code = %s WHERE id = %s",
                (new_code, product_id),
            )
