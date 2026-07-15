# -*- coding: utf-8 -*-
{
    'name': 'Novu CRM',
    'author': 'Mayra Samuel',
    'website': '',
    'license': 'LGPL-3',
    'version': '19.0.1.0.0',
    'summary': 'CRM campos etapas ',
    'description': """Se agregan campos en la oportunidad y se bloquea el cambio de etapa si falta alguno por llenar""",

    'depends': [
        'crm', 'contacts',
    ],
    "data": [
            'views/res_partner_view.xml',
            'views/crm_lead_view.xml',
            'views/crm_lead_kanban_view.xml',
            'views/res_user_view.xml',
            'security/groups_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': True
}
