# -*- coding: utf-8 -*-
from odoo import models, fields


# MIGRACIÓN V19: `x_wizard_rechcoti` era un modelo creado enteramente con
# Odoo Studio (sin código de módulo), usado por el asistente de "Rechazar
# cotización" (ver `views/x_wizard_rechcoti_view.xml` y el botón
# "Rechazar" en `views/sale_order_view.xml`). Se formaliza aquí con el
# mismo nombre técnico y campos que en el export de Studio.
class XWizardRechcoti(models.Model):
    _name = 'x_wizard_rechcoti'
    _description = 'Rechazar cotización'

    x_name = fields.Char(string='Name')
    x_descripcion = fields.Text(string='Motivo de rechazo')
    x_rel = fields.Many2one('sale.order', string='Cotización')
