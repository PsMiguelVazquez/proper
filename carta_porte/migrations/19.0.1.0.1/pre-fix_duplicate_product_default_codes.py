# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: este módulo agrega `_default_code_unique`
(`models/product.py`, `unique(default_code)`) a `product.product`. En
15.0 ese campo no tenía índice único, así que quedaron variantes con el
mismo `default_code` -en los casos encontrados, siempre una activa y una
archivada (`active=False`)-. Al montar el índice en 19.0, Postgres falla
con "could not create unique index ... is duplicated" y Odoo sólo deja
un WARNING en el log (no detiene el upgrade), así que el índice nunca
llega a crearse mientras el duplicado siga ahí.

Este script corre como `pre-` (antes de que este módulo monte su propio
esquema/constraints) para liberar el `default_code` de la copia
ARCHIVADA antes de que Postgres intente crear el índice. Sólo actúa
cuando hay exactamente un producto ACTIVO con ese código -si hay 0 o 2+
activos compartiendo el código, es ambiguo cuál es "el bueno" y se deja
sin tocar para revisión manual-. Usa SQL directo (no `write()`) porque
en este punto de la carga el registro de `product.product` puede no
estar listo para ORM.

`studio_fields_v19` (que depende de este módulo) repite el mismo fix en
`_fix_duplicate_product_default_codes` como red de seguridad idempotente
para duplicados nuevos que pudieran aparecer después; este script es el
que evita el WARNING en el primer despliegue donde se agrega el índice.
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
