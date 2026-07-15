# Copyright 2018-2021 ForgeFlow S.L.

from odoo import models, api
from odoo.tools import float_compare


class AccountMove(models.Model):

    _inherit = "account.move"

    def js_assign_outstanding_line(self, line_id):
        self.ensure_one()
        if "paid_amount" in self.env.context:
            return super(
                AccountMove,
                self.with_context(
                    move_id=self.id,
                    line_id=line_id,
                    # MIGRACIÓN V19: diccionario mutable para rastrear cuánto
                    # de `paid_amount` sigue disponible a través de las
                    # llamadas recursivas dentro de un mismo reconcile() (ver
                    # AccountMoveLine._prepare_reconciliation_single_partial).
                    # No se puede usar un atributo de instancia en el
                    # recordset (account.move.line no lo permite), pero un
                    # objeto mutable guardado en el contexto sí sobrevive a
                    # los `with_context()` intermedios, porque estos solo
                    # copian el dict de contexto de forma superficial.
                    _paid_amount_state={"remaining": self.env.context["paid_amount"]},
                ),
            ).js_assign_outstanding_line(line_id)
        return super(AccountMove, self).js_assign_outstanding_line(line_id)


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    # MIGRACIÓN V19: el motor de conciliación fue reescrito por completo.
    # `_prepare_reconciliation_partials` (que en 15.0 recibía la lista plana
    # de partials ya calculados y simplemente recortaba `amount` de cada uno
    # hasta agotar `paid_amount`) ya no existe. La construcción de cada
    # partial ahora ocurre línea por línea en `_prepare_reconciliation_single_partial`,
    # llamada repetidamente por `_prepare_reconciliation_amls` mientras el par
    # débito/crédito siga teniendo residual (lo que incluye el residual que
    # nosotros mismos dejamos al recortar el monto). Por eso, en cuanto se
    # recorta un partial, hay que señalar explícitamente que no se debe volver
    # a intentar conciliar ese mismo par en esta llamada (si no, el bucle
    # seguiría creando partials cada vez más chicos hasta agotar el monto
    # original completo, anulando el recorte).
    #
    # Se deja que el core calcule el partial normalmente (con toda su lógica
    # de tipos de cambio/monedas intacta) y solo se recorta proporcionalmente
    # el resultado, devolviendo el remanente al residual de ambas líneas para
    # que la contabilidad cuadre.
    def _prepare_reconciliation_single_partial(self, debit_values, credit_values, shadowed_aml_values=None):
        res = super()._prepare_reconciliation_single_partial(
            debit_values, credit_values, shadowed_aml_values=shadowed_aml_values
        )
        state = self.env.context.get("_paid_amount_state")
        partial_values = res.get("partial_values")
        if not state or not partial_values:
            return res

        remaining = state["remaining"]
        company = self[:1].company_id or self.env.company
        precision = company.currency_id.decimal_places
        original_amount = partial_values["amount"]
        to_apply = min(remaining, original_amount)

        if float_compare(to_apply, original_amount, precision_digits=precision) >= 0:
            # Alcanza para aplicar todo el partial calculado por el core.
            state["remaining"] = remaining - original_amount
            return res

        ratio = (to_apply / original_amount) if original_amount else 0.0
        unapplied_amount = original_amount - to_apply
        unapplied_debit_currency = partial_values["debit_amount_currency"] * (1 - ratio)
        unapplied_credit_currency = partial_values["credit_amount_currency"] * (1 - ratio)

        partial_values["amount"] = to_apply
        partial_values["debit_amount_currency"] *= ratio
        partial_values["credit_amount_currency"] *= ratio
        state["remaining"] = remaining - to_apply

        debit_values["amount_residual"] += unapplied_amount
        credit_values["amount_residual"] -= unapplied_amount
        debit_values["amount_residual_currency"] += unapplied_debit_currency
        credit_values["amount_residual_currency"] -= unapplied_credit_currency

        # No reintentar este mismo par en esta llamada a reconcile(): ya se
        # aplicó el recorte deseado, el resto del residual debe quedar
        # disponible para usarse en otra conciliación posterior.
        res["debit_values"] = None
        res["credit_values"] = None
        return res
