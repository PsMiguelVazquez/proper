# -*- coding: utf-8 -*-

from odoo import models, fields, api

usos = [('P01', 'P01 - Por definir'),
        ('G01', 'G01 - Adquisición de mercancías'),
        ('G02', 'G02 - Devoluciones, descuentos o bonificaciones'),
        ('G03', 'G03 - Gastos en general'), ('I01', 'I01 - Construcciones'),
        ('I02', 'I02 - Mobilario y equipo de oficina por inversiones'), ('I03', 'I03 - Equipo de transporte'),
        ('I04', 'I04 - Equipo de cómputo y accesorios'),
        ('I05', 'I05 - Dados, troqueles, moldes, matrices y herramental'),
        ('I06', 'I06 - Comunicaciones telefónicas'), ('I07', 'I07 - Comunicaciones satelitales'),
        ('I08', 'I08 - Otra maquinaria y equipo'),
        ('D01', 'D01 - Honorarios médicos, dentales y gastos hospitalarios.'),
        ('D02', 'D02 - Gastos médicos por incapacidad o discapacidad'), ('D03', 'D03 - Gastos funerales'),
        ('D04', 'D04 - Donativos'),
        ('D05', 'D05 - Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)'),
        ('D06', 'D06 - Aportaciones voluntarias al SAR'), ('D07', 'D07 - Primas por seguros de gastos médicos'),
        ('D08', 'D08 - Gastos de transportación escolar obligatoria'),
        ('D09', 'D09 - Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.'),
        ('D10', 'D10 - Pagos por servicios educativos (colegiaturas)'),
        ('S01', 'S01 - Sin efectos fiscales')]

regimenes = [('601', '601- General de Ley Personas Morales')
    , ('603', '603- Personas Morales con Fines no Lucrativos')
    , ('605', '605- Sueldos y Salarios e Ingresos Asimilados a Salarios')
    , ('606', '606- Arrendamiento')
    , ('607', '607- Régimen de Enajenación o Adquisición de Bienes')
    , ('608', '608- Demás ingresos')
    , ('609', '609- Consolidación')
    , ('610', '610- Residentes en el Extranjero sin Establecimiento Permanente en México')
    , ('611', '611- Ingresos por Dividendos (socios y accionistas)')
    , ('612', '612- Personas Físicas con Actividades Empresariales y Profesionales')
    , ('614', '614- Ingresos por intereses')
    , ('615', '615- Régimen de los ingresos por obtención de premios')
    , ('616', '616- Sin obligaciones fiscales')
    , ('620', '620- Sociedades Cooperativas de Producción que optan por diferir sus ingresos')
    , ('621', '621- Incorporación Fiscal')
    , ('622', '622- Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras')
    , ('623', '623- Opcional para Grupos de Sociedades')
    , ('624', '624- Coordinados')
    , ('625', '625- Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas')
    , ('626', '626- Régimen Simplificado de Confianza - RESICO')
    , ('628', '628- Hidrocarburos')
    , ('629', '629- De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales')
    , ('630', '630- Enajenación de acciones en bolsa de valores')]

# MIGRACIÓN V19: `x_cat_com`, `x_studio_mtodo_de_pago`, `x_nombre_agente_venta`,
# `x_nivel_cliente`, `x_nom_corto_agente_venta`, `x_nombre_corto_tpago`,
# `x_es_marketplace`, `x_grupo_cliente`, `x_estado_cli_actua`,
# `x_studio_triple_a` y `x_studio_lista_de_precios` eran personalizaciones de
# Odoo Studio (creadas directamente en la base de datos de producción de
# v15, sin código de módulo). A partir de esta migración se formalizan aquí
# como campos reales -con el mismo nombre técnico exacto-, de modo que al
# actualizar la base de datos de producción real Odoo reconozca las
# columnas ya existentes y las tome como propias sin perder datos (el campo
# deja de ser `state='manual'` y pasa a pertenecer a este módulo). Los
# modelos propios `x_categoria_compania`, `x_niveles_de_cliente` y
# `x_grupo_cliente` se formalizan igual, con los campos realmente usados por
# el código (se omiten campos de Studio no referenciados por ninguno de los
# 36 módulos, como `x_categoria_compania.x_sub_cat`, para no depender de
# modelos fuera de alcance).


class XSubcategiaCompania(models.Model):
    _name = 'x_subcategia_compania'
    _description = 'Subcategoría de compañía'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XCategoriaCompania(models.Model):
    _name = 'x_categoria_compania'
    _description = 'Categoría de compañía'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Nombre')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')
    # MIGRACIÓN V19: una ronda posterior de formalización sí encontró uso
    # real de este campo (antes se había omitido a propósito).
    x_sub_cat = fields.Many2one('x_subcategia_compania', string='Subcategoría')


class XNivelesDeCliente(models.Model):
    _name = 'x_niveles_de_cliente'
    _description = 'Niveles de cliente'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Nivel de cliente')
    x_active = fields.Boolean(string='Activo', default=True)
    x_res = fields.Many2one('res.partner', string='Cliente')
    x_studio_descripcin_de_lista_de_precios = fields.Char(string='Descripción de lista de precios')
    x_studio_lista_de_precios = fields.Selection([
        ('COMERCIALIZADORAS', 'COMERCIALIZADORAS'),
        ('CATÁLOGOS (ILEALTAD)', 'CATÁLOGOS (ILEALTAD)'),
        ('CATÁLOGOS VENTA DIRECTA', 'CATÁLOGOS VENTA DIRECTA'),
        ('CORPORATIVOS', 'CORPORATIVOS'),
    ], string='Lista de precios')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XGrupoCliente(models.Model):
    _name = 'x_grupo_cliente'
    _description = 'Grupo de cliente'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Nombre')
    x_active = fields.Boolean(string='Activo', default=True)
    x_responsable_grupo_cliente = fields.Many2one('res.users', string='Responsable')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XAgenteDeVenta(models.Model):
    _name = 'x_agente_de_venta'
    _description = 'Agente de venta'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
    x_studio_user_id = fields.Many2one('res.users', string='Responsable')


class XRefBanco(models.Model):
    _name = 'x_ref_banco'
    _description = 'Referencias Bancarias'

    x_banco = fields.Char(string='Banco')
    x_no_cuenta = fields.Char(string='No Cuenta')
    x_contacto = fields.Char(string='Contacto')
    x_telefono = fields.Char(string='Telefono')
    x_anos_apertura = fields.Integer(string='Años de apertura')
    x_ref_cliente = fields.Many2one('res.partner', string='cliente')


class XClaveP(models.Model):
    _name = 'x_clave_p'
    _description = 'Clave proveedor'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Clave')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
    x_user_id = fields.Many2one('res.users', string='Usuario')


class XGrupoProveedor(models.Model):
    _name = 'x_grupo_proveedor'
    _description = 'Grupo proveedor'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Nombre')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')
    x_studio_user_id = fields.Many2one('res.users', string='Responsable')


class XRefComercial(models.Model):
    _name = 'x_ref_comercial'
    _description = 'Referencias Comerciales'

    x_razon_social = fields.Char(string='Razón social')
    x_contacto = fields.Char(string='Contacto')
    x_telefono = fields.Char(string='Telefono')
    x_puesto = fields.Char(string='Puesto')
    x_anos_operar = fields.Integer(string='Años de operar')
    x_plazo = fields.Integer(string='Plazo')
    x_linea_credito = fields.Float(string='Linea de Credito')
    x_rel_id = fields.Many2one('res.partner', string='cliente')


class ResUsers(models.Model):
    _inherit = 'res.users'
    x_studio_clave_del_vendedor_1 = fields.Char(string='Clave Corta')


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    x_nombre_corto = fields.Char(string='Nombre corto')


class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    sales_agent = fields.Many2one('res.users', string='Agente de ventas', store=True)
    codigo_uso_cfdi = fields.Char(string="Código Uso CFDi", compute='_compute_codigo_uso_cfdi', store=False)
    codigo_metodo_pago = fields.Char(string="Codigo forma de pago", compute='_compute_codigo_metodo_pago', store=False)
    x_studio_uso_de_cfdi = fields.Selection(string="Uso de CFDI", selection=usos)
    l10n_mx_edi_fiscal_regime = fields.Selection(selection=regimenes)

    x_cat_com = fields.Many2one('x_categoria_compania', string='Categoría')
    x_studio_mtodo_de_pago = fields.Many2one('l10n_mx_edi.payment.method', string='Forma de Pago')
    x_nombre_agente_venta = fields.Char(string='nombre de agente de venta')
    x_nivel_cliente = fields.Many2one('x_niveles_de_cliente', string='Nivel del cliente')
    x_nombre_corto_tpago = fields.Char(
        string='Política de pago', related='property_payment_term_id.x_nombre_corto', readonly=True)
    x_es_marketplace = fields.Boolean(string='Marketplace')
    x_grupo_cliente = fields.Many2one('x_grupo_cliente', string='Grupo')
    x_estado_cli_actua = fields.Selection([('3.3', '3.3'), ('4', '4')], string='Cliente Actualizado')
    x_studio_triple_a = fields.Boolean(string='Triple A')
    x_studio_lista_de_precios = fields.Selection([
        ('COMERCIALIZADORAS', 'COMERCIALIZADORAS'),
        ('CATÁLOGOS (ILEALTAD)', 'CATÁLOGOS (ILEALTAD)'),
        ('CATÁLOGOS VENTA DIRECTA', 'CATÁLOGOS VENTA DIRECTA'),
        ('CORPORATIVOS', 'CORPORATIVOS'),
    ], string='Lista de precios')
    x_nom_corto_agente_venta = fields.Char(
        string='Clave de agente de venta', compute='_compute_nom_corto_agente_venta', store=True, readonly=True)
    # MIGRACIÓN V19: usado por `sale_purchase_confirm` (account.move.supervisor_credito).
    x_nombre_supervisor_credito = fields.Many2one('res.users', string='Nombre del supervisor de crédito')

    @api.depends('sales_agent', 'sales_agent.x_studio_clave_del_vendedor_1')
    def _compute_nom_corto_agente_venta(self):
        for record in self:
            if record.sales_agent:
                record.x_nom_corto_agente_venta = record.sales_agent.x_studio_clave_del_vendedor_1
            else:
                record.x_nom_corto_agente_venta = False

    @api.onchange('x_cat_com')
    def _on_change_categoria(self):
        # MIGRACIÓN V19: `team_id` no es un campo real de `res.partner` (ni
        # en el core ni en el export de Studio -sin prefijo `x_`, no es una
        # personalización de Studio-); ya era una referencia muerta en
        # 15.0. Se conserva el guard defensivo por no tener forma de
        # resolverlo con los datos disponibles.
        if 'team_id' not in self._fields:
            return
        for record in self:
            if not record.x_cat_com:
                continue
            team_id = self.env['crm.team'].search([('name', '=', record.x_cat_com.x_name)])
            if team_id:
                record.team_id = team_id

    @api.depends('x_studio_uso_de_cfdi')
    def _compute_codigo_uso_cfdi(self):
        for record in self:
            if record.x_studio_uso_de_cfdi:
                record.codigo_uso_cfdi = str(record.x_studio_uso_de_cfdi)
            else:
                record.codigo_uso_cfdi = ''

    @api.depends('x_studio_mtodo_de_pago')
    def _compute_codigo_metodo_pago(self):
        for record in self:
            if record.x_studio_mtodo_de_pago:
                record.codigo_metodo_pago = str(record.x_studio_mtodo_de_pago.code)
            else:
                record.codigo_metodo_pago = ''

    @api.onchange('sales_agent')
    def _on_change_sales_agent(self):
        for record in self:
            record.x_nombre_agente_venta = record.sales_agent.name

    @api.onchange('property_account_position_id')
    def _on_change_property_account_position_id(self):
        for record in self:
            try:
                record.l10n_mx_edi_fiscal_regime = record.property_account_position_id.name.split('-')[0].strip()
            except Exception:
                record.l10n_mx_edi_fiscal_regime = ''

    # MIGRACIÓN V19: este aviso ("se configuró el nivel de cliente...") vivía
    # en un `@api.onchange`, que se dispara mientras el formulario todavía
    # no se guarda -el registro puede ser un `NewId` sin persistir-. En
    # v19 `message_post()` ahora rechaza explícitamente publicarse sobre un
    # registro que no sea "un documento de negocio" ya guardado
    # (`ValueError: Posting a message should be done on a business
    # document`), rompiendo el formulario del contacto en cuanto se tocaba
    # el campo. Se mueve la notificación de "cuándo cambia en el
    # formulario" a "cuándo se guarda de verdad" (`write`/`create`), que
    # es además más correcto: antes se registraba un mensaje en el chatter
    # por cada selección en el combo, incluso si el usuario cancelaba sin
    # guardar.
    def _notify_nivel_cliente_change(self, records):
        for record in records:
            if not record.x_nivel_cliente:
                continue
            message = "Se configuró el nivel de cliente " + record.x_nivel_cliente.x_name + ' para el usuario ' + record.name
            for par in record.commercial_partner_id:
                par.message_post(body=message, message_type="notification", partner_ids=[record.create_uid.partner_id.id])

    def write(self, vals):
        result = super().write(vals)
        if 'x_nivel_cliente' in vals:
            self._notify_nivel_cliente_change(self)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records_to_notify = records.browse(
            record.id for record, vals in zip(records, vals_list) if 'x_nivel_cliente' in vals
        )
        self._notify_nivel_cliente_change(records_to_notify)
        return records
