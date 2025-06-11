# -*- coding: utf-8 -*-
{
    'name': 'Novu CRM',
    'author': 'Mayra Samuel',
    'website': '',
    'license': 'LGPL-3',
    'summary': 'CRM campos etapas ',
    'description': """Se agregan campos en la oportunidad y se bloquea el cambio de etapa si falta alguno por llenar""",

    'depends': [
        'crm','contacts', 'web_studio', 'website_sale'
    ],
    'assets': {
        
    },
    "data": [
            'views/res_partner_view.xml',
            'views/crm_lead_view.xml',
            'views/crm_lead_kanban_view.xml',
            'views/res_user_view.xml',
            'security/groups_view.xml',
            'data/bloqueo_cambio_etapa_automation.xml',
    ],
    'demo': [],
    'external_dependencies': {
    },
    'application': False,
    'installable': True,
    'auto_install': False
}
