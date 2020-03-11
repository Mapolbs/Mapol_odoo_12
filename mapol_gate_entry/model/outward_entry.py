# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import ValidationError

class InwardEntry(models.Model):
    _name = 'outward.entry'
    _description = 'Outward Entry'
    _rec_name = 'lr_rr_no'
    
    
    lr_rr_no = fields.Char('LR/RR No', help='Lorry Receipt / Railway Receipt Number.',required=True)
    lr_rr_date = fields.Date('LR/RR Date', help='Lorry Receipt / Railway Receipt Date.')
    document_date = fields.Date('Enrty Date',default=date.today(),help='Entry Date of the Vehicle.')
    is_company_vehicle = fields.Boolean('Our Company Vehicle',help='Vehicle from Our Company.')
    vehicle_number = fields.Char('Vehicle Number',help='Vehicle Number')
    company_vehicle_id = fields.Many2one('fleet.vehicle','Company Vehicle Number',help='Company Vehicle Number')
    odometer_value = fields.Float('Vehicle Odometer Value',help='Company Vehicle Odometer Value',related="company_vehicle_id.odometer")
    description = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    comment = fields.Text('Comment')
    purchase_outward_ids = fields.One2many('purchase.outward.entry','outward_id',help='Purchase Inward Challan Details')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft')
    sale_outward_ids = fields.One2many('sale.outward.entry','outward_id',help="Sale Return Challan Details")
    
    sale_id = fields.Many2one('sale.order','Sale Order')
    partner_id = fields.Many2one('res.partner','Vendor')
    purchase_id = fields.Many2one('purchase.order','Purchase Order')
    
    
    @api.onchange('purchase_id')
    def onchange_purchase(self):
        product = []
        for rec in self:
            if rec.purchase_id:
                rec.partner_id = rec.purchase_id.partner_id.id
                purchase = rec.purchase_id.id
                for stock in rec.purchase_id.picking_ids:
                    if stock.state != 'done':
                        for line in stock.move_ids_without_package:
                            product.append((0,0,{'product_id':line.product_id.id,'quantity':line.product_uom_qty,'received_qty':line.product_uom_qty}))
                rec.purchase_outward_ids.unlink()
                rec.purchase_id = purchase
                rec.update({'purchase_outward_ids': product})
                product = []
                
    @api.onchange('sale_id')
    def onchange_sale(self):
        product = []
        for rec in self:
            if rec.sale_id:
                rec.partner_id = rec.sale_id.partner_id.id
                sale = rec.sale_id.id
                print(rec.sale_id.picking_ids)
                for stock in rec.sale_id.picking_ids:
                    if stock.state != 'done':
                        for line in stock.move_ids_without_package:
                            product.append((0,0,{'product_id':line.product_id.id,'quantity':line.product_uom_qty,'received_qty':line.product_uom_qty}))
                rec.sale_outward_ids.unlink()
                rec.sale_id = sale
                rec.update({'sale_outward_ids': product})
                product = []
    
    
    
    
    @api.multi
    def change_done(self):
        self.update({'state':'done'})


class PurchaseInward(models.Model):
    _name = 'purchase.outward.entry'
    _description = 'Outward Purchase Entry'
    
    outward_id = fields.Many2one('outward.entry',help='Outward Entry Reference')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Order Quantity')
    received_qty = fields.Float('Received Quantity')
#     challan_no = fields.Char('Challan Number',help='Challan Number')
#     challan_date = fields.Date('Challan Date',help='Challan Date')
#     purchase_id = fields.Many2one('purchase.order','Purchase Order',help='Challan Against Purchase Order')
#     quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
#     reference = fields.Char('Reference',help='Reference of the Goods')
    
    
    @api.onchange('received_qty')
    def onchange_qty(self):
        if self.quantity:
            if self.received_qty > self.quantity:
                raise ValidationError('Received Qty should be less than Actual Qty')
    
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    outward_entry_id = fields.Many2many('outward.entry',string='Outward Entry Check',copy=False)
    outward_entry_count = fields.Integer('Outward Entry Count',default=0,copy=False)
    
    @api.multi
    def action_view_outward_entry(self):
        tree_id = self.env.ref('mapol_gate_entry.view_outward_entry_tree').id
        form_id = self.env.ref('mapol_gate_entry.view_outward_entry_form').id
        return {
            'name': _('Outward Gate Entry'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'outward.entry',
            'view_id':tree_id,
            'views': [(tree_id, 'tree'),(form_id,'form')],
            'type': 'ir.actions.act_window',
            'domain':[('purchase_id', '=', self.id)],
            'target': 'current'
                }
        
#         
#         return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'outward.entry',
#                 'view_type': 'form',
#                 'view_mode': 'tree',
#                 'views': [[self.env.ref('mapol_gate_entry.view_outward_entry_tree').id, 'tree']],
# #                 'res_id': self.outward_entry_id.id,
#                 'domain':  [('purchase_id', '=', self.id)], 
#                 'target': 'current',
#                }
        
class SaleReturn(models.Model):
    _name = 'sale.outward.entry'
    _description = 'Sale Outward'
    
    outward_id = fields.Many2one('outward.entry',help='Outward Entry Reference')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Order Quantity')
    received_qty = fields.Float('Received Quantity')
#     challan_no = fields.Char('Challan Number',help='Challan Number')
#     challan_date = fields.Date('Challan Date',help='Challan Date')
#     sale_id = fields.Many2one('sale.order','Sale Order',help='Challan Against Purchase Order')
#     quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
#     reference = fields.Char('Reference',help='Reference of the Goods')

    @api.onchange('received_qty')
    def onchange_qty(self):
        if self.quantity:
            if self.received_qty > self.quantity:
                raise ValidationError('Received Qty should be less than Actual Qty')
    
class Sale(models.Model):
    _inherit = 'sale.order'
    
    outward_entry_id = fields.Many2many('outward.entry',string='Outward Entry Check',copy=False)
    outward_entry_count = fields.Integer('Outward Entry Count',default=0,copy=False)
    
    @api.multi
    def action_view_outward_entry(self):
        tree_id = self.env.ref('mapol_gate_entry.view_outward_entry_tree').id
        form_id = self.env.ref('mapol_gate_entry.view_outward_entry_form').id
        return {
            'name': _('Outward Gate Entry'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'outward.entry',
            'view_id':tree_id,
            'views': [(tree_id, 'tree'),(form_id,'form')],
            'type': 'ir.actions.act_window',
            'domain':[('sale_id', '=', self.id)],
            'target': 'current'
                }
        
        
#         return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'outward.entry',
#                 'view_type': 'form',
#                 'view_mode': 'tree',
#                 'views': [[self.env.ref('mapol_gate_entry.view_outward_entry_tree').id, 'tree']],
# #                 'res_id': self.outward_entry_id.id,
#                 'domain':  [('sale_id', '=', self.id)],
#                 'target': 'current',
#                }
#         
