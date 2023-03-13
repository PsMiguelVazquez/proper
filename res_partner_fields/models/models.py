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


class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    sales_agent = fields.Many2one('res.users', string='Agente de ventas', store=True)
    codigo_uso_cfdi = fields.Char(string="Código Uso CFDi", compute='_compute_codigo_uso_cfdi', store=False)
    codigo_metodo_pago = fields.Char(string="Codigo forma de pago", compute='_compute_codigo_metodo_pago', store=False)
    x_studio_uso_de_cfdi = fields.Selection(string="Uso de CFDI", selection=usos)
    l10n_mx_edi_fiscal_regime = fields.Selection(selection=regimenes)
    @api.onchange('x_cat_com')
    def _on_change_categoria(self):
        for record in self:
            team_id = self.env['crm.team'].search([('name', '=', record.x_cat_com.x_name)])
            if team_id:
                record.team_id = team_id



    def _compute_codigo_uso_cfdi(self):
        for record in self:
            if record.x_studio_uso_de_cfdi:
                record.codigo_uso_cfdi = str(record.x_studio_uso_de_cfdi)
            else:
                record.codigo_uso_cfdi = ''

    def _compute_codigo_metodo_pago(self):
        for record in self:
            if record.x_studio_mtodo_de_pago:
                record.codigo_metodo_pago = str(record.x_studio_mtodo_de_pago.code)
            else:
                record.codigo_metodo_pago = ''

    @api.onchange('sales_agent')
    def _on_change_sales_agent(self):
        for record in self:
            self.x_nombre_agente_venta = record.sales_agent.name

    @api.onchange('property_account_position_id')
    def _on_change_property_account_position_id(self):
        for record in self:
            try:
                record.l10n_mx_edi_fiscal_regime = record.property_account_position_id.name.split('-')[0].strip()
            except:
                record.l10n_mx_edi_fiscal_regime =''

    @api.onchange('x_nivel_cliente')
    def _on_change_level(self):
        for record in self:
            if record.x_nivel_cliente:
                partner = record.commercial_partner_id
                for par in partner:
                    message = "Se configuró el nivel de cliente " + record.x_nivel_cliente.x_name + ' para el usuario ' + record.name
                    par.message_post(body=message, type="notification", partner_ids=[record.create_uid.partner_id.id])