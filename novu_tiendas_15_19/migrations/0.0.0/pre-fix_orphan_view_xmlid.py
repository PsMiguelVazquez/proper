# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_orphan_view_xmlid` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle.
"""
ORPHAN_XMLID_CANDIDATES = [
    ('novu_tiendas_15_19', 'view_extend_product_template_form'),
]


def migrate(cr, version):
    for module, name in ORPHAN_XMLID_CANDIDATES:
        cr.execute(
            """
            DELETE FROM ir_model_data
            WHERE module = %s AND name = %s AND model = 'ir.ui.view'
              AND NOT EXISTS (
                  SELECT 1 FROM ir_ui_view WHERE id = ir_model_data.res_id
              )
            """,
            (module, name),
        )
