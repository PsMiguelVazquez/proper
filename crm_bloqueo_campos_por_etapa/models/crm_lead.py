from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    giro = fields.Selection([('abarrotes','Abarrotes'), ('abastecimiento_hotelero','Abastecimiento Hotelero'), ('accesorios_para_el_hogar','Accesorios Para El Hogar'), ('aceites_y_lubricantes','Aceites Y Lubricantes'), ('ahorro_y_credito_popula','Ahorro Y Credito Popula'), ('alimentos','Alimentos'),('automotriz','Automotriz'), ('bebidas','Bebidas'), ('cafeterías','Cafeterías'), ('canastas_y_arcones_navideños','Canastas Y Arcones Navideños'),('cines','Cines'), ('comercializadora','Comercializadora'), ('comercializadora_y_viajes','Comercializadora Y Viajes'), ('comunicaciones','Comunicaciones'), ('conductores_electricos','Conductores Eléctricos'), ('constructora','Constructora'), ('consultoria_y_comercialziación_','Consultoria Y Comercialziación '), ('cooperativa','Cooperativa'), ('cuidado_personal','Cuidado Personal'), ('distribuidora','Distribuidora'), ('distribuidora_de_juguetes','Distribuidora De Juguetes'), ('embotelladora','Embotelladora'), ('empresa_de_envases','Empresa De Envases'), ('entretenimiento','Entretenimiento'), ('equipos_de_oficina','Equipos De Oficina'), ('estudios_de_mercado','Estudios De Mercado'), ('fabricante_de_hilos_industriales','Fabricante De Hilos Industriales'), ('fabricantes','Fabricantes'), ('fabricantes_de_muebles_para_el_hogar','Fabricantes De Muebles Para El Hogar'), ('farmaceutica','Farmaceutica'), ('ferreterias','Ferreterías'), ('fundacion','Fundación'), ('gasolineros','Gasolineros'), ('higiene','Higiene'), ('hospital_','Hospital '), ('hotelero','Hotelero'), ('industria_quimica_y_petroquimica','Industria Química Y Petroquímica'), ('inmobiliaria_','Inmobiliaria '), ('insumos_cocina','Insumos Cocina'),  ('laboratorios_y_farmaceutica','Laboratorios Y Farmaceutica'), ('limpieza_del_hogar','Limpieza Del Hogar'), ('maquiladora_de_ropa_','Maquiladora De Ropa '), ('papelera','Papelera'), ('plataforma_de_pagos_','Plataforma De Pagos '), ('programas_de_incentivos_y_lealtad','Programas De Incentivos Y Lealtad'), ('programas_de_lealtad','Programas De Lealtad'), ('refrigeracion','Refrigeracion'), ('servicios_graficos_','Servicios Gráficos '), ('servicios_logisticos','Servicios Logisticos'), ('soluciones_integrales_en_seguridad','Soluciones Integrales En Seguridad'), ('suministro_de_equipos_de_limpieza','Suministro De Equipos De Limpieza'), ('tecnologia','Tecnologia'), ('television','Television'),  ('tienda_de_autoservicio','Tienda de autoservicio'), ('tienda_de_conveniencia','Tienda de conveniencia'), ('transporte','Transporte'), ('venta_directa','Venta Directa'), ('venta_mayoreo','Venta mayoreo'), ('zapateria','Zapateria')], string='Giro')

    segmento = fields.Selection([('cuentas_especiales','Cuentas Especiales'), ('jr','Jr.'), ('kam','KAM'), ('proper_services','Proper Services')], string='Segmento')

    temporalidad = fields.Selection([('una_vez_al_anio','1 Vez Al Año'),('esporadico','Esporádico'),('semestrales','Semestrales'),('todo_el_anio','Todo El Año'),('trimestrales','Trimestrales')], string='Temporalidad')
    es_admin = fields.Boolean(compute="_compute_es_solo_lectura")

    @api.depends('user_id')
    def _compute_es_solo_lectura(self):
        for record in self:
            user = self.env.user
            # Verifica si el usuario pertenece a un grupo específico ADMIN DE MARKETING social.group_social_manager
            esta_en_grupo = user.has_group('social.group_social_manager')
            esta_en_grupo2 = user.has_group('crm_bloqueo_campos_por_etapa.gerente_mostrar_documentos_equipo')
            if esta_en_grupo or esta_en_grupo2:
                record.es_admin = True
            else:
                record.es_admin = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('contact_name'):
                raise ValidationError('El campo Nombre del contacto es requerido.')
            if not vals.get('email_from'):
                raise ValidationError('El campo Correo Electronico es requerido.')
            if not vals.get('phone'):
                raise ValidationError('El campo Telefono es requerido.')
            if not vals.get('source_id'):
                raise ValidationError('El campo Digital (Origen) es requerido.')

        leads = super(CrmLead, self).create(vals_list)

        return leads

    def write(self, vals):
        # Validación de campos obligatorios
        if 'contact_name' in vals and (not vals.get('contact_name') or vals.get('contact_name') == ''):
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
            self.contact_name = self.partner_id.name
            self.source_id = self.partner_id.origen.id
            # MIGRACIÓN V19: `x_studio_por_segmento_de_vendedor`, `x_studio_temporalidad`
            # y `x_studio_giro_1` son campos creados con Studio directamente sobre la
            # base de datos de producción de v15 (no existen como código de módulo,
            # por lo que no se migran junto con este módulo). Si el partner todavía
            # no tiene esos campos (p.ej. base de datos nueva sin recrearlos en
            # Studio), se omite el prellenado en vez de fallar el onchange.
            partner_fields = self.partner_id._fields
            if 'x_studio_por_segmento_de_vendedor' in partner_fields:
                self.segmento = self.partner_id.x_studio_por_segmento_de_vendedor
            if 'x_studio_temporalidad' in partner_fields:
                self.temporalidad = self.partner_id.x_studio_temporalidad
            if 'x_studio_giro_1' in partner_fields:
                self.giro = self.partner_id.x_studio_giro_1
