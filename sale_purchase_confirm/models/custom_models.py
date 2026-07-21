# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: `x_fabricante`, `x_familia`, `x_linea`, `x_grupo`,
`x_caracteristica_1`, `x_color`, `x_sublinea`, `x_modelo_del_producto` y
`x_numero_de_serie_arti`/`x_numero_de_serie_moto` eran modelos propios
creados enteramente con Odoo Studio en la base de datos de producción de
v15 (sin código de módulo), usados para clasificar productos y calcular
márgenes por nivel de cliente. Se formalizan aquí con los mismos nombres
técnicos y campos que en el export de Studio, para que al actualizar la
base de datos de producción real Odoo tome las tablas ya existentes sin
perder datos.
"""

from odoo import models, fields


class XFabricante(models.Model):
    _name = 'x_fabricante'
    _description = 'Fabricante'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_margen_A = fields.Float(string='Margen A')
    x_studio_margen_B = fields.Float(string='Margen B')
    x_studio_margen_C = fields.Float(string='Margen C')
    x_studio_margen_D = fields.Float(string='Margen D')
    x_studio_margen_E = fields.Float(string='Margen E')
    x_studio_margen_F = fields.Float(string='Margen F')
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XFamilia(models.Model):
    _name = 'x_familia'
    _description = 'Familia'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XLinea(models.Model):
    _name = 'x_linea'
    _description = 'Línea'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XGrupo(models.Model):
    _name = 'x_grupo'
    _description = 'Grupo'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XCaracteristica1(models.Model):
    _name = 'x_caracteristica_1'
    _description = 'Característica 1'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XColor(models.Model):
    _name = 'x_color'
    _description = 'Color'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XSublinea(models.Model):
    _name = 'x_sublinea'
    _description = 'Sublínea'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XMarca(models.Model):
    _name = 'x_marca'
    _description = 'Marca'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XLargo(models.Model):
    _name = 'x_largo'
    _description = 'Largo'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XMarcaDelProducto(models.Model):
    _name = 'x_marca_del_producto'
    _description = 'Marca del producto'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_notes = fields.Text(string='Notas')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XModeloDelProducto(models.Model):
    _name = 'x_modelo_del_producto'
    _description = 'Modelo del producto'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
    # MIGRACIÓN V19: usados por `product.template.x_studio_fabricante_del_producto`/
    # `x_studio_marca` (formalizados en `studio_fields_v19`).
    x_studio_many2one_field_KjDbr = fields.Many2one('x_fabricante', string='Fabricante')
    x_studio_many2one_field_qQUTn = fields.Many2one('x_marca_del_producto', string='Marca del producto')


class XEstadoDelProducto(models.Model):
    _name = 'x_estado_del_producto'
    _description = 'Estado del producto'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XConceptosDeBaja(models.Model):
    _name = 'x_conceptos_de_baja'
    _description = 'Conceptos de baja'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XConceptosBasicosDe(models.Model):
    _name = 'x_conceptos_basicos_de'
    _description = 'Conceptos básicos de operación'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XWizardPartner(models.Model):
    _name = 'x_wizard_partner'
    _description = 'Asistente de nuevo cliente'

    x_partner_id = fields.Many2one('res.partner', string='Cliente')
    x_sale_id = fields.Many2one('sale.order', string='Pedido de venta')
    x_solicitud_credito = fields.Binary(string='Solicitud Credito')
    x_uso_cfdi = fields.Selection(
        [('P01', 'P01 - Por definir'), ('G01', 'G01 - Adquisición de mercancías'),
         ('G03', 'G03 - Gastos en general')],
        string='Uso de CFDI')
    x_rfc = fields.Char(string='RFC')
    x_correo = fields.Char(string='Correo')
    x_copia_estado_cuenta = fields.Binary(string='Copia Estado Cuenta')
    x_copia_identificaion = fields.Binary(string='Copia Identificación')
    x_metodo_pago = fields.Many2one('l10n_mx_edi.payment.method', string='Método de pago')
    x_constancia_fiscal = fields.Binary(string='Constancia Fiscal')


class XTemporadas(models.Model):
    _name = 'x_temporadas'
    _description = 'Temporadas'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
    x_color = fields.Integer(string='Color')
    x_fecha1 = fields.Date(string='Fecha inicio')
    x_fecha2 = fields.Date(string='Fecha fin')


class XSegmento(models.Model):
    _name = 'x_segmento'
    _description = 'Segmento'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Segmento')
    x_active = fields.Boolean(string='Activo', default=True)
    x_descripcion = fields.Char(string='Criterio del segmento')
    x_studio_sequence = fields.Integer(string='Secuencia')


class XNumeroDeSerieArti(models.Model):
    _name = 'x_numero_de_serie_arti'
    _description = 'Numero de serie articulo'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')


class XNumeroDeSerieMoto(models.Model):
    _name = 'x_numero_de_serie_moto'
    _description = 'Número de serie Motor'
    _rec_name = 'x_name'

    x_name = fields.Char(string='Name')
    x_active = fields.Boolean(string='Activo', default=True)
    x_studio_sequence = fields.Integer(string='Secuencia')
