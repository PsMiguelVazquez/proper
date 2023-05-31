from odoo import fields,models, api, _, modules
from odoo.exceptions import UserError
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    version = fields.Char(compute='get_xml_data_edi', string='Version')
    transporte = fields.Char(compute='get_xml_data_edi', string='Transporte')
    code_vehicle = fields.Char(compute='get_xml_data_edi', string='Codigo Vehicular')
    rfc_figura = fields.Char(compute='get_xml_data_edi', string='RFC Figura')
    fecha_timbrado_carta = fields.Datetime('Fecha de timbrado de Carta Porte')

    def l10n_mx_edi_action_send_delivery_guide(self):
        date_done_original = self.date_done
        if not self.move_lines.filtered(lambda ml: ml.quantity_done > 0):
            raise UserError('No hay cantidades hechas, no se puede generar la carta porte')
        self.date_done = fields.Datetime.now()
        r = super(StockPicking, self).l10n_mx_edi_action_send_delivery_guide()
        if r:
            self.fecha_timbrado_carta = fields.Datetime.now()
        self.date_done = date_done_original
        return r

    @api.depends('l10n_mx_edi_cfdi_file_id')
    def get_xml_data_edi(self):
        for record in self:
            if record.l10n_mx_edi_cfdi_file_id.datas:
                path = record.l10n_mx_edi_cfdi_file_id._full_path(record.l10n_mx_edi_cfdi_file_id.store_fname)
                with open(path, 'r') as f:
                    data = f.read()
                Bs_data = BeautifulSoup(data, "xml")
                complemeto = False
                for s in Bs_data.children:
                    for ss in s.children:
                        if ss.name == 'Complemento':
                            complemeto = ss
                element = list(complemeto.children)[0]
                try:
                    ult = list(element.children)[-1]
                    pen = list(element.children)[-2]
                    record.version = element.attrs.get("Version") if element and element.attrs.get("Version") else ''
                    record.transporte = element.attrs.get("TranspInternac") if element and element.attrs.get("TranspInternac") else ''
                    record.code_vehicle = list(list(pen.children)[-1].children)[0].attrs.get('ConfigVehicular') if pen and list(list(pen.children)[-1].children)[0].attrs.get('ConfigVehicular') else ''
                    record.rfc_figura = list(ult.children)[0].attrs.get('RFCFigura') if ult and list(ult.children)[0].attrs.get('RFCFigura') else ''
                except:
                    record.version = ""
                    record.transporte = ""
                    record.code_vehicle = ""
                    record.rfc_figura = ""
            else:
                record.version = ""
                record.transporte = ""
                record.code_vehicle = ""
                record.rfc_figura = ""