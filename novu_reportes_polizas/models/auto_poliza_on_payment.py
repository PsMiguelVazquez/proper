# -*- coding: utf-8 -*-
import io
import os
import base64
import logging
import datetime
import pytz
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from odoo import models, api, tools, fields

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    poliza_generada = fields.Boolean(string='Póliza generada', default=False, copy=False)

    def _generate_poliza_attachment(self):
        """Genera un Excel (poliza diario) usando la plantilla y lo adjunta a la factura."""
        _logger.error(f"Llegue a generar")
        if self.env.context.get('skip_poliza'):
            return
        
        self.ensure_one()

        addons_paths = tools.config['addons_path'].split(',')
        module_name = 'novu_reportes_polizas'
        file_relative_path = 'static/layouts/Layout_poliza_diario.xlsx'
        path = False
        for addons_path in addons_paths:
            test_path = os.path.join(addons_path.strip(), module_name, file_relative_path)
            if os.path.exists(test_path):
                path = test_path
                break

        if not path:
            _logger.error('No se encontró la plantilla %s en los addons_path', file_relative_path)
            return False

        workbook = load_workbook(filename=path)
        sheet = workbook.active

        # Valores para encabezado
        tz = pytz.timezone(self.env.user.tz or 'America/Mexico_City')
        timestamp2 = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.datetime.now(tz).strftime('%Y-%m-%d_%H_%M_%S')

        date_use = self.invoice_date or self.date or fields.Date.context_today(self)
        if isinstance(date_use, str):
            date_obj = datetime.datetime.strptime(date_use, '%Y-%m-%d').date()
        else:
            date_obj = date_use

        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        mes_nombre = meses.get(date_obj.month, "")

        folio_poliza = self.env['ir.sequence'].next_by_code('poliza.diario.seq') or '/'

        # Escribir encabezados en plantilla (mismas celdas que el wizard)
        def safe_write(sheet, cell_ref, value):
            cell = sheet[cell_ref]
            if isinstance(cell, MergedCell):
                for merge_range in sheet.merged_cells.ranges:
                    if cell.coordinate in merge_range:
                        master_cell = sheet.cell(merge_range.min_row, merge_range.min_col)
                        master_cell.value = value
                        return
                raise ValueError("No se encontró celda combinada para %s" % cell_ref)
            else:
                cell.value = value

        safe_write(sheet, 'B2', f"{folio_poliza}")
        safe_write(sheet, 'B3', f"{timestamp2}")
        safe_write(sheet, 'B4', f"{mes_nombre.upper()} EJERCICIO: {date_obj.year}")
        safe_write(sheet, 'B5', self.name or self.invoice_origin or '')

        dia = date_obj.day
        row = 8

        # Obtener las líneas contables de la factura
        lines = self.line_ids.filtered(lambda l: l.account_id)

        # Filtrar similares a la lógica del wizard
        lines_clientes = lines.filtered(lambda m: m.account_id.code and m.account_id.code.startswith('105'))
        lines_otros = lines.filtered(lambda m: not (m.account_id.code and m.account_id.code.startswith('105')))

        suma_debitos = 0.0
        suma_creditos = 0.0

        mov_ant = ''
        for mov in lines_clientes:
            factura = self.name
            if mov_ant == factura:
                row += 1
            else:
                mov_ant = factura
                row += 2

            if mov.debit and float(mov.debit) > 0:
                sheet[f"A{row}"] = mov.account_id.code
                sheet[f"B{row}"] = mov.partner_id.name
                sheet[f"C{row}"] = self.name
                sheet[f"D{row}"] = dia
                cell_debit = sheet[f"G{row}"]
                cell_debit.value = float(mov.debit or 0.0)
                cell_debit.number_format = '#,##0.00'
                suma_debitos += float(mov.debit or 0.0)

        row += 1
        resumen_por_cuenta = {}
        for mov in lines_otros:
            code = mov.account_id.code or ''
            name = mov.account_id.name or ''
            resumen_por_cuenta.setdefault(code, {"name": name, "debit": 0.0, "credit": 0.0})
            resumen_por_cuenta[code]["debit"] += float(mov.debit or 0.0)
            resumen_por_cuenta[code]["credit"] += float(mov.credit or 0.0)
            suma_debitos += float(mov.debit or 0.0)
            suma_creditos += float(mov.credit or 0.0)

        total_debito = 0.0
        total_credito = 0.0
        for code, datos in sorted(resumen_por_cuenta.items()):
            total_debito = datos["debit"]
            total_credito = datos["credit"]
            sheet[f"A{row}"] = code
            sheet[f"B{row}"] = datos["name"]
            sheet[f"D{row}"] = dia

            if total_debito > total_credito:
                cell_total_debit = sheet[f"G{row}"]
                cell_total_debit.value = float(total_debito - total_credito or 0.0)
                cell_total_debit.number_format = '#,##0.00'
            elif total_credito > total_debito:
                cell_total_credit = sheet[f"H{row}"]
                cell_total_credit.value = float(total_credito - total_debito or 0.0)
                cell_total_credit.number_format = '#,##0.00'
            else:
                sheet[f"G{row}"] = 0
                sheet[f"H{row}"] = 0
            row += 2

        # Totales
        sheet[f"F{row}"] = "Totales"
        cell_suma_total_debit = sheet[f"G{row}"]
        cell_suma_total_debit.value = float(suma_debitos or 0.0)
        cell_suma_total_debit.number_format = '#,##0.00'

        cell_suma_total_credit = sheet[f"H{row}"]
        cell_suma_total_credit.value = float(suma_creditos or 0.0)
        cell_suma_total_credit.number_format = '#,##0.00'

        # Guardar en memoria
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        
        _logger.error("Sali de generar, ire a adjuntar")
        attachment = self.env['ir.attachment'].create({
            'name': f'Poliza_de_diario_{self.name or self.id}_{timestamp}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'account.move',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        output.close()
        _logger.error("Sali de adjuntar y termine")
        
        _logger.info('Se generó poliza (attachment id=%s) para factura %s', attachment.id, self.name)
        return True


    def descarga_poliza(self):
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('name', 'ilike', 'Poliza_de_diario_')
        ], order='create_date desc', limit=1)
    
        if not attachment:
            return False
    
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def reconcile(self):
        _logger.error("🔥 ENTRO A reconcile")

        moves = self.mapped('move_id')
        res = super().reconcile()

        for move in moves:
            if (
                move.move_type in ('out_invoice', 'in_invoice')
                and move.payment_state == 'paid'
                and not move.poliza_generada
            ):
                try:
                    move._generate_poliza_attachment()
                    move.poliza_generada = True
                except Exception:
                    _logger.exception(
                        'Error generando póliza para factura %s', move.name
                    )

        return res

    def remove_move_reconcile(self):
        moves = self.mapped('move_id')
        res = super().remove_move_reconcile()

        for move in moves:
            if move.payment_state != 'paid':
                move.poliza_generada = False
                #Eliminar la poliza previa para poner la nueva cuando se concilie nuevamente
                attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', move.id),
                ('name', 'ilike', 'Poliza_de_diario_'),
            ])

            if attachments:
                _logger.info(
                    'Eliminando %s póliza(s) de la factura %s por desconciliación',
                    len(attachments), move.name
                )
                attachments.sudo().unlink()

        return res
        