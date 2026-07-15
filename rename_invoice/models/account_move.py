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
    # Para PAGOS no existe un método público equivalente: el nombre del
    # adjunto de CFDI de pago se arma inline dentro de un método privado
    # (`f'{journal.code}-{name}-MX-Payment-20.xml'`, sin hook de
    # extensión). Interceptarlo requeriría parchear un método privado no
    # documentado, lo cual es fràgil ante futuros cambios de esta
    # dependencia Enterprise; se opta por mantener el nombre por defecto
    # de 19.0 para pagos y no tocar ese flujo, priorizando la estabilidad
    # del módulo.
    def _l10n_mx_edi_get_invoice_cfdi_filename(self):
        self.ensure_one()
        return (self.name or '').replace('/', '') + '.xml'
