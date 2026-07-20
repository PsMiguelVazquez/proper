# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_partner_id_account_move_count = fields.Integer(
        string='Partner count', compute='_compute_x_partner_id_account_move_count')
    x_x_holding__res_partner_count = fields.Integer(
        string='Empresa count', compute='_compute_x_x_holding__res_partner_count')

    # MIGRACIÓN V19: campos manuales de Studio usados por la vista de
    # formulario formalizada (ver `views/res_partner_form.xml`). Antes sólo
    # vivían como metadatos de Studio y se perdían en cada rebuild de
    # Odoo.sh; se declaran aquí para que sobrevivan.
    x_studio_estatus_de_la_cuenta = fields.Selection(
        [('Alta', 'Alta'), ('Baja', 'Baja'), ('Bloqueado', 'Bloqueado'), ('En legal', 'En legal'),
         ('Cambio de razon social', 'Cambio de razon social')],
        string='Estatus de la Cuenta')
    x_studio_entre_las_calles = fields.Char(string='Entre las calles')
    x_studio_plano = fields.Char(string='Plano')
    x_sector = fields.Selection(
        [('COMERCIALIZADORA', 'COMERCIALIZADORA'), ('CORPORATIVO', 'CORPORATIVO'),
         ('VENTA DIRECTA', 'VENTA DIRECTA'), ('PARTICULAR', 'PARTICULAR')],
        string='Sector de compañia')
    x_es_cliente = fields.Selection(
        [('cliente', 'cliente'), ('proveedor', 'proveedor'), ('ambos', 'son ambos'),
         ('acreedor', 'ACREEDOR')],
        string='Tipo de Empresa')
    x_conductor = fields.Boolean(string='¿Es Conductor?')
    x_tel_oficina = fields.Char(string='Teléfono de oficina')
    x_ext = fields.Char(string='Ext.')
    x_otro_tel = fields.Char(string='Otro teléfono')
    x_otra_ext = fields.Char(string='Ext.')

    _DIAS_SEMANA = [
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'), ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo'),
    ]
    x_dia1 = fields.Selection(_DIAS_SEMANA, string='Día')
    x_dia2 = fields.Selection(_DIAS_SEMANA, string='Día')
    x_dia3 = fields.Selection(_DIAS_SEMANA, string='Día')
    x_dia4 = fields.Selection(_DIAS_SEMANA, string='Día')
    x_hora1 = fields.Char(string='Hora')
    x_hora2 = fields.Char(string='Hora')

    x_studio_por_segmento_de_vendedor = fields.Selection(
        [('cuentas_especiales', 'Cuentas Especiales'), ('jr', 'Jr.'), ('kam', 'KAM'),
         ('proper_services', 'Proper Services')],
        string='Por segmento de vendedor')
    x_studio_temporalidad = fields.Selection(
        [('todo_el_anio', 'Todo El Año'), ('semestrales', 'Semestrales'), ('trimestrales', 'Trimestrales'),
         ('una_vez_al_anio', '1 Vez Al Año'), ('esporadico', 'Esporádico')],
        string='Temporalidad')
    x_studio_giro_1 = fields.Selection(
        [('abarrotes', 'Abarrotes'), ('abastecimiento_hotelero', 'Abastecimiento Hotelero'),
         ('aceites_y_lubricantes', 'Aceites Y Lubricantes'),
         ('ahorro_y_credito_popula', 'Ahorro Y Credito Popula'), ('alimentos', 'Alimentos'),
         ('automotriz', 'Automotriz'), ('bebidas', 'Bebidas'), ('cafeterías', 'Cafeterías'),
         ('canastas_y_arcones_navideños', 'Canastas Y Arcones Navideños'),
         ('comercializadora', 'Comercializadora'), ('comercializadora_y_viajes', 'Comercializadora Y Viajes'),
         ('conductores_electricos', 'Conductores Eléctricos'), ('constructora', 'Constructora'),
         ('consultoria_y_comercialziación_', 'Consultoria Y Comercialziación'), ('cooperativa', 'Cooperativa'),
         ('cuidado_personal', 'Cuidado Personal'), ('distribuidora', 'Distribuidora'),
         ('distribuidora_de_juguetes', 'Distribuidora De Juguetes'), ('embotelladora', 'Embotelladora'),
         ('empresa_de_envases', 'Empresa De EnvasesEntretenimiento'), ('entretenimiento', 'Entretenimiento'),
         ('equipos_de_oficina', 'Equipos De Oficina'), ('estudios_de_mercado', 'Estudios De Mercado'),
         ('fabricante_de_hilos_industriales', 'Fabricante De Hilos Industriales'),
         ('fabricantes', 'Fabricantes'),
         ('fabricantes_de_muebles_para_el_hogar', 'Fabricantes De Muebles Para El Hogar'),
         ('farmaceutica', 'Farmaceutica'), ('ferreterias', 'Ferreterías'), ('fundacion', 'Fundación'),
         ('gasolineros', 'Gasolineros'), ('higiene', 'Higiene'), ('hospital_', 'Hospital'),
         ('hotelero', 'Hotelero'), ('industria_quimica_y_petroquimica', 'Industria Química Y Petroquímica'),
         ('inmobiliaria_', 'Inmobiliaria'), ('insumos_cocina', 'Insumos Cocina'),
         ('limpieza_del_hogar', 'Limpieza Del Hogar'), ('maquiladora_de_ropa_', 'Maquiladora De Ropa'),
         ('papelera', 'Papelera'), ('plataforma_de_pagos_', 'Plataforma De Pagos'),
         ('programas_de_incentivos_y_lealtad', 'Programas De Incentivos Y Lealtad'),
         ('programas_de_lealtad', 'Programas De Lealtad'), ('refrigeracion', 'Refrigeracion'),
         ('servicios_graficos_', 'Servicios Gráficos'),
         ('soluciones_integrales_en_seguridad', 'Soluciones Integrales En Seguridad'),
         ('suministro_de_equipos_de_limpieza', 'Suministro De Equipos De Limpieza'),
         ('tecnologia', 'Tecnologia'), ('television', 'Television'),
         ('tienda_de_autoservicio', 'Tienda de autoservicio'), ('tienda_de_conveniencia', 'Tienda de conveniencia'),
         ('transporte', 'Transporte'), ('venta_directa', 'Venta Directa'), ('venta_mayoreo', 'Venta mayoreo'),
         ('zapateria', 'Zapateria'), ('accesorios_para_el_hogar', 'Accesorios Para El Hogar'),
         ('cines', 'Cines'), ('comunicaciones', 'Comunicaciones'),
         ('laboratorios_y_farmaceutica', 'Laboratorios Y Farmaceutica'),
         ('servicios_logisticos', 'Servicios Logisticos')],
        string='Giro')

    x_studio_catlogos_revista_especial = fields.Boolean(string='Catálogos Revista Especial')
    x_studio_revista_asesoras = fields.Boolean(string='Revista Asesoras')
    x_studio_incentivos_1 = fields.Boolean(string='Incentivos')
    x_studio_reventa = fields.Boolean(string='Reventa')
    x_studio_campaas_1 = fields.Boolean(string='Campañas')
    x_studio_programa_especial = fields.Boolean(string='Programa especial')
    x_studio_consumo_interno = fields.Boolean(string='Consumo Interno')
    x_studio_catlogos = fields.Boolean(string='Catálogos')
    x_studio_regalos_de_fin_de_ao = fields.Boolean(string='Regalos fin de año')

    x_fecha_alta = fields.Datetime(string='Fecha de alta')
    x_studio_nombre_corto = fields.Char(string='Nombre Corto')
    x_comprador_proveedor = fields.Many2one('res.users', string='Nombre del comprador')
    x_num_cliente = fields.Char(string='Número de Cliente')
    x_num_pro = fields.Char(string='Número de proveedor')
    x_nombre_agente_servicio = fields.Many2one('res.users', string='Nombre de Agente de servicio')

    x_studio_usuario = fields.Char(string='Usuario')
    x_contra_usu_portal = fields.Char(string='Constraseña')
    x_studio_manejo_de_portal = fields.Char(string='Manejo de Portal')
    x_archivo_alta_cliente = fields.Binary(string='Alta de Clientes')
    x_studio_requiere_un_nmero_de_entrada_para_revision = fields.Boolean(
        string='Requiere un Número de Entrada para Revision')
    x_studio_documentacion_cuando_se_entrega_mercancia = fields.Selection(
        [('Folio', 'Folio'), ('Hoja de entrada', 'Hoja de entrada'), ('Otro', 'Otro')],
        string='Documentacion cuando se entrega Mercancia')
    _DIAS_LABORALES = [
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miercoles', 'Miercoles'), ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'), ('LunesViernes', 'Lunes a Viernes'),
    ]
    x_studio_dias_de_revision = fields.Selection(_DIAS_LABORALES, string='Dias de Revision')
    x_nota_dia_revision = fields.Text(string='Notas de revisión')
    x_studio_dias_de_pago = fields.Selection(_DIAS_LABORALES, string='Dias de Pago')
    x_nota_dia_pago = fields.Text(string='Nota de pago')
    x_studio_maneja_factoraje = fields.Boolean(string='Maneja Factoraje')

    x_studio_adjunto_poltica_de_pagos = fields.Binary(string='Política de pagos')
    x_studio_adjunto_poltica_de_pagos_filename = fields.Char(string='Nombre de archivo (política de pagos)')
    x_studio_binary_field_1omC5 = fields.Binary(string='Manual del portal')
    x_studio_binary_field_1omC5_filename = fields.Char(string='Nombre de archivo (manual del portal)')
    x_studio_otros_1 = fields.Binary(string='Otros 1')
    x_studio_otros_1_filename = fields.Char(string='Nombre de archivo (otros 1)')

    x_studio_acta_constitutiva = fields.Boolean(string='Acta Constitutiva')
    x_studio_copia_del_acta_constitutiva = fields.Binary(string='Copia del Acta Constitutiva')
    x_studio_constancia_situacin_fiscal = fields.Date(string='Constancia Situación Fiscal')
    x_studio_constancia_fiscal = fields.Binary(string='Constancia Fiscal')
    x_studio_fecha_de_constancia = fields.Date(string='Fecha de constancia')
    x_studio_opinion_de_cumplimiento = fields.Date(string='Opinión de Cumplimiento')
    x_studio_binary_field_vmKoa = fields.Binary(string='Para la opinión de cumplimiento')
    x_studio_binary_field_vmKoa_filename = fields.Char(string='Nombre de archivo (opinión de cumplimiento)')
    x_estados_financieros = fields.Text(string='Estados Financieros')
    x_studio_copia_de_los_estados_financieros = fields.Binary(string='Copia de los Estados Financieros')
    x_declaracion_anual = fields.Text(string='Declaracion Anual')
    x_estado_cuenta_bancario = fields.Text(string='Estado de Cuenta Bancario ( copia )')
    x_studio_copia_del_comprobante_de_domicilio = fields.Binary(string='Copia del Comprobante de Domicilio')
    x_pagare = fields.Monetary(string='Pagare')
    x_studio_copia_identificacion = fields.Binary(string='Copia Identificacion')
    x_comprobante_domicilio = fields.Boolean(string='Comprobante Domicilio')
    x_copia_INE = fields.Char(string='Copia INE')
    x_aval_nombre = fields.Char(string='Aval (es) Nombre (s)')
    x_notificaciones_fiscales_cliente = fields.Text(string='Notificaciones Fiscales del Cliente')
    x_notas_revision = fields.Html(string='Notas')

    # MIGRACIÓN V19: en Studio era `related='team_id.user_id.display_name'`,
    # pero `team_id` nunca existió como campo real de `res.partner` (ver
    # comentario en `res_partner_fields/models/models.py`, ya detectado ahí
    # como referencia muerta desde 15.0). Se usa la misma cadena correcta
    # que el campo gemelo `x_gerente_venta` (a través de
    # `user_id.sale_team_id`, en `res.users`).
    x_ad_equipo_venta_gerente = fields.Char(
        related='user_id.sale_team_id.user_id.display_name', string='Gerente de venta')
    x_clave_supervisor_credito = fields.Char(
        related='x_nombre_supervisor_credito.x_studio_clave_del_vendedor_1',
        string='Clave de supervisor de crédito')
    x_clave_agente_servicio = fields.Char(
        related='x_nombre_agente_servicio.x_studio_clave_del_vendedor_1',
        string='Clave de agente de servicio')
    x_cuenta_proveedor = fields.Many2one(
        'account.account', related='property_account_payable_id', string='Cuenta a pagar de proveedor')
    x_cuenta_cliente = fields.Many2one(
        'account.account', related='property_account_receivable_id', string='cuentas de cliente')

    # MIGRACIÓN V19: modelos propios de Studio, formalizados en
    # `res_partner_fields/models/models.py` (junto con `x_categoria_compania`/
    # `x_niveles_de_cliente`/`x_grupo_cliente`, ya formalizados ahí).
    x_clave_proveedor = fields.Many2one('x_clave_p', string='Clave de proveedor')
    x_grupo_proveedor = fields.Many2one('x_grupo_proveedor', string='Grupo Proveedor')
    x_studio_ref_comercial = fields.One2many(
        'x_ref_comercial', 'x_rel_id', string='Referencias Comerciales')

    def _compute_x_partner_id_account_move_count(self):
        for record in self:
            record.x_partner_id_account_move_count = self.env['account.move'].search_count(
                [('partner_id', '=', record.id)])

    def _compute_x_x_holding__res_partner_count(self):
        # MIGRACIÓN V19: el original usaba `read_group` con la firma antigua
        # (diccionarios con clave `<campo>_count`); se reescribe con
        # `search_count`, más simple y compatible. `x_holding` es un campo
        # de Odoo Studio que puede no existir en todas las bases (ver
        # `common.py`); si no existe, el conteo queda en 0.
        if 'x_holding' not in self._fields:
            self.x_x_holding__res_partner_count = 0
            return
        for record in self:
            record.x_x_holding__res_partner_count = self.env['res.partner'].search_count(
                [('x_holding', '=', record.id)])
