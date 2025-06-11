from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
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
    
    temporalidad = fields.Selection([('una_vez_al_anio','1 Vez Al Año'),('esporadico','Esporádico'),('semestrales','Semestrales'),('todo_el_anio','Todo El Año'),('trimestrales','Trimestrales')], string='Temporalidad')
    es_admin = fields.Boolean(compute="_compute_es_solo_lectura")

    @api.depends('user_id')
    def _compute_es_solo_lectura(self):
        for record in self:
            user = self.env.user
            _logger.error('user {}'.format(user))
            # Verifica si el usuario pertenece a un grupo específico ADMIN DE MARKETING social.group_social_manager
            esta_en_grupo = user.has_group('social.group_social_manager')
            esta_en_grupo2 = user.has_group('crm_bloqueo_campos_por_etapa.gerente_mostrar_documentos_equipo')
            group_id = 118  # ID interno del grupo
            es_miembro = user.groups_id.filtered(lambda g: g.id == group_id)
            
            #esta_en_grupo_2 = user.has_group('Usuario: Gerente Ventas documentos equipo')
            _logger.error('esta_en_grupo {} {}'.format(esta_en_grupo, es_miembro.id))
           # if esta_en_grupo or es_miembro:
            if esta_en_grupo or esta_en_grupo2:
                _logger.error('TRUE')
                record.es_admin = True
            else:
                _logger.error('FALSE')
                record.es_admin = False


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

    @api.onchange('partner_id')
    def _completa_info_cliente(self):
        if self.partner_id:
            #self.email_from = self.partner_id.email
            #self.phone = self.partner_id.phone
            _logger.error('self.partner_id.x_studio_por_segmento_de_vendedor {}'.format(self.partner_id.x_studio_por_segmento_de_vendedor))
            self.contact_name = self.partner_id.name
            self.source_id = self.partner_id.origen.id
            self.segmento = self.partner_id.x_studio_por_segmento_de_vendedor
            self.temporalidad = self.partner_id.x_studio_temporalidad
            self.giro = self.partner_id.x_studio_giro_1


    #METODO QUE EJECUTA LA ACCION AUTOMATIZADA Novu: CRM - bloquea cambio de etapa por falta de información
    def validar_informacion(self):
        for record in self:
            #se obtiene la info del partner actual
            partner = record.partner_id
        
            # Verificar si la etapa del registro es 'Seguimiento'
            if record.stage_id.display_name == 'Oportunidad':
              # Lista para recolectar los campos faltantes
              campos_faltantes = []
              
              # Verificar si los campos esenciales están rellenados (no son None o cadena vacía) GIRO, TIPO COMPRA, INE, UBICACION
              if not partner.x_studio_giro_1:
                campos_faltantes.append('Giro')
              if not partner.tipo_compra:
                campos_faltantes.append('Tipo de Compra')
              #if not partner.ine:
                #campos_faltantes.append('INE')
              if record.quotation_count == 0:
                campos_faltantes.append('Cotizacion')
              if record.expected_revenue == 0.0:
                campos_faltantes.append('Ingresos esperados')
                
              # Lanzar un error si hay campos faltantes
              if campos_faltantes:
                  raise UserError(f'Los siguientes campos son requeridos para cambiar a la etapa {record.stage_id.display_name}: {", ".join(campos_faltantes)}')
                  
                    
            if record.stage_id.display_name == 'Evaluación':
              # Lista para recolectar los campos faltantes
              campos_faltantes = []
              
              #CAMPOS DE SEGUIMIENTO
              if not partner.x_studio_giro_1:
                  campos_faltantes.append('Giro')
              if not partner.tipo_compra:
                campos_faltantes.append('Tipo de Compra')
              #if not partner.ine:
                #campos_faltantes.append('INE')
              if record.quotation_count == 0:
                campos_faltantes.append('Cotizacion')
              if record.expected_revenue == 0.0:
                campos_faltantes.append('Ingresos esperados')
                
              #CAMPOS DE EVALUACION
              if not partner.opinion_cumplimiento:
                campos_faltantes.append('Opinion de cumplimiento')
              if not partner.identificacion_representante_legal:
                campos_faltantes.append('Identificación de representante legal')
              if not partner.comprobante_domicilio:
                campos_faltantes.append('Comprobante de domicilio')
              if not partner.llenado_solicitud:
                campos_faltantes.append('Llenado de solicitud de credito')
                
              # Lanzar un error si hay campos faltantes
              if campos_faltantes:
                raise UserError(f'Los siguientes campos son requeridos para cambiar a la etapa {record.stage_id.display_name}: {", ".join(campos_faltantes)}')
                
                
            if record.stage_id.display_name == 'Alta':
              # Lista para recolectar los campos faltantes
              campos_faltantes = []
              
              #CAMPOS DE SEGUIMIENTO
              if not partner.x_studio_giro_1:
                  campos_faltantes.append('Giro')
              if not partner.tipo_compra:
                campos_faltantes.append('Tipo de Compra')
              #if not partner.ine:
                #campos_faltantes.append('INE')
              if record.quotation_count == 0:
                campos_faltantes.append('Cotizacion')
              if record.expected_revenue == 0.0:
                campos_faltantes.append('Ingresos esperados')
                
              #CAMPOS DE EVALUACION
              if not partner.opinion_cumplimiento:
                campos_faltantes.append('Opinion de cumplimiento')
              if not partner.identificacion_representante_legal:
                campos_faltantes.append('Identificación de representante legal')
              if not partner.comprobante_domicilio:
                campos_faltantes.append('Comprobante de domicilio')
              if not partner.llenado_solicitud:
                campos_faltantes.append('Llenado de solicitud de credito')
                
              # Lanzar un error si hay campos faltantes
              if campos_faltantes:
                raise UserError(f'Los siguientes campos son requeridos para cambiar a la etapa {record.stage_id.display_name}: {", ".join(campos_faltantes)}')
                
                  
            if record.stage_id.display_name == 'Ganado':
              # Lista para recolectar los campos faltantes
              campos_faltantes = []
              
              #CAMPOS DE SEGUIMIENTO
              if not partner.x_studio_giro_1:
                campos_faltantes.append('Giro')
              if not partner.tipo_compra:
                campos_faltantes.append('Tipo de Compra')
              #if not partner.ine:
                #campos_faltantes.append('INE')
              #if record.quotation_count == 0:
                #campos_faltantes.append('Cotizacion')
              if record.expected_revenue == 0.0:
                campos_faltantes.append('Ingresos esperados')
                
              #CAMPOS DE EVALUACION
              if not partner.opinion_cumplimiento:
                campos_faltantes.append('Opinion de cumplimiento')
              if not partner.identificacion_representante_legal:
                campos_faltantes.append('Identificación de representante legal')
              if not partner.comprobante_domicilio:
                campos_faltantes.append('Comprobante de domicilio')
              if not partner.llenado_solicitud:
                campos_faltantes.append('Llenado de solicitud de credito')
              
              #CAMPOS GANADO
              if not record.sale_amount_total:
                campos_faltantes.append('Orden de Venta')
                
              # Lanzar un error si hay campos faltantes
              if campos_faltantes:
                raise UserError(f'Los siguientes campos son requeridos para cambiar a la etapa {record.stage_id.display_name}: {", ".join(campos_faltantes)}')


            
        