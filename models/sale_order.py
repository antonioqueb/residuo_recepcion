from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if any(line.product_id.es_recoleccion for line in order.order_line):
                order.env['residuo.recepcion'].create({
                    'sale_order_id': order.id,
                    'name': order.env['ir.sequence'].next_by_code('residuo.recepcion') or _('Nueva'),
                })
        return res
