from odoo import fields,models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    use_cfdi = fields.Char('Uso CFDI', compute='get_cfi_use')
    nombre_receptor = fields.Char("Nombre")

    @api.depends('attachment_ids')
    def get_cfi_use(self):
        for record in self:
            record.use_cfdi = ""
            if record.attachment_ids:
                for att in record.attachment_ids:
                    if att.datas:
                        if 'Invoice' in att.name and 'xml' in att.name:
                            path = att._full_path(att.store_fname)
                            try:
                                with open(path, 'r') as f:
                                    data = f.read()
                                Bs_data = BeautifulSoup(data, "xml")
                                for s in Bs_data.children:
                                    for ss in s.children:
                                        if ss.name == "Receptor":
                                            record.use_cfdi = ss.attrs.get("UsoCFDI")
                                            record.nombre_receptor = ss.attrs.get("Nombre")
                            except:
                                continue

    def _l10n_mx_edi_create_cfdi(self):
        raise UserError('Entre _l10n_mx_edi_create_cfdi')
        cfdi_str = super()._l10n_mx_edi_create_cfdi()

        # Convierte a árbol XML
        if not cfdi_str:
            return cfdi_str
        cfdi_xml = etree.fromstring(cfdi_str.encode('UTF-8'))

        # Buscar el complemento Carta Porte
        complemento = cfdi_xml.find('{http://www.sat.gob.mx/cfd/4}Complemento')
        if complemento is not None:
            carta_porte = complemento.find('{http://www.sat.gob.mx/CartaPorte20}CartaPorte')
            if carta_porte is not None:
                # Buscar todos los nodos Mercancias/Mercancia
                for mercancia in carta_porte.findall('.//{http://www.sat.gob.mx/CartaPorte20}Mercancia'):
                    # Agregar el atributo BienesTransp opcionalmente si falta
                    # Agregar MaterialPeligroso = "No"
                    mercancia.set('MaterialPeligroso', 'No')

        # Retornar el nuevo XML como string
        return etree.tostring(cfdi_xml, pretty_print=True, encoding='UTF-8').decode('UTF-8')



class AccountPayment(models.Model):
    _inherit = 'account.payment'
    use_cfdi = fields.Char('Uso CFDI', compute='get_cfi_use')
    nombre_receptor = fields.Char("Nombre")


    @api.depends('attachment_ids')
    def get_cfi_use(self):
        for record in self:
            record.use_cfdi = ""
            if record.attachment_ids:
                for att in record.attachment_ids:
                    if att.datas:
                        if att.description and 'CFDI de pago' in att.description and 'xml' in att.name:
                            path = att._full_path(att.store_fname)
                            try:
                                with open(path, 'r') as f:
                                    data = f.read()
                                Bs_data = BeautifulSoup(data, "xml")
                                for s in Bs_data.children:
                                    for ss in s.children:
                                        if ss.name == "Receptor":
                                            record.use_cfdi = ss.attrs.get("UsoCFDI")
                                            record.nombre_receptor = ss.attrs.get("Nombre")
                            except:
                                continue