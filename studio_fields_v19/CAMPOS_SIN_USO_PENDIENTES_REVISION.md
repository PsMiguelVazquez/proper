# Campos de Odoo Studio sin uso detectado, pendientes de revisión manual

Estos 40 campos tienen un nombre/etiqueta real en español (alguien los
configuró a propósito, no son el nombre genérico que deja Odoo Studio por
defecto), pero mi búsqueda automática (vistas, cómputos, `related`/
`depends` de otros campos, dominios de acciones/reglas/filtros,
automatizaciones y plantillas de correo, en la base `proper15`) no
encontró ningún lugar donde se usen actualmente.

A diferencia de los 88 campos genéricos (`x_studio_related_field_XXXXX`
= "New Campo relacionado", nunca renombrados), **no se tocaron** -se
dejan documentados aquí para que se revisen caso por caso antes de
decidir si se formalizan (si de verdad hacen falta) o se eliminan (si
ya no aplican). `ir.model.fields` no tiene forma de "desactivar" un
campo en 19.0, así que la única acción posible sobre estos sería
eliminarlos -irreversible-, por eso se prefirió no decidir por cuenta
propia.

| Modelo | Campo técnico | Etiqueta | Tipo |
|---|---|---|---|
| `hr.employee` | `x_studio_concepto_de_baja` | Concepto de baja | Carácter |
| `hr.employee` | `x_studio_reportar_a` | Reportar a | Carácter |
| `crm.lead` | `x_industry_id` | Sector | many2one |
| `crm.lead` | `x_nivel_cliente_opo` | Nivel del cliente | many2one |
| `crm.lead` | `x_producto_no_almacen` | Productos que no están en almacén | many2many |
| `crm.lead` | `x_studio_descripcin` | Descripción | Carácter |
| `purchase.order.line` | `x_studio_estado_del_producto` | Estado del producto | Selección |
| `stock.move` | `x_studio_referencia` | Referencia | Carácter |
| `stock.move` | `x_studio_referencia_del_pedido` | Referencia del pedido | many2one |
| `stock.move.line` | `x_fecha_entrega` | Fecha de entrega | Fecha y hora |
| `stock.move.line` | `x_ultimo_costo` | Último costo | Monetario |
| `purchase.order` | `x_oordenes_venta` | ordenes de venta | many2many |
| `purchase.order` | `x_studio_contacto_del_proveedor` |  | Carácter |
| `purchase.order` | `x_studio_contacto_del_proveedor_1` | Contacto del Proveedor | Carácter |
| `purchase.order` | `x_studio_obsercvaciones` | OBsercvaciones | Carácter |
| `purchase.order` | `x_studio_responsable_de_tesorera` | responsable de tesorería | many2one |
| `purchase.order` | `x_studio_responsable_de_ventas` | Responsable de ventas | many2one |
| `sale.order` | `x_fecha_fallo` | Fecha de fallo del cliente | Fecha y hora |
| `sale.order` | `x_presupuesto_general` | Presupuesto general | número flotante |
| `sale.order` | `x_productos_no` | Productos | many2many |
| `sale.order` | `x_productos_si` | Productos | many2many |
| `sale.order` | `x_requerimiento_para` | Requerimiento para | texto |
| `sale.order` | `x_se_espera_respuesta` | Se espera respuesta | Fecha y hora |
| `sale.order` | `x_studio_n_gua` | N° Guía | Carácter |
| `sale.order` | `x_tipo_cotizacion` | Tipo de cotización | Selección |
| `stock.quant` | `x_no_archivado` | No archivado | booleano |
| `stock.quant` | `x_se_puede_vender` | Se puede vender | booleano |
| `x_ref_banco` | `x_anos_apertura` | Años de apertura | entero |
| `x_ref_banco` | `x_banco` | Banco | Carácter |
| `x_ref_banco` | `x_no_cuenta` | No Cuenta | Carácter |
| `helpdesk.ticket` | `x_studio_cliente` | Cliente | Carácter |
| `helpdesk.ticket` | `x_studio_correo_electrnico` | Correo electrónico | Carácter |
| `helpdesk.ticket` | `x_studio_telfono` | Teléfono | Carácter |
| `helpdesk.ticket` | `x_studio_telfono_de_oficina` | Teléfono de oficina | Carácter |
| `stock.picking` | `x_studio_cliente` | Cliente | many2one |
| `stock.picking` | `x_studio_contacto_1` | Destino | Carácter |
| `stock.picking` | `x_studio_distancia` | Distancia  | número flotante |
| `stock.picking` | `x_studio_mtodo_de_entrega` | Método de Entrega  | Carácter |
| `stock.picking` | `x_studio_otros_documentos` | Otros Documentos | binario |
| `res.users` | `x_studio_clave_del_comprador` | Clave del Comprador | Carácter |
