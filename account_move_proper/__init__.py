# -*- coding: utf-8 -*-

from . import models


def pre_init_hook(env):
    _delete_old_studio_account_move_form_view(env)
    _reactivate_studio_views(env)


# MIGRACIÓN V19: esta vista (formalizada, con xmlid propio, declarada
# normalmente en `views/views.xml`) apareció desactivada (`active=False`)
# en la base real sin que nadie la haya tocado a mano -mismo fenómeno
# observado con las automatizaciones de Studio en `studio_fields_v19`
# (`_reactivate_studio_automations`), probablemente ligado a la
# neutralización de bases de prueba de Odoo.sh-. Sin ella, "Movimientos de
# almacén" y `fecha_entrega_mercancia_html` desaparecen de la factura sin
# ningún error visible. Se reactiva por xmlid en cada actualización del
# módulo como red de seguridad.
STUDIO_VIEW_XMLIDS = [
    'account_move_proper.view_account_move_form_inherited_dates',
]


# MIGRACIÓN V19: vista original generada por Odoo Studio para
# `account.view_move_form` (state='manual', módulo fantasma
# `studio_customization`) - es el origen del bloque formalizado en
# `studio_fields_v19/views/account_move_form.xml` (confirmado campo por
# campo contra su `arch_db` real). Está inactiva, pero `active=False` NO
# la excluye de la validación del árbol de vistas heredadas de
# `account.view_move_form`: al actualizar `view_account_move_form_
# inherited_dates` (abajo) Odoo la revalida igual, y su xpath a
# `l10n_mx_edi_origin` -campo eliminado en 19.0- rompe la actualización
# con "El elemento ... no puede ser localizado en la vista padre". Se
# elimina aquí (no solo en `studio_fields_v19`) porque nada garantiza que
# ese módulo se procese antes que este durante el deploy -ninguno depende
# del otro-, y esta es la vista que de hecho dispara el fallo al cargar
# `views/views.xml` de este módulo.
OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID = 'studio_customization.odoo_studio_account__ac74cbfb-da24-46b5-aca5-f72183fdfc26'


def _delete_old_studio_account_move_form_view(env):
    view = env.ref(OLD_STUDIO_ACCOUNT_MOVE_FORM_VIEW_XMLID, raise_if_not_found=False)
    if view:
        env.cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id = %s", (view.id,))
        env.cr.execute("DELETE FROM ir_ui_view WHERE id = %s", (view.id,))


def _reactivate_studio_views(env):
    # MIGRACIÓN V19: se usa SQL directo en vez de `view.active = True` (ORM)
    # a propósito: escribir por ORM dispara la validación inmediata del
    # arch de la vista (`_check_xml`), y en esta etapa tan temprana del
    # hook el registro todavía no tiene armados todos los campos del
    # módulo -causaba "Field ... does not exist in model account.move"
    # incluso para campos que sí existen en el código-. SQL directo evita
    # ese disparador.
    for xmlid in STUDIO_VIEW_XMLIDS:
        view = env.ref(xmlid, raise_if_not_found=False)
        if view and not view.active:
            env.cr.execute(
                "UPDATE ir_ui_view SET active = true WHERE id = %s",
                (view.id,),
            )
