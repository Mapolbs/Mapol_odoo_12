from odoo import api, fields, models, _

class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', default=False)
    purchase_type = fields.Selection([('general',"General Purchase"),('production','Production Purchase')],'Purchase Type',default="general",compute="compute_purchase_type",store=True)
#     state = fields.Selection(selection_add=[('open_po','Open PO'),('done','Close PO')])
    state_type = fields.Selection([('general','General PO'),('open_po',"Open PO"),('close_po','Close PO')],'State Type',default="general",compute="compute_purchase_type",store=True)
    close_order = fields.Boolean('Close PO',default=False)
    open_order = fields.Boolean('Open PO',default=False)
    billing_progress = fields.Integer(default=0,compute="onchange_progress")
    color = fields.Integer('color',default=0,compute="onchange_color")
#     vendor_ref_date = fields.Date('Vendor Invoice Date')
    
    @api.onchange('close_order')
    def change_close_po_state(self):
        if self.close_order == True:
            self.open_order = False
                
    @api.onchange('open_order')
    def change_open_po_state(self):
        if self.open_order == True:
            self.close_order = False
    
#     @api.multi
#     def write(self, vals):
#         if vals.get('open_order') == True:
#             vals['state'] =  'open_po'
#         if vals.get('close_order') == True:
#             vals['state'] =  'done'
#         return super(Purchase,self).write(vals)
    
    def onchange_color(self):
        for rec in self:
            if rec.state == 'draft':
                rec.color = 3
            elif rec.state == 'sent':
                rec.color = 4
            elif rec.state == 'purchase':
                rec.color = 10
            elif rec.state == 'cancel':
                rec.color = 9 
    
    
    @api.depends('invoice_status')
    def onchange_progress(self):
        for rec in self:
            if rec.invoice_status == 'no':
                rec.billing_progress = 25
            elif rec.invoice_status == 'to invoice':
                rec.billing_progress = 50
            elif rec.invoice_status == 'invoiced':
                rec.billing_progress = 100
            if rec.state == 'cancel':
                rec.billing_progress = 0
                
                
                
    @api.depends('is_production_purchase','close_order','open_order')
    def compute_purchase_type(self):
        for rec in self:
            if rec.is_production_purchase == True:
                rec.purchase_type = 'production'
            elif rec.is_production_purchase == False:
                rec.purchase_type = 'general'
            if rec.close_order == True:
                rec.state_type = 'close_po'
            elif rec.open_order == True:
                rec.state_type = 'open_po'
            elif rec.open_order == False and rec.close_order == False:
                rec.state_type = 'general'
    
#     @api.multi
#     def change_open_po(self):
#         self.write({'state': 'open_po'})

    @api.depends('order_line.date_planned', 'date_order')
    def _compute_date_planned(self):
        for order in self:
            min_date = False
            for line in order.order_line:
                if not min_date or line.date_planned < min_date:
                    min_date = line.date_planned
#             if min_date:
#                 order.date_planned = min_date
            order.date_planned = order.date_order
class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', default=False)
    
    @api.onchange('product_id')
    def onchange_product(self):
        product = self.env['product.product'].search([])
        partner = []
        if self.order_id.partner_id and self.order_id.is_production_purchase == False:
            for rec in product:
                for line in rec.seller_ids:
                    if self.order_id.partner_id.id == line.name.id:
                        partner.append(rec.id)
            return {'domain': {'product_id': [('id', 'in', partner)]}}
        else:
            for rec in product:
                if rec.is_production_purchase == True:
                    for line in rec.seller_ids:
                        if self.order_id.partner_id.id == line.name.id:
                            partner.append(rec.id)
            return {'domain': {'product_id': [('id', 'in', partner)]}}
    
class Product(models.Model):
    _inherit = 'product.template'
    
    is_production_purchase = fields.Boolean('Production Purchase', help='consider this purchase as Production Purchase', default=False)
    model = fields.Char('Product Model')
    
#     @api.depends('route_ids')
#     def onchange_route_ids(self):
#         for rec in self:
#             if rec.route_ids:
#                 for res in rec.route_ids:
#                     if res.name == 'Manufacture':
#                         rec.is_production_purchase = True
#                     elif res.name != 'Manufacture':
#                         rec.is_production_purchase = False
    

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('vendor.number')

        return super(ResPartner, self).create(vals)
    
    @api.multi
    def name_get(self):
        res = []
        for field in self:
            if field.ref:
                res.append((field.id, '[%s] %s' %(field.ref,field.name)))
            else:
                res.append((field.id, '%s' %(field.name)))
        return res
    