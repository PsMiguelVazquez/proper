# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        r = super(StockPicking, self).write(vals)
        if r:
            if self.env.context.get('default_pick_ids'):
                picks = self.env['stock.picking'].search([('id', '=', self.env.context.get('default_pick_ids')[0])])
                ticket = self.env['helpdesk.ticket'].sudo().search([('sale_order_id', '=', picks.sale_id.id)]).filtered(lambda x:  picks in x.picking_ids)
                if ticket:
                    if not self.env['mail.activity'].search(
                            [('res_id', '=', ticket.id), ('activity_type_id', '=', 4), ('summary', '=', 'Ticket reasignado')]):
                        ticket.activity_schedule(
                            activity_type_id=4,
                            summary="Ticket reasignado",
                            note='Se ha completado la devolución y se le ha reasignado el ticket: ' + ticket.name,
                            user_id= ticket.create_uid.id
                        )
        return r
