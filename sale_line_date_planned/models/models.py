# -*- coding: utf-8 -*-
from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_is_zero, float_round
from datetime import datetime, timedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    date_planned_l = fields.Date('Fecha Entrega')
    partner_ids = fields.Many2many('res.partner', compute='set_domain_addres')
    date_planned_line = fields.Many2one('res.partner', 'Dirección', domain="[('id', 'in', partner_ids)]")

    @api.depends('order_partner_id')
    def set_domain_addres(self):
        for record in self:
            if record.order_partner_id:
                childs = self.env['res.partner'].search([('parent_id', '=', record.order_partner_id.id)])
                record.partner_ids = [(6, 0, childs.ids+record.order_partner_id.ids)]
            else:
                record.partner_ids = [(6, 0, [])]


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _assign_picking(self):
        order_id = self.env['sale.order'].browse(self.mapped('sale_line_id.order_id.id'))
        r = super(StockMove, self)._assign_picking()
        if order_id:
            delivery = order_id.partner_shipping_id.id
            direcciones = order_id.mapped('order_line.date_planned_line')
            fechas = order_id.mapped('order_line.date_planned_l')
            i = 0
            if len(direcciones)>1 or len(fechas)>1:
                for moves in self:
                    if moves.sale_line_id.date_planned_line or moves.sale_line_id.date_planned_l:
                        if i == 0:
                            moves.picking_id.write({'partner_id': delivery})
                        Picking = self.env['stock.picking']
                        new_picking = True
                        fecha = moves.picking_id.partner_id
                        fecha2 = moves.picking_id.scheduled_date
                        if fecha != moves.sale_line_id.date_planned_line or fecha2 != moves.sale_line_id.date_planned_l:
                            # MIGRACIÓN V19: `fields.datetime` nunca existió
                            # como constructor en `odoo.fields` (ni en
                            # 15.0); se usa la clase `datetime` ya importada
                            # de la librería estándar, que es lo que la
                            # lógica claramente pretendía construir.
                            fecha_new = datetime(moves.sale_line_id.date_planned_l.year, moves.sale_line_id.date_planned_l.month, moves.sale_line_id.date_planned_l.day) + timedelta(hours=18) if moves.sale_line_id.date_planned_l else order_id.date_order
                            picking = self.env['stock.picking'].search([['location_id', '=', moves.location_id.id], ['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')],['scheduled_date', '=', fecha_new ], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]]) if moves.sale_line_id.date_planned_l else self.env['stock.picking'].search([['location_id', '=', moves.location_id.id],['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]])
                            if picking:
                                moves.write({'date': fecha_new, 'date_deadline': fecha_new})
                                moves.write({'picking_id': picking[0].id if len(picking)>1 else picking.id})
                                moves._assign_picking_post_process(new=new_picking)
                                move_l = moves.move_orig_ids
                                while move_l:
                                    picking_child = self.env['stock.picking'].search([['location_id', '=', move_l.location_id.id],['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')],['scheduled_date', '=', fecha_new ], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]]) if moves.sale_line_id.date_planned_l else self.env['stock.picking'].search([['location_id', '=', move_l.location_id.id],['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]])
                                    if picking_child:
                                        move_l.write({'date': fecha_new, 'date_deadline': fecha_new})
                                        move_l.write({'picking_id': picking_child[0].id if len(picking_child) > 1 else picking_child.id})
                                        move_l._assign_picking_post_process(new=new_picking)
                                    else:
                                        move_l.write({'date': fecha_new, 'date_deadline': fecha_new})
                                        rr = move_l._get_new_picking_values()
                                        rr['partner_id'] = moves.sale_line_id.date_planned_line.id
                                        picking_child = Picking.create(rr)
                                        picking_child.write({'scheduled_date': fecha_new, 'date_deadline': fecha_new})
                                        move_l.write({'picking_id': picking_child.id})
                                        move_l._assign_picking_post_process(new=new_picking)
                                    move_l = move_l.move_orig_ids
                            else:
                                moves.write({'date': fecha_new , 'date_deadline': fecha_new})
                                rr = moves._get_new_picking_values()
                                rr['partner_id'] = moves.sale_line_id.date_planned_line.id
                                picking = Picking.create(rr)
                                picking.write({'scheduled_date':fecha_new, 'date_deadline': fecha_new})
                                moves.write({'picking_id': picking.id})
                                moves._assign_picking_post_process(new=new_picking)
                                move_l = moves.move_orig_ids
                                while move_l:
                                    picking_child = self.env['stock.picking'].search(
                                        [['location_id', '=', move_l.location_id.id],['sale_id', '=', order_id.id],
                                         ['state', 'not in', ('done', 'cancel')], ['scheduled_date', '=', fecha_new],
                                         ['partner_id', '=',
                                          moves.sale_line_id.date_planned_line.id]]) if moves.sale_line_id.date_planned_l else \
                                    self.env['stock.picking'].search(
                                        [['location_id', '=', move_l.location_id.id],['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')],
                                         ['partner_id', '=', moves.sale_line_id.date_planned_line.id]])
                                    if picking_child:
                                        move_l.write({'date': fecha_new, 'date_deadline': fecha_new})
                                        move_l.write({'picking_id': picking_child[0].id if len(picking_child) > 1 else picking_child.id})
                                        move_l._assign_picking_post_process(new=new_picking)
                                    else:
                                        move_l.write({'date': fecha_new, 'date_deadline': fecha_new})
                                        rr = move_l._get_new_picking_values()
                                        rr['partner_id'] = moves.sale_line_id.date_planned_line.id
                                        picking_child = Picking.create(rr)
                                        picking_child.write({'scheduled_date': fecha_new, 'date_deadline': fecha_new})
                                        move_l.write({'picking_id': picking_child.id})
                                        move_l._assign_picking_post_process(new=new_picking)
                                    move_l = move_l.move_orig_ids
                        i = i+1
        return r
