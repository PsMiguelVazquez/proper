# -*- coding: utf-8 -*-
from datetime import datetime

from markupsafe import Markup

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring


class NeteoWizard(models.TransientModel):
    _name = 'neteo.wizard'
    _description = 'Muestra un wizard para el proceso de Pago por compensación de saldos'

    factura_cliente = fields.Many2one('account.move', string='Factura de cliente', help='Factura de cliente que se va a pagar' )
    facturas_proveedor = fields.Many2many('account.move', string='Factura de proveedor', help='Factura de proveedor que se va a pagar' )
    cliente = fields.Many2one('res.partner', string='Cliente', help='Nombre del cliente')
    amount_cliente = fields.Float(string='Monto de la factura del cliente',help='Monto de la factura de cliente')
    amount_proveedor = fields.Float(string='Monto de la factura del proveedor', help='Monto de la factura de proveedor')
    amount = fields.Float(string='Total aplicado', help='Total aplicado', compute='_compute_amount')

    @api.depends('facturas_proveedor')
    def _compute_amount(self):
        for record in self:
            record.amount = sum(record.facturas_proveedor.mapped('porcent_assign'))

    def done_neteo(self):
        if self:
            journal_id = self.env['account.journal'].search([('code','=','NETEO')])
            if not journal_id:
                raise UserError('No hay diario para llevar a cabo la operación de neteo.')
            neteo = self.env['neteo.move'].create({
                'journal_id': journal_id.id,
                'partner_id': self.cliente.id,
                'factura_cliente': self.factura_cliente.id,
                'facturas_proveedor': self.facturas_proveedor.mapped('id')
            })
            if neteo:
                line_ids_list = [
                    {
                        'name': 'NETEO ' + neteo.partner_id.name,
                        'move_id': neteo.move_id.id,
                        'partner_id': neteo.partner_id.id,
                        'account_id': neteo.partner_id.property_account_receivable_id.id,
                        'credit': self.amount,
                    },
                    {
                        # MIGRACIÓN V19: `neteo.name` (delegado de
                        # `move_id.name`) todavía no está asignado en este
                        # punto -se calcula por secuencia recién al hacer
                        # `action_post()`, más abajo-; ya era así en 15.0,
                        # solo que nunca se había ejercido este camino con
                        # datos reales. Se usa el id, disponible de inmediato.
                        'name': 'NETEO ' + str(neteo.id),
                        'move_id': neteo.move_id.id,
                        'partner_id': neteo.partner_id.id,
                        'account_id': neteo.partner_id.property_account_payable_id.id,
                        'debit': self.amount,
                    }
                ]
                lineas = self.env['account.move.line'].create(line_ids_list)
                neteo.action_post()
                invoice_msg = (
                                  "Se generó el Neteo: <a href=# data-oe-model=neteo.move data-oe-id=%d>%s</a> a partir de esta factura") % (
                                  neteo.id, neteo.name)
                neteo_msg = (
                                 "Este movimiento fue creado desde: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                                 self.factura_cliente.id, self.factura_cliente.name)
                # MIGRACIÓN V19: `message_post(..., type=...)` ya no es un
                # kwarg válido; el parámetro correcto es `message_type`
                # ('notification' ya es su valor por defecto). Y `body` debe
                # envolverse en `Markup` para que se renderice como HTML en
                # vez de aparecer como texto crudo (cambio de seguridad
                # anti-XSS del core: un `str` normal ahora se escapa).
                self.factura_cliente.message_post(body=Markup(invoice_msg), message_type="notification")
                self.facturas_proveedor.message_post(body=Markup(invoice_msg), message_type="notification")
                neteo.message_post(body=Markup(neteo_msg), message_type="notification")
                return {
                    'name': _('Neteo'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('neteo_proper.neteo_form_view').id,
                    'res_model': 'neteo.move',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'res_id': neteo.id,
                    'target': 'current',
                }
