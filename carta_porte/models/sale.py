from odoo import fields,models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def action_cancel(self):
    #     if 'posted' in self.invoice_ids.mapped('state'):
    #         raise UserError(" No se puede cancelar dado que:\n Existen Facturas publicadas")
    #     else:
    #         return super(SaleOrder, self).action_cancel()