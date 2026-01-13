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

        #Obtener las lineas de la factura
        invoice_lines = self.line_ids

        #obener lineas consiliables
        reconcilable = invoice_lines.filtered(
            lambda l: l.account_id.internal_type in ('receivable', 'payable')
        )
        
        #Obtener lo conciliado
        related_lines = self.env['account.move.line']
        related_lines |= invoice_lines
    
        for line in reconcilable:
            related_lines |= line.matched_debit_ids.mapped('debit_move_id')
            related_lines |= line.matched_credit_ids.mapped('credit_move_id')
    
        #Lineas extras como pagos
        all_moves = related_lines.mapped('move_id')
        all_lines = all_moves.mapped('line_ids')
    
        #Ordenar las lineas
        all_lines = all_lines.sorted(
            lambda l: (l.date, l.move_id.id, l.id)
        )
    
        #Escribir las lineas en el reporte
        row = 9
        suma_debitos = 0.0
        suma_creditos = 0.0
        last_move = False
    
        for line in all_lines:
            #Línea en blanco entre asientos
            if last_move and last_move != line.move_id:
                row += 1
    
            sheet[f"A{row}"] = line.account_id.code or ''
            sheet[f"B{row}"] = line.account_id.name or ''
            sheet[f"C{row}"] = line.move_id.name or ''
            sheet[f"D{row}"] = dia
    
            if line.debit:
                sheet[f"G{row}"] = float(line.debit)
                sheet[f"G{row}"].number_format = '#,##0.00'
                suma_debitos += line.debit
    
            if line.credit:
                sheet[f"H{row}"] = float(line.credit)
                sheet[f"H{row}"].number_format = '#,##0.00'
                suma_creditos += line.credit
    
            last_move = line.move_id
            row += 1
    
        #Totales generales del reporte
        sheet[f"F{row}"] = "Totales"
        sheet[f"G{row}"] = suma_debitos
        sheet[f"H{row}"] = suma_creditos
        sheet[f"G{row}"].number_format = '#,##0.00'
        sheet[f"H{row}"].number_format = '#,##0.00'

        #Guardar cambios y adjuntarlo al move
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'Poliza_de_diario_{self.name}_{timestamp}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'account.move',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        output.close()

        self.poliza_generada = True

        _logger.info(f"Póliza generada correctamente (attachment id={attachment.id}) para {self.name}")
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
        _logger.error("ENTRO A reconcile")

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
                    _logger.exception(f'Error generando póliza para factura {move.name}')

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
                    f'Eliminando {len(attachments)} póliza(s) de la factura {move.name} por desconciliación')
                attachments.sudo().unlink()

        return res
        