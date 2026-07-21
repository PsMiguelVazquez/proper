# -*- coding: utf-8 -*-

from . import models


# MIGRACIÓN V19: `stock_alm_0_14_form` (vista `vehiculos.stock_alm_0_14_form`,
# `stock.picking`) se quitó deliberadamente del código en una migración
# anterior (duplicaba el formulario estándar de 15.0 con campos obsoletos,
# ver el comentario en `views/views.xml`). El registro sigue existiendo en
# la base de datos real -Odoo lo detecta como "ya no declarado por este
# módulo" y trata de borrarlo automáticamente al final de cada actualización
# (`ir.model.data._process_end`)-, pero no puede: una vista de Odoo Studio
# ("Odoo Studio: Form inherit alm0 customization", sin xmlid propio, nunca
# limpiada cuando se quitó la vista padre) todavía hereda de ella
# (`inherit_id`), y la relación de llave foránea bloquea el DELETE con
# "violates foreign key constraint ir_ui_view_inherit_id_fkey", un CRITICAL
# que tumba toda la actualización. Se limpia esa vista huérfana de Studio
# primero para que la vista padre, ya obsoleta, se pueda borrar sola.
def pre_init_hook(env):
    env.cr.execute("SELECT id FROM ir_ui_view WHERE name = 'Form inherit alm0'")
    parent_ids = [row[0] for row in env.cr.fetchall()]
    if not parent_ids:
        return
    # Borra en cascada cualquier vista huérfana que herede (directa o
    # indirectamente) de la vista padre obsoleta, sin importar cuántos
    # niveles de "Odoo Studio: ... customization" se hayan apilado encima.
    to_delete = list(parent_ids)
    while True:
        env.cr.execute(
            "SELECT id FROM ir_ui_view WHERE inherit_id = ANY(%s)",
            (to_delete,),
        )
        children = [row[0] for row in env.cr.fetchall()]
        if not children:
            break
        env.cr.execute("DELETE FROM ir_ui_view WHERE id = ANY(%s)", (children,))
        to_delete = children
