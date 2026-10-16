# -*- coding: utf-8 -*-
"""
Segunda mitad de la migración de `x_studio_origen_mkp` (Selection ->
Many2one hacia `novu_sale_order.marketplace`): ver
`pre-migrate_origen_mkp_a_catalogo.py` para la razón del rename previo.

Para cuando este script corre, `_auto_init` ya creó la tabla del
catálogo nuevo y las columnas `x_studio_origen_mkp` (sale_order),
`x_studio_mkp_1` (account_move) y `x_studio_origen_mkp`
(helpdesk_ticket) como int4 vacías (las originales quedaron renombradas
con el sufijo `__pre_m2o`). Aquí se arma un registro de catálogo por
cada valor de texto distinto que existía, se reescriben las tres
columnas a partir de ese catálogo, y se eliminan las columnas viejas.

En una instalación nueva (sin datos que migrar) las columnas
`__pre_m2o` no existen y este script no hace nada.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute(
        "SELECT 1 FROM information_schema.columns"
        " WHERE table_name = 'sale_order' AND column_name = 'x_studio_origen_mkp__pre_m2o'"
    )
    if not env.cr.fetchone():
        return

    env.cr.execute(
        "SELECT DISTINCT x_studio_origen_mkp__pre_m2o FROM sale_order"
        " WHERE x_studio_origen_mkp__pre_m2o IS NOT NULL"
        " AND x_studio_origen_mkp__pre_m2o != ''"
    )
    valores = [row[0] for row in env.cr.fetchall()]

    Marketplace = env['novu_sale_order.marketplace']
    for valor in valores:
        marketplace = Marketplace.search([('name', '=', valor)], limit=1)
        if not marketplace:
            marketplace = Marketplace.create({'name': valor})
        env.cr.execute(
            "UPDATE sale_order SET x_studio_origen_mkp = %s"
            " WHERE x_studio_origen_mkp__pre_m2o = %s",
            (marketplace.id, valor),
        )

    # x_studio_mkp_1 (account.move) y x_studio_origen_mkp (helpdesk.ticket)
    # son related=....x_studio_origen_mkp, store=True: se reescriben
    # directo desde la orden ya migrada -más confiable en una migración
    # que depender del mecanismo de recompute de related fields-.
    # sale_id (account.move) y sale_order_id (helpdesk.ticket) son
    # Many2one reales y propios, no related.
    env.cr.execute("""
        UPDATE account_move am
           SET x_studio_mkp_1 = so.x_studio_origen_mkp
          FROM sale_order so
         WHERE am.sale_id = so.id
    """)
    env.cr.execute("""
        UPDATE helpdesk_ticket ht
           SET x_studio_origen_mkp = so.x_studio_origen_mkp
          FROM sale_order so
         WHERE ht.sale_order_id = so.id
    """)

    env.cr.execute('ALTER TABLE sale_order DROP COLUMN x_studio_origen_mkp__pre_m2o')
    for tabla, columna in (
        ('account_move', 'x_studio_mkp_1'),
        ('helpdesk_ticket', 'x_studio_origen_mkp'),
    ):
        env.cr.execute(
            "SELECT 1 FROM information_schema.columns"
            " WHERE table_name = %s AND column_name = %s",
            (tabla, columna + '__pre_m2o'),
        )
        if env.cr.fetchone():
            env.cr.execute(
                'ALTER TABLE "%s" DROP COLUMN "%s__pre_m2o"' % (tabla, columna)
            )
