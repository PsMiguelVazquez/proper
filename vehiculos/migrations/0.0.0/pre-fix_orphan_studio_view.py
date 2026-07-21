# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `pre_init_hook` en `__init__.py`, pero para el
caso de actualización (`-u`) en vez de instalación limpia. Ver la nota en
`__init__.py` para el detalle del problema (vista huérfana de Odoo Studio
bloqueando la limpieza automática de `stock_alm_0_14_form` con un
ForeignKeyViolation en `ir_ui_view_inherit_id_fkey`).
"""
def migrate(cr, version):
    cr.execute("SELECT id FROM ir_ui_view WHERE name = 'Form inherit alm0'")
    parent_ids = [row[0] for row in cr.fetchall()]
    if not parent_ids:
        return
    to_delete = list(parent_ids)
    while True:
        cr.execute(
            "SELECT id FROM ir_ui_view WHERE inherit_id = ANY(%s)",
            (to_delete,),
        )
        children = [row[0] for row in cr.fetchall()]
        if not children:
            break
        cr.execute("DELETE FROM ir_ui_view WHERE id = ANY(%s)", (children,))
        to_delete = children
