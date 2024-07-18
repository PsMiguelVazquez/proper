from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    #ine = fields.Boolean(string='INE', default=False)
    #identificacion_representante_legal = fields.Boolean(string='Identificación de representante legal', default=False)
    #llenado_solicitud = fields.Boolean(string='Llenado de solicitud', default=False)

    #giro = fields.Char(string='Giro')
    giro = fields.Selection([('abarrotes','Abarrotes'), ('abastecimiento_hotelero','Abastecimiento Hotelero'), ('accesorios_para_el_hogar','Accesorios Para El Hogar'), ('aceites_y_lubricantes','Aceites Y Lubricantes'), ('ahorro_y_credito_popula','Ahorro Y Credito Popula'), ('alimentos','Alimentos'),('automotriz','Automotriz'), ('bebidas','Bebidas'), ('cafeterías','Cafeterías'), ('canastas_y_arcones_navideños','Canastas Y Arcones Navideños'),('cines','Cines'), ('comercializadora','Comercializadora'), ('comercializadora_y_viajes','Comercializadora Y Viajes'), ('comunicaciones','Comunicaciones'), ('conductores_electricos','Conductores Eléctricos'), ('constructora','Constructora'), ('consultoria_y_comercialziación_','Consultoria Y Comercialziación '), ('cooperativa','Cooperativa'), ('cuidado_personal','Cuidado Personal'), ('distribuidora','Distribuidora'), ('distribuidora_de_juguetes','Distribuidora De Juguetes'), ('embotelladora','Embotelladora'), ('empresa_de_envases','Empresa De Envases'), ('entretenimiento','Entretenimiento'), ('equipos_de_oficina','Equipos De Oficina'), ('estudios_de_mercado','Estudios De Mercado'), ('fabricante_de_hilos_industriales','Fabricante De Hilos Industriales'), ('fabricantes','Fabricantes'), ('fabricantes_de_muebles_para_el_hogar','Fabricantes De Muebles Para El Hogar'), ('farmaceutica','Farmaceutica'), ('ferreterias','Ferreterías'), ('fundacion','Fundación'), ('gasolineros','Gasolineros'), ('higiene','Higiene'), ('hospital_','Hospital '), ('hotelero','Hotelero'), ('industria_quimica_y_petroquimica','Industria Química Y Petroquímica'), ('inmobiliaria_','Inmobiliaria '), ('insumos_cocina','Insumos Cocina'),  ('laboratorios_y_farmaceutica','Laboratorios Y Farmaceutica'), ('limpieza_del_hogar','Limpieza Del Hogar'), ('maquiladora_de_ropa_','Maquiladora De Ropa '), ('papelera','Papelera'), ('plataforma_de_pagos_','Plataforma De Pagos '), ('programas_de_incentivos_y_lealtad','Programas De Incentivos Y Lealtad'), ('programas_de_lealtad','Programas De Lealtad'), ('refrigeracion','Refrigeracion'), ('servicios_graficos_','Servicios Gráficos '), ('servicios_logisticos','Servicios Logisticos'), ('soluciones_integrales_en_seguridad','Soluciones Integrales En Seguridad'), ('suministro_de_equipos_de_limpieza','Suministro De Equipos De Limpieza'), ('tecnologia','Tecnologia'), ('television','Television'),  ('tienda_de_autoservicio','Tienda de autoservicio'), ('tienda_de_conveniencia','Tienda de conveniencia'), ('transporte','Transporte'), ('venta_directa','Venta Directa'), ('venta_mayoreo','Venta mayoreo'), ('zapateria','Zapateria')], string='Giro')
    
    segmento = fields.Selection([('cuentas_especiales','Cuentas Especiales'), ('jr','Jr.'), ('kam','KAM'), ('proper_services','Proper Services')], string='Segmento')
    
    temporalidad = fields.Selection([('una_vez_al_anio','1 Vez Al Año'),('esporadico','Esporádico'),('semestrales','Semestrales'),('todo_el_anio ','Todo El Año'),('trimestrales','Trimestrales')], string='Temporalidad')
    es_admin = fields.Boolean(compute="_compute_es_solo_lectura")

    @api.depends('user_id')
    def _compute_es_solo_lectura(self):
        for record in self:
            user = self.env.user
            _logger.error('user {}'.format(user))
            # Verifica si el usuario pertenece a un grupo específico
            esta_en_grupo = user.has_group('sales_team.group_sale_salesman_all_leads')
            #esta_en_grupo_2 = user.has_group('Usuario: Gerente Ventas documentos equipo')
            _logger.error('esta_en_grupo {}'.format(esta_en_grupo))
            record.es_admin = user.has_group('sales_team.group_sale_salesman_all_leads')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            #if not vals.get('partner_name'):
                #raise ValidationError('El campo Nombre empresa es requerido.')
            _logger.error('create vals {}'.format(vals))
            if not vals['contact_name']:
                _logger.error('contact_name {}'.format(vals.get('contact_name')))
                raise ValidationError('El campo Nombre del contacto es requerido.')
            if not vals['email_from']:
                raise ValidationError('El campo Correo Electronico es requerido.')
            if not vals['phone']:
                raise ValidationError('El campo Telefono es requerido.')
            if not vals['source_id']:
                raise ValidationError('El campo Digital (Origen) es requerido.')
                
        leads = super(CrmLead, self).create(vals_list)

        return leads 


    def write(self, vals):
       # Loguea los valores recibidos en 'vals'
        _logger.error('edit vals {}'.format(vals))

        # Validación de campos obligatorios
        if 'contact_name' in vals and (not vals.get('contact_name') or vals.get('contact_name') == ''):
            _logger.error('vals[contact_name] {}'.format(vals.get('contact_name')))
            raise ValidationError('El campo Nombre del contacto es requerido.')
        
        if 'email_from' in vals and (not vals.get('email_from') or vals.get('email_from') == ''):
            raise ValidationError('El campo Correo es requerido.')
        
        if 'phone' in vals and (not vals.get('phone') or vals.get('phone') == ''):
            raise ValidationError('El campo Teléfono es requerido.')

        if 'source_id' in vals and (not vals.get('source_id') or vals.get('source_id') == ''):
            raise ValidationError('El campo Digital (Origen) es requerido.')

        # Llama al método write del modelo padre
        result = super(CrmLead, self).write(vals)
        
        return result