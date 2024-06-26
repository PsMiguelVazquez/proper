# -*- coding: utf-8 -*-
{
    'name': 'Novu CRM',
    'author': 'Mayra Samuel',
    'website': '',
    'license': 'LGPL-3',
    'summary': 'CRM campos etapas ',
    'description': """Se agregan campos en la oportunidad y se bloquea el cambio de etapa si falta alguno por llenar""",

    'depends': [
        'crm','contacts',
    ],
    'assets': {
        
    },
    "data": [
            'views/res_partner_view.xml',
            'views/crm_lead_view.xml'
    ],
    'demo': [],
    'external_dependencies': {
    },
    'application': True,
    'installable': True,
    'auto_install': True
}
