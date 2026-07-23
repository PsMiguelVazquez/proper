# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_delete_old_studio_account_move_form_view` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID = 'studio_customization.odoo_studio_account__ac74cbfb-da24-46b5-aca5-f72183fdfc26'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref(OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID, raise_if_not_found=False)
    if view:
        cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id = %s", (view.id,))
        cr.execute("DELETE FROM ir_ui_view WHERE id = %s", (view.id,))
