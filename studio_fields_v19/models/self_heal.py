# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)

# MIGRACIÓN V19: varios de los fixes de este módulo (reactivar el menú
# "Marketplace", las automatizaciones de Studio, el contenido de reportes
# QWeb, etc. - ver `__init__.py`) se aplican en `pre_init_hook`/
# `post_init_hook` y sus migraciones espejo `pre-*.py`/`post-*.py`, que
# sólo corren cuando Odoo detecta que la versión INSTALADA de este módulo
# es menor a la del código (`ir_module_module.latest_version` < versión del
# manifest). Se confirmó en Odoo.sh (build de julio 2026, menú
# "Marketplace") que eso deja un agujero real: cada build de una base de
# pruebas se restaura desde un backup completo -que trae de vuelta TODO el
# estado de la base, incluido `latest_version` ya en la versión actual si
# un build anterior llegó a instalarla-, mientras que el propio paso de
# neutralización de la plataforma sí puede resetear datos puntuales
# (`active=False` en menús/automatizaciones de Studio). El resultado: Odoo
# no ve una versión "menor" que instalar, se salta enteros `pre_init_hook`/
# `post_init_hook`/migraciones, y el dato roto nunca se vuelve a corregir
# solo -confirmado revisando `upgrade.log`: la migración ni siquiera
# aparece como ejecutada-.
#
# Un `ir.cron` tampoco sirve como red de seguridad: `neutralize.sql` (core)
# desactiva los crons en bases no productivas, así que en una base de
# pruebas nunca llegaría a dispararse solo.
#
# `_register_hook()` sí es confiable para esto: Odoo lo llama sobre cada
# modelo una vez por cada carga del registro en memoria (cada arranque de
# proceso, cada `-u`/`-i`, cada reload) -ver `odoo/modules/loading.py`,
# STEP 9-, y esa llamada NO está condicionada a `update_module` ni a
# ninguna comparación de versión. Se cuelga de `ir.module.module` por ser
# un modelo del core siempre instalado y cargado. Todas las funciones que
# se vuelven a correr aquí ya estaban escritas para ser idempotentes
# (comprueban el estado actual antes de escribir), así que repetirlas en
# cada arranque es seguro.
class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _register_hook(self):
        super()._register_hook()
        self._studio_fields_v19_self_heal()

    def _studio_fields_v19_self_heal(self):
        # Se importa aquí (no arriba del archivo) para evitar un ciclo de
        # import: `__init__.py` del módulo hace `from . import models`
        # antes de definir esta función.
        from .. import _self_heal_idempotent_fixes

        env = self.env
        if not env.ref('studio_fields_v19.sale_order_action_marketplace', raise_if_not_found=False):
            # Los `data/` de este módulo (acciones/vistas propias) todavía
            # no cargaron -p.ej. instalación limpia en curso, primera
            # pasada del registro-. `_fix_sale_order_menu_actions` (parte
            # de `_self_heal_idempotent_fixes`) necesita que ya existan; en
            # ese caso no hay nada que autocorregir todavía, el propio
            # `post_init_hook` normal se encargará al terminar la
            # instalación.
            return
        try:
            _self_heal_idempotent_fixes(env)
        except Exception:
            _logger.exception("studio_fields_v19: fallo en la autocorrección al arrancar el registro")
