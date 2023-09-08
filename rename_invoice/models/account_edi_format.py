from odoo import models,api, fields, _
class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _post_invoice_edi(self, invoices):
        # EXTENDS l10n_mx_edi - rename attachment
        edi_result = super()._post_invoice_edi(invoices)
        if self.code != 'cfdi_3_3':
            return edi_result
        for invoice in invoices:
            if edi_result[invoice].get('attachment', False):
                cfdi_filename = ('%s%sMXInvoice4.0.xml' % (
                invoice.journal_id.code, invoice.payment_reference or invoice.name)).replace('/', '')
                edi_result[invoice]['attachment'].name = cfdi_filename
        return edi_result
