# -*- coding: utf-8 -*-
from odoo import models

# MIGRACIÓN V19: la vista de Studio que muestra las columnas de kardex
# (Entradas/Salidas/Saldo origen y destino, Costo de compra, Referencia del
# proveedor, etc. -las columnas ya formalizadas como campos reales en
# `stock_picking.py`, extendiendo `stock.move.line`-) apareció con
# `active=False` en un build de pruebas -mismo fenómeno ya visto varias
# veces esta sesión (Marketplace, endoso, neteo, distribución de
# vehículos)-, a pesar de heredar correctamente de la vista real que usa
# "Historial de movimientos" (`stock.view_move_line_tree`). Se reafirma vía
# `_register_hook()` -corre en cada arranque del registro, sin depender de
# comparar versiones de módulo-, mismo patrón que en los módulos
# anteriores.
STUDIO_MOVE_LINE_TREE_XMLID = 'studio_customization.odoo_studio_stock_mo_cda76ee2-3d9c-452b-bb11-55ce40a0b49b'


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _register_hook(self):
        super()._register_hook()
        view = self.env.ref(STUDIO_MOVE_LINE_TREE_XMLID, raise_if_not_found=False)
        if view and not view.active:
            view.write({'active': True})
