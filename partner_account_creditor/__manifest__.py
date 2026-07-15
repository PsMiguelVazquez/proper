# -*- coding: utf-8 -*-
{
    'name': "Cuenta de acreedor para el partner",

    'summary': """
                Agrega la opción de configurar la cuenta de acreedor para los clientes/proveedores
            """,

    'description': """
        Agrega la opción de configurar la cuenta de acreedor para los clientes/proveedores necesaria para el proceso de factoraje
    """,

    'author': "Jonathan Alfaro",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    # MIGRACIÓN V19: el campo `property_account_creditor` usa el modelo
    # 'account.account', que solo existe si el módulo 'account' está
    # instalado. El manifest original solo declaraba 'base' como dependencia;
    # se corrige para reflejar la dependencia real (factoraje_financiero,
    # que consume este campo, ya depende de 'account').
    'depends': ['base', 'account'],

    'data': [
        # 'views/res_partner.xml',
    ],

}
