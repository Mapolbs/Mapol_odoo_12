# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class InwardEntry(models.Model):
    _name = 'inward.entry'
    _description = 'Inward Entry'
    _rec_name = 'lr_rr_no'
    
    
    lr_rr_no = fields.Char('LR/RR No', help='Lorry Receipt / Railway Receipt Number.',required=True)
    lr_rr_date = fields.Date('LR/RR Date', help='Lorry Receipt / Railway Receipt Date.')
    document_date = fields.Datetime('Enrty Date',help='Entry Date of the Vehicle.')
    goods_from = fields.Char('Goods From', help='Vehicle from the city.')
    is_company_vehicle = fields.Boolean('Our Company Vehicle',help='Vehicle from Our Company.')
    vehicle_number = fields.Char('Vehicle Number',help='Vehicle Number')
    company_vehicle_id = fields.Many2one('fleet.vehicle','Company Vehicle Number',help='Company Vehicle Number')
    odometer_value = fields.Float('Vehicle Odometer Value',help='Company Vehicle Odometer Value',related="company_vehicle_id.odometer")
    description = fields.Char('Material Description')
    comment = fields.Text('Comment')
    purchase_inward_ids = fields.One2many('purchase.inward.entry','inward_id',help='Purchase Inward Challan Details')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft')
    sale_return_ids = fields.One2many('sale.return.inward','inward_id',help="Sale Return Challan Details")
    
    
    
    
    @api.multi
    def change_done(self):
        self.update({'state':'done'})
        if self.state == 'done':
            if self.purchase_inward_ids:
                for line in self.purchase_inward_ids.purchase_id:
                    line.inward_entry_id = self.id
                    line.inward_entry_count = line.inward_entry_count + 1
                    if line.picking_ids:
                        for picking in line.picking_ids:
                            picking.gate_entry_check = True
            if self.sale_return_ids:
                for line in self.sale_return_ids.sale_id:
                    line.inward_entry_id = self.id
                    line.inward_entry_count = line.inward_entry_count + 1
                    if line.picking_ids:
                        for picking in line.picking_ids:
                            picking.gate_entry_check = True


class PurchaseInward(models.Model):
    _name = 'purchase.inward.entry'
    _description = 'Inward Purchase Entry'
    
    inward_id = fields.Many2one('inward.entry',help='Inward Entry Reference')
    challan_no = fields.Char('Challan Number',help='Challan Number')
    challan_date = fields.Date('Challan Date',help='Challan Date')
    purchase_id = fields.Many2one('purchase.order','Purchase Order',help='Challan Against Purchase Order')
    quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    reference = fields.Char('Reference',help='Reference of the Goods')
    
    
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    inward_entry_id = fields.Many2one('inward.entry','Inward Entry Check')
    inward_entry_count = fields.Integer('Inward Entry Count',default=0)
    
    @api.multi
    def action_view_inward_entry(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'inward.entry',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [[self.env.ref('mapol_gate_entry.view_inward_entry_form').id, 'form']],
                'res_id': self.inward_entry_id.id,
                'target': 'current',
               }
        
class SaleReturn(models.Model):
    _name = 'sale.return.inward'
    _description = 'Sale Return Inward'
    
    inward_id = fields.Many2one('inward.entry',help='Inward Entry Reference')
    challan_no = fields.Char('Challan Number',help='Challan Number')
    challan_date = fields.Date('Challan Date',help='Challan Date')
    sale_id = fields.Many2one('sale.order','Sale Order',help='Challan Against Purchase Order')
    quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    reference = fields.Char('Reference',help='Reference of the Goods')
    
class Sale(models.Model):
    _inherit = 'sale.order'
    
    inward_entry_id = fields.Many2one('inward.entry','Inward Entry Check')
    inward_entry_count = fields.Integer('Inward Entry Count',default=0)
    
    @api.multi
    def action_view_inward_entry(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'inward.entry',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [[self.env.ref('mapol_gate_entry.view_inward_entry_form').id, 'form']],
                'res_id': self.inward_entry_id.id,
                'target': 'current',
               }
        


class StockPicking(models.Model):
    _inherit = 'stock.picking'
     
    gate_entry_check = fields.Boolean('Gate Entry Check',default=False)


 
    