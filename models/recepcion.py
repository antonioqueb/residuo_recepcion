from odoo import models, fields, api, _

class ResiduoRecepcion(models.Model):
    _name = 'residuo.recepcion'
    _description = 'Recepción de Residuos Peligrosos'
    _inherit = ['mail.thread']

    name = fields.Char(default=lambda self: _('Nueva'), readonly=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta', required=True, tracking=True)
    picking_id = fields.Many2one('stock.picking', string='Entrada de Inventario', readonly=True)
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado')
    ], default='borrador', string='Estado', tracking=True)
    linea_ids = fields.One2many('residuo.recepcion.linea', 'recepcion_id', string='Residuos Recolectados')

    def action_confirmar(self):
        stock_location_cliente = self.sale_order_id.partner_id.property_stock_customer.id
        stock_location_destino = self.env.ref('stock.stock_location_stock').id
        picking_type_in = self.env.ref('stock.picking_type_in')

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type_in.id,
            'location_id': stock_location_cliente,
            'location_dest_id': stock_location_destino,
            'origin': self.name,
        })

        for linea in self.linea_ids:
            self.env['stock.move'].create({
                'name': linea.product_id.name,
                'product_id': linea.product_id.id,
                'product_uom_qty': linea.cantidad,
                'product_uom': linea.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': stock_location_cliente,
                'location_dest_id': stock_location_destino,
            })

        picking.action_confirm()
        picking.action_assign()

        self.write({
            'estado': 'confirmado',
            'picking_id': picking.id
        })

class ResiduoRecepcionLinea(models.Model):
    _name = 'residuo.recepcion.linea'
    _description = 'Detalle de Residuos Recolectados'

    recepcion_id = fields.Many2one('residuo.recepcion', string='Recepción', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Residuo', domain=[('type','=','product')], required=True)
    cantidad = fields.Float(string='Cantidad', required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    es_recoleccion = fields.Boolean(string="Es un servicio de recolección")

