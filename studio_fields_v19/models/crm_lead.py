# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_fecha = fields.Text(
        string='Fecha', compute='_compute_x_fecha', store=True)
    x_probabilidad_lead = fields.Float(
        string='Probabilidad', compute='_compute_x_probabilidad_lead', store=True)

    @api.depends('partner_id')
    def _compute_x_fecha(self):
        for record in self:
            hoy = datetime.date.today()
            array = str(hoy).split('-')
            meses = ["Unknown", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
                     "Septiembre", "Octubrer", "Noviembre", "Diciembre"]
            record.x_fecha = "Ciudad de México a " + str(array[2]) + ' de ' + meses[int(array[1])] \
                + " del " + str(array[0])

    # MIGRACIÓN V19: `mobile` ya no existe como campo propio de crm.lead (se
    # unificó con `phone` en versiones anteriores del core); se retiran las
    # ramas que sólo evaluaban `mobile` por separado, quedan cubiertas por
    # `phone`.
    @api.depends('email_from', 'phone', 'contact_name')
    def _compute_x_probabilidad_lead(self):
        for record in self:
            if record.email_from and record.phone and record.contact_name:
                record.x_probabilidad_lead = 10
            elif (record.contact_name and record.phone) or (record.contact_name and record.email_from):
                record.x_probabilidad_lead = 7
            elif record.phone and record.email_from:
                record.x_probabilidad_lead = 6
            elif record.contact_name and not record.phone and not record.email_from:
                record.x_probabilidad_lead = 4
            elif (record.phone and not record.contact_name and not record.email_from) \
                    or (record.email_from and not record.contact_name and not record.phone):
                record.x_probabilidad_lead = 3
            else:
                record.x_probabilidad_lead = 0
