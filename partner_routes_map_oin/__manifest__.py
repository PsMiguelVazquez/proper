# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2020 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Route Map of Partners',
    'summary': 'Route Map of multiple selected partners',
    'description': """
This module allows us to open an itinerary map from the start address of the
logged-in user to the addresses of the selected partners from the list.

It will open a pop-up when we select an option from the Action after the
selection of partners. We can see all the selected partners in pop-up and
can also do arrangement as per our route plan.

It will use the latitude and longitude to localize the partner if this
information is present on the partner.
    """,
    'version': '14.0.1',
    'category': 'Extra Tools',

    'author': "Odoo IT now",
    'website': "http://www.odooitnow.com/",
    'license': 'Other proprietary',

    'depends': [
        'base',
        'website_google_map',
        'vehiculos'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_partner_route_map_view.xml',
        ],
    'images': ['images/OdooITnow_screenshot.png'],

    'price': 11.00,
    'currency': 'EUR',

    'installable': True,
    'application': True,
    'auto_install': False
}
