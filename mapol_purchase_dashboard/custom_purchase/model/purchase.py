from odoo import api, fields, models, _

class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', default=False)
    purchase_type = fields.Selection([('general',"General Purchase"),('production','Production Purchase')],'Purchase Type',default="general",compute="compute_purchase_type",store=True)
    state = fields.Selection(selection_add=[('open_po','Open PO'),('done','Close PO')])
    
    @api.depends('is_production_purchase')
    def compute_purchase_type(self):
        for rec in self:
            if rec.is_production_purchase == True:
                rec.purchase_type = 'production'
            elif rec.is_production_purchase == False:
                rec.purchase_type = 'general'
    
    @api.multi
    def change_open_po(self):
        self.write({'state': 'open_po'})
    
class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', default=False)
    
class Product(models.Model):
    _inherit = 'product.template'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', compute="onchange_route_ids", default=False,store=True)
    
    @api.depends('route_ids')
    def onchange_route_ids(self):
        for rec in self:
            if rec.route_ids:
                for res in rec.route_ids:
                    if res.name == 'Manufacture':
                        rec.is_production_purchase = True
                    elif res.name != 'Manufacture':
                        rec.is_production_purchase = False
    
    
    