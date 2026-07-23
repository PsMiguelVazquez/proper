# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_reactivate_studio_views` en `__init__.py`
(llamada desde `pre_init_hook`), pero para el caso de actualización. Ver el
comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

STUDIO_VIEW_XMLIDS = [
    'account_move_proper.view_account_move_form_inherited_dates',
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view and not view.active:
            cr.execute(
                "UPDATE ir_ui_view SET active = true WHERE id = %s",
                (view.id,),
            )
