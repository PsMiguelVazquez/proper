# -*- coding: utf-8 -*-
from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_is_zero, float_round
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    date_planned_line = fields.Many2one('res.partner', 'Dirección')
    date_planned_l = fields.Date('Fecha Entrega')

class ProcurementRule(models.Model):
    _inherit = 'procurement.group'

    # @api.model
    # def run(self, procurements):
    #     """ Method used in a procurement case. The purpose is to supply the
    #     product passed as argument in the location also given as an argument.
    #     In order to be able to find a suitable location that provide the product
    #     it will search among stock.rule.
    #     """
    #     actions_to_run = defaultdict(list)
    #     errors = []
    #     for procurement in procurements:
    #         procurement.values.setdefault('company_id', procurement.location_id.company_id)
    #         procurement.values.setdefault('priority', '1')
    #         #procurement.values.setdefault('date_planned', fields.Datetime.now())
    #         if (
    #             procurement.product_id.type not in ('consu', 'product') or
    #             float_is_zero(procurement.product_qty, precision_rounding=procurement.product_uom.rounding)
    #         ):
    #             continue
    #         rule = self._get_rule(procurement.product_id, procurement.location_id, procurement.values)
    #         if not rule:
    #             errors.append(_('No rule has been found to replenish "%s" in "%s".\nVerify the routes configuration on the product.') %
    #                 (procurement.product_id.display_name, procurement.location_id.display_name))
    #         else:
    #             action = 'pull' if rule.action == 'pull_push' else rule.action
    #             actions_to_run[action].append((procurement, rule))
    #
    #     if errors:
    #         raise UserError('\n'.join(errors))
    #
    #     for action, procurements in actions_to_run.items():
    #         if hasattr(self.env['stock.rule'], '_run_%s' % action):
    #             try:
    #                 getattr(self.env['stock.rule'], '_run_%s' % action)(procurements)
    #             except UserError as e:
    #                 errors.append(e.name)
    #         else:
    #             _logger.error("The method _run_%s doesn't exist on the procurement rules" % action)
    #
    #     if errors:
    #         raise UserError('\n'.join(errors))
    #     return True


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
                            fecha_new = fields.datetime(moves.sale_line_id.date_planned_l.year, moves.sale_line_id.date_planned_l.month, moves.sale_line_id.date_planned_l.day) + timedelta(hours=18) if moves.sale_line_id.date_planned_l else order_id.date_order
                            picking = self.env['stock.picking'].search([['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')],['scheduled_date', '=', fecha_new ], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]]) if moves.sale_line_id.date_planned_l else self.env['stock.picking'].search([['sale_id', '=', order_id.id], ['state', 'not in', ('done', 'cancel')], ['partner_id', '=', moves.sale_line_id.date_planned_line.id]])
                            if picking:
                                moves.write({'date': fecha_new, 'date_deadline': fecha_new})
                                moves.write({'picking_id': picking[0].id if len(picking)>1 else picking.id})
                                moves._assign_picking_post_process(new=new_picking)
                            else:
                                moves.write({'date': fecha_new , 'date_deadline': fecha_new})
                                rr = moves._get_new_picking_values()
                                rr['partner_id'] = moves.sale_line_id.date_planned_line.id
                                picking = Picking.create(rr)
                                picking.write({'scheduled_date':fecha_new, 'date_deadline': fecha_new})
                                moves.write({'picking_id': picking.id})
                                moves._assign_picking_post_process(new=new_picking)
                        i = i+1
        return r
