# -*- coding:utf-8 -*-
from . import models


def pre_init_hook(env):
    _fix_orphan_view_xmlid(env)


# MIGRACIÓN V19: `view_extend_product_template_form` (ver
# `views/product_template_views.xml`) dejó de aparecer en la base real sin
# ningún error visible -"Actualizar" el módulo corría limpio, pero la vista
# nunca se recreaba-. La causa: su `ir.model.data` quedó apuntando
# (`res_id`) a una fila de `ir_ui_view` que ya no existe -mismo fenómeno de
# "registros que desaparecen sin causa rastreable en el código" ya visto
# con vistas/automatizaciones de Studio en este mismo proyecto-. En una
# actualización normal Odoo detecta esa referencia colgada y se autorepara
# solo (se confirmó reproduciéndolo en local), pero en la base real no
# ocurrió por alguna razón no determinada. Se limpia la referencia huérfana
# por SQL directo antes de que se carguen los datos del módulo, para que la
# carga normal de `views/product_template_views.xml` la recree desde cero.
ORPHAN_XMLID_CANDIDATES = [
    ('novu_tiendas_15_19', 'view_extend_product_template_form'),
]


def _fix_orphan_view_xmlid(env):
    for module, name in ORPHAN_XMLID_CANDIDATES:
        env.cr.execute(
            """
            DELETE FROM ir_model_data
            WHERE module = %s AND name = %s AND model = 'ir.ui.view'
              AND NOT EXISTS (
                  SELECT 1 FROM ir_ui_view WHERE id = ir_model_data.res_id
              )
            """,
            (module, name),
        )
