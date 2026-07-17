# -*- coding: utf-8 -*-

import base64

from datetime import datetime
import xml.etree.ElementTree as ET
import pytz

from odoo import models, fields, api
from .. import extensions


class AccountMove(models.Model):
    _inherit = 'account.move'
    sale_id = fields.Many2one('sale.order')
    serie = fields.Char('Serie', compute="set_folio")
    folio = fields.Char('Folio', compute="set_folio")
    reason = fields.Char("Motivo")
    tipo_nota = fields.Selection(string='Tipo de nota de crédito', selection=[('01','01 - Descuentos o bonificaciones'),('03','03 - Devolición de mercancia')])
    invoice_datetime = fields.Char('Fecha y hora de timbrado', compute='_compute_invoice_datetime')
    # MIGRACIÓN V19: `x_estado_cli_actua` (res.partner) y
    # `x_nombre_supervisor_credito` (res.partner) se formalizaron como
    # campos reales en `res_partner_fields`. `x_doc_entrega` (sale.order)
    # se formaliza en este mismo módulo, más abajo.
    x_estado_actuali_cli = fields.Selection(
        string='Estado de actualizacion del cliente', selection=[('3.3', '3.3'), ('4', '4')],
        related='partner_id.x_estado_cli_actua')
    supervisor_credito = fields.Many2one(string='Supervisor de crédito', related='partner_id.x_nombre_supervisor_credito', store=True)
    documento_entrega_venta = fields.Selection(string='Documento de entrega', related='sale_id.x_doc_entrega')
    invoice_datetime_date = fields.Date('Fecha de timbrado', compute="_compute_invoice_datetime_date", store=True)
    orden_compra_relacionada = fields.Char(compute='_compute_orden_compra')

    def _compute_orden_compra(self):
        for record in self:
            record['orden_compra_relacionada'] = ''
            if not record.sale_id:
                if record.invoice_origin:
                    sale = self.env['sale.order'].search([('name','=',record.invoice_origin.split(',')[0])])
                    if sale:
                        record['orden_compra_relacionada'] = sale.x_studio_n_orden_de_compra
                        record.sale_id = sale
            else:
                record['orden_compra_relacionada'] = record.sale_id.x_studio_n_orden_de_compra

    @api.depends('invoice_datetime')
    def _compute_invoice_datetime_date(self):
        for record in self:
            if record.invoice_datetime:
                record.invoice_datetime_date = datetime.strptime(record.invoice_datetime, "%d/%m/%Y %H:%M:%S").date()
            else:
                record.invoice_datetime_date = None

    def _compute_invoice_datetime(self):
        for record in self:
            record.invoice_datetime = ''
            user_tz = self.env.user.tz if self.env.user.tz else 'America/Mexico_City'
            user_local = pytz.timezone(user_tz)
            att_xml = self.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',record.id),('mimetype','=','application/xml')])
            if att_xml:
                try:
                    path = att_xml[0]._full_path(att_xml.store_fname)
                    tree = ET.parse(path)
                    elements = [el for el in tree.iter()]
                    for element in elements:
                        if 'TimbreFiscalDigital' in element.tag:
                            local_date = user_local.localize(datetime.strptime(element.attrib['FechaTimbrado'], '%Y-%m-%dT%H:%M:%S'), is_dst=None)
                            record.invoice_datetime = local_date.strftime("%d/%m/%Y %H:%M:%S")
                except Exception:
                    continue

    @api.onchange('tipo_nota')
    def onchange_tipo_nota(self):
        for record in self:
            record.x_tipo_de_relacion = record.tipo_nota

    @api.depends('name')
    def set_folio(self):
        for record in self:
            serie = ""
            folio = ""
            if record.name and len(record.name)>1:
                tmp = record.name.split('/') if record.name else ""
                for i in range(len(tmp)):
                    if i == (len(tmp) - 1):
                        folio = str(int(tmp[i]))
                    else:
                        serie = serie + (tmp[i] + '/')
            record.serie = serie
            record.folio = folio

    def action_post(self):
        if not self.invoice_payment_term_id:
            self.write({'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id})
        return super(AccountMove, self).action_post()

    def remove_other_lines(self, picking_lines):
        self = self.with_context({'check_move_validity': False})
        self.invoice_line_ids = self.invoice_line_ids.filtered(lambda x: x.product_id.id in picking_lines.mapped('product_id.id'))
        self.line_ids.filtered(lambda x: not x.product_id)[0].recompute_tax_line = True
        for linea in picking_lines:
            # MIGRACIÓN V19: `qty_done` -> `quantity`.
            self.invoice_line_ids.filtered(lambda x: x.product_id == linea.product_id)\
                .write({'quantity': linea.quantity})
        self._onchange_recompute_dynamic_lines()


class Requirement(models.Model):
    """
    MIGRACIÓN V19: `x_client_requirement` ("Solicitud de requerimiento del
    cliente") es un modelo creado originalmente por Odoo Studio -distinto
    de `requiriment.client` (definido en `requerimiet.py`), que es un
    modelo "limpio" creado por código con un esquema equivalente pero
    tablas separadas-. En 15.0 sólo se sobrescribía `create()` aquí y
    todos sus campos vivían como columnas manejadas por Studio. Se
    formalizan ahora con el mismo esquema visto en el export de Studio
    para que Odoo tome el control de las columnas ya existentes en la
    base de datos de producción sin pérdida de información.
    """
    _name = 'x_client_requirement'
    _description = 'Solicitud de requerimiento del cliente (legado Studio)'

    x_cantidad = fields.Float("cantidad")
    x_comprar = fields.Boolean("Comprar")
    x_count = fields.Integer("count", compute='_compute_x_count')
    x_descripcion = fields.Char("Descripcion")
    x_lines_proposal = fields.One2many('x_proposal_purchase', 'x_rel_id', "Propuestas")
    x_link_sitio = fields.Html("Link producto")
    x_marca = fields.Char("Marca")
    x_modelo = fields.Char("Modelo")
    x_name = fields.Char("Name")
    x_order_id = fields.Many2one('sale.order', "orden")
    x_precio_uni = fields.Float("Precio unitario")
    x_presupuesto = fields.Float("presupuesto")
    x_proveedor = fields.Char("proveedor")
    # MIGRACIÓN V19: sin valores de opción confirmados por el usuario para
    # este campo en este modelo (a diferencia de `requiriment.client`, cuyo
    # `x_studio_estado` sí se confirmó como código); se declara como Char
    # -compatible a nivel de columna con Selección- para no perder datos.
    x_studio_estado = fields.Char("estado")
    x_studio_related_field_1eaGE = fields.Char("Cliente", related='x_order_id.partner_id.name')
    x_studio_related_field_DGJgC = fields.Char("New Campo relacionado", related='x_order_id.company_id.display_name')
    x_studio_related_field_ap2ah = fields.Char("Vendedor", related='x_order_id.user_id.display_name')

    @api.depends('x_lines_proposal')
    def _compute_x_count(self):
        for record in self:
            record.x_count = len(record.x_lines_proposal)

    @api.model_create_multi
    def create(self, vals_list):
        return super(Requirement, self).create(vals_list)


class Proposal(models.Model):
    """
    MIGRACIÓN V19: `x_proposal_purchase` ("Propuesta de Compras") es el
    equivalente Studio de `proposal.purchases` (`requerimiet.py`), ver nota
    en `Requirement` arriba. Se formaliza con el esquema real del export
    de Studio.
    """
    _name = 'x_proposal_purchase'
    _description = 'Propuesta de Compras (legado Studio)'

    x_rel_id = fields.Many2one('x_client_requirement', "Requerimiento")
    x_agente_compra = fields.Char(".")
    x_archivo = fields.Binary("Imagen del producto")
    x_cantidad = fields.Float("Cantidad")
    x_caracteristicas = fields.Text("Caracteristicas")
    x_categoria_id = fields.Many2one("product.category", "Categoría")
    x_condiciones_de_pago = fields.Char("Condiciones de Pago")
    x_costo = fields.Float("Costo")
    x_descripcion = fields.Char("Descripción")
    # MIGRACIÓN V19: `Html` en vez de `Char` (mismo motivo que
    # `proposal.purchases.x_detalle`/`wizard.proposal.x_detalle` en
    # `requerimiet.py`: el compute arma una `<table>`).
    x_detalle = fields.Html("Detalle", compute='_compute_x_detalle')
    x_documento = fields.Binary("Documento")
    x_familia_id = fields.Many2one("x_familia", "Familia")
    x_garantias = fields.Text("Garantias")
    x_grup_id = fields.Many2one("x_grupo", "Grupo")
    x_iva = fields.Boolean("Incluye IVA")
    x_linea_id = fields.Many2one("x_linea", "Línea")
    x_marca = fields.Char("Marca")
    x_modelo = fields.Char("Modelo")
    x_motivo_cancelacion = fields.Char("Motivo de Cancelación")
    x_name = fields.Char("Propuesta")
    x_new_prod_prop = fields.Boolean("Producto de propuesta")
    x_notas = fields.Text("Notas")
    x_note = fields.Text("Notas")
    x_pro_aten = fields.Selection([('yes', 'SI'), ('no', 'NO')], "Propuesta atendida")
    x_product_id = fields.Many2one("product.product", "producto")
    x_proveedor = fields.Many2one("res.partner", "Proveedor")
    x_state = fields.Selection([('draft', 'Borrador'), ('done', 'Propuesta Aceptada'), ('cancel', 'Cancelado'), ('validar', 'Re-Validar'), ('atendido', 'Atendido'), ('confirm', 'Compra Autorizada')], "Estado")
    x_studio_aprovacin_de_compras = fields.Boolean("Aprovación de Compras", related='x_rel_id.x_order_id.x_aprovacion_compras')
    x_studio_archivo = fields.Binary("Archivo")
    x_studio_archivo_filename = fields.Char("Filename for x_studio_binary_field_kkNkg")
    x_studio_estado_de_cotizacin = fields.Selection(related='x_rel_id.x_order_id.state', string="Estado de Cotización")
    x_studio_integer_field_Olr5a = fields.Integer("New Entero")
    x_studio_proveedor = fields.Char("Proveedor")
    x_studio_related_field_gKx5P = fields.Char("Orden de venta", related='x_rel_id.x_order_id.display_name')
    x_studio_revalidacion = fields.Char("Motivo de revalidación")
    x_studio_text_field_GWDee = fields.Text("Notas")
    x_terminado = fields.Boolean("Regresar propuesta")
    x_tiempo_entrega = fields.Char("Tiempo de entrega")
    x_vigencia = fields.Char("Vigencia")

    @api.depends('x_rel_id')
    def _compute_x_detalle(self):
        for record in self:
            record.x_detalle = ''
            if record.x_rel_id.id:
                t = "<table class='table'><tr><td>Nombre</td><td>Descripción</td><td>Marca</td><td>Modelo</td><td>Cantidad</td><td>Precio Unitario</td><td>Presupuesto</td><td>Proveedor</td><td>linkproducto</td></tr>"
                t = t + "<tr><td>" + str(record.x_rel_id.x_name) + "</td><td>" + str(
                    record.x_rel_id.x_descripcion) + "</td><td>" + str(record.x_rel_id.x_marca) + "</td><td>" + str(
                    record.x_rel_id.x_modelo) + "</td><td>" + str(record.x_rel_id.x_cantidad) + "</td><td>" + str(
                    record.x_rel_id.x_precio_uni) + "</td><td>" + str(record.x_rel_id.x_presupuesto) + "</td><td>" + str(
                    record.x_rel_id.x_proveedor) + "</td><td>" + str(record.x_rel_id.x_link_sitio) + "</td></tr></table>"
                record.x_detalle = t

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Proposal, self).create(vals_list)
        for r in records:
            if not (r.x_rel_id and r.x_rel_id.x_order_id):
                continue
            user = r.x_rel_id.x_order_id.user_id
            odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
            mesagge = "Alertas la siguientes Venta: \n" + str(r.x_rel_id.x_order_id.name)+'tiene nuevas propuestas'
            users_to_send_message = [(4, user.partner_id.id), (4, odoobot_id)]
            self.env['mail.message'].sudo().search([('message_type', '=', 'comment'), ('author_id', '=', odoobot_id), ('record_name', '=', 'Alerta de leads')]).unlink()
            channel = self.env['discuss.channel'].sudo().search([('name', '=', 'Alerta de leads'), ('channel_partner_ids', 'in', [user.partner_id.id])], limit=1)
            if not channel:
                channel = self.env['discuss.channel'].with_context(mail_create_nosubscribe=True).sudo().create({'channel_partner_ids': users_to_send_message, 'public': 'private', 'channel_type': 'chat', 'name': 'Alerta de leads'})
            channel.sudo().message_post(body=mesagge, author_id=odoobot_id, message_type="comment", subtype_xmlid="mail.mt_comment")
        return records


class AccountMoveRevers(models.TransientModel):
    _inherit = 'account.move.reversal'
    uso_cfdi = fields.Selection(string='Uso de CFDI', selection=[('G02', 'G02 - Devoluciones, descuentos o bonificaciones')], default='G02')
    tipo_relacion = fields.Selection(string='Tipo de relación', selection=[('01', '01 - Descuentos o bonificaciones'),('03', '03 - Devolución de mercancias')],default='03')
    motivo = fields.Selection(string='Razón de devolución',selection=[('fallasdeentrega','Fallas de entrega'),('empaquedanado','Empaque dañado'),
                                                                      ('noeslosolicitadoporelcliente','No es lo solicitado por el cliente'),('clienteinsatisfecho','Cliente Insatisfecho'),
                                                                      ('productoequivocado','Producto equivocado'),('productoincompleto','Producto Incompleto'),
                                                                      ('pedidoincompleto','Pedido incompleto'),('clienteyanolorequiere','Cliente ya no lo requiere'),
                                                                      ('productomalestado','Producto en mal estado'),('refacturacion','Refacturación'),
                                                                      ('otros','Otros (Especifique)')
                                                                      ])

    @api.onchange('motivo')
    def onchange_motivo(self):
        for record in self:
            if record.motivo:
                record.reason = ''
            else:
                record.reason = dict(self._fields['motivo'].selection).get(self.motivo)

    def _prepare_default_reversal(self, move):
        r = super(AccountMoveRevers, self)._prepare_default_reversal(move)
        r['invoice_payment_term_id'] = move.invoice_payment_term_id.id
        r['l10n_mx_edi_payment_policy'] = 'PUE'
        if self.uso_cfdi:
            r['l10n_mx_edi_usage'] = self.uso_cfdi
        return r

    def reverse_moves(self):
        r = super(AccountMoveRevers, self).reverse_moves()
        nota_credito = self.env['account.move'].browse(r['res_id'])
        nota_credito.reason = self.reason
        # MIGRACIÓN V19: `helpdesk_ticket_id` no está definido en ninguno de
        # los 36 módulos ni en el export de personalizaciones de Studio
        # entregado; se desconoce su origen exacto (posiblemente otra app
        # Enterprise de helpdesk no incluida). Se accede de forma
        # defensiva para no romper este asistente si el campo no existe.
        if 'helpdesk_ticket_id' in self._fields and self.helpdesk_ticket_id:
            # MIGRACIÓN V19: `move_line_ids_without_package` -> `move_line_ids`.
            picking_lines = self.helpdesk_ticket_id.picking_ids.move_line_ids
            if picking_lines:
                nota_credito.remove_other_lines(picking_lines)
        nota_credito.x_tipo_de_relacion = self.tipo_relacion
        # MIGRACIÓN V19: `l10n_mx_edi_origin` -> `l10n_mx_edi_cfdi_origin`.
        if nota_credito.l10n_mx_edi_cfdi_origin:
            origin = nota_credito.l10n_mx_edi_cfdi_origin.split('|')
            if len(origin) > 1:
                nota_credito.l10n_mx_edi_cfdi_origin = nota_credito.x_tipo_de_relacion + '|' + origin[1]
            if len(origin) == 1:
                nota_credito.l10n_mx_edi_cfdi_origin = nota_credito.x_tipo_de_relacion = nota_credito.l10n_mx_edi_cfdi_origin + '|' + origin[0]
        return r
