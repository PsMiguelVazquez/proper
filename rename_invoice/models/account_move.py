from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # MIGRACIÓN V19: en 15.0 este módulo sobreescribía
    # `account.edi.format._post_invoice_edi()`/`_post_payment_edi()`
    # (filtrando `self.code == 'cfdi_3_3'`) para renombrar el adjunto XML a
    # `<nombre_factura>.xml`. En 19.0, `l10n_mx_edi` ya NO depende de
    # `account_edi` en absoluto (arquitectura de timbrado propia, ver
    # `l10n_mx_edi.document`); esos hooks nunca se llaman para facturas MX,
    # por lo que la lógica original quedaría completamente muerta si se
    # migrara tal cual.
    #
    # El nuevo punto de extensión público para el nombre del adjunto de
    # FACTURAS es `_l10n_mx_edi_get_invoice_cfdi_filename()` (ver
    # `enterprise/l10n_mx_edi/models/account_move.py`), cuyo valor por
    # defecto en 19.0 ya es descriptivo
    # (`f"{journal.code}-{name}-MX-Invoice-4.0.xml"`), pero distinto del
    # nombre simple que este módulo entregaba (`<nombre_factura>.xml`).
    # Se sobreescribe para conservar el nombre original tal como lo espera
    # el cliente.
    #
    def _l10n_mx_edi_get_invoice_cfdi_filename(self):
        self.ensure_one()
        return (self.name or '').replace('/', '') + '.xml'

    # Para PAGOS no existe un método público equivalente al de facturas: el
    # nombre del adjunto de CFDI de pago se arma inline dentro de un método
    # privado no documentado dos niveles arriba
    # (`l10n_mx_edi_cfdi_invoice_try_update_payment`, línea
    # `cfdi_filename = f'{journal.code}-{name}-MX-Payment-20.xml'`), que a
    # su vez pasa ese nombre a `l10n_mx_edi.document._send_api()` y de ahí a
    # los callbacks de abajo. Parchear ese método directamente sería frágil
    # (es privado y puede cambiar de forma en cualquier upgrade de
    # Enterprise). En cambio, `_l10n_mx_edi_cfdi_payment_document_sent(_failed)`
    # sí son un punto de extensión razonablemente estable: reciben el
    # nombre ya calculado y solo lo usan para el campo `name` del
    # `ir.attachment` final -el nombre no participa en el armado del CFDI,
    # el sellado ni el envío al PAC (confirmado leyendo `_send_api` en
    # `l10n_mx_edi_document.py`)-, así que sobreescribirlo aquí es seguro.
    # El cliente pidió que el XML del complemento de pago se llame igual
    # que el PDF de "Complemento de pago" (reporte Studio sobre
    # `account.report_payment_receipt`, `print_report_name =
    # object.name.replace('/','')`); se replica la misma fórmula.
    def _l10n_mx_edi_cfdi_payment_document_sent(self, invoices, cfdi_filename, cfdi_str):
        cfdi_filename = (self.name or '').replace('/', '') + '.xml'
        return super()._l10n_mx_edi_cfdi_payment_document_sent(invoices, cfdi_filename, cfdi_str)

    def _l10n_mx_edi_cfdi_payment_document_sent_failed(self, error, invoices, cfdi_filename=None, cfdi_str=None):
        if cfdi_filename and cfdi_str:
            cfdi_filename = (self.name or '').replace('/', '') + '.xml'
        return super()._l10n_mx_edi_cfdi_payment_document_sent_failed(
            error, invoices, cfdi_filename=cfdi_filename, cfdi_str=cfdi_str)
