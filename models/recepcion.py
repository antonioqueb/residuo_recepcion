from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
        for rec in self:
            if rec.estado != 'borrador':
                raise UserError(_('La recepción ya ha sido confirmada.'))

            if not rec.linea_ids:
                raise UserError(_('Debe agregar al menos un residuo a recolectar.'))

            for linea in rec.linea_ids:
                if not linea.product_id.uom_id or not linea.product_id.categ_id:
                    raise UserError(_('El producto %s no tiene unidad de medida o categoría definida.') % linea.product_id.display_name)

            stock_location_cliente = rec.sale_order_id.partner_id.property_stock_customer.id
            stock_location_destino = rec.env.ref('stock.stock_location_stock').id
            picking_type_in = rec.env.ref('stock.picking_type_in')

            picking = rec.env['stock.picking'].create({
                'picking_type_id': picking_type_in.id,
                'location_id': stock_location_cliente,
                'location_dest_id': stock_location_destino,
                'origin': rec.name,
            })

            for linea in rec.linea_ids:
                rec.env['stock.move'].create({
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

            # Valida automáticamente usando button_validate() directo en Odoo 18
            if picking.state in ('assigned', 'confirmed'):
                picking.button_validate()
            else:
                raise UserError(_('No se pudo reservar completamente el inventario. Verifique existencias o configuraciones.'))

            rec.write({
                'estado': 'confirmado',
                'picking_id': picking.id
            })

class ResiduoRecepcionLinea(models.Model):
    _name = 'residuo.recepcion.linea'
    _description = 'Detalle de Residuos Recolectados'

    recepcion_id = fields.Many2one('residuo.recepcion', string='Recepción', ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Residuo',
        domain=[('product_tmpl_id.type', '=', 'consu')],
        required=True,
        context={'create': False}
    )
    cantidad = fields.Float(string='Cantidad', required=True)

    unidad = fields.Char(string='Unidad de Medida', related='product_id.uom_id.name', readonly=True)
    categoria = fields.Char(string='Categoría', related='product_id.categ_id.name', readonly=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    es_recoleccion = fields.Boolean(string="Es un servicio de recolección")
