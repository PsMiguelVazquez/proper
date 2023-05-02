from odoo import fields,models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    version = fields.Char(compute='get_xml_data_edi', string='Version')
    transporte = fields.Char(compute='get_xml_data_edi', string='Transporte')
    code_vehicle = fields.Char(compute='get_xml_data_edi', string='Codigo Vehicular')
    rfc_figura = fields.Char(compute='get_xml_data_edi', string='RFC Figura')

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
                ult = list(element.children)[-1]
                pen = list(element.children)[-2]
                record.version = element.attrs.get("Version")
                record.transporte = element.attrs.get("TranspInternac")
                record.code_vehicle = list(list(pen.children)[-1].children)[0].attrs.get('ConfigVehicular')
                record.rfc_figura = list(ult.children)[0].attrs.get('RFCFigura')
            else:
                record.version = ""
                record.transporte = ""
                record.code_vehicle = ""
                record.rfc_figura = ""

