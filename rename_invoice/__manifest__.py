{
    "name": "Cambio de nombre en adjunto EDI MX",
    "author": "Cesar Lopez R",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    # MIGRACIÓN V19: `l10n_mx_edi_40` nunca existió como módulo separado en
    # 19.0 -el soporte de CFDI 4.0 ya está integrado directamente en
    # `l10n_mx_edi`-, así que la dependencia real es `l10n_mx_edi`
    # (Enterprise en 19.0).
    "depends": ["base", "l10n_mx_edi"],
}
