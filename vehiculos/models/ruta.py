from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)


class CreacionRuta(Model):
    _name='creacion.ruta'
    _description = 'Ruta'
    name=fields.Char()
    chofer = fields.Many2one('res.users')
    vehiculo=fields.Many2one('fleet.vehicle')
    ordenes=fields.Many2many('stock.picking')
    zona=fields.Selection([["SUR","SUR"],["NORTE","NORTE"],["PONIENTE","PONIENTE"],["ORIENTE","ORIENTE"],["CENTRO","CENTRO"],["DISTRIBUIDOR","DISTRIBUIDOR"],["MONTERREY","MONTERREY"],["CUERNAVACA","CUERNAVACA"],["GUADALAJARA","GUADALAJARA"],["QUERETARO","QUERETARO"],["CANCUN","CANCUN"],["VERACRUZ","VERACRUZ"],["PUEBLA","PUEBLA"],["TOLUCA","TOLUCA"],["LEON","LEON"],["COMODIN","COMODIN"],["VILLAHERMOSA","VILLAHERMOSA"],["MERIDA","MERIDA"],["VERACRUZ","VERACRUZ"],["ALTAMIRA","ALTAMIRA"]])
    estado=fields.Selection([["borrador","Borrador"],["valido","Confirmado"]])
    odometro=fields.Integer()
    nivel_tanque=fields.Selection([["reserva","Reserva"],[".25","1/4"],[".5","1/2"],[".75","3/4"],["1","Lleno"]])
    tipo=fields.Selection([["local","Local"],["foraneo","Foraneo"],["guadalajara","Guadalajara"],["monterrey","Monterrey"],["queretaro","Querétaro"]])
    EstadoPais=fields.Many2one('res.country.state',string="Estado")
    EstadoPaisName=fields.Char(related='EstadoPais.name',string="Estado")
    ticket=fields.Char()
    #almacen=fields.Many2one('stock.warehouse')
    #picking_type=fields.Many2many('stock.picking.type')
    usuarios = fields.Many2many('res.users')
    arreglo=fields.Char()
    active = fields.Boolean('Active', default=True, track_visibility=True)

    def confirmar(self):
        if len(self.ordenes) > 0:
            self.ordenes.write({'ruta_id':self.id})
            self.ordenes.write({'estado':'ruta'})
            self.ordenes.write({'ajusta':True})
            self.estado="valido"
            #if(self.chofer.id):
            #    us=self.env['res.users'].search([['id','=', 1380]])
            #    _logger.info(us.name)
            if(self.odometro==0 and self.tipo.lower()=="local"):
                raise UserError(_('Tiene que ingresas el Odometro'))
            for o in self.ordenes:
                o.write({'ruta_id': self.id, 'chofer': self.chofer.id})
            odometroAnterior = self.env['fleet.vehicle.odometer'].search([['vehicle_id','=',self.vehiculo.id]], order='id desc',limit=1)
            odometroAnt = odometroAnterior.value if(odometroAnterior.id) else 0
            if(odometroAnt>=self.odometro and self.tipo.lower()=="local"):
                raise UserError(_('Registro de odometro invalido debe ser mayor al anterior. Favor de revisar'))    
            if(self.odometro>odometroAnt):
                self.vehiculo.write({'driver_id': self.chofer.partner_id.id})
                self.env['fleet.vehicle.assignation.log'].create({'vehicle_id': self.vehiculo.id, 'driver_id': self.chofer.partner_id.id, 'date_start': fields.Date.today(), 'date_end': fields.Date.today()})
                self.env['fleet.vehicle.odometer'].sudo().create({'vehicle_id': self.vehiculo.id, 'value': self.odometro, 'nivel_tanque': self.nivel_tanque,'driver_id': self.chofer.partner_id.id})
        else:
            raise UserError(_('No se ha selaccionado ninguna orden'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ruta') or _('New')
        result = super(CreacionRuta, self).create(vals)
        return result
    
    @api.onchange('tipo')
    def dominio(self):
        res={}
        operacion=self.env['stock.picking.type'].search([['code','=','outgoing']])
        u=operacion
        res['domain'] = {'ordenes':["&","&","&",["picking_type_id.id","in",u.mapped('id')],["ruta_id","=",False],["state","=","assigned"],["state","!=","done"]]}
        return res


class StockPicking(Model):
    _inherit = 'stock.picking'
    ruta_id = fields.Many2one('creacion.ruta')
    guia = fields.Char()
    estado = fields.Selection([('recepcion','Recepción'),('draft', 'Draft'),('almacen', 'Almacen'),('compras', 'Solicitud de Compra'),('waiting', 'Esperando otra operación'),('confirmed', 'Sin Stock'),('assigned', 'Por Validar'),('done', 'Validado'),('distribucion', 'Distribución'),('cancel', 'Cancelled'),('aDistribucion', 'A Distribución'),('Xenrutar', 'Por en Rutar'),('ruta', 'En Ruta'),('entregado', 'Entregado')],store=True)
    chofer = fields.Many2one('res.users')
    ajusta = fields.Boolean('Ajusta',store=True)

