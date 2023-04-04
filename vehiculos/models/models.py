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
    odometro_registro=fields.One2many('registro.odometro','rel_vehiculo')


class Odometro(models.Model):
    _name='registro.odometro'
    _description='Registro de Odometro'
    chofer=fields.Many2one('hr.employee')
    odometro=fields.Integer()
    nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])
    rel_vehiculo=fields.Many2one('automovil')


class Fleet(models.Model):
    _inherit = 'fleet.vehicle'
    nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])


class FleetOdometro(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    carrier_tracking_ref = fields.Char(string='Tracking Reference')
    guia = fields.Char(string='No de Guia')
    # def _compute_address(self):
    #     for record in self:
    #         #if record.sale_id:
    #         record.update({'carrier_tracking_ref': record.sale_id.carrier_tracking_ref})
    #         #else:
    #          #   record.update({'carrier_tracking_ref': False})
    #
    # def _inverse_street(self):
    #     for company in self:
    #         company.sale_id.carrier_tracking_ref = company.carrier_tracking_ref

    def write(self, vals):
        if 'carrier_tracking_ref' in vals:
            if self.sale_id:
                self.sale_id.write({'carrier_tracking_ref': vals['carrier_tracking_ref']})
        return super(StockPicking, self).write(vals)



class StockPickingLL(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    evidencia = fields.Binary('Evidencia')
    code = fields.Boolean(default=False)

    def process(self):
        r = super(StockPickingLL, self).process()
        return r

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    facturas = fields.Many2many('account.move', 'Facturas', compute='get_facturas')


    @api.depends('write_date', 'picking_id')
    def get_facturas(self):
        for record in self:
            record.facturas = record.picking_id.mapped('sale_id.invoice_ids')




