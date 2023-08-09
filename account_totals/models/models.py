from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        r = super(AccountMove, self)._get_tax_totals(partner, tax_lines_data, amount_total, amount_untaxed, currency)
        symbol = self.currency_id.symbol if self.currency_id else self.env.company.currency_id.symbol
        for k in list(r.keys()):
            data = r.get(k)
            if type(data) == float:
                r[k] = round(data, 2)
            if type(data) == str:
                amount = r[k].split(symbol)
                monto = round(float(amount[1].replace(',', '')), 2)
                r[k] = str(symbol)+"\xa0"+f"{monto:,.2f}"
            if type(data) == dict:
                for tax in list(r[k].keys()):
                    for li in r[k][tax]:
                        for taxlis in list(li.keys()):
                            data = li.get(taxlis)
                            if type(data) == float:
                                li[taxlis] = round(data, 2)
                            if type(data) == str:
                                if symbol in data:
                                    amount = li[taxlis].split(symbol)
                                    monto = round(float(amount[1].replace(',', '')), 2)
                                    li[taxlis] = str(symbol) + "\xa0" + f"{monto:,.2f}"
        return r

