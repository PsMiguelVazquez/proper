from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ine = fields.Boolean(string='INE', default=False)
    identificacion_representante_legal = fields.Boolean(string='Identificación de representante legal', default=False)
    llenado_solicitud = fields.Boolean(string='Llenado de solicitud', default=False)
    origen = fields.Many2one(string='Origen', comodel_name='utm.source')
    opinion_cumplimiento = fields.Boolean(string='Opinin de cumpplimiento', default=False)
    comprobante_domicilio = fields.Boolean(string='Comprobante de domicilio', default=False)

    tipo_compra = fields.Selection([('2_catálogos_revista_especial_revista_asesoras_consumo_interno','2 Catálogos  Revista Especial / Revista Asesoras / Consumo interno'),
('campañas','Campañas'),
('campañas_consumo_interno_regalos_de_fin_de_año','Campañas / Consumo Interno / Regalos De Fin De Año'),
('catálogos','Catálogos'),
('catálogos_campañas','Catálogos / Campañas'),
('catálogos_incentivos_regalos_de_fin_de_año','Catálogos /Incentivos / Regalos De Fin De Año'),
('catálogos_programas_especiales','Catálogos / Programas especiales'),
('catálogos_regalos_de_fin_de_año','Catálogos / Regalos De Fin De Año'),
('catálogos_revista_especial_revista_asesoras_consumo_interno','Catálogos  Revista Especial / Revista Asesoras / Consumo interno'),
('consumo_interno','Consumo Interno'),
('consumo_interno_incentivos','Consumo Interno / Incentivos'),
('consumo_interno_regalos_de_fin_de_año','Consumo Interno/ Regalos De Fin De Año'),
('consumo_interno_regalos_de_fin_de_año_incentivos','Consumo Interno / Regalos De Fin De Año / Incentivos'),
('consumo_interno_reventa','Consumo Interno / Reventa'),
('incentivos','Incentivos'),
('incentivos_consumo_interno_regalos_de_fin_de_año','Incentivos / Consumo Interno / Regalos De Fin De Año'),
('incentivos_regalos_de_fin_de_año','Incentivos / Regalos de fin de año'),
('regalos_de_fin_de_año_','Regalos De Fin De Año'),
('reventa','Reventa')], string='Tipo de compra')
    