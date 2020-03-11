# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import ValidationError
from odoo.tools.func import default

class InwardEntry(models.Model):
    _name = 'inward.entry'
    _description = 'Inward Entry'
    _rec_name = 'lr_rr_no'
    
    
    lr_rr_no = fields.Char('LR/RR No', help='Lorry Receipt / Railway Receipt Number.',required=True)
    lr_rr_date = fields.Date('LR/RR Date', help='Lorry Receipt / Railway Receipt Date.')
    document_date = fields.Date('Enrty Date',default=date.today(),help='Entry Date of the Vehicle.')
    partner_id = fields.Many2one('res.partner','Vendor')
    purchase_id = fields.Many2one('purchase.order','Purchase Order')
    is_company_vehicle = fields.Boolean('Our Company Vehicle',help='Vehicle from Our Company.')
    vehicle_number = fields.Char('Vehicle Number',help='Vehicle Number')
    company_vehicle_id = fields.Many2one('fleet.vehicle','Company Vehicle Number',help='Company Vehicle Number')
    odometer_value = fields.Float('Vehicle Odometer Value',help='Company Vehicle Odometer Value',related="company_vehicle_id.odometer")
    description = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    comment = fields.Text('Comment')
    purchase_inward_ids = fields.One2many('purchase.inward.entry','inward_id',help='Purchase Inward Challan Details')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft')
    sale_return_ids = fields.One2many('sale.return.inward','inward_id',help="Sale Return Challan Details")
    sale_id = fields.Many2one('sale.order','Sale Order')
    
    
    
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
                rec.purchase_inward_ids.unlink()
                rec.purchase_id = purchase
                rec.update({'purchase_inward_ids': product})
                product = []
                
    @api.onchange('sale_id')
    def onchange_sale(self):
        product = []
        for rec in self:
            if rec.sale_id:
                rec.partner_id = rec.sale_id.partner_id.id
                sale = rec.sale_id.id
                for stock in rec.sale_id.picking_ids:
                    if stock.state != 'done':
                        for line in stock.move_ids_without_package:
                            product.append((0,0,{'product_id':line.product_id.id,'quantity':line.product_uom_qty,'received_qty':line.product_uom_qty}))
                rec.sale_return_ids.unlink()
                rec.sale_id = sale
                rec.update({'sale_return_ids': product})
                product = []
    
    @api.multi
    def change_done(self):
        if self.purchase_inward_ids:
            for line in self.purchase_id:
                line.inward_entry_id = [(6,0,self.ids)]
                line.inward_entry_count = line.inward_entry_count + 1
#                 if line.picking_ids:
#                     for picking in line.picking_ids:
#                         picking.onchange_gate_check()
        if self.sale_return_ids:
            for line in self.sale_id:
                line.inward_entry_id = [(6,0,self.ids)]
                line.inward_entry_count = line.inward_entry_count + 1
                if line.picking_ids:
                    for picking in line.picking_ids:
                        picking.onchange_gate_check()
        self.update({'state':'done'})


class PurchaseInward(models.Model):
    _name = 'purchase.inward.entry'
    _description = 'Inward Purchase Entry'
    
    inward_id = fields.Many2one('inward.entry',help='Inward Entry Reference')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Order Quantity')
    received_qty = fields.Float('Received Quantity')
    
    
    @api.onchange('received_qty')
    def onchange_qty(self):
        if self.quantity:
            print('sdjjsbd')
            if self.received_qty > self.quantity:
                raise ValidationError('Received Qty should be less than Actual Qty')
#     challan_no = fields.Char('Challan Number',help='Challan Number')
#     challan_date = fields.Date('Challan Date',help='Challan Date')
#     purchase_id = fields.Many2one('purchase.order','Purchase Order',help='Challan Against Purchase Order')
#     quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
#     reference = fields.Char('Reference',help='Reference of the Goods')
    
    
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    inward_entry_id = fields.Many2many('inward.entry',string='Inward Entry Check',copy=False)
    inward_entry_count = fields.Integer('Inward Entry Count',default=0,copy=False)
    
    @api.multi
    def action_view_inward_entry(self):
        tree_id = self.env.ref('mapol_gate_entry.view_inward_entry_tree').id
        form_id = self.env.ref('mapol_gate_entry.view_inward_entry_form').id
        return {
            'name': _('Inward Gate Entry'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'inward.entry',
            'view_id':tree_id,
            'views': [(tree_id, 'tree'),(form_id,'form')],
            'type': 'ir.actions.act_window',
            'domain':[('purchase_id', '=', self.id)],
            'target': 'current'
                }
        
#         return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'inward.entry',
#                 'view_type': 'form',
#                 'view_mode': 'tree',
#                 'view_id': self.env.ref('mapol_gate_entry.view_inward_entry_tree').id,
#                 'domain':  [('purchase_id', '=', self.id)], 
#                 'target': 'current',
#                }
        
class SaleReturn(models.Model):
    _name = 'sale.return.inward'
    _description = 'Sale Return Inward'
    
    inward_id = fields.Many2one('inward.entry',help='Inward Entry Reference')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Order Quantity')
    received_qty = fields.Float('Received Quantity')
    
    @api.onchange('received_qty')
    def onchange_qty(self):
        if self.quantity:
            if self.received_qty > self.quantity:
                raise ValidationError('Received Qty should be less than Actual Qty')
    
#     inward_id = fields.Many2one('inward.entry',help='Inward Entry Reference')
#     challan_no = fields.Char('Challan Number',help='Challan Number')
#     challan_date = fields.Date('Challan Date',help='Challan Date')
#     sale_id = fields.Many2one('sale.order','Sale Order',help='Challan Against Purchase Order')
#     quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
#     reference = fields.Char('Reference',help='Reference of the Goods')
    
class Sale(models.Model):
    _inherit = 'sale.order'
    
    inward_entry_id = fields.Many2one('inward.entry','Inward Entry Check',copy=False)
    inward_entry_count = fields.Integer('Inward Entry Count',default=0,copy=False)
    
    @api.multi
    def action_view_inward_entry(self):
        tree_id = self.env.ref('mapol_gate_entry.view_inward_entry_tree').id
        form_id = self.env.ref('mapol_gate_entry.view_inward_entry_form').id
        return {
            'name': _('Inward Gate Entry'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'inward.entry',
            'view_id':tree_id,
            'views': [(tree_id, 'tree'),(form_id,'form')],
            'type': 'ir.actions.act_window',
            'domain':[('sale_id', '=', self.id)],
            'target': 'current'
                }
        
#         return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'inward.entry',
#                 'view_type': 'form',
#                 'view_mode': 'tree',
#                 'views': [[self.env.ref('mapol_gate_entry.view_inward_entry_tree').id, 'tree']],
# #                 'res_id': self.inward_entry_id.id,
#                 'domain':  [('sale_id', '=', self.id)],
#                 'target': 'current',
#                }
        
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#     
#     gate_validation_str = fields.Char('Gate Validation String',default='*Inward Quantity is not equal to Done Quantity') 
#     quantity_check = fields.Boolean('Quantity Check',default=False)



class StockPicking(models.Model):
    _inherit = 'stock.picking'
     
    gate_entry_check = fields.Boolean('Gate Entry Check',default=False,compute="onchange_gate_check",store=True)
#     gate_validation_str = fields.Char('Gate Validation String',default='Inward Quantity is not equal to Done Quantity*',store=True)
    quantity_check = fields.Boolean('Quantity Check',default=True)
    gate_validation_strh = fields.Char('Gate Validation String',default='Inward Quantity is not equal to Done Quantity*',store=True)
    
    @api.depends('picking_type_id','move_ids_without_package','move_ids_without_package.quantity_done')
    def onchange_gate_check(self):
        for rec in self:
            if not rec.origin:
                rec.gate_entry_check = True
            elif rec.picking_type_id.name == 'Delivery Orders':
                rec.gate_entry_check = True
            elif rec.picking_type_id.name == 'Receipts':
                purchase_id = self.env['purchase.order'].search([('name','=',rec.origin)])
                entry_qty = 0
                actual_qty = 0
                inward_entry_id = self.env['inward.entry'].search([('purchase_id','=',purchase_id.id)])
                if inward_entry_id:
                    print(inward_entry_id,'sds')
                    for entry in inward_entry_id:
                        for line in entry.purchase_inward_ids:
                            entry_qty += line.received_qty
                    for stock in purchase_id.picking_ids:
#                         if stock.state != 'done':
                        for line in stock.move_ids_without_package:
                            actual_qty += line.quantity_done
                    print(actual_qty,entry_qty,'sadd')            
                    if entry_qty == actual_qty:
                        rec.gate_entry_check = True
                        rec.quantity_check = True
                    else:
                        rec.quantity_check = False
                        print(rec.quantity_check)
#                         rec.gate_validation_str = 'Inward Quantity is not equal to Done Quantity*'
                    
                if rec.sale_id:
                    inward_sale_id = self.env['inward.entry'].search([('sale_id','=',rec.sale_id.id)])
                    for entry in inward_sale_id:
                        for line in entry.sale_inward_ids:
                            entry_qty += line.received_qty
                    for stock in rec.sale_id.picking_ids:
                        if stock.state != 'done':
                            for line in stock.move_ids_without_package:
                                actual_qty += line.quantity_done
                    if entry_qty == actual_qty:
                        rec.gate_entry_check = True
                        rec.quantity_check = True
                    else:
                        rec.quantity_check = False
#                         rec.gate_validation_str = 'Inward Quantity is not equal to Done Quantity*'
            else:
                rec.gate_entry_check = False
            
                
    @api.multi
    def button_validate(self):
        res = super(StockPicking,self).button_validate()
        print('hjhjhj')
        for rec in self:
            if rec.gate_entry_check == True and rec.origin != False:
                purchase = self.env['purchase.order'].search([('name','=',rec.origin)])
                sale = self.env['sale.order'].search([('name','=',rec.origin)])
                if purchase:
                    entry_qty = 0
                    actual_qty = 0
                    inward_entry_id = self.env['inward.entry'].search([('purchase_id','=',purchase.id)])
                    if inward_entry_id:
                        for entry in inward_entry_id:
                            for line in entry.purchase_inward_ids:
                                entry_qty += line.received_qty
                        for stock in purchase.picking_ids:
                            if stock.state != 'done':
                                for line in stock.move_ids_without_package:
                                    actual_qty += line.quantity_done
#                         if entry_qty != actual_qty:
#                             rec.gate_entry_check = False
                elif sale:
                    entry_qty = 0
                    actual_qty = 0
                    inward_sale_id = self.env['inward.entry'].search([('sale_id','=',rec.sale_id.id)])
                    for entry in inward_sale_id:
                        for line in entry.sale_inward_ids:
                            entry_qty += line.received_qty
                    for stock in rec.sale_id.picking_ids:
                        if stock.state != 'done':
                            for line in stock.move_ids_without_package:
                                actual_qty += line.quantity_done
#                     if entry_qty == actual_qty:
#                         raise ValidationError('Inward Quantity is not equal to Done Quantity')
                
                else:
                    return res
            else:
                return res
        return res
    
    @api.model
    def action_generate_backorder_wizard(self):
        return self.action_done()
    