# -*- coding: utf-8 -*-
"""
`sale.order.x_studio_origen_mkp` pasa de Selection a Many2one hacia el
nuevo catálogo `novu_sale_order.marketplace` (y con él,
`account.move.x_studio_mkp_1` y `helpdesk.ticket.x_studio_origen_mkp`,
ambos `related=... store=True`). Si se deja que `_auto_init` convierta
las columnas directo, hace `ALTER COLUMN ... TYPE int4 USING
columna::int4`, y truena porque los valores existentes son texto
('AMAZON', 'MERCADO LIBRE', ...), no enteros.

Aquí se renombran las columnas viejas ANTES de que `_auto_init` intente
esa conversión: con el nombre nuevo "no existen", así que `_auto_init`
simplemente crea la columna int4 vacía (su camino normal para una
columna nueva), sin intentar convertir nada.
`post-migrate_origen_mkp_a_catalogo.py` arma el catálogo y reescribe los
valores a partir de estas columnas renombradas, y las elimina al final.

`helpdesk.ticket.x_studio_origen_mkp` NO estaba formalizado en código
-era un campo manual de Studio, por eso no apareció en una búsqueda de
texto del repo al auditar quién más usaba este campo-; se formaliza
aquí mismo (ver models/helpdesk_ticket.py) y, siguiendo el patrón ya
establecido en este módulo para este mismo caso (ver
`_fix_stale_manual_field_related` en __init__.py), se limpia la fila
vieja de `ir_model_fields` para que dicho registro deje de describir la
relación por su cuenta -ahora la describe el campo de código-.
"""
from odoo import api, SUPERUSER_ID

COLUMNAS = (
    ('sale_order', 'x_studio_origen_mkp'),
    ('account_move', 'x_studio_mkp_1'),
    ('helpdesk_ticket', 'x_studio_origen_mkp'),
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for tabla, columna in COLUMNAS:
        env.cr.execute(
            "SELECT 1 FROM information_schema.columns"
            " WHERE table_name = %s AND column_name = %s",
            (tabla, columna),
        )
        if not env.cr.fetchone():
            continue
        env.cr.execute(
            'ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s__pre_m2o"'
            % (tabla, columna, columna)
        )

    env.cr.execute("""
        UPDATE ir_model_fields
           SET related = NULL, state = 'base'
         WHERE model = 'helpdesk.ticket' AND name = 'x_studio_origen_mkp'
    """)
