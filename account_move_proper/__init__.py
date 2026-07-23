# -*- coding: utf-8 -*-

from . import models


def pre_init_hook(env):
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
