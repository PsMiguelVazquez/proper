# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    entradas_origen = fields.Float('Entradas origen', compute='_compute_kardex')
    salidas_origen = fields.Float('Salidas origen', compute='_compute_kardex')
    saldo_origen = fields.Float('Saldo origen', compute='_compute_kardex')
    entradas_destino = fields.Float('Entradas destino', compute='_compute_kardex')
    salidas_destino = fields.Float('Salidas destino', compute='_compute_kardex')
    saldo_destino = fields.Float('Saldo destino', compute='_compute_kardex')
    localidad_origen = fields.Char(string='Localidad de Origen',related='location_id.location_id.name')
    localidad_destino = fields.Char(string='Localidad de Destino',related='location_dest_id.location_id.name')
    tipo_mov = fields.Char(string='Tipo de movimiento', compute='_compute_kardex')


    def _compute_kardex(self):
        movs_ant = self.env['stock.move.line']
        for line in self:
            line.tipo_mov = line.reference if line.reference else '/' + line.picking_type_id.sequence_code + '/'
            line.entradas_origen = 0.0
            line.salidas_origen = 0.0
            line.saldo_origen = 0.0
            line.entradas_destino = 0.0
            line.salidas_destino = 0.0
            line.saldo_destino = 0.0
        movs_producto = self.env['stock.move.line'].search([('product_id','=',self[0].product_id.id),('state','=','done')], order='date asc')
        for record in movs_producto:
            record.tipo_mov = record.reference if record.reference else '/' +record.picking_type_id.sequence_code +'/'
            record.entradas_origen = 0.0
            record.salidas_origen = 0.0
            record.saldo_origen = 0.0
            record.entradas_destino = 0.0
            record.salidas_destino = 0.0
            record.saldo_destino = 0.0
            # Si es un ajuste de inventario el saldo es la cantidad hecha en ese movimiento
            if record.location_id.id == 14:
                record.entradas_destino = record.qty_done
                record.saldo_destino = record.entradas_destino
                movs_ant|=record
            elif '/IN/' in record.tipo_mov or '/INT/' in record.tipo_mov or '/OUT/' in record.tipo_mov or 'INT' in record.tipo_mov:
                if '/IN/' in record.tipo_mov:
                    record.entradas_destino = record.qty_done
                    movs_origen = movs_ant.filtered \
                        (lambda y: (y.localidad_origen == record.localidad_destino and '/OUT/' in y.tipo_mov)  # Salidas
                                   or (y.localidad_destino == record.localidad_destino and '/IN/' in y.tipo_mov)  # entradas
                                   or ((y.localidad_origen == record.localidad_destino or y.localidad_destino == record.localidad_destino) and ('/INT/' in y.tipo_mov or 'INT' in y.tipo_mov))  # Internas
                                   or (y.localidad_destino == record.localidad_destino and y.location_id.id == 14)  # Ajustes
                                   and '/PACK/' not in y.tipo_mov and '/PICK/' not in y.tipo_mov)
                    if movs_origen:
                        ultimo_mov_origen = movs_origen[-1]
                        if record.localidad_destino == ultimo_mov_origen.localidad_origen:
                            saldo_destino = ultimo_mov_origen.saldo_origen
                            record.saldo_destino = saldo_destino + record.qty_done
                        else:
                            saldo_destino = ultimo_mov_origen.saldo_destino
                            record.saldo_destino = saldo_destino + record.qty_done
                    else:
                        record.saldo_destino = record.qty_done
                elif '/OUT/' in record.tipo_mov:
                    record.salidas_origen = record.qty_done
                    movs_origen = movs_ant.filtered\
                                    (lambda y: (y.localidad_origen == record.localidad_origen and '/OUT/' in y.tipo_mov) #Salidas
                                    or (y.localidad_destino == record.localidad_origen and '/IN/' in y.tipo_mov) # entradas
                                    or ((y.localidad_origen == record.localidad_origen or y.localidad_destino == record.localidad_origen) and ('/INT/' in y.tipo_mov or 'INT' in y.tipo_mov)) # Internas
                                    or (y.localidad_destino == record.localidad_origen and y.location_id.id == 14) # Ajustes
                                    and '/PACK/' not in y.tipo_mov and '/PICK/' not in y.tipo_mov)
                    if movs_origen:
                        ultimo_mov_origen = movs_origen[-1]
                        if record.localidad_origen == ultimo_mov_origen.localidad_origen:
                            saldo_origen = ultimo_mov_origen.saldo_origen
                            record.saldo_origen = saldo_origen - record.qty_done
                        else:
                            saldo_destino = ultimo_mov_origen.saldo_destino
                            record.saldo_origen = saldo_destino - record.qty_done
                    else:
                        record.saldo_origen
                elif 'INT' in record.tipo_mov:
                    movs_origen = movs_ant.filtered(lambda y: (y.localidad_origen == record.localidad_origen and '/OUT/' in y.tipo_mov) #Salidas
                                    or (y.localidad_destino == record.localidad_origen and '/IN/' in y.tipo_mov) # entradas
                                    or ((y.localidad_origen == record.localidad_origen or y.localidad_destino == record.localidad_origen) and ('/INT/' in y.tipo_mov or 'INT' in y.tipo_mov)) # Internas
                                    or (y.localidad_destino == record.localidad_origen and y.location_id.id == 14) # Ajustes
                                    and '/PACK/' not in y.tipo_mov and '/PICK/' not in y.tipo_mov)
                    movs_destino = movs_ant.filtered(lambda y: (y.localidad_origen == record.localidad_destino and '/OUT/' in y.tipo_mov)  # Salidas
                                   or (y.localidad_destino == record.localidad_destino and '/IN/' in y.tipo_mov)  # entradas
                                   or ((y.localidad_origen == record.localidad_destino or y.localidad_destino == record.localidad_destino) and ('/INT/' in y.tipo_mov or 'INT' in y.tipo_mov))  # Internas
                                   or (y.localidad_destino == record.localidad_destino and y.location_id.id == 14)  # Ajustes
                                   and '/PACK/' not in y.tipo_mov and '/PICK/' not in y.tipo_mov)
                    if movs_origen:
                        if movs_origen[-1].localidad_origen == record.localidad_origen:
                            saldo_movs_origen = movs_origen[-1].saldo_origen
                        else:
                            saldo_movs_origen = movs_origen[-1].saldo_destino
                    else:
                        saldo_movs_origen = 0
                    if movs_destino:
                        if movs_destino[-1].localidad_origen == record.localidad_destino:
                            saldo_movs_destino = movs_destino[-1].saldo_origen
                        else:
                            saldo_movs_destino = movs_destino[-1].saldo_destino
                    else:
                        saldo_movs_destino = 0.0
                    record.salidas_origen = record.qty_done
                    record.entradas_destino = record.qty_done
                    record.saldo_origen = saldo_movs_origen - record.salidas_origen
                    record.saldo_destino = saldo_movs_destino + record.entradas_destino
                movs_ant|=record



