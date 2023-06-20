# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    entradas = fields.Float('Entradas', compute='_compute_kardex')
    salidas = fields.Float('Salidas', compute='_compute_kardex')
    saldo = fields.Float('Saldo', compute='_compute_kardex')
    localidad = fields.Char(string='Localidad',related='location_id.location_id.name',store=True)

    def _compute_kardex(self):
        for record in self:
            entradas = 0.0
            salidas = 0.0
            saldo = 0.0
            # Si es un ajuste de inventario el saldo es la cantidad hecha en ese movimiento
            if record.location_id.id == 14:
                localidad_padre = record.location_dest_id.location_id
                record.entradas = record.qty_done
                record.salidas = 0.0
                record.saldo = record.entradas - record.salidas
            else:
                localidad_padre = record.location_dest_id.location_id
                movs_ant = self.env['stock.move.line'].search(
                    [('date', '<=', record.date), ('id', '<', record.id), ('product_id', '=', record.product_id.id),
                     ('state', '=', 'done')], order='id asc')
                if record.picking_type_id.code == 'outgoing':
                    movs_ant = movs_ant.filtered(
                                  lambda y: (y.location_dest_id.location_id == record.location_id.location_id and y.location_id.id == 14)  # Ajustes de almacén
                                  or (y.location_id.location_id == record.location_id.location_id and y.picking_type_id.code == 'outgoing')  # Salidas
                                  or (y.location_dest_id.location_id == record.location_id.location_id and y.picking_type_id.code == 'incoming')  # Entradas
                                  or (y.picking_type_id.code == 'internal' and y.picking_type_id.id == 202 and y.location_dest_id.location_id == record.location_id.location_id))  # Internas
                    salidas = record.qty_done
                    entradas = 0.0
                elif record.picking_type_id.code == 'incoming':
                    movs_ant = movs_ant.filtered(
                                  lambda y: (y.location_dest_id == record.location_dest_id and y.location_id.id == 14)  # Ajustes de almacén
                                  or (y.location_id.location_id == record.location_dest_id.location_id and y.picking_type_id.code == 'outgoing')  # Salidas
                                  or (y.location_dest_id == record.location_dest_id and y.picking_type_id.code == 'incoming')  # Entradas
                                  or (y.picking_type_id.code == 'internal' and y.picking_type_id.id == 202 and y.location_dest_id == record.location_dest_id))  # Internas
                    entradas = record.qty_done
                    salidas = 0.0
                elif record.picking_type_id.code == 'internal' and record.picking_type_id.id == 202:
                    movs_ant = movs_ant.filtered(
                                  lambda y: (y.location_dest_id == record.location_dest_id and y.location_id.id == 14)  # Ajustes de almacén
                                  or (y.location_id.location_id == record.location_dest_id.location_id and y.picking_type_id.code == 'outgoing')  # Salidas
                                  or (y.location_dest_id == record.location_dest_id and y.picking_type_id.code == 'incoming')  # Entradas
                                  or (y.picking_type_id.code == 'internal' and y.picking_type_id.id == 202 and y.location_dest_id == record.location_dest_id))  # Internas
                    entradas = record.qty_done
                    salidas = 0.0
                else:
                    record.entradas = entradas
                    record.salidas = salidas
                    record.saldo = entradas - salidas
                    return
                if movs_ant:
                    mov_ant = movs_ant[-1]
                    saldo_mov_anterior = mov_ant.saldo
                else:
                    saldo_mov_anterior = 0
                record.entradas = entradas
                record.salidas = salidas
                record.saldo = saldo_mov_anterior + entradas - salidas
