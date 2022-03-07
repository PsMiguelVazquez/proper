# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2020 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils
from datetime import datetime
import dateutil.parser


class WizardPartnerRouteMap(models.TransientModel):
    _name = 'wizard.partner.route.map'
    _description = 'Partner Routes Map'

    partner_route_ids = fields.One2many(
        'partner.route.map.lines', 'partner_route_map_id')

    @api.model
    def default_get(self, fields_lst):
        res = super(WizardPartnerRouteMap, self).default_get(fields_lst)
        ctx = dict(self.env.context)
        partner_route_ids = []
        sequence = 1
        pickings = self.env['stock.picking'].browse(ctx.get('active_ids', []))
        for partner in pickings.mapped('partner_id'):
            partner_route_ids.append(
                (0, 0, {'partner_id': partner.id, 'sequence': sequence}))
            sequence += 1
        res.update({'partner_route_ids': partner_route_ids})
        return res

    def action_show_routes_map(self):
        if not self.partner_route_ids:
            return {'type': 'ir.actions.act_window_close'}
        url = 'https://www.google.com/maps/dir/?api=1'
        # Origin
        start_partner = self.env.user.partner_id
        if not start_partner.partner_latitude and start_partner.partner_longitude:
            raise UserError(
                _('Missing %s Geolocation!' % (start_partner.name)))
        origin_coordinates = start_partner.mapped(
            lambda x: (str(x.partner_latitude), str(x.partner_longitude)))
        origin_res = origin_coordinates[0][0] + ',' + origin_coordinates[0][1]
        url += '&origin=%s' % (origin_res)

        # Destination
        last_partner = self.partner_route_ids[-1].partner_id
        if not last_partner.partner_latitude and \
                last_partner.partner_longitude:
            raise UserError(
                _('Missing %s Geolocation!' % (last_partner.name)))
        url += '&destination=%s' % (
            str(last_partner.partner_latitude) + ',' + str(
                last_partner.partner_longitude))

        # WayPoints
        if len(self.partner_route_ids.ids) > 1:
            partner_ids = self.partner_route_ids.mapped(
                'partner_id') - last_partner
            coordinates = partner_ids.filtered(
                lambda res: res.partner_latitude and res.partner_longitude
            ).mapped(lambda x: (str(x.partner_latitude),
                                str(x.partner_longitude)))
            if not coordinates:
                raise UserError(_('Missing Partners Geolocation!'))
            partner_res = []
            partner_res += [i[0] + ',' + i[1] for i in coordinates]
            url += '&waypoints=%s' % ('|'.join(partner_res))

        # Creando citas
        for line in self.partner_route_ids:
            vals = {
                'partner_id': line.partner_id.id,
                'user_id': line.user_id.id,
                'visit_reason_id': line.visit_reason_id.id,
                'date': line.visit_date,
            }
            if not line.visit_period:
                self.env['customer.visits'].create(vals)
            else:
                days = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
                if line.start_period and line.end_period and line.days_period:
                    for date in date_utils.date_range(
                            start=datetime.combine(line.start_period, datetime.min.time()),
                            end=datetime.combine(line.end_period, datetime.min.time()),
                            step=relativedelta(days=line.days_period),
                    ):
                        if date.weekday() < 5 and not self.env['customer.visits'].search(
                                [('date', '=', dateutil.parser.parse(line.visit_date.strftime('%Y-%m-%d')).date())]):
                            vals['date'] = dateutil.parser.parse(date.strftime('%Y-%m-%d')).date()
                            self.env['customer.visits'].create(vals)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


class PartnerRouteLines(models.TransientModel):
    _name = 'partner.route.map.lines'
    _description = 'Partner Route Lines'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", index=True, default=1)
    partner_id = fields.Many2one('res.partner', required=True)
    partner_route_map_id = fields.Many2one('wizard.partner.route.map')

    user_id = fields.Many2one(comodel_name="res.users", string="Empleado", required=False, )
    visit_reason_id = fields.Many2one(comodel_name="visit.reason", string="Motivo de visita", store=True, )
    visit_date = fields.Datetime(string="Día de visita", required=False, store=True,
                                 help="En caso de ser una visita periodica, se tomara el día de visita como la visita "
                                      "inicial")

    visit_period = fields.Boolean(string="Visitas periodicas", store=True)
    start_period = fields.Date(string="Inicio de periodo de visita", required=False, store=True)
    end_period = fields.Date(string="Fin de periodo de visita", required=False, store=True)
    days_period = fields.Integer(string="Días", required=False, store=True)

    @api.onchange("visit_date")
    def onchange_visit_date(self):
        if self.env['customer.visits'].search(
                [('date', '=', dateutil.parser.parse(self.visit_date.strftime('%Y-%m-%d')).date())]):
            raise UserError(_("Ya existe una visita asignada en la fecha seleccionada"))
