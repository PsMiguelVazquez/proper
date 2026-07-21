# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_tax_totals_structure` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

_TAX_TOTALS_DOCUMENT_TEMPLATE = """<t t-name="account.document_tax_totals_copy_{n}">
            <t t-set="same_tax_base" t-value="tax_totals['same_tax_base']"/>
            <t t-set="currency" t-value="o.currency_id"/>
            <t t-foreach="tax_totals['subtotals']" t-as="subtotal">
                <tr class="border-black o_subtotal">
                    <td style="border-right: black 1px solid;" class="small"><strong t-esc="subtotal['name']"/></td>

                    <td class="text-right small bg-white">
                        <span t-att-class="oe_subtotal_footer_separator" t-out="subtotal['base_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                    </td>
                </tr>

                <t t-call="account.tax_groups_totals_copy_{n}"/>
            </t>

            <!--Total amount with all taxes-->
            <tr class="border-black o_total">
                <td style="font-size:12px; color: black; border-right: black 1px solid;" class="bg-white"><strong style="font-size:12px; color: black;">Total</strong></td>
                <td style="font-size:12px;" class="text-right bg-white">
                    <span style="font-size:12px; color: black;" t-out="tax_totals['total_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                </td>
            </tr>
        </t>"""

_TAX_GROUPS_TEMPLATE = """<t t-name="account.tax_groups_totals_copy_{n}">
            <t t-foreach="subtotal['tax_groups']" t-as="tax_group">
                <tr>
                    <t t-if="same_tax_base or tax_group['display_base_amount_currency'] is False">
                        <td class="small"><span class="text-nowrap" t-esc="tax_group['group_name']"/></td>
                        <td class="text-right o_price_total small bg-white">
                            <span class="text-nowrap" t-out="tax_group['tax_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                        </td>
                    </t>
                    <t t-else="">
                        <td>
                            <span t-esc="tax_group['group_name']"/>
                            <span class="text-nowrap"> on
                                <span t-out="tax_group['display_base_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                            </span>
                        </td>
                        <td class="text-right o_price_total">
                            <span class="text-nowrap" t-out="tax_group['tax_amount_currency']" t-options='{{"widget": "monetary", "display_currency": currency}}'/>
                        </td>
                    </t>
                </tr>
            </t>
        </t>"""

# `_copy_1`/`_copy_1_copy_1` ya están formalizados aparte (ver comentario en
# `__init__.py`); sólo `_copy_2`/`_copy_3` (reportes de factura) seguían rotos.
_TAX_TOTALS_COPY_SUFFIXES = ['2', '3']


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrUiView = env['ir.ui.view']
    for suffix in _TAX_TOTALS_COPY_SUFFIXES:
        doc_view = IrUiView.search([('key', '=', f'account.document_tax_totals_copy_{suffix}')], limit=1)
        if doc_view and doc_view.arch_db != _TAX_TOTALS_DOCUMENT_TEMPLATE.format(n=suffix):
            doc_view.write({'arch_db': _TAX_TOTALS_DOCUMENT_TEMPLATE.format(n=suffix)})
        groups_view = IrUiView.search([('key', '=', f'account.tax_groups_totals_copy_{suffix}')], limit=1)
        if groups_view and groups_view.arch_db != _TAX_GROUPS_TEMPLATE.format(n=suffix):
            groups_view.write({'arch_db': _TAX_GROUPS_TEMPLATE.format(n=suffix)})
