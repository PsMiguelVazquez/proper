# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_stale_manual_field_related` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_fields
        SET related = NULL, state = 'base'
        WHERE model = 'res.partner' AND name IN ('x_area', 'x_area_trabajo')
        AND related LIKE 'self.%%'
    """)
