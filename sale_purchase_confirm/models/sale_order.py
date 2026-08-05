# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _
from .. import extensions
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_in_text = fields.Char(compute='set_amount_text', string='Total en letra')
    # MIGRACIÓN V19: antes se sobreescribía `state` con la lista completa a
    # mano -mismo problema que `purchase.order.state`: "overrides existing
    # selection"-. Se usa `selection_add` para agregar sólo los 4 estados
    # propios sobre la selección real del core (`draft`, `sent`, `sale`,
    # `cancel`; ya no incluye `done`/Locked como estado -ahora es el
    # booleano `locked`-, salvo que aquí `done` SÍ se sigue usando como
    # estado propio, ver `write({'state': 'done', ...})` más abajo, así que
    # se conserva). Los singletons `('sale',)`/`('cancel',)` son anclas de
    # posición -no agregan nada nuevo, sólo indican dónde insertar lo que
    # va antes- para mantener el mismo orden visual que tenía la lista
    # completa original.
    state = fields.Selection(
        selection_add=[
            ('sale_conf', 'Validación ventas'),
            ('purchase_conf', 'Validación compras'),
            ('credito_conf', 'Validación credito'),
            ('sale',),
            ('done', 'Locked'),
            ('cancel',),
        ],
        ondelete={
            'sale_conf': 'set default',
            'purchase_conf': 'set default',
            'credito_conf': 'set default',
            'done': 'set default',
        },
        string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft',
    )
    purchase_ids = fields.Many2many('purchase.order', string='OC', readonly=True)
    check_solicitudes = fields.Boolean(default=False, compute='solicitud_reduccion')
    albaran = fields.Many2one('stock.picking', 'Albaran')
    states_proposals = fields.Many2many('proposal.state', string='Estados de propuestas', compute='set_states_proposal')
    requirements_line_ids = fields.One2many('requiriment.client', 'x_order_id', 'Requerimientos')
    proposal_line_ids = fields.Many2many('proposal.purchases', compute='get_proposals')
    partner_loc_ids = fields.Many2many('res.partner', compute='get_partner')
    partner_child = fields.Many2one('res.partner', 'Solicitante')
    # MIGRACIÓN V19: el parámetro `states=` en campos fue eliminado; la
    # lógica de solo-lectura condicional según el estado se maneja ahora a
    # nivel de vista (`readonly="state not in (...)"`), ver views/views.xml.
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True,
        required=True, change_default=True, index=True, tracking=1,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]",)
    partner_id_uso_cfdi = fields.Selection(string='Uso CFDI', related='partner_id.x_studio_uso_de_cfdi')
    partner_id_payment_method = fields.Char('Forma de pago', related='partner_id.x_studio_mtodo_de_pago.name')
    partner_id_payment_method_code = fields.Char(string='Código Forma de pago', related='partner_id.x_studio_mtodo_de_pago.code')
    validacion_parcial = fields.Boolean(string='Validación parcial', default=False)
    solicitud_parcial = fields.Boolean(default=False)
    solicito_validacion = fields.Boolean(default=False)
    es_orden_parcial = fields.Boolean(compute='_compute_es_orden_parcial')
    sales_agent = fields.Many2one(related='partner_id.sales_agent')
    numero_ordenes_compra_activas = fields.Integer('Númerode órdenes de compra activas', compute='_compute_num_ordenes_compra')
    fecha_factura = fields.Date(string='Fecha de la factura', compute='_compute_fecha_factura', store=True)
    fechas_factura = fields.Char(string='Fechas de las facturas', compute='_compute_fechas_facturas')

    # MIGRACIÓN V19: campos de Odoo Studio en `sale.order` formalizados como
    # código real (ver nota en `custom_models.py`).
    x_doc_entrega = fields.Selection(
        string='Documento de entrega', tracking=True,
        selection=[('factura', 'Factura'), ('remision_sin_costo', 'Remisión sin costo'), ('remision_con_costo', 'Remisión con costo')])
    x_metodo_entrega = fields.Selection(
        string='Método de entrega',
        selection=[('flotilla', 'Flotilla'), ('paqueteria', 'Paqueteria'), ('recolecta', 'Recolecta'), ('Foráneo', 'Foráneo')])
    x_aprovacion_compras = fields.Boolean(string='Aprovación de Compras')
    x_bloqueo = fields.Boolean(string='Bloqueo')
    x_aprovar = fields.Boolean(string='Aprovar')
    x_studio_cliente_de_marketplace = fields.Char(string='Cliente de marketplace')
    x_otros_documentos = fields.Many2many('ir.attachment', string='Otros documentos', tracking=True)
    x_estado_surtido = fields.Selection(string='Estado de surtido', selection=[('pendiente', 'Pendiente'), ('surtir', 'Surtir')])
    x_studio_n_orden_de_compra = fields.Char(string='N° Orden de compra', tracking=True)
    x_observaciones = fields.Text(string='Observaciones')
    x_studio_nivel = fields.Char(string='Nivel', related='partner_id.x_nivel_cliente.x_name', tracking=True)

    def _compute_fechas_facturas(self):
        for record in self:
            record.fechas_factura = ''
            invs = record.invoice_ids.filtered(lambda x: x.state == 'posted' and x.move_type == 'out_invoice')
            all_fechas = list(set(invs.mapped('invoice_date')))
            fechas = [fecha.strftime("%d/%m/%Y") for fecha in all_fechas]
            if all_fechas:
                record.fechas_factura = ', '.join(fechas)
                record.fecha_factura = all_fechas[-1]

    def _compute_fecha_factura(self):
        for record in self:
            invs = record.invoice_ids.filtered(lambda x: x.state == 'posted' and x.move_type == 'out_invoice')
            if invs:
                record.fecha_factura = invs[-1].invoice_date
            else:
                record.fecha_factura = None

    def _compute_num_ordenes_compra(self):
        for record in self:
            if record.purchase_ids:
                record['numero_ordenes_compra_activas'] = len(record.mapped('purchase_ids').filtered(lambda y: y.state != 'cancel'))
            else:
                record['numero_ordenes_compra_activas'] = 0

    @api.constrains('x_studio_n_orden_de_compra')
    def _check_orden_compra(self):
        for record in self:
            if self.partner_child.x_es_marketplace:
                orden_venta = self.env['sale.order'].search([('x_studio_n_orden_de_compra', '=', record.x_studio_n_orden_de_compra), ('id', '!=', record.id)])
                if orden_venta and record.x_studio_n_orden_de_compra and record.x_studio_n_orden_de_compra != '':
                    raise ValidationError('Ya existe otro pedido (' + ', '.join(orden_venta.mapped('name')) + ') con ese número de orden de compra')

    @api.depends('order_line')
    def _compute_es_orden_parcial(self):
        for record in self:
            if record.order_line.filtered(lambda x: x.cantidad_asignada + x.qty_invoiced + x.qty_delivered < x.product_uom_qty) and record.state == 'sale':
                record.es_orden_parcial = True
            else:
                record.es_orden_parcial = False

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals.update({'l10n_mx_edi_usage': self.partner_id.x_studio_uso_de_cfdi})
        vals.update({'l10n_mx_edi_payment_method_id': self.partner_id.x_studio_mtodo_de_pago.id})
        return vals

    @api.depends('requirements_line_ids')
    def get_proposals(self):
        for record in self:
            record.proposal_line_ids = [(6, 0, record.requirements_line_ids.mapped('x_lines_proposal.id'))]

    @api.depends('proposal_line_ids')
    def set_states_proposal(self):
        for record in self:
            record.states_proposals = [(5, 0, 0)]
            for li in record.proposal_line_ids:
                record.states_proposals = [(0, 0, {'name': li.x_name + ":" + str(dict(li._fields['x_state'].selection).get(li.x_state))})]

    @api.onchange('partner_child')
    def set_partner_id(self):
        for record in self:
            if record.partner_child:
                if record.partner_child.parent_id:
                    record.partner_id = record.partner_child.parent_id
                else:
                    record.partner_id = record.partner_child
                record.x_studio_cliente_de_marketplace = record.partner_child.name
                record.user_id = self.env.user.id
                # busca un almacén con el mismo nombre del cliente
                if record.partner_child.x_es_marketplace:
                    default_warehouse = self.env['stock.warehouse'].search([('name', '=', 'MARKETPLACE')])
                    if default_warehouse:
                        self.warehouse_id = default_warehouse

    # MIGRACIÓN V19: `onchange_partner_id` ya no existe en `sale.order`
    # (el core reemplazó ese onchange por campos compute con
    # `@api.depends('partner_id', ...)`, que se recalculan solos); no hay
    # implementación de la clase base que llamar por `super()`.
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.update({'user_id': self.env.user.id})

    def update_stock(self):
        for rec in self.order_line:
            rec.get_stock()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get('partner_child') and not vals.get('partner_id'):
                partner = self.env['res.partner'].browse(vals['partner_child'])
                vals['partner_id'] = (
                    partner.parent_id.id
                    if partner.parent_id
                    else partner.id
                )


            if 'user_id' in vals:
                vals['user_id'] = self.env.user.id
        res = super(SaleOrder, self).create(vals_list)
        for r in res:
            if not r.payment_term_id:
                r.write({'payment_term_id': r.partner_id.property_payment_term_id.id})
            adjuntos = r.x_otros_documentos
            for adjunto in adjuntos:
                adjunto.write({'res_model': self._name, 'res_id': r.id})
        return res

    @api.depends('amount_total')
    def set_amount_text(self):
        for record in self:
            if record.amount_total:
                record.total_in_text = extensions.text_converter.number_to_text_es(record.amount_total)
            else:
                record.total_in_text = extensions.text_converter.number_to_text_es(0)

    def conf_credito(self):
        self.write({'x_aprovacion_compras': True, 'x_bloqueo': False})
        self.action_confirm()

    def conf_purchase(self):
        total = self.partner_id.credit_rest - self.amount_total
        check = total >= 0 if self.payment_term_id.id != 1 else False
        cliente = self.partner_id.x_studio_triple_a
        if cliente and check:
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            self.action_confirm()
        else:
            self.write({'state': 'credito_conf'})

    def conf_ventas(self):
        order_lines = self.order_line
        for ol in order_lines:
            ol.check_price_reduce = False
            ol.price_reduce_solicit = False
        self.validacion_parcial = True
        self.solicito_validacion = False
        total = self.partner_id.credit_rest - self.amount_total
        check = total >= 0 if self.payment_term_id.id != 1 else False
        cliente = self.partner_id.x_studio_triple_a
        # MIGRACIÓN V19: `x_fecha_pago_pro` (account.move, formalizado en
        # `account_move_proper`) se lee de forma defensiva para evitar una
        # dependencia circular (`account_move_proper` depende de este módulo).
        facturas_vencidas_cliente = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<', fields.Datetime().now()),
        ])
        if 'x_fecha_pago_pro' in self.env['account.move']._fields:
            facturas_vencidas_cliente = facturas_vencidas_cliente.filtered(
                lambda x: not x.x_fecha_pago_pro or x.x_fecha_pago_pro < fields.Date.today())
        if check or (cliente and not facturas_vencidas_cliente):
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            return self.action_confirm()
        else:
            self.write({'state': 'credito_conf'})

    def is_valid_order_sale(self):
        valid = True
        message = ''
        dic_nuevos_precios = {}
        dic_cantidades_disponibles = {}

        if self.validacion_parcial:
            if not self.x_doc_entrega:
                valid = False
                message += 'No se ha definido el documento de entrega.\n'

            if not self.x_metodo_entrega:
                valid = False
                message += 'No se ha definido el método de entrega.\n'
            if not valid:
                return valid, message
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            valid = True
            message = ''
            return valid, message
        # MIGRACIÓN V19: `partner_id.team_id` no es un campo real de
        # `res.partner` (ni en el core ni en el export de Studio); ya era
        # una referencia muerta en 15.0, por lo que esta condición nunca
        # se cumplía. Se documenta y se deja el bloque inalcanzable.
        if self.order_line.filtered(lambda x: x.check_price_reduce):
            if not ('team_id' in self.partner_id._fields and self.partner_id.team_id and self.partner_id.team_id.id == 6):
                message += 'No ha solicitado la reducción de precios para los siguientes productos:'
                for order_line in self.order_line:
                    if order_line.check_price_reduce:
                        valid = False
                        message += '\n- ' + order_line.product_id.name

        if not self.x_doc_entrega:
            valid = False
            message += '\n\n- No se ha definido el documento de entrega.'

        if not self.x_metodo_entrega:
            valid = False
            message += '\n- No se ha definido el método de entrega.\n'

        if len(self.order_line) <= 0:
            valid = False
            message = 'No hay productos en la cotización'
            return valid, message

        for i, line in enumerate(self.order_line, start=1):
            margen = line.product_id.x_fabricante['x_studio_margen_' + str(line.order_id.x_studio_nivel)] if line.product_id.x_fabricante else 12
            id_producto = line.product_id.id
            if line.x_studio_nuevo_costo > 0.0:
                nuevo_precio_minimo = line.x_studio_nuevo_costo / (1 - (margen / 100))
                if id_producto not in dic_nuevos_precios.keys():
                    dic_nuevos_precios.update({id_producto: nuevo_precio_minimo})
                else:
                    if dic_nuevos_precios[id_producto] < nuevo_precio_minimo:
                        dic_nuevos_precios[id_producto] = nuevo_precio_minimo

            if line.x_cantidad_disponible_compra > 0.0:
                if id_producto not in dic_cantidades_disponibles.keys():
                    dic_cantidades_disponibles.update({id_producto: line.x_cantidad_disponible_compra})
                else:
                    dic_cantidades_disponibles[id_producto] += line.x_cantidad_disponible_compra

        for i, line in enumerate(self.order_line, start=1):
            if line.x_validacion_precio and line.x_studio_nuevo_costo == 0:
                valid = False
                message += '\n- No se ha establecido el nuevo costo para el producto' + line.name.replace('\n', '') + ' línea(' + str(i) + ')'

            # MIGRACIÓN V19: `partner_id.team_id` es una referencia muerta
            # (ver nota arriba); esta rama de validación de stock en
            # almacenes marketplace nunca se activa, se mantiene tal cual.
            if 'team_id' in line.order_id.partner_id._fields and line.order_id.partner_id.team_id and line.order_id.partner_id.team_id.id == 6:
                wh = line.order_id.warehouse_id.lot_stock_id
                disponibles_total = sum(line.product_id.stock_quant_ids.filtered(lambda x: x.location_id == wh).mapped('available_quantity'))
                disponibles_total = disponibles_total - line.product_uom_qty
                if disponibles_total < 0.0:
                    # MIGRACIÓN V19: `detailed_type` fue removido de
                    # `product.template` en 19.0; se revierte a `type`.
                    if line.product_id.type != 'service':
                        message += '\n- No hay stock suficiente en el almacén ' + line.order_id.warehouse_id.name + ' para el producto: ' + \
                                   line.name.replace('\n', ' ') + '. Requiere ' + str(abs(disponibles_total)) \
                                   + ' producto(s) más. línea(' + str(i) + ')'
                        valid = False
            else:
                disponibles_total = line.product_id.stock_quant_warehouse_zero - line.product_uom_qty
                if line.product_id.id in dic_cantidades_disponibles:
                    disponibles_total += dic_cantidades_disponibles[line.product_id.id]
                if disponibles_total < 0.0:
                    if line.product_id.type != 'service':
                        message += '\n- No hay stock suficiente para el producto: ' + line.name.replace('\n', ' ') + '. Requiere ' + str(abs(disponibles_total)) + ' producto(s) más. línea(' + str(i) + ')'
                        valid = False

            if not line.order_id.x_aprovacion_compras and line.product_id.id in dic_nuevos_precios.keys() and dic_nuevos_precios[line.product_id.id] > line.price_unit:
                valid = False
                message += '\n -El precio unitario para producto' + line.name.replace('\n', ' ') + ' no cumple con la utilidad esperada según el nuevo costo.' + ' línea(' + str(i) + ')'

        for i, line in enumerate(self.order_line, start=1):
            if not line.product_id.default_code or line.product_id.default_code == '':
                valid = False
                message += '\n - El producto ' + line.name.replace('\n', ' ') + ' no tiene configurado un código. ' + ' línea(' + str(i) + ')'
            for propuesta in self.proposal_line_ids:
                if propuesta.x_descripcion == line.product_id.name:
                    if propuesta.x_modelo != line.product_id.default_code:
                        valid = False
                        message += '\n - No coincide el nombre del producto ' + line.name.replace('\n', ' ') + ' con el un código. ' + ' en la línea(' + str(i) + ')'

        return valid, message

    def action_confirm_sale(self):
        if self.warehouse_id.id == 30:
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            return self.action_confirm()

        lines_no_stock = self.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0 and x.x_validacion_precio == True)
        for line in lines_no_stock:
            line.write({'cantidad_a_comprar': line.product_uom_qty - line.product_id.stock_quant_warehouse_zero})
        mensaje = ''
        mensaje_bottom = ''
        if lines_no_stock:
            view = self.env.ref('sale_purchase_confirm.sale_order_partial_view')
            mensaje = '<h3>Se solicita aprobar la orden parcial.</h3>'
            lines_price_reduce = self.order_line.filtered(lambda x: x.check_price_reduce and not x.price_reduce_solicit)
            if lines_price_reduce:
                mensaje_bottom += '</tbody></table>'
                mensaje_bottom += '<h3>Se solicitará la aprobación de reducción de precio de los siguientes productos.</h3><table class="table" style="width: 100%"><thead>' \
                          '<tr style="width: 30% !important;"><th>Producto</th>' \
                          '<th style="width: 10%">Costo promedio</th>' \
                          '<th style="width: 10%">Precio unitario anterior</th>' \
                          '<th style="width: 10%">Margen anterior</th>' \
                          '<th style="width: 10%">Nuevo costo</th>' \
                          '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                          '<th style="width: 10%">Nuevo precio unitario</th>' \
                          '<th style="width: 10%">Nuevo margen</th>' \
                          '</tr></thead>' \
                          '<tbody>'
                for order_line in lines_price_reduce:
                    margen = order_line.product_id.x_fabricante[
                        'x_studio_margen_' + str(order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                    mensaje_bottom += '<tr><td>' + order_line.name + '</td><td>' \
                               + str(order_line.product_id.standard_price) + '</td><td>' \
                               + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                               + str(margen) + '</td><td>' \
                               + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                               + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                               + str(round(order_line.price_unit)) + '</td><td>' \
                               + str(round((1 - (
                                order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                               + '</td></tr>'
                mensaje_bottom += '</tbody></table>'
            wiz = self.env['sale.order.alerta'].create({'sale_id': self.id, 'mensaje': mensaje, 'line_ids': lines_no_stock, 'mensaje_bottom': mensaje_bottom})
            return {
                'name': _('Alerta'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        valid, message = self.is_valid_order_sale()
        if not valid:
            raise UserError(message)
        self.write({'x_aprovar': False})
        total = self.partner_id.credit_rest - self.amount_total
        check = total >= 0 if self.payment_term_id.id != 1 else False
        cliente = self.partner_id.x_studio_triple_a
        facturas_vencidas_cliente = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<', fields.Datetime().now()),
        ])
        if 'x_fecha_pago_pro' in self.env['account.move']._fields:
            facturas_vencidas_cliente = facturas_vencidas_cliente.filtered(
                lambda x: not x.x_fecha_pago_pro or x.x_fecha_pago_pro < fields.Date.today())
        if cliente or (check and not facturas_vencidas_cliente):
            # MIGRACIÓN V19: `partner_id.team_id` es una referencia muerta,
            # ver nota en `is_valid_order_sale`.
            if 'team_id' in self.partner_id._fields and self.partner_id.team_id and self.partner_id.team_id.id == 6:
                self.write({'state': 'credito_conf'})
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            return self.action_confirm()
        else:
            self.write({'state': 'credito_conf'})

    # MIGRACIÓN V19: el core agregó el parámetro `invoices=False` a
    # `action_view_invoice()` (`sale_make_invoice_advance.py` lo llama con
    # `invoices=` al crear una factura desde el wizard "Crear factura"); este
    # override no lo aceptaba, causando "TypeError: got an unexpected
    # keyword argument 'invoices'" al confirmar el wizard.
    def action_view_invoice(self, invoices=False):
        if len(self) == 1:
            self.invoice_ids.write({'sale_id': self.id})
        return super(SaleOrder, self).action_view_invoice(invoices=invoices)

    @api.depends('partner_id', 'partner_child')
    def get_partner(self):
        for record in self:
            user = self.env.user
            # MIGRACIÓN V19: `res.groups.users` ya no existe (renombrado a
            # `user_ids`/`all_user_ids`); se usa `has_group`, que ya resuelve
            # la pertenencia incluyendo grupos implicados.
            if (
                user.has_group('sales_team.group_sale_salesman')
                and not user.has_group('sales_team.group_sale_salesman_all_leads')
                and not user.has_group('sales_team.group_sale_manager')
            ):
                partner = self.env['res.partner'].search(['|', '|', ['x_nombre_agente_venta', '=', self.env.user.name], ['agente_temporal', '=', self.env.user.name], ['x_nombre_agente_venta', '=', False]])
            else:
                partner = self.env['res.partner'].search([])
            partner_general = self.env["res.partner"].search([("name", '=', "\"PUBLICO EN GENERAL\"")])
            partner_ids = partner.ids + partner.mapped('child_ids').ids + partner_general.ids + partner_general.mapped('child_ids').ids
            record.partner_loc_ids = [(6, 0, partner_ids)]

    def solicitud_reduccion(self):
        for record in self:
            lines = record.order_line.filtered(lambda x: x.check_price_reduce and not x.price_reduce_solicit)
            if lines:
                self.check_solicitudes = True
            else:
                record.check_solicitudes = False

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.picking_ids:
            stock_pick = self.picking_ids.filtered(lambda x: '/PICK/' in x.name and x.state != 'cancel')
            if len(stock_pick) == 1:
                if stock_pick and stock_pick.state not in ('cancel', 'done'):
                    if self.x_estado_surtido == 'surtir':
                        stock_pick.write({'state': 'assigned'})
                    else:
                        stock_pick.write({'state': 'confirmed'})
        return res

    def solicitud_reduccion_send(self):
        lines = self.order_line.filtered(lambda x: x.check_price_reduce and not x.price_reduce_solicit)
        mensaje = '<h3>Se solicitará la reducción de precio de los siguientes productos</h3><table class="table" style="width: 100%"><thead>' \
                  '<tr style="width: 30% !important;"><th>Producto</th>' \
                  '<th style="width: 10%">Costo promedio</th>' \
                  '<th style="width: 10%">Precio unitario anterior</th>' \
                  '<th style="width: 10%">Margen anterior</th>' \
                  '<th style="width: 10%">Nuevo costo</th>' \
                  '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                  '<th style="width: 10%">Nuevo precio unitario</th>' \
                  '<th style="width: 10%">Nuevo margen</th>' \
                  '</tr></thead>' \
                  '<tbody>'
        if lines:
            view = self.env.ref('sale_purchase_confirm.sale_order_alerta_view')
            for order_line in lines:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.name + '</td><td>' \
                           + str(order_line.product_id.standard_price) + '</td><td>' \
                           + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                           + str(margen) + '</td><td>' \
                           + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                           + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                           + str(round(order_line.price_unit)) + '</td><td>' \
                           + str(round((1 - (order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                           + '</td></tr>'
            lines_no_stock = self.order_line.filtered(
                lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0)
            if lines_no_stock:
                mensaje += '</tbody></table>'
                mensaje += '<h3>Los siguientes productos no tienen existencia o tienen existencia parcial y se solicitará validar datos</h3><table class="table" style="width: 100%;margin-left: auto;margin-right: auto;"><thead>' \
                  '<tr><th>Producto</th>' \
                  '<th>Disponible en almacén 0</th>' \
                  '<th>Costo promedio</th>' \
                  '<th>Cantidad solicitada</th>' \
                  '<th>Cantidad faltante</th>' \
                  '</tr></thead>' \
                  '<tbody>'
                for order_line in lines_no_stock:
                    margen = order_line.product_id.x_fabricante[
                        'x_studio_margen_' + str(
                            order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                    mensaje += '<tr><td>' + order_line.x_descripcion_corta + '</td><td>' \
                               + str(order_line.product_id.stock_quant_warehouse_zero) + '</td><td>' \
                               + str(order_line.product_id.standard_price) + '</td><td>' \
                               + str(order_line.product_uom_qty) + '</td><td>' \
                               + str(order_line.product_uom_qty + order_line.x_cantidad_disponible_compra - order_line.product_id.stock_quant_warehouse_zero) + '</td></tr>'
            mensaje += '</tbody></table>'
            wiz = self.env['sale.order.alerta'].create({'sale_id': self.id, 'mensaje': mensaje})
            return {
                'name': _('Alerta'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def validar_precio_masivo(self):
        lines = self.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero + x.product_id.stock_quant_warehouse_zero - x.product_uom_qty) < 0 and x.x_validacion_precio != True)
        mensaje = '<h3>Se solicitará validar datos de los siguientes productos</h3><table class="table" style="width: 100%;margin-left: auto;margin-right: auto;"><thead>' \
                  '<tr><th>Producto</th>' \
                  '<th>Disponible en almacén 0</th>' \
                  '<th>Costo promedio</th>' \
                  '<th>Cantidad solicitada</th>' \
                  '<th>Cantidad faltante</th>' \
                  '</tr></thead>' \
                  '<tbody>'
        if lines:
            view = self.env.ref('sale_purchase_confirm.sale_order_validar_view')
            for order_line in lines:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.x_descripcion_corta + '</td><td>' \
                           + str(order_line.product_id.stock_quant_warehouse_zero) + '</td><td>' \
                           + str(round(order_line.product_id.standard_price, 2)) + '</td><td>' \
                           + str(order_line.product_uom_qty) + '</td><td>' \
                           + str(order_line.product_uom_qty + order_line.x_cantidad_disponible_compra - order_line.product_id.stock_quant_warehouse_zero) + '</td></tr>'
            mensaje += '</tbody></table>'
            wiz = self.env['sale.order.alerta'].create({'sale_id': self.id, 'mensaje': mensaje})
            return {
                'name': _('Alerta'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def action_confirm(self):
        # MIGRACIÓN V19: en 19.0 varios flujos del core (p. ej.
        # `delivery`/`payment` al post-procesar transacciones de "Cash on
        # Delivery") invocan `action_confirm()` sobre un recordset de
        # `sale.order` potencialmente vacío como parte de su limpieza
        # rutinaria. Sin este guard, `is_valid_order_sale()` se ejecutaba
        # igual sobre `self` vacío (los accesos a campos de un recordset
        # vacío devuelven valores por defecto) y terminaba lanzando
        # UserError incluso sin ninguna orden real involucrada.
        if not self:
            return super(SaleOrder, self).action_confirm()
        valid, message = self.is_valid_order_sale()
        if self.warehouse_id.id == 30:
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            valid = True
            message = ''
        if valid:
            if self.solicito_validacion:
                self.write({'state': 'sale_conf', 'solicito_validacion': False})
            else:
                r = super(SaleOrder, self).action_confirm()
                for line in self.order_line.filtered(lambda y: y.proposal_id):
                    line.write({'cantidad_a_comprar': line.proposal_id.x_cantidad})
                for line in self.order_line.filtered(lambda x: x.x_validacion_precio):
                    if line.product_uom_qty > 0 and line.cantidad_a_comprar == 0:
                        line.write({'cantidad_a_comprar': line.proposal_id.x_cantidad})
                if r and self.order_line.filtered(lambda x: x.cantidad_a_comprar > 0):
                    prods_html = '<table class="table" style="width:100%"><thead><tr><th style="width:60% !important;">Producto</th><th style="width:15% !important; text-align:center">Cantidad requerida</th><th style="width:15% !important; text-align:center">Cantidad validada por compras</th><th style="text-align:center">Costo validado por compras</th></thead><tbody></tr>'
                    for line in self.order_line.filtered(lambda x: x.cantidad_a_comprar > 0):
                        prods_html += '<tr><td style="text-align:justify">' + line.name + '</td><td style="text-align:center">' + str(line.cantidad_a_comprar) + '</td><td style="text-align:center">' + str(line.x_cantidad_disponible_compra) + '</td><td style="text-align:center">' + str(line.x_studio_nuevo_costo) + '</td></tr>'
                    prods_html += '</tbody></table>'
                    activity_message = ("<h3>Por favor realizar la compra de los siguientes productos</h3> %s") % (prods_html)
                    activity_user = self.env['res.users'].search([('login', 'like', '%compras1%')])
                    self.activity_schedule(
                        activity_type_id=4,
                        summary="Compra de productos",
                        note=activity_message,
                        user_id=activity_user.id
                    )
                if self.picking_ids:
                    self.picking_ids.write({'sale': self.id})
                    self.write({'albaran': self.picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.state not in ('cancel', 'draft', 'done'))[0].id})
                return r
        else:
            raise UserError(message)

    def action_cancel(self):
        if 'posted' in self.invoice_ids.mapped('state'):
            raise UserError(" No se puede cancelar dado que:\n Existen Facturas publicadas")
        else:
            if self.purchase_ids:
                if self.env.user.has_group('purchase.group_purchase_manager'):
                    return super(SaleOrder, self).action_cancel()
                else:
                    # MIGRACIÓN V19: `type` -> `message_type` en `message_post`.
                    self.message_post(body="Existen OC en proceso", message_type='notification')
                    self.write({'state': 'done', 'x_aprovacion_compras': True})
            else:
                return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    # MIGRACIÓN V19: declarado como `Html` (antes `Char`) porque el compute
    # guarda markup HTML (`<table>...`) y la vista usa `widget="html"` para
    # mostrarlo; con `Char`, v19 ya no lo renderiza y se ve el HTML crudo
    # como texto.
    existencia = fields.Html('Cantidades', compute='get_stock')
    check_price_reduce = fields.Boolean('Solicitud', default=False, store=True, compute='_compute_check_price_reduce')
    price_reduce_v = fields.Float('Precio solicitado')
    price_reduce_solicit = fields.Boolean('Solicitud (enviada)', default=False)
    invoice = fields.Boolean('Facturar', default=False)
    price_unit = fields.Float(copy=True)
    costo_envio = fields.Float('Costo de envío')
    comision = fields.Float('Comisión')
    proposal_id = fields.Many2one('proposal.purchases', 'Propuesta de origen')
    utilidad_esperada = fields.Integer('Utilidad esperada', compute='_compute_utilidad_esperada')
    existencia_alm_0 = fields.Float(related='product_id.stock_quant_warehouse_zero')
    # MIGRACIÓN V19: `Html` en vez de `Char`, mismo motivo que `existencia`
    # arriba (el compute guarda un `<img>` y la vista usa `widget="html"`).
    existencia_html = fields.Html(string="", compute='_compute_existencia_html')
    cantidad_asignada = fields.Integer(string="Cantidad asignada", compute='_compute_cantidad_asignada')
    facturas = fields.Char('Facturas', compute='_compute_facturas')
    existencias_mkp = fields.Html(compute='get_stock')
    valor_utilidad = fields.Monetary('Valor de la utilidad', compute='_compute_valor_utilidad')
    valor_utilidad_por_producto = fields.Monetary('Utilidad por producto', compute='_compute_valor_utilidad')
    costo_prom_total_venta = fields.Monetary('Costo promedio total (al momento de la venta)', compute='_compute_costos_promedio')
    costo_promedio_total = fields.Monetary('Costo promedio total', compute='_compute_costos_promedio')
    costo_promedio_venta = fields.Monetary('Costo promedio unitario (al momento de la venta)', compute='_compute_costos_promedio')
    cantidad_a_comprar = fields.Integer(string='Cantidad a comprar')
    cantidad_faltante = fields.Integer('Cantidad faltante', compute='_compute_cantidad_faltante')
    atendido_por = fields.Many2one('res.users', compute='_on_change_x_solicitud_atendida', store=True)

    # MIGRACIÓN V19: campos de Odoo Studio en `sale.order.line` formalizados
    # como código real (ver nota en `custom_models.py`). `x_studio_nivel`
    # aquí es la variante Selection (A-F) declarada en Studio sobre esta
    # línea; no se lee directamente en el código migrado (solo se usa
    # `order_id.x_studio_nivel`, el Char de `sale.order`), pero se formaliza
    # de cualquier forma para no perder el dato de producción.
    x_studio_nuevo_costo = fields.Monetary('Nuevo costo')
    x_studio_nivel = fields.Selection(string='Nivel', selection=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F')])
    # MIGRACIÓN V19: sin valores de opción confirmados por el usuario para
    # este campo; se declara como Char (compatible a nivel de columna con
    # Selection) para no perder los datos ya almacenados en producción.
    x_solicitud_atendida = fields.Char(string='Atendido')
    x_utilidad_por = fields.Integer(string='Utilidad %', compute='_compute_x_utilidad_por')
    x_descripcion_corta = fields.Char(string='Descripción corta', related='product_id.name')
    x_validacion_precio = fields.Boolean(string='Validación de precio')
    x_precio_propuesta = fields.Float(string='Precio propuesta')
    x_cantidad_disponible_compra = fields.Integer(string='Cantidad disponible compra')
    x_tiempo_entrega_compra = fields.Char(string='Tiempo de entrega compra')
    x_vigencia_compra = fields.Char(string='Vigencia compra')
    x_nuevo_precio = fields.Monetary(string='Nuevo precio')
    x_studio_costo_promedio = fields.Float(string='Costo promedio', related='product_id.standard_price')

    @api.depends('x_studio_nuevo_costo', 'price_unit', 'x_studio_costo_promedio')
    def _compute_x_utilidad_por(self):
        for record in self:
            if record.x_studio_nuevo_costo > 0:
                record.x_utilidad_por = (1 - (record.x_studio_nuevo_costo / record.price_unit)) * 100 if record.price_unit else 0
            elif record.price_unit > 0:
                record.x_utilidad_por = (1 - (record.x_studio_costo_promedio / record.price_unit)) * 100
            else:
                record.x_utilidad_por = 0

    def _compute_cantidad_faltante(self):
        for record in self:
            record.cantidad_faltante = record.product_uom_qty - record.product_id.stock_quant_warehouse_zero

    @api.depends('x_solicitud_atendida')
    def _on_change_x_solicitud_atendida(self):
        for record in self:
            if record.x_solicitud_atendida == 'Atendido':
                record.atendido_por = self.env.uid
            else:
                record.atendido_por = None

    def _compute_costos_promedio(self):
        for record in self:
            record.costo_promedio_venta = record.price_unit * (1 - record.x_utilidad_por / 100)
            record.costo_promedio_total = record.product_uom_qty * record.x_studio_costo_promedio
            record.costo_prom_total_venta = record.price_unit * (1 - record.x_utilidad_por / 100) * record.product_uom_qty

    def _compute_valor_utilidad(self):
        for record in self:
            utilidad_x_producto = record.price_unit - record.x_studio_costo_promedio
            valor_utilidad = record.product_uom_qty * (utilidad_x_producto)
            record.valor_utilidad = valor_utilidad
            record.valor_utilidad_por_producto = utilidad_x_producto

    def _compute_facturas(self):
        lista_fact = []
        for record in self:
            record['facturas'] = ''
            if record.order_id:
                if record.order_id.invoice_ids:
                    for i, inv in enumerate(record.order_id.invoice_ids):
                        if inv.name == '/':
                            lista_fact.append('(* ' + str(inv.id) + ')')
                        else:
                            lista_fact.append(inv.name)
                    record['facturas'] = ', '.join(lista_fact)
                    lista_fact = []

    @api.depends('product_uom_qty')
    def _compute_cantidad_asignada(self):
        for record in self:
            # MIGRACIÓN V19: `detailed_type` -> `type`.
            if record.product_id.type == 'service':
                record.cantidad_asignada = record.product_uom_qty
            else:
                orden = record.order_id
                record.cantidad_asignada = 0
                # MIGRACIÓN V19: `move_ids_without_package` -> `move_ids`.
                picking_lines = orden.picking_ids.filtered(lambda x: ('PICK' in x.name or 'PACK' in x.name or 'OUT' in x.name) and x.state in ['assigned', 'confirmed'])\
                    .mapped('move_ids').filtered(lambda y: y.product_id == record.product_id)
                if not picking_lines:
                    kit = record.product_id.bom_ids.bom_line_ids
                    productos_kit = kit.mapped('product_id')
                    picking_lines = orden.picking_ids.filtered(
                        lambda x: ('PICK' in x.name or 'PACK' in x.name or 'OUT' in x.name) and x.state in ['assigned', 'confirmed']) \
                        .mapped('move_ids').filtered(lambda y: y.product_id in productos_kit)
                    asignados = []
                    for producto in productos_kit:
                        asignados.append(sum(picking_lines.filtered(lambda x: x.product_id == producto).mapped('product_uom_qty')))
                    if asignados:
                        record.cantidad_asignada = min(asignados)
                    else:
                        record.cantidad_asignada = 0
                else:
                    producto = picking_lines[0].product_id
                    # MIGRACIÓN V19: `reserved_availability` -> `quantity`.
                    total_reservado = sum(picking_lines.mapped('quantity'))
                    lineas_pedido = record.order_id.order_line.filtered(lambda x: x.product_id == producto)
                    if len(lineas_pedido) > 1:
                        for linea in lineas_pedido:
                            if total_reservado > linea.qty_to_deliver:
                                linea.cantidad_asignada = linea.qty_to_deliver
                                total_reservado -= linea.qty_to_deliver
                            else:
                                linea.cantidad_asignada = total_reservado
                                total_reservado = 0
                    else:
                        record.cantidad_asignada = total_reservado

    def get_valor_minimo(self):
        if self.order_id.x_studio_nivel:
            margen = self.product_id.x_fabricante['x_studio_margen_' + str(self.order_id.x_studio_nivel)] if self.product_id.x_fabricante else 12
        else:
            raise UserError("Falta definir el nivel en el cliente")
        return self.product_id.standard_price / ((100 - margen) / 100)

    @api.depends('price_unit', 'x_studio_nuevo_costo')
    def _compute_check_price_reduce(self):
        valor_nuevo_costo = 0.0
        for record in self:
            if record.order_id.x_studio_nivel:
                margen = record.product_id.x_fabricante['x_studio_margen_' + str(record.order_id.x_studio_nivel)] if record.product_id.x_fabricante else 12
                if record.x_studio_nuevo_costo > 0.0:
                    valor_nuevo_costo = record.x_studio_nuevo_costo / ((100 - margen) / 100)
                valor = round(record.product_id.standard_price / ((100 - margen) / 100) + .5)
            else:
                raise UserError("Falta definir el nivel en el cliente")
            if valor_nuevo_costo > record.price_unit:
                record.price_reduce_v = record.price_unit
                record.check_price_reduce = True
            elif valor <= record.price_unit:
                record.check_price_reduce = False
                record.price_reduce_v = 0.0
            else:
                record.price_reduce_v = record.price_unit
                record.check_price_reduce = True

    # MIGRACIÓN V19: `product_id_change`/`product_uom_change` ya no existen
    # como métodos públicos en `sale.order.line` (el core los reemplazó por
    # `_onchange_product_id` -privado- y campos `compute` para el precio,
    # que se recalculan solos); no hay implementación de la clase base que
    # llamar por `super()`. También se corrige `product_uom` -> `product_uom_id`
    # en el segundo `@api.onchange`, que con el nombre viejo nunca se
    # disparaba al cambiar la unidad de medida.
    @api.onchange('product_id')
    def product_id_change(self):
        self.limit_price()

    @api.onchange('product_uom_id', 'product_uom_qty')
    def product_uom_change(self):
        old_price = self.price_unit
        self.limit_price()
        if round(old_price, 2) != round(self.price_unit, 2):
            self.price_unit = old_price

    @api.depends('product_uom_qty', 'product_id')
    def _compute_existencia_html(self):
        for record in self:
            if record.order_id.state != 'sale':
                color = '#D23F3A' if record.product_id.stock_quant_warehouse_zero - record.product_uom_qty < 0 else ' #00A09D'
            else:
                color = '#D23F3A' if record.cantidad_asignada + record.qty_delivered + record.qty_invoiced - record.product_uom_qty < 0 else ' #00A09D'
            record.existencia_html = '<img src="/sale_purchase_confirm/static/img/chart.png" style="width:15px; filter: opacity(0.5) drop-shadow(0 0 0 ' + color + ') saturate(450%);;"/>'

    def limit_price(self):
        for record in self:
            valor = 0
            if record.product_id:
                if record.order_id.x_studio_nivel:
                    margen = record.product_id.x_fabricante['x_studio_margen_' + str(record.order_id.x_studio_nivel)] if record.product_id.x_fabricante else 12
                else:
                    margen = 12
                valor = record.product_id.standard_price / ((100 - margen) / 100)
                record.product_id.update({'lst_price': 0})
            record['x_nuevo_precio'] = round(valor + .5)
            record.update({'price_unit': round(valor + .5)})

    @api.depends('product_id')
    def get_stock(self):
        for record in self:
            existencia = ""
            existencia_mkp = ""
            nombre = ""
            if record.product_id:
                zero = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 187).mapped('available_quantity'))
                zero1 = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 187).mapped('reserved_quantity'))
                market = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 80).mapped('available_quantity'))
                market1 = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 80).mapped('reserved_quantity'))
                existencia = "<table><thead><tr><th>A-0</th><th>A14</th></tr><tr><th>D/R</th><th>D/R</th></tr></thead><tbody><tr><td>" + str(int(zero)) + "/" + str(int(zero1)) + "</td><td>" + str(int(market)) + "/" + str(int(market1)) + "</td></tr></tbody>"
                nombre = record.warehouse_id.name
                if not nombre:
                    nombre = ''
                wh = record.order_id.warehouse_id.lot_stock_id
                disponible = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id == wh).mapped('available_quantity'))
                reservado = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id == wh).mapped('reserved_quantity'))

                existencia_mkp = '<table><thead style="width: 100%; text-align: center;font-size: 10px;"><tr><th>' + nombre + '</th></tr></thead>' \
                                                                                                                              '<tbody>' \
                                                                                                                              '<tr style="width: 100%; text-align: center;"><td >D/R</td></tr>' \
                                                                                                                              '<tr style="width: 100%; text-align: center;"><td>' + str(
                                                                                                                                int(disponible)) + '/' + str(int(reservado)) + '</td></tr>' \
                                                                                                                                '</tbody>' \
                                                                                                                                '</table>'
            record.existencias_mkp = existencia_mkp
            record.existencia = existencia

    @api.depends('x_studio_nuevo_costo', 'price_unit')
    def _compute_utilidad_esperada(self):
        for record in self:
            if not record.order_id.x_studio_nivel:
                raise UserError('Falta definir el nivel del cliente')
            record.utilidad_esperada = record.product_id.x_fabricante['x_studio_margen_' + str(record.order_id.x_studio_nivel)] if record.product_id.x_fabricante and record.order_id.x_studio_nivel else 12
            if record['x_studio_nuevo_costo'] > 0.0:
                utilidad_esperada_nuevo_costo = (1 - (record.x_studio_nuevo_costo / record.price_unit)) * 100
                record.utilidad_esperada = max(utilidad_esperada_nuevo_costo, record.utilidad_esperada)


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        r = super(AccountMoveReversal, self).reverse_moves()
        move = self.env['account.move'].browse(r['res_id'])
        move.write({'reason': self.reason})
        return r


class SaleAdvancePay(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        r = super(SaleAdvancePay, self).create_invoices()
        for s in sale_orders:
            s.invoice_ids.write({'l10n_mx_edi_usage': s.partner_id_uso_cfdi})
        return r


class Alerta_limite_de_credito(models.TransientModel):
    _name = 'sale.order.alerta'
    _description = 'Alerta para reduccion de precio'

    sale_id = fields.Many2one('sale.order', 'Pedido de venta relacionado')
    line_ids = fields.Many2many('sale.order.line', string='Productos a comprar')
    mensaje = fields.Html('Mensaje')
    mensaje_bottom = fields.Html('Mensaje (detalle)')

    def confirmar_sale(self):
        self.sale_id.order_line.filtered(lambda x: x.check_price_reduce).write({'price_reduce_solicit': True})
        self.sale_id.write({'solicito_validacion': True})
        lines_no_stock = self.sale_id.order_line.filtered(
            lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0)
        if lines_no_stock:
            self.sale_id.write({'state': 'sale_conf', 'solicitud_parcial': True})
            lines_no_stock.write({'x_validacion_precio': True})
        self.sale_id.order_line.order_id.update({'state': 'sale_conf'})
        mensaje = ''
        if self.sale_id.order_line.filtered(lambda y: y.price_reduce_v > 0.0):
            mensaje = '<h3>Se solicita la reducción de precio de los siguientes productos</h3><table class="table" style="width: 100%"><thead>' \
                      '<tr style="width: 30% !important;"><th>Producto</th>' \
                      '<th style="width: 10%">Costo promedio</th>' \
                      '<th style="width: 10%">Precio unitario anterior</th>' \
                      '<th style="width: 10%">Margen anterior</th>' \
                      '<th style="width: 10%">Nuevo costo</th>' \
                      '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                      '<th style="width: 10%">Nuevo precio unitario</th>' \
                      '<th style="width: 10%">Nuevo margen</th>' \
                      '</tr></thead>' \
                      '<tbody>'
            for order_line in self.sale_id.order_line:
                if order_line.price_reduce_v > 0.0:
                    margen = order_line.product_id.x_fabricante[
                        'x_studio_margen_' + str(order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                    mensaje += '<tr><td>' + order_line.name + '</td><td>' \
                               + str(order_line.product_id.standard_price) + '</td><td>' \
                               + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                               + str(margen) + '</td><td>' \
                               + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                               + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                               + str(round(order_line.price_unit)) + '</td><td>' \
                               + str(round((1 - (order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                               + '</td></tr>'
            mensaje += '</tbody></table>'
        if lines_no_stock:
            mensaje += '</tbody></table>'
            mensaje += '<h3>Los siguientes productos no tienen existencia o tienen existencia parcial y se solicita la aprobación de la orden parcial</h3><table class="table" style="width: 100%;margin-left: auto;margin-right: auto;"><thead>' \
                       '<tr><th>Producto</th>' \
                       '<th>Disponible en almacén 0</th>' \
                       '<th>Costo promedio</th>' \
                       '<th>Cantidad solicitada</th>' \
                       '<th>Cantidad faltante</th>' \
                       '</tr></thead>' \
                       '<tbody>'
            for order_line in lines_no_stock:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.x_descripcion_corta + '</td><td>' \
                           + str(order_line.product_id.stock_quant_warehouse_zero) + '</td><td>' \
                           + str(order_line.product_id.standard_price) + '</td><td>' \
                           + str(order_line.product_uom_qty) + '</td><td>' \
                           + str(
                    order_line.product_uom_qty + order_line.x_cantidad_disponible_compra - order_line.product_id.stock_quant_warehouse_zero) + '</td></tr>'
            mensaje += '</tbody></table>'

        # MIGRACIÓN V19: `type` -> `message_type` en `message_post`; y
        # `body` -> `Markup(...)`, ver la nota en `confirmar_parcial`.
        self.sale_id.message_post(body=Markup(mensaje), message_type="notification")

    def confirmar_validacion(self):
        o_lines = self.sale_id.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0)
        o_lines.write({'x_validacion_precio': True})
        self.sale_id.write({'solicito_validacion': True})
        msg = self.mensaje.replace('Se solicitará validar datos de los siguientes productos', 'Se solicitó validar datos masivamente')
        self.sale_id.message_post(body=Markup(msg), message_type="notification")
        activity_user = self.env['res.users'].search([('login', 'like', '%compras1%')])
        self.sale_id.activity_schedule(
            activity_type_id=4,
            summary="Validación de precios",
            note=msg,
            user_id=activity_user.id
        )

    def confirmar_parcial(self):
        mensaje = ''
        self.sale_id.order_line.order_id.update({'state': 'sale_conf', 'solicitud_parcial': True})
        self.sale_id.order_line.filtered(lambda x: x.check_price_reduce).write({'price_reduce_solicit': True})
        lines = self.sale_id.order_line.filtered(lambda x: (x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0)
        if lines:
            mensaje = '<h3>Se solicita aprobar la orden parcial</h3><table class="table" style="width: 100%"><thead>' \
                      '<tr style="width: 40% !important;"><th>Producto</th>' \
                      '<th style="width: 20%">Existencia en almacén 0</th>' \
                      '<th style="width: 20%">Cantidad validad por compras</th>' \
                      '<th style="width: 20%">Cantidad solicitada</th>' \
                      '</tr></thead>' \
                      '<tbody>'
            for order_line in lines:
                mensaje += '<tr><td>' + order_line.name + '</td><td>' \
                           + str(order_line.product_id.stock_quant_warehouse_zero) + '</td><td>' \
                           + str(order_line.x_cantidad_disponible_compra) + '</td><td>' \
                           + str(order_line.product_uom_qty) + '</td><td>' \
                           + '</td></tr>'
            mensaje += '</tbody></table>'
        lines_reduc = self.sale_id.order_line.filtered(lambda x: x.check_price_reduce)
        if lines_reduc:
            mensaje += '<h3>Se solicita la aprobación de reducción de precio de los siguientes productos.</h3><table class="table" style="width: 100%"><thead>' \
                       '<tr style="width: 30% !important;"><th>Producto</th>' \
                       '<th style="width: 10%">Costo promedio</th>' \
                       '<th style="width: 10%">Precio unitario anterior</th>' \
                       '<th style="width: 10%">Margen anterior</th>' \
                       '<th style="width: 10%">Nuevo costo</th>' \
                       '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                       '<th style="width: 10%">Nuevo precio unitario</th>' \
                       '<th style="width: 10%">Nuevo margen</th>' \
                       '</tr></thead>' \
                       '<tbody>'
            for order_line in lines_reduc:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.name + '</td><td>' \
                           + str(order_line.product_id.standard_price) + '</td><td>' \
                           + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                           + str(margen) + '</td><td>' \
                           + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                           + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                           + str(round(order_line.price_unit)) + '</td><td>' \
                           + str(round((1 - (
                        order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                           + '</td></tr>'
            mensaje += '</tbody></table>'
        # MIGRACIÓN V19: `message_post` en 19.0 escapa por defecto el
        # `body` si es un `str` normal -sólo lo renderiza como HTML si
        # viene envuelto en `Markup`, cambio de seguridad anti-XSS del
        # core-; sin esto el mensaje aparecía como HTML crudo (las
        # etiquetas `<table>`, `<tr>`, etc. visibles como texto) en vez de
        # la tabla renderizada.
        self.sale_id.message_post(body=Markup(mensaje), message_type="notification")


class SaleInvoice(models.TransientModel):
    _name = 'sale.orders.invoice'
    _description = 'Wizard de facturacion'
    name = fields.Char()
    sale_ids = fields.Many2many('sale.order', store=True)
    order_lines_ids = fields.One2many('sale.line.wizar', 'rel_id')

    def get_filtered_record(self):
        ordenes = self.env['sale.order'].browse(self.env.context.get('active_ids')).filtered(lambda x: x.state in ('sale', 'done'))
        reg = self.create({'sale_ids': [(6, 0, ordenes.ids)]})
        for sale_line in ordenes.mapped('order_line'):
            if sale_line.qty_invoiced != sale_line.product_uom_qty:
                self.env['sale.line.wizar'].create({'rel_id': reg.id, 'sale_line_id': sale_line.id})
        view = self.env.ref('sale_purchase_confirm.sale_order_invoice_conf_view')
        return {
            "name": _("Facturar"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.orders.invoice",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": reg.id,
            "context": self.env.context,
        }

    def confir(self):
        valor = self.order_lines_ids.filtered(lambda x: x.check == True)
        if not valor:
            raise UserError('No se ha seleccionado nada para facturar.')
        if valor.filtered(lambda y: y.qty_invoice == 0):
            raise UserError('Especifique una cantidad a facturar.')
        if valor.filtered(lambda y: y.cantidad_asignada < y.qty_invoice and not y.order_id.invoice_approved):
            raise UserError('No se puede facturar una cantidad mayor a la asignada si no se ha solicitado aprobación.')
        ordenes = self.env['sale.order'].browse(self.env.context.get('active_ids')).filtered(lambda x: x.state in ('sale', 'done'))
        if valor.filtered(lambda w: w.qty_invoice > w.qty):
            raise UserError('No se puede facturar una cantidad mayor a cantidad solicita.')
        if len(ordenes.mapped('partner_id')) > 1:
            raise UserError("No se puede crear la factura con diferentes clientes")
        else:
            if valor:
                invoice_vals = self.sale_ids[0]._prepare_invoice() if len(self.sale_ids) > 1 else self.sale_ids._prepare_invoice()
                invoice_line_vals = []
                for line in valor:
                    data = line.sale_line_id._prepare_invoice_line()
                    data['quantity'] = line.qty_invoice
                    invoice_vals['invoice_line_ids'] += [(0, 0, data)]
                moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)
                for move in moves:
                    # MIGRACIÓN V19: `message_post_with_view` fue eliminado
                    # sin reemplazo directo; se reemplaza por un
                    # `message_post` simple enlazando el/los pedido(s) de
                    # origen en el cuerpo del mensaje.
                    origins = move.line_ids.mapped('sale_line_ids.order_id')
                    move.message_post(
                        body=_("Origin: %s") % (', '.join(origins.mapped('name')) or ''),
                        subtype_id=self.env.ref('mail.mt_note').id,
                    )
                if moves:
                    return self.sale_ids[0].action_view_invoice()
        return True


class SaleInvoiceWizard(models.TransientModel):
    _name = 'sale.line.wizar'
    _description = 'Wizard linea orden de venta'
    sale_line_id = fields.Many2one('sale.order.line')
    order_id = fields.Many2one(related='sale_line_id.order_id')
    product_id = fields.Many2one(related='sale_line_id.product_id')
    qty = fields.Float(related='sale_line_id.product_uom_qty', string='Cantidad Solicitada')
    qty_sale_invoice = fields.Float(related='sale_line_id.qty_invoiced', string='Cantidad Facturada')
    cantidad_asignada = fields.Integer(related='sale_line_id.cantidad_asignada', string='Cantidad Asignada')
    cantidad_entregada = fields.Float(related='sale_line_id.qty_delivered', string='Cantidad Entregada')
    qty_invoice = fields.Float('Cantidad a Facturar')
    rel_id = fields.Many2one('sale.orders.invoice')
    check = fields.Boolean('Facturar', default=False)


class ProposalState(models.Model):
    _name = 'proposal.state'
    _description = 'Estado de propuesta de compra'
    name = fields.Char()


class ProductInherit(models.Model):
    _inherit = 'product.product'
    stock_quant_warehouse_zero = fields.Float(string='Cantidad disponible en almacén 0', compute='_compute_stock_quant_warehouse_zero')

    def _compute_stock_quant_warehouse_zero(self):
        for record in self:
            record.stock_quant_warehouse_zero = sum(record.stock_quant_ids.filtered(lambda x: x.location_id.id == 187).mapped('available_quantity'))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ultimo_costo_compra = fields.Float(string='Último costo de compra', compute='_compute_ultimo_costo')

    def _compute_ultimo_costo(self):
        for record in self:
            record.ultimo_costo_compra = 0.0
            if record.seller_ids:
                record.ultimo_costo_compra = record.seller_ids[-1].price
