from . import models
from . import wizard
from . import controllers


def _create_raffle_location(env):
    """Crea la ubicación 'Sorteos' como hija de view_location_id del warehouse,
    al mismo nivel que Stock, separada del inventario de venta."""
    warehouse = env['stock.warehouse'].search(
        [('company_id', '=', env.ref('base.main_company').id)], limit=1
    )
    if not warehouse:
        return
    location = env['stock.location'].create({
        'name': 'Sorteos',
        'usage': 'internal',
        'location_id': warehouse.view_location_id.id,
        'company_id': warehouse.company_id.id,
    })
    # Registrar xmlid para que env.ref() funcione en el resto del módulo
    env['ir.model.data'].create({
        'name': 'stock_location_raffles',
        'module': 'raffle_management',
        'model': 'stock.location',
        'res_id': location.id,
        'noupdate': True,
    })
