# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: mismo fix que `_fix_broken_modifiers_attribute` en
`__init__.py` (llamada desde `pre_init_hook`), pero para el caso de
actualización. Ver el comentario en `__init__.py` para el detalle.
"""
from odoo import api, SUPERUSER_ID

_MODIFIERS_REPLACEMENTS = [
    (' modifiers="{}"', ''),
    (' modifiers="{&quot;readonly&quot;: true, &quot;required&quot;: true}"', ' readonly="1" required="1"'),
    (' modifiers="{&quot;readonly&quot;: true}"', ' readonly="1"'),
    (' modifiers="{&quot;required&quot;: true}"', ' required="1"'),
]


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].search([('arch_db', 'like', 'modifiers=')])
    for view in views:
        arch = view.arch_db
        if not arch:
            continue
        new_arch = arch
        for old, new in _MODIFIERS_REPLACEMENTS:
            new_arch = new_arch.replace(old, new)
        if new_arch != arch:
            view.write({'arch_db': new_arch})
