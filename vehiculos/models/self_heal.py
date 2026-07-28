# -*- coding: utf-8 -*-
from odoo import models

# MIGRACIÓN V19: `distribucion_menu` (padre de "Vehículos"/"Ruta" bajo
# Inventario) apareció con `active=False` en un build de pruebas -mismo
# fenómeno ya visto varias veces esta sesión (Marketplace, endoso, neteo)-,
# a pesar de que `<menuitem>` SÍ fuerza `active=True` en cada carga de
# datos (ver `nodeattr2bool(rec, 'active', default=True)` en
# `odoo/tools/convert.py::_tag_menuitem`) -o sea, no es un problema de que
# el XML no declare el campo, como en los casos anteriores, sino de que la
# actualización del módulo simplemente no se ejecuta en ese build (mismo
# mecanismo sospechado: si el backup restaurado ya trae
# `ir_module_module.latest_version` igual a la versión actual, Odoo no ve
# upgrade pendiente y se salta la carga de `menuitem`)-. Con un menú padre
# inactivo, Odoo oculta toda la rama aunque los hijos sigan activos. Se
# reafirma vía `_register_hook()` -corre en cada arranque del registro,
# sin depender de comparar versiones de módulo ni del scheduler de cron-,
# mismo patrón que `studio_fields_v19`/`add_invoice_to_paid`.
class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _register_hook(self):
        super()._register_hook()
        menu = self.env.ref('vehiculos.distribucion_menu', raise_if_not_found=False)
        if menu and not menu.active:
            menu.write({'active': True})
