# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    entradas = fields.Float('Entradas', compute='_compute_kardex')
    salidas = fields.Float('Salidas', compute='_compute_kardex')
    saldo = fields.Float('Saldo', compute='_compute_kardex')

    def _compute_kardex(self):
        for index, record in enumerate(self ,start=0):

            entradas = 0.0
            salidas = 0.0
            saldo = 0.0
            mov_ant = self.filtered(lambda x :x.date < record.date and x.location_dest_id == record.location_id
                                    )
            # Si es un ajuste de inventario el saldo es la cantidad hecha en ese movimiento
            if record.location_id.id == 14:
                record.entradas = 0.0
                record.salidas = 0.0
                record.saldo = record.qty_done
            else:
                # Si es IN busca el último movimiento que tenga el mismo destino "A" en los movimientos anteriores
                if record.picking_type_id and record.picking_type_id.id == 101:
                    movs_mismo_dia = self.filtered(lambda x: x.date == record.date)
                    movs_ant = self.filtered(lambda x: x.date < record.date
                                                       and x.location_dest_id == record.location_dest_id)
                    # Si se hicieron entradas parciales el mismo dia y misma fecha
                    if len(movs_mismo_dia) > 1:
                        # Si es el primer movimiento, el movimiento anterior es el movimiento inmediato anterior
                        # a la fecha del movimiento actual
                        if record == movs_mismo_dia[0]:
                            mov_ant = movs_ant.filtered(lambda x: x.id != record.id and x.date != record.date)[-1]
                        else:
                            mov_ant = movs_mismo_dia[0]
                    else:
                        mov_ant = movs_ant.filtered(lambda x: x.id != record.id and x.date != record.date)[-1]
                    saldo_mov_anterior = mov_ant.saldo
                    entradas = record.qty_done
                    salidas = 0.0
                    record.entradas = entradas
                    record.salidas = salidas
                    record.saldo = saldo_mov_anterior + entradas - salidas
                else:
                    # Si es un pick obtiene el saldo anterior donde el origen es igual al destino en el movimiento anterior
                    if record.picking_type_id and record.picking_type_id == 103:
                        record.entradas = 0
                        record.salidas = 0
                        record.saldo = 0
                    else:
                        record.picking_type_id.id
                        record.location_id
                        record.entradas = 0.0
                        record.salidas = 0.0
                        record.saldo = entradas - salidas

