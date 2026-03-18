Diseño funcional de implementación en Odoo 19
Proyecto
Implementación del proceso de producción de pacas de ropa clasificadas a partir
de contenedores de ropa usada.
Objetivo
Diseñar una implementación completa en Odoo 19 para controlar la operación
desde la recepción del contenedor hasta la venta y despacho de pacas
terminadas, con trazabilidad total por lote, control operativo por etapas y
capacidad de costeo.

Resumen ejecutivo El negocio debe modelarse en Odoo 19 como un proceso híbrido entre Inventario y Manufactura, apoyado por Compras, Ventas, Contactos y Contabilidad. La lógica correcta no es tratar el contenedor como un producto terminado para reventa, sino como materia prima trazable que entra al almacén, pasa por un proceso de clasificación, grading, pesaje y empacado, y luego se convierte en productos terminados llamados pacas. La base estándar de Odoo 19 que soporta este diseño incluye: • Bills of Materials (BoM) • By-products • Work Orders • Work Centers • Lots & Serial Numbers • Product tracking in manufacturing • Inventory locations Esto permite implementar la base del proceso con el estándar, y completar la operatividad real del negocio con un módulo personalizado de apoyo para clasificación, grading y consolidación automática de pacas.

Módulos a utilizar Módulos estándar de Odoo 19 • Inventory • Manufacturing • Purchase • Sales • Contacts • Accounting Módulo personalizado recomendado • pacas_production_management Este módulo custom servirá para: • registrar contenedores • controlar etapas operativas • capturar clasificación por categoría y calidad • acumular pesos • generar pacas automáticamente o semi-automáticamente • mantener trazabilidad completa • producir reportes operativos

Alcance funcional del sistema El sistema debe cubrir:

Compra del contenedor al proveedor

Recepción física del contenedor

Registro de lote del contenedor

Descarga y separación inicial de ropa

Clasificación por categoría

Grading por calidad

Pesaje por categoría/calidad

Empacado en pacas

Palletizado 10.Disponibilidad para venta 11.Despacho al cliente

Trazabilidad desde contenedor hasta paca y desde paca hasta cliente 13.Cálculo de costos e inventarios 14.Registro de merma o desperdicio

Concepto funcional del proceso Flujo general Compra del contenedor ↓ Recepción de materia prima ↓ Descarga del contenedor ↓ Clasificación por categoría ↓ Grading por calidad ↓ Pesaje ↓ Empacado ↓ Creación de paca terminada ↓ Palletizado ↓ Despacho / venta

Modelo operativo recomendado 5.1 Materia prima La materia prima principal será el contenedor de ropa usada mezclada. Opciones de modelado: Opción A: producto por contenedor • Producto: Contenedor ropa usada mix 40HC • Unidad de medida: Unidad Opción B: producto por peso • Producto: Ropa usada mixta • Unidad de medida: kg o lb Recomendación Usar una combinación de ambas: • el documento comercial y logístico maneja el contenedor • el inventario operativo se convierte a peso real utilizable Así, el contenedor se recibe como lote trazable, y el proceso interno opera principalmente por kilos o libras.

Estructura de productos 6.1 Productos de materia prima Ejemplos: • Contenedor ropa usada mix 40HC • Contenedor ropa usada mix 20HC • Ropa usada mixta a clasificar Tipo de producto: • Almacenable Tracking: • Por lote Ruta: • Buy 6.2 Productos intermedios Representan la ropa clasificada antes de empacar. Ejemplos por categoría: • Ropa hombre clasificada • Ropa mujer clasificada • Ropa niño clasificada • Zapatos clasificados • Carteras clasificadas • Trapo / descarte Ejemplos por categoría + calidad: • Ropa hombre premium • Ropa hombre A • Ropa hombre B • Ropa mujer premium • Ropa mujer A • Ropa niño premium Tipo: • Almacenable Tracking: • Por lote 6.3 Productos terminados Representan las pacas listas para vender. Ejemplos: • Paca hombre premium 100 lb • Paca mujer premium 100 lb • Paca niño premium 100 lb • Paca hombre A 100 lb • Paca mujer A 100 lb • Paca zapato mixto 100 lb Tipo: • Almacenable Ruta: • Manufacture Tracking: • Por lote

Estructura de categorías de producto Se recomienda separar de esta forma: Materia prima • Materia prima / Contenedores • Materia prima / Ropa mixta Producto intermedio • Clasificados / Hombre • Clasificados / Mujer • Clasificados / Niño • Clasificados / Zapatos • Clasificados / Descarte Producto terminado • Pacas / Hombre • Pacas / Mujer • Pacas / Niño • Pacas / Zapatos Esto ayuda a: • reportes • costeo • visibilidad en inventario • análisis de márgenes

Ubicaciones internas recomendadas Crear ubicaciones internas por etapa. Almacén principal • WH/Recepción Contenedor • WH/Cuarentena Contenedor (opcional) • WH/Descarga • WH/Clasificación • WH/Grading • WH/Pesaje • WH/Empacado • WH/Pacas Terminadas • WH/Palletizado • WH/Despacho • WH/Merma Beneficios • saber qué cantidad está en cada etapa • medir cuellos de botella • auditar pérdidas • ubicar rápidamente pacas listas

Trazabilidad obligatoria La trazabilidad debe implementarse con lotes. Nivel 1: lote del contenedor Ejemplo: • CONT-2026-0001 Nivel 2: lotes de producción intermedia Ejemplo: • CLAS-H-0001 • CLAS-M-0001 Nivel 3: lote de paca terminada Ejemplo: • PACA-HP-0001 • PACA-MA-0001 Objetivo de la trazabilidad Poder responder preguntas como: • de qué contenedor salió esta paca • cuántas pacas premium produjo el contenedor X • cuánto descarte se generó del contenedor Y • a qué cliente se vendieron las pacas del lote Z Odoo 19 soporta seguimiento por lotes tanto en inventario como en manufactura.

Diseño del flujo funcional en Odoo 19 10.1 Compra del contenedor Módulo Purchase Documento Orden de compra Datos principales • Proveedor • Referencia del contenedor • Tipo de contenedor • Peso estimado • Costo de compra • Costos asociados si se integran luego (flete, aduana, manejo) Resultado Generación de recepción en inventario. 10.2 Recepción del contenedor Módulo Inventory Proceso Recepción de mercancía contra la orden de compra. Datos a capturar • lote del contenedor • número de contenedor • fecha de llegada • peso bruto • peso neto estimado • observaciones Resultado El contenedor queda disponible en WH/Recepción Contenedor. Recomendación Crear un formulario custom de registro de contenedor para capturar todos los datos operativos sin depender solo del picking estándar. 10.3 Descarga del contenedor Objetivo Registrar el inicio del proceso físico de apertura y vaciado. Operación sugerida Transferencia interna: • Origen: WH/Recepción Contenedor • Destino: WH/Descarga Información útil a capturar • fecha/hora de inicio • fecha/hora de fin • operarios asignados • incidencias 10.4 Clasificación por categoría Objetivo Separar la ropa mixta en grandes familias. Implementación recomendada Usar una orden de manufactura de descomposición / separación. Consumo • lote del contenedor o ropa mixta a clasificar Salidas esperadas • Ropa hombre clasificada • Ropa mujer clasificada • Ropa niño clasificada • Zapatos clasificados • Carteras clasificadas • Trapo / descarte Alternativa técnica Utilizar BoM con by-products para registrar varias salidas desde una sola entrada. Observación importante A nivel de estándar, Odoo trabaja naturalmente con un producto principal y subproductos. Si se desea máxima limpieza funcional, el módulo custom debe manejar una pantalla de clasificación que cree automáticamente los movimientos de inventario o MOs correspondientes. 10.5 Grading por calidad Objetivo Clasificar cada categoría por nivel de calidad. Ejemplo para ropa hombre • Ropa hombre premium • Ropa hombre A • Ropa hombre B • Ropa hombre C • Trapo hombre Implementación recomendada Segunda etapa del proceso de manufactura o work order adicional. Resultado Cada categoría inicial se transforma en productos intermedios más específicos, que serán luego usados en el empacado final. 10.6 Pesaje Objetivo Registrar peso real de cada lote intermedio. Implementación recomendada Work Center: Pesaje Datos a registrar • producto • lote • peso real • operario • fecha/hora • observaciones Uso funcional El peso real definirá cuántas pacas se pueden formar. 10.7 Empacado Objetivo Formar pacas a partir del material clasificado y gradeado. Ejemplo Entrada: • 100 lb de ropa hombre premium Salida: • 1 paca hombre premium 100 lb Implementación recomendada Orden de manufactura para producto terminado. BoM ejemplo Producto final: • Paca hombre premium 100 lb Componente: • 100 lb ropa hombre premium Operaciones: • Empacado • Pesaje final • Etiquetado Resultado Se crea la paca como producto terminado, con su lote propio. 10.8 Palletizado Objetivo Agrupar pacas terminadas para almacenamiento o despacho. Implementación Transferencia interna: • Origen: WH/Pacas Terminadas • Destino: WH/Palletizado Datos sugeridos • código de pallet • cantidad de pacas • peso total del pallet • destino comercial 10.9 Despacho y venta Módulos Sales + Inventory + Accounting Flujo • cotización • pedido de venta • entrega • factura Producto vendido La paca terminada. Trazabilidad Debe poder verse qué lotes de pacas se enviaron a cada cliente.

Configuración de manufactura en Odoo 19 11.1 Rutas Para productos de materia prima • Buy Para pacas terminadas • Manufacture Para productos intermedios Depende de diseño: • pueden ser almacenables sin ruta especial • o manufacturados si se formaliza cada etapa por MO 11.2 Bills of Materials BoM tipo 1: clasificación primaria Ejemplo: • Producto de referencia: Proceso clasificación contenedor • Componente: 1 unidad contenedor o X kg de ropa mixta • By-products: hombre, mujer, niño, zapatos, trapo BoM tipo 2: grading Ejemplo: • Entrada: ropa hombre clasificada • By-products: premium, A, B, C, trapo BoM tipo 3: empacado final Ejemplo: • Entrada: 100 lb ropa hombre premium • Salida: 1 paca hombre premium 100 lb 11.3 Work Centers Crear los siguientes: • Descarga • Clasificación • Grading • Pesaje • Empacado • Etiquetado • Palletizado Uso • control de tiempos • medición de eficiencia • secuencia de operaciones • seguimiento en piso con work orders 11.4 Work Orders Activar Work Orders en Manufacturing Settings. Cada BoM que requiera ejecución operativa debe incluir operaciones. Ejemplo para paca terminada:

Preparar material

Empacar

Pesar

Etiquetar

Mover a terminados

Diseño del módulo personalizado 12.1 Nombre técnico sugerido pacas_production_management 12.2 Objetivo Agregar una capa funcional amigable para usuarios operativos, evitando que el negocio dependa solo de formularios estándar complejos de Odoo. 12.3 Modelos sugeridos a. pacas.container Registro maestro del contenedor. Campos sugeridos: • name • container_number • supplier_id • purchase_order_id • lot_id • arrival_date • gross_weight • net_weight • status • notes • company_id Estados: • draft • received • in_process • classified • closed b. pacas.container.line Detalle opcional de incidencias o métricas del contenedor. Campos: • container_id • description • quantity • uom_id • remark c. pacas.classification.batch Cabecera de jornada o lote de clasificación. Campos: • name • container_id • date_start • date_end • operator_ids • source_location_id • destination_location_id • status Estados: • draft • in_progress • done • cancelled d. pacas.classification.line Líneas por categoría y calidad. Campos: • batch_id • product_category_type • grade • product_id • weight • lot_source_id • lot_result_id • remarks e. pacas.bale.order Orden operativa de creación de paca. Campos: • name • product_id • source_product_id • source_lot_id • target_lot_id • target_weight • actual_weight • batch_id • operator_id • production_id • state Estados: • draft • ready • packed • validated f. pacas.pallet Control de pallet. Campos: • name • bale_ids • total_weight • total_bales • destination_partner_id • state 12.4 Funciones clave del módulo custom

Registro de contenedor con captura completa

Botón para iniciar clasificación

Pantalla rápida de clasificación por líneas

Validación automática de que el peso total clasificado no exceda el peso disponible

Generación automática de movimientos internos o MOs

Generación de lotes de salida

Cálculo de merma

Generación asistida de pacas

Impresión de etiquetas de paca 10.Dashboard operativo

Reglas de negocio obligatorias 13.1 Regla de peso La suma de pesos clasificados no puede exceder el peso utilizable del contenedor. 13.2 Regla de trazabilidad Toda paca debe conservar referencia al lote fuente del cual provino. 13.3 Regla de cierre del contenedor Un contenedor no puede cerrarse hasta que: • su clasificación esté completada • su merma esté registrada • no queden cantidades pendientes sin explicar 13.4 Regla de empacado Una paca solo puede validarse cuando tenga peso final confirmado. 13.5 Regla de venta Solo pueden venderse pacas ubicadas en stock disponible para despacho. 13.6 Regla de calidad Si se desea, ciertas calidades pueden bloquearse para venta hasta revisión.

Diseño de pantallas recomendadas 14.1 Pantalla: Registro de contenedor Debe mostrar: • datos generales • proveedor • OC relacionada • lote • pesos • estado • botones operativos Botones: • Recibir • Iniciar proceso • Ver clasificación • Ver pacas generadas • Cerrar contenedor 14.2 Pantalla: Clasificación rápida Debe permitir capturar múltiples líneas sin abrir formularios complejos. Columnas sugeridas: • categoría • calidad • peso • producto resultante • observación Botones: • Guardar borrador • Validar clasificación • Generar movimientos 14.3 Pantalla: Órdenes de paca Debe mostrar: • producto final a fabricar • lote fuente • peso esperado • peso real • operario • estado Botones: • Iniciar empaque • Registrar peso • Validar paca • Imprimir etiqueta 14.4 Pantalla: Dashboard operativo Indicadores: • contenedores recibidos • contenedores en proceso • kg clasificados hoy • kg en grading • pacas creadas hoy • merma total • pacas listas para despacho

Documentos y reportes requeridos

Registro de recepción de contenedor

Reporte de clasificación por contenedor

Reporte de grading por categoría

Reporte de merma

Etiqueta de paca

Reporte de pallet

Trazabilidad de paca a contenedor

Producción por día / operario / categoría

Inventario de pacas terminadas 10.Rentabilidad por contenedor

Costeo Enfoque recomendado Usar costo promedio o costo estándar ampliado según nivel de madurez del proyecto. Recomendación inicial Fase 1: • costear el contenedor como materia prima principal • distribuir el costo sobre productos intermedios y finales de forma funcional Posible evolución Fase 2: • incluir landed costs • distribuir costo por peso utilizable • incorporar mano de obra por work center • incorporar costos indirectos

Seguridad y roles Roles sugeridos Operario de recepción • registrar entrada de contenedor • consultar sus movimientos Operario de clasificación • capturar líneas de clasificación • no modificar configuración Supervisor de producción • validar clasificación • generar pacas • registrar merma Jefe de almacén • transferencias internas • control de stock • despacho Comercial • cotizaciones y ventas Contabilidad • facturación • costos • reportes financieros Administrador del sistema • configuración completa

Secuencia recomendada de implementación Fase 1 - Base operativa

instalar módulos estándar

configurar almacenes y ubicaciones

configurar lotes

crear productos

crear categorías de producto

crear work centers

crear BoMs principales

validar flujo estándar mínimo Fase 2 - Desarrollo custom

modelo de contenedores

pantalla de clasificación rápida

lógica de grading

lógica de generación de pacas

trazabilidad extendida

dashboard operativo

reportes y etiquetas Fase 3 - Puesta en marcha

carga de maestros

capacitación

pruebas integrales

piloto con contenedor real

ajustes

salida en producción

Plan de pruebas funcionales Caso 1: recepción de contenedor • crear OC • recibir contenedor • asignar lote • validar stock en ubicación correcta Caso 2: clasificación • iniciar clasificación • registrar categorías • validar pesos • revisar productos resultantes Caso 3: grading • procesar una categoría clasificada • dividir por calidad • verificar lotes de salida Caso 4: empacado • crear paca desde material gradeado • registrar peso real • validar producto terminado Caso 5: despacho • vender paca • generar entrega • verificar trazabilidad en entrega Caso 6: trazabilidad inversa • tomar una paca terminada • identificar contenedor origen

Recomendación final de arquitectura La mejor implementación para este negocio en Odoo 19 es: Núcleo estándar • Inventory • Manufacturing • Purchase • Sales • Contacts • Accounting Configuración clave • Lots & Serial Numbers • Work Orders • Work Centers • BoM con by-products • ubicaciones por etapa Capa custom • gestión de contenedores • clasificación rápida • grading • consolidación de pacas • reportes operativos

Conclusión ejecutiva En Odoo 19, este negocio debe implementarse como un proceso de transformación industrial ligera con fuerte componente logístico. El contenedor entra como materia prima trazable. La ropa se clasifica, se gradea, se pesa y se empaca. La salida final son pacas terminadas listas para venta. El sistema debe mantener trazabilidad total, control por ubicación, control por lote y capacidad de medición operativa. La base del estándar de Odoo 19 sí soporta la arquitectura principal mediante BoM, by-products, lotes, work centers y work orders. Sin embargo, para que la operación sea realmente eficiente en piso y fácil de usar, es altamente recomendable desarrollar un módulo personalizado orientado al proceso real del negocio.

Referencias funcionales Odoo 19 La propuesta se apoya en capacidades documentadas oficialmente por Odoo 19 para: • Manufacturing • Bills of Materials • By-products • Lots & Serial Numbers • Work Centers • Work Orders • Manufacturing product tracking