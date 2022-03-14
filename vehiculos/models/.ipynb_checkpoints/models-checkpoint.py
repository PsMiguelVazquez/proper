# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression
class MarcaAutomovil(models.Model):
    _name='marca.automovil'
    _description='Marca del Automovil'
    name = fields.Char('Marca', required=True)
    imagen=fields.Binary()

    
class ModelAutomovil(models.Model):
    _name = 'modelo.automovil'
    _description = 'Modelo de Automovil'
    name = fields.Char('Nombre del modelo', required=True)
    marca_id = fields.Many2one('marca.automovil', string='Marca', required=True)
    imagen = fields.Binary(related='marca_id.imagen', string="Logo", readonly=False)
    
class Automovil(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'automovil'
    _description = 'Automovil'
    name = fields.Char(store=True)
    active = fields.Boolean('Active', default=True, track_visibility="onchange")
    compania = fields.Many2one('res.company', 'Company')
    license_plate = fields.Char()
    vin_sn = fields.Char('Chassis Number')
    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange", help='Driver of the vehicle', copy=False, auto_join=True)
    modelo = fields.Many2one('modelo.automovil', 'Model')
    fecha_adquisicion = fields.Date('Fecha de Adquisición')
    color = fields.Char(help='Color')
    ubicacion = fields.Char(help='Ubicacion del automovil (garage, ...)')
    asientos = fields.Integer('Numero de asientos', help='Numero de asientos del automovil')
    ano_modelo = fields.Char('Año Molelo',help='El año del modelo')
    puertas = fields.Integer('Numero puerta', help='Numero de puestas de automovil', default=5)
    odometro = fields.Float('Ultimio odometro')
    unidad_odometro = fields.Selection([('kilometros', 'Kilómetros'),('millas', 'Millas')], default='kilometros', required=True)
    transmision = fields.Selection([('manual', 'Manual'), ('automatico', 'Automatico')], 'Transmision', help='Transmision')
    fuel_type = fields.Selection([('gasolina', 'Gasolina'),('diesel', 'Diesel'),('electricio', 'Electrico'),('hybrido', 'Hybrido')], 'Tipo de Combustible')
    caballos = fields.Integer()
    imagen = fields.Binary(related='modelo.imagen', string="Logo", readonly=False)
    valor_auto = fields.Float(string="Valor de catalogo (IVA Incl.)")



