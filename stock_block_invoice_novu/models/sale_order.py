# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Nuevo campo computado para mostrar advertencias en la orden
    warning_message = fields.Text(compute='_compute_warning_message', store=False)

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'warehouse_id')
    def _compute_warning_message(self):
        """
        Calcula un mensaje de advertencia para la orden si algún producto no tiene stock.
        Esto se muestra en la vista como un alerta.
        """
        for order in self:
            lineas_problematicas = []
            # Reutilizamos la misma lógica de verificación de stock
            for line in order.order_line:
                if line.product_id.type == 'product' and line.product_id.detailed_type == 'product':
                    warehouse = order.warehouse_id
                    cantidad_disponible = line.product_id.with_context(warehouse=warehouse.id).free_qty
                    cantidad_a_comparar = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                    
                    if cantidad_disponible < cantidad_a_comparar:
                        lineas_problematicas.append(
                            f"- {line.product_id.display_name} (Necesario: {cantidad_a_comparar}, Disponible: {cantidad_disponible})"
                        )
            # Unimos todas las advertencias en un solo mensaje
            if lineas_problematicas:
                order.warning_message = "⚠️ Advertencia: Stock insuficiente para facturar:\n" + "\n".join(lineas_problematicas)
            else:
                order.warning_message = False

    def action_invoice_create(self, grouped=False, final=False):
        """
        Override del método estándar para verificar la disponibilidad de stock
        antes de crear las facturas.
        """
        for order in self:
            lineas_sin_stock = []
            for line in order.order_line:
                if line.product_id.type == 'product' and line.product_id.detailed_type == 'product':
                    warehouse = order.warehouse_id
                    cantidad_disponible = line.product_id.with_context(warehouse=warehouse.id).free_qty
                    cantidad_a_comparar = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                    
                    if cantidad_disponible < cantidad_a_comparar:
                        lineas_sin_stock.append(
                            f"- {line.product_id.display_name} (Necesario: {cantidad_a_comparar}, Disponible: {cantidad_disponible})"
                        )

            if lineas_sin_stock:
                mensaje_error = "❌ No se puede facturar debido a stock insuficiente:\n" + "\n".join(lineas_sin_stock)
                raise UserError(mensaje_error)

        return super(SaleOrder, self).action_invoice_create(grouped, final)