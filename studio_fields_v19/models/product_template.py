# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # MIGRACIÓN V19: campos manuales de Studio usados por la vista de
    # formulario de producto formalizada (ver
    # `views/product_template_form.xml`). Antes sólo vivían como metadatos
    # de Studio (`ir.model.fields` state=manual) y se perdían en cada
    # rebuild de Odoo.sh; se declaran aquí para que sobrevivan.
    x_es_auto_moto = fields.Boolean(string='Auto/Moto')
    x_tipo_transporte_ma = fields.Selection(
        [('moto', 'Motocicleta'), ('auto', 'Automóvil')], string='Tipo de transporte')
    x_producto_propuesta = fields.Boolean(string='Por configurar')
    x_studio_rama = fields.Selection(
        [('SOBREPEDIDO', 'SOBREPEDIDO'), ('LINEA', 'LINEA'), ('OBSOLETO', 'OBSOLETO'),
         ('DESCONTINUADO', 'DESCONTINUADO'), ('CATALOGO', 'CATALOGO'), ('ACTIVO FIJO', 'ACTIVO FIJO'),
         ('ADMON', 'ADMON'), ('DESCONTINUA', 'DESCONTINUA'), ('PROMOCION', 'PROMOCION'),
         ('Producto prueba', 'Producto prueba'), ('IMPORTACION', 'IMPORTACION'), ('GASTO', 'GASTO')],
        string='Rama')
    x_studio_costo_de_lista = fields.Monetary(string='Costo de lista', currency_field='currency_id')
    x_studio_ultimo_costo = fields.Monetary(string='Ultimo Costo', currency_field='currency_id')
    x_num_motor_vemot = fields.Char(string='Número de motor')
    x_studio_eliminar_producto = fields.Boolean(string='Eliminar Producto')
    x_studio_peso_caja_master = fields.Float(string='Peso caja master')
    x_studio_alto_c_m = fields.Float(string='Alto c-m')
    x_studio_largo_c_m = fields.Float(string='Largo c-m')
    x_studio_ancho_c_m = fields.Float(string='Ancho c-m')
    x_Al = fields.Float(string='Alto')
    x_An = fields.Float(string='Ancho')
    x_La = fields.Float(string='Largo')
    x_Alto = fields.Char(string='Alto')
    x_largo = fields.Char(string='Largo')
    x_studio_volumen = fields.Float(string='Volumen')
    x_studio_ancho_1 = fields.Float(string='Ancho')
    x_bin_auto = fields.Boolean(string='BIN')
    x_bin_detalle = fields.Char(string='Detalle del BIN')
    x_cilindros_auto = fields.Integer(string='Cilindros')
    x_clave_vehicular = fields.Char(string='Clave vehicular')
    x_num_puertas = fields.Integer(string='Número de puertas')
    x_transmision_auto = fields.Char(string='Transmisión')
    x_version_auto = fields.Char(string='Versión')
    x_placas = fields.Char(string='Placas')
    x_repuve = fields.Char(string='REPUVE')
    x_modelo_vemot = fields.Integer(string='Año Modelo')
    x_cilindraje_moto = fields.Char(string='Cilindraje')

    # MIGRACIÓN V19: en Studio eran `related=`; se mantienen igual.
    x_studio_alto = fields.Char(related='product_variant_id.x_Alto', store=True, string='Alto')
    x_studio_largo_2 = fields.Char(related='product_variant_id.x_largo', store=True, string='Largo')
    x_studio_alto_c_m_1 = fields.Float(
        related='product_variant_id.x_studio_alto_c_m', string='Alto c-m')
    x_studio_ancho_c_m_1 = fields.Float(
        related='product_variant_id.x_studio_ancho_c_m', string='Ancho c-m')
    x_studio_largo_c_m_2 = fields.Float(
        related='product_variant_id.x_studio_largo_c_m', string='Largo c-m')
    x_studio_volumen_c_m_2 = fields.Float(
        related='product_variant_id.x_studio_volumen_c_m', string='Volumen c-m')
    x_num_propuesta = fields.Char(
        related='product_variant_id.x_num_pro', store=True, string='Numero de propuesta')

    # MIGRACIÓN V19: modelos propios de Studio, formalizados en
    # `sale_purchase_confirm/models/custom_models.py` (junto con
    # `x_fabricante`/`x_familia`/`x_linea`/`x_grupo`, ya formalizados ahí).
    x_studio_many2one_field_0X3u9 = fields.Many2one('x_grupo', string='Grupo')
    x_studio_many2one_field_RWuq7 = fields.Many2one('x_familia', string='Familia')
    x_studio_many2one_field_LZOP8 = fields.Many2one('x_linea', string='Línea')
    x_studio_many2one_field_CGUKb = fields.Many2one('x_caracteristica_1', string='Característica 1')
    x_studio_color = fields.Many2one('x_color', string='Color')
    x_studio_many2one_field_et5Lo = fields.Many2one('x_sublinea', string='Sublínea')
    x_fabricante = fields.Many2one('x_fabricante', string='Marca')
    x_studio_many2one_field_AqNlU = fields.Many2one(
        'x_modelo_del_producto', string='Modelo del producto anterior')
    x_studio_many2one_field_NsBLe = fields.Many2one(
        'x_numero_de_serie_arti', string='Número de serie articulo')
    x_numero_serie_vemot = fields.Many2one('x_numero_de_serie_moto', string='Número de serie')

    # MIGRACIÓN V19: sin `store` a propósito (ver `common.py`): sin
    # `@api.depends`, `store=True` sólo calcularía estos campos una vez, al
    # crear el registro, y nunca se volverían a evaluar.
    x_studio_volumen_c_m = fields.Float(
        string='Volumen c-m', compute='_compute_x_studio_volumen_c_m')
    x_vol = fields.Float(
        string='Volumen', compute='_compute_x_vol')

    # MIGRACIÓN V19: `x_studio_alto_c_m`/`x_studio_ancho_c_m`/
    # `x_studio_largo_c_m` ya no son campos "fantasma" de Studio, ahora se
    # formalizan arriba; se puede depender de ellos normalmente.
    @api.depends('x_studio_alto_c_m', 'x_studio_ancho_c_m', 'x_studio_largo_c_m')
    def _compute_x_studio_volumen_c_m(self):
        for record in self:
            record.x_studio_volumen_c_m = (
                record.x_studio_alto_c_m * record.x_studio_ancho_c_m * record.x_studio_largo_c_m)

    @api.depends('x_Al', 'x_An', 'x_La')
    def _compute_x_vol(self):
        for record in self:
            record.x_vol = record.x_Al * record.x_An * record.x_La


class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_num_pro = fields.Char(string='Num Pro')
    # MIGRACIÓN V19: campo propio de Studio en `product.product` (no
    # delegado desde `product.template`), usado por la lista de variantes
    # embebida en `crm.lead.form` (ver `views/crm_lead_form.xml`).
    x_studio_many2one_field_AqNlU = fields.Many2one(
        'x_modelo_del_producto', string='Modelo del producto anterior')
    # MIGRACIÓN V19: en Studio eran `related=` hacia `product_tmpl_id`.
    x_Alto = fields.Char(related='product_tmpl_id.x_Alto', string='Alto')
    x_largo = fields.Char(related='product_tmpl_id.x_largo', string='Largo')
    x_studio_alto_c_m = fields.Float(related='product_tmpl_id.x_studio_alto_c_m', string='Alto c-m')
    x_studio_ancho_c_m = fields.Float(related='product_tmpl_id.x_studio_ancho_c_m', string='Ancho c-m')
    x_studio_largo_c_m = fields.Float(related='product_tmpl_id.x_studio_largo_c_m', string='Largo c-m')
    x_studio_volumen_c_m = fields.Float(
        related='product_tmpl_id.x_studio_volumen_c_m', string='Volumen c-m')
