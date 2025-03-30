from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    recepcion_ids = fields.One2many('residuo.recepcion', 'sale_order_id', string='Recepciones')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            # Ahora se considera TODAS las líneas sin importar el campo "es_recoleccion"
            lineas = [(0, 0, {
                'product_id': line.product_id.id,
                'cantidad': line.product_uom_qty,
            }) for line in order.order_line]

            # Crear siempre la recepción (estado borrador por defecto)
            recepcion = order.env['residuo.recepcion'].create({
                'sale_order_id': order.id,
                'name': order.env['ir.sequence'].next_by_code('residuo.recepcion') or _('Nueva'),
                'linea_ids': lineas,
            })

            # Log para verificar creación correcta
            _logger.info(f'Recepción creada automáticamente: {recepcion.name}, ID: {recepcion.id}, Orden de venta: {order.name}')

            # Invalida la caché para reflejar los cambios inmediatos en la UI
            order.invalidate_model(['recepcion_ids'])

        return res
