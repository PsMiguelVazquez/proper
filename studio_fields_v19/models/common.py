# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: varios de los campos calculados que se formalizan en este
módulo dependen de OTROS campos que siguen viviendo únicamente como
metadatos de Odoo Studio (nunca se declararon en código). Esos campos no
existen siempre: algunas bases (staging/dev, copias neutralizadas más
viejas que la producción, etc.) pueden no tenerlos, y a diferencia de un
campo de código, Odoo no puede garantizar en tiempo de instalación que un
nombre de campo declarado en `@api.depends` exista de verdad -> si no
existe, el módulo entero deja de instalar (`ValueError: Wrong @depends`).

`studio_get` lee esos campos de forma defensiva: si el campo no existe en
el modelo, devuelve `default` en lugar de reventar. Por eso mismo estos
campos NO se listan en `@api.depends` de los métodos que los usan -declarar
ahí un campo que puede no existir es exactamente lo que causaba el error-,
a costa de que el cálculo no se recalcule automáticamente cuando cambian
(sólo se recalcula cuando cambian sus otras dependencias, o al abrir el
registro sin valor todavía). Si en tu base estos campos sí existen siempre,
conviene formalizarlos como campos de código (ver el resto del módulo para
ejemplos) y moverlos a `@api.depends` normal.
"""


def studio_get(record, field_name, default=0.0):
    return getattr(record, field_name, default)
