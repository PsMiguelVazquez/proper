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
    x_Alto = fields.Char(string='Alto (texto)')
    x_largo = fields.Char(string='Largo (texto)')
    x_studio_volumen = fields.Float(string='Volumen')
    x_studio_ancho_1 = fields.Float(string='Ancho (Studio)')
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

    # MIGRACIÓN V19: en Studio eran `related='product_variant_id...'`.
    # `product_variant_id` es un campo `compute` sin `search=` (no se puede
    # buscar por él), así que Odoo no puede armar el árbol de disparo para
    # saber qué plantillas recalcular cuando cambia el dato en la variante
    # -eso es lo que avisa el `UserWarning: ... should be searchable`, no
    # rompe nada pero el campo puede quedar desactualizado en caché-. Se
    # reescriben como compute normal a través de `product_variant_ids`
    # (el One2many real, almacenado y buscable) tomando la primera
    # variante, que si dispara los recálculos correctamente.
    x_studio_alto = fields.Char(
        string='Alto (variante)', compute='_compute_x_studio_alto_largo', store=True)
    x_studio_largo_2 = fields.Char(
        string='Largo (variante)', compute='_compute_x_studio_alto_largo', store=True)
    x_studio_alto_c_m_1 = fields.Float(
        string='Alto c-m (plantilla)', compute='_compute_x_studio_medidas_c_m_1')
    x_studio_ancho_c_m_1 = fields.Float(
        string='Ancho c-m (plantilla)', compute='_compute_x_studio_medidas_c_m_1')
    x_studio_largo_c_m_2 = fields.Float(
        string='Largo c-m (plantilla)', compute='_compute_x_studio_medidas_c_m_1')
    x_studio_volumen_c_m_2 = fields.Float(
        string='Volumen c-m (plantilla)', compute='_compute_x_studio_medidas_c_m_1')
    x_num_propuesta = fields.Char(
        string='Numero de propuesta', compute='_compute_x_num_propuesta', store=True)

    @api.depends('product_variant_ids.x_Alto', 'product_variant_ids.x_largo')
    def _compute_x_studio_alto_largo(self):
        for record in self:
            variant = record.product_variant_ids[:1]
            record.x_studio_alto = variant.x_Alto
            record.x_studio_largo_2 = variant.x_largo

    @api.depends('product_variant_ids.x_studio_alto_c_m', 'product_variant_ids.x_studio_ancho_c_m',
                 'product_variant_ids.x_studio_largo_c_m', 'product_variant_ids.x_studio_volumen_c_m')
    def _compute_x_studio_medidas_c_m_1(self):
        for record in self:
            variant = record.product_variant_ids[:1]
            record.x_studio_alto_c_m_1 = variant.x_studio_alto_c_m
            record.x_studio_ancho_c_m_1 = variant.x_studio_ancho_c_m
            record.x_studio_largo_c_m_2 = variant.x_studio_largo_c_m
            record.x_studio_volumen_c_m_2 = variant.x_studio_volumen_c_m

    @api.depends('product_variant_ids.x_num_pro')
    def _compute_x_num_propuesta(self):
        for record in self:
            record.x_num_propuesta = record.product_variant_ids[:1].x_num_pro

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
        string='Volumen (Al×An×La)', compute='_compute_x_vol')

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

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio (export
    # "Campos (ir.model.fields) (3)"). No se agregan a ninguna vista -eso
    # quedó fuera de alcance de esta tanda-, sólo se formalizan como
    # campos reales para que no se pierdan en el próximo rebuild.
    x_studio_many2one_field_Dp30u = fields.Many2one('stock.picking', string='Albarán')
    x_studio_cantidad_a_pedir = fields.Text(string='Cantidad a pedir')
    x_studio_adquirir = fields.Boolean(string='Adquirir')
    x_studio_many2one_field_3tVuB = fields.Many2one('x_marca', string='X Studio Many2One Field 3Tvub')
    x_studio_marca_1 = fields.Char(string='Marca (texto)')
    x_studio_many2one_field_KG3IS = fields.Many2one('x_marca', string='Marca (x_marca)')
    x_studio_many2one_field_voXz4 = fields.Many2one(
        'x_marca_del_producto', string='X Studio Many2One Field Voxz4')
    x_studio_float_field_XqVhh = fields.Float(string='New Decimal')
    x_studio_many2one_field_RteqX = fields.Many2one('x_largo', string='Largo (selección)')
    x_studio_many2one_field_Nzndt = fields.Many2one('x_largo', string='Largo (selección 2)')
    x_studio_ancho = fields.Integer(string='Ancho (entero)')
    x_studio_monetary_field_ppjZO = fields.Monetary(string='New Monetario')
    # MIGRACIÓN V19: estos 3 son duplicados con nombre de Studio de los
    # campos reales `de_hogar`/`proper`/`tienda_linea` (módulo
    # `novu_tiendas_15_19`) -esos ya están formalizados con su propio
    # nombre técnico, comentados en la vista de Studio-; se formalizan
    # igual porque sí tienen datos propios guardados en producción.
    x_studio_de_hogar = fields.Boolean(string='De Hogar (Studio)')
    x_studio_proper = fields.Boolean(string='Proper (Studio)')
    x_studio_tienda_en_linea = fields.Boolean(string='Tienda en linea')

    # MIGRACIÓN V19: en Studio eran `related=` a través de campos
    # `Many2one` (`property_stock_inventory`/`x_studio_many2one_field_AqNlU`),
    # se mantienen igual.
    x_studio_related_field_xVNKQ = fields.Char(
        related='property_stock_inventory.name', string='Ubicación de inventario')
    x_studio_related_field_jjrgH = fields.Char(
        related='property_stock_inventory.location_id.parent_path', string='Ruta de ubicación de inventario')
    # MIGRACIÓN V19: `warehouse_id` en `product.template`/`product.product`
    # es `store=False` sin `compute=` -existe sólo para recibir un valor
    # desde el contexto de búsqueda y así filtrar otros campos calculados,
    # nunca tiene un valor real en un registro normal (ver
    # `addons/stock/models/product.py`)-. Un `related=` a través de él
    # nunca traería dato real (ni en Studio, en v15 tenía la misma
    # limitación) y además dispara el `UserWarning: ... should be
    # searchable` porque Odoo no puede saber cuándo recalcularlo; se
    # dejan como campos planos en vez de `related=`.
    x_studio_related_field_ZYZfw = fields.Selection(
        [('view', 'View'), ('internal', 'Internal'), ('customer', 'Customer'), ('vendor', 'Vendor'),
         ('inventory', 'Inventory'), ('production', 'Production'), ('transit', 'Transit Location')],
        string='Tipo de ubicación')
    x_studio_related_field_RFqJS = fields.Char(string='Almacén (referencia)')
    x_studio_fabricante_del_producto = fields.Many2one(
        'x_fabricante', related='x_studio_many2one_field_AqNlU.x_studio_many2one_field_KjDbr',
        string='Fabricante del producto')
    x_studio_marca = fields.Many2one(
        'x_marca_del_producto', related='x_studio_many2one_field_AqNlU.x_studio_many2one_field_qQUTn',
        string='*Marca')
    # MIGRACIÓN V19: en Studio eran `related='product_variant_id...'`;
    # igual que el bloque de medidas más arriba, se reescriben como
    # compute a través de `product_variant_ids` (buscable) en vez de
    # `product_variant_id` (compute sin `search=`, dispara el
    # `UserWarning: ... should be searchable`).
    x_studio_largo = fields.Char(string='Largo (Studio)', compute='_compute_x_studio_largo_variante')
    x_studio_largo_1 = fields.Many2one(
        'x_largo', string='Largo (relación)', compute='_compute_x_studio_largo_variante')
    x_studio_stock_disponible = fields.Float(
        string='Stock Total', compute='_compute_x_studio_stock_disponible')
    # MIGRACIÓN V19: en Studio era `related='product_variant_id.price'`,
    # pero `price` (precio contextual por lista de precios) ya no existe
    # como campo de `product.product` -mismo campo que ya se quitó de la
    # vista de `crm.lead.form` por esta razón-; se deja como campo plano.
    x_studio_related_field_hPxQY = fields.Float(string='Precio (heredado)')
    x_studio_related_field_HW6gD = fields.Selection(
        [('sale', 'Ventas'), ('purchase', 'Compras'), ('none', 'Ninguno')],
        string='Tipo de impuesto (proveedor)', compute='_compute_x_studio_related_field_HW6gD')
    x_studio_largo_c_m_1 = fields.Float(
        string='Largo c-m (duplicado)', compute='_compute_x_studio_largo_c_m_1')
    # MIGRACIÓN V19: `warehouse_id` en `product.product` tiene la misma
    # limitación explicada arriba (`store=False` sin `compute=`, nunca
    # tiene valor real); se deja como campo plano en vez de `related=`.
    x_studio_related_field_sPlxt = fields.Char(string='Almacén (producto)')
    x_studio_related_field_TcPtR = fields.Char(
        string='Ubicación de inventario (variante)', compute='_compute_x_studio_related_field_TcPtR')
    # MIGRACIÓN V19: en Studio era `related='product_variant_id.seller_ids.
    # name.name'`. `seller_ids` ya vive en `product.template` -no varía por
    # variante-, así que no hace falta pasar por `product_variant_id`
    # (fuente del warning "should be searchable" en producción, mismo
    # motivo que el resto de estos campos); se toma directo desde
    # `seller_ids` del propio registro.
    x_studio_proveedor = fields.Char(
        string='Proveedor', compute='_compute_x_studio_proveedor')

    # MIGRACIÓN V19: en Studio era `related=` a través de
    # `product_variant_id` (`Many2one`) hacia `supplier_taxes_id`
    # (`Many2many` en `product.product`); `related=` no soporta ese último
    # salto x2many, así que se declara igual que el campo que referencia
    # (`Many2many` propio, sin `related=`) en vez de intentar heredarlo.
    x_studio_related_field_wVH62 = fields.Many2many(
        'account.tax', 'product_template_supplier_taxes_wVH62_rel', string='Impuestos proveedor (relacionado)')

    @api.depends('product_variant_ids.x_largo', 'product_variant_ids.x_studio_many2one_field_RteqX')
    def _compute_x_studio_largo_variante(self):
        for record in self:
            variant = record.product_variant_ids[:1]
            record.x_studio_largo = variant.x_largo
            record.x_studio_largo_1 = variant.x_studio_many2one_field_RteqX

    @api.depends('product_variant_ids.qty_available')
    def _compute_x_studio_stock_disponible(self):
        for record in self:
            record.x_studio_stock_disponible = record.product_variant_ids[:1].qty_available

    @api.depends('product_variant_ids.supplier_taxes_id.type_tax_use')
    def _compute_x_studio_related_field_HW6gD(self):
        for record in self:
            record.x_studio_related_field_HW6gD = record.product_variant_ids[:1].supplier_taxes_id[:1].type_tax_use

    @api.depends('product_variant_ids.x_studio_largo_c_m')
    def _compute_x_studio_largo_c_m_1(self):
        for record in self:
            record.x_studio_largo_c_m_1 = record.product_variant_ids[:1].x_studio_largo_c_m

    @api.depends('product_variant_ids.property_stock_inventory.name')
    def _compute_x_studio_related_field_TcPtR(self):
        for record in self:
            record.x_studio_related_field_TcPtR = record.product_variant_ids[:1].property_stock_inventory.name

    @api.depends('seller_ids.partner_id.name')
    def _compute_x_studio_proveedor(self):
        for record in self:
            record.x_studio_proveedor = record.seller_ids[:1].partner_id.name


class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_num_pro = fields.Char(string='Num Pro')
    # MIGRACIÓN V19: campo propio de Studio en `product.product` (no
    # delegado desde `product.template`), usado por la lista de variantes
    # embebida en `crm.lead.form` (ver `views/crm_lead_form.xml`).
    x_studio_many2one_field_AqNlU = fields.Many2one(
        'x_modelo_del_producto', string='Modelo del producto anterior')
    # MIGRACIÓN V19: en Studio eran `related=` hacia `product_tmpl_id`.
    x_Alto = fields.Char(related='product_tmpl_id.x_Alto', string='Alto (texto)')
    x_largo = fields.Char(related='product_tmpl_id.x_largo', string='Largo (texto)')
    x_studio_alto_c_m = fields.Float(related='product_tmpl_id.x_studio_alto_c_m', string='Alto c-m')
    x_studio_ancho_c_m = fields.Float(related='product_tmpl_id.x_studio_ancho_c_m', string='Ancho c-m')
    x_studio_largo_c_m = fields.Float(related='product_tmpl_id.x_studio_largo_c_m', string='Largo c-m')
    x_studio_volumen_c_m = fields.Float(
        related='product_tmpl_id.x_studio_volumen_c_m', string='Volumen c-m')

    # MIGRACIÓN V19: en Studio era `related='product_variant_id.stock_quant_ids.
    # x_studio_cantidad_reservada'` -`stock_quant_ids` es `One2many`, no
    # soportado por `related=`-; se reescribe como compute sumando los
    # quants del producto.
    x_studio_cantidad_reservada = fields.Float(
        string='Cantidad reservada', compute='_compute_x_studio_cantidad_reservada')

    @api.depends('stock_quant_ids.x_studio_cantidad_reservada')
    def _compute_x_studio_cantidad_reservada(self):
        for record in self:
            record.x_studio_cantidad_reservada = sum(
                record.stock_quant_ids.mapped('x_studio_cantidad_reservada'))
