# -*- coding: utf-8 -*-

from . import models


def pre_init_hook(env):
    _delete_old_studio_account_move_form_view(env)


# MIGRACIÓN V19: a diferencia de `_delete_old_studio_account_move_form_
# view` (que sólo usa `env.ref`/SQL crudo), `_backfill_x_studio_almacn`
# necesita el campo `account.move.x_studio_almacn` -definido en este mismo
# módulo- ya registrado en el ORM. `pre_init_hook` corre ANTES de que este
# módulo cargue sus propios modelos (mismo motivo por el que la migración
# espejo es `post-`, no `pre-`), así que llamarlo desde ahí revienta con
# "Invalid field account.move.x_studio_almacn" -confirmado en local-. Va
# en `post_init_hook`, que corre después.
def post_init_hook(env):
    _backfill_x_studio_almacn(env)


# MIGRACIÓN V19: `view_account_move_form_inherited_dates` (abajo, en
# `views/views.xml`) aparecía desactivada (`active=False`) en la base real
# sin causa rastreable en el código -mismo fenómeno observado con las
# automatizaciones de Studio en `studio_fields_v19`
# (`_reactivate_studio_automations`), probablemente ligado a la
# neutralización de bases de prueba de Odoo.sh-. Anteriormente esto se
# corregía aquí, reactivándola por SQL crudo en este hook, ANTES de que
# `load_data` reescribiera su `arch_db`. Eso resultó ser un bug real: abre
# una ventana donde la vista queda activa con su contenido VIEJO todavía
# sin corregir, y en esa ventana, validar CUALQUIER vista hermana de
# `account.view_move_form` (ej. `account_move_cancel_reason`, procesada
# antes en el mismo archivo) recorre el árbol combinado, encuentra el
# `arch_db` viejo de esta vista (con xpaths a campos ya renombrados/
# eliminados como `l10n_mx_edi_origin`) y falla con "Element ... cannot be
# located in parent view" -reproducido y confirmado en local-. El fix
# correcto es declarar `<field name="active" eval="True"/>` directo en el
# `<record>` de la vista, para que reactivación y corrección de contenido
# ocurran en el mismo `write()` atómico, sin ventana intermedia.


# MIGRACIÓN V19: vista original generada por Odoo Studio para
# `account.view_move_form` (state='manual', módulo fantasma
# `studio_customization`) - es el origen del bloque formalizado en
# `studio_fields_v19/views/account_move_form.xml` (confirmado campo por
# campo contra su `arch_db` real). Está inactiva; una vista inactiva NO
# participa en la validación del árbol combinado de `account.view_move_
# form` (Odoo la excluye explícitamente, ver `_get_inheriting_views_
# domain`), así que NO es la causa de ningún error de validación -se
# eliminó, en su momento, sospechando lo contrario; la causa real resultó
# ser otra (ver comentario en `pre_init_hook`)-. Se elimina de todos modos
# porque es contenido 100% redundante/muerto, sin ningún propósito ya que
# `studio_fields_v19/views/account_move_form.xml` la reemplaza por
# completo.
OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID = 'studio_customization.odoo_studio_account__ac74cbfb-da24-46b5-aca5-f72183fdfc26'


def _delete_old_studio_account_move_form_view(env):
    view = env.ref(OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID, raise_if_not_found=False)
    if view:
        env.cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id = %s", (view.id,))
        env.cr.execute("DELETE FROM ir_ui_view WHERE id = %s", (view.id,))


# MIGRACIÓN V19: `account.move.x_studio_almacn` (arriba, en `models/
# account_move.py`) reutiliza el nombre de columna que ya existía como
# metadato crudo de Studio en 15.0 -a propósito, según el comentario al
# inicio de ese archivo, para que Odoo tomara la columna existente sin
# perder datos-. El problema: al ser `store=True` sobre una columna que YA
# EXISTÍA, Odoo nunca dispara el recompute inicial (eso sólo pasa cuando
# la columna se crea por primera vez), así que cualquier factura cuyo
# valor viejo de Studio ya viniera vacío en la columna se queda vacía para
# siempre, aunque `sale_id.warehouse_id.code` sí tenga un valor real -
# confirmado en producción: `INV/2026/03024` tenía `x_studio_almacn` vacío
# con `sale_id.warehouse_id.code = 'ALM14'`-. Se recalcula una sola vez
# para las facturas afectadas (con venta y almacén, pero sin el dato ya
# guardado).
def _backfill_x_studio_almacn(env):
    moves = env['account.move'].search([
        ('sale_id.warehouse_id.code', '!=', False),
        ('x_studio_almacn', '=', False),
    ])
    moves._compute_x_studio_almacn()
