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
                if edi_result[invoice]['attachment'].mimetype == 'application/xml':
                    cfdi_filename = invoice.name.replace('/','') + '.xml'
                edi_result[invoice]['attachment'].name = cfdi_filename
        return edi_result

    def _post_payment_edi(self, payments):
        # EXTENDS l10n_mx_edi - rename attachment
        edi_result = super()._post_payment_edi(payments)
        if self.code != 'cfdi_3_3':
            return edi_result
        for move in payments:
            if edi_result[move].get('attachment', False):
                cfdi_filename = move.name.replace('/', '')
                edi_result[move]['attachment'].name = cfdi_filename
        return edi_result
