/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { usePopover } from "@web/core/popover/popover_hook";
import { Component, useState } from "@odoo/owl";
import { AccountPaymentField } from "@account/components/account_payment_field/account_payment_field";

// MIGRACIÓN V19: reemplaza static/src/js/account_payment_field.js (widget
// legacy `odoo.define`/AbstractField que extendía
// `account.payment.ShowPaymentLineWidget`, arquitectura pre-OWL). El campo
// "payment" es ahora el componente OWL `AccountPaymentField`
// (account/static/src/components/account_payment_field). En vez de un
// `include` sobre un widget viejo, se usa `patch()` para añadir el popover
// de "monto a aplicar" antes de llamar a `js_assign_outstanding_line`.
class AccountPaymentAmountPopOver extends Component {
    static template = "account_payment_widget_amount.PaymentAmountPopOver";
    static props = ["*"];

    setup() {
        this.state = useState({ amount: this.props.amount });
    }

    onApplyClick() {
        this.props._onApply(this.state.amount);
    }
}

patch(AccountPaymentField.prototype, {
    setup() {
        super.setup();
        this.amountPopover = usePopover(AccountPaymentAmountPopOver, { position: "left" });
    },

    onOutstandingCreditAssignClick(ev, moveId, line) {
        this.amountPopover.open(ev.currentTarget, {
            amount: line.amount,
            _onApply: (amount) => {
                this.amountPopover.close();
                this.assignOutstandingCredit(moveId, line.id, amount);
            },
        });
    },

    async assignOutstandingCredit(moveId, id, amount) {
        const kwargs = {};
        if (amount) {
            kwargs.context = { paid_amount: amount };
        }
        await this.orm.call(this.props.record.resModel, "js_assign_outstanding_line", [moveId, id], kwargs);
        await this.props.record.model.root.load();
    },
});
