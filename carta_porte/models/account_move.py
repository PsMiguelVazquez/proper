from odoo import fields,models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    use_cfdi = fields.Char('Uso CFDI', compute='get_cfi_use')

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
                            except:
                                continue

