from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    recepcion_ids = fields.One2many('residuo.recepcion', 'sale_order_id', string='Recepciones')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            residuos = order.order_line.filtered(lambda l: l.product_id.es_recoleccion)
            if residuos:
                lineas = [(0, 0, {
                    'product_id': l.product_id.id,
                    'cantidad': l.product_uom_qty,
                }) for l in residuos]

                order.env['residuo.recepcion'].create({
                    'sale_order_id': order.id,
                    'name': order.env['ir.sequence'].next_by_code('residuo.recepcion') or _('Nueva'),
                    'linea_ids': lineas,
                })

                # Fuerza a Odoo a refrescar el campo One2many inmediatamente
                order.invalidate_model(['recepcion_ids'])

        return res
