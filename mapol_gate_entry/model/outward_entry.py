# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class InwardEntry(models.Model):
    _name = 'outward.entry'
    _description = 'Outward Entry'
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
    purchase_outward_ids = fields.One2many('purchase.outward.entry','outward_id',help='Purchase Inward Challan Details')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft')
    sale_outward_ids = fields.One2many('sale.outward.entry','outward_id',help="Sale Return Challan Details")
    
    
    
    
    @api.multi
    def change_done(self):
        self.update({'state':'done'})
        if self.state == 'done':
            if self.purchase_outward_ids:
                for line in self.purchase_outward_ids.purchase_id:
                    line.outward_entry_id = self.id
                    line.outward_entry_count = line.outward_entry_count + 1
#                     if line.picking_ids:
#                         for picking in line.picking_ids:
#                             picking.gate_entry_check = True
            if self.sale_outward_ids:
                for line in self.sale_outward_ids.sale_id:
                    line.outward_entry_id = self.id
                    line.outward_entry_count = line.outward_entry_count + 1
#                     if line.picking_ids:
#                         for picking in line.picking_ids:
#                             picking.gate_entry_check = True


class PurchaseInward(models.Model):
    _name = 'purchase.outward.entry'
    _description = 'Outward Purchase Entry'
    
    outward_id = fields.Many2one('outward.entry',help='Outward Entry Reference')
    challan_no = fields.Char('Challan Number',help='Challan Number')
    challan_date = fields.Date('Challan Date',help='Challan Date')
    purchase_id = fields.Many2one('purchase.order','Purchase Order',help='Challan Against Purchase Order')
    quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    reference = fields.Char('Reference',help='Reference of the Goods')
    
    
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    outward_entry_id = fields.Many2one('outward.entry','Outward Entry Check')
    outward_entry_count = fields.Integer('Outward Entry Count',default=0)
    
    @api.multi
    def action_view_outward_entry(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'outward.entry',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [[self.env.ref('mapol_gate_entry.view_outward_entry_form').id, 'form']],
                'res_id': self.outward_entry_id.id,
                'target': 'current',
               }
        
class SaleReturn(models.Model):
    _name = 'sale.outward.entry'
    _description = 'Sale Outward'
    
    outward_id = fields.Many2one('outward.entry',help='Outward Entry Reference')
    challan_no = fields.Char('Challan Number',help='Challan Number')
    challan_date = fields.Date('Challan Date',help='Challan Date')
    sale_id = fields.Many2one('sale.order','Sale Order',help='Challan Against Purchase Order')
    quality = fields.Selection([('good','Good'),('average','Average'),('bad','Bad')],'Goods Quality',help='Quality of Goods')
    reference = fields.Char('Reference',help='Reference of the Goods')
    
class Sale(models.Model):
    _inherit = 'sale.order'
    
    outward_entry_id = fields.Many2one('outward.entry','Outward Entry Check')
    outward_entry_count = fields.Integer('Outward Entry Count',default=0)
    
    @api.multi
    def action_view_outward_entry(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'outward.entry',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [[self.env.ref('mapol_gate_entry.view_outward_entry_form').id, 'form']],
                'res_id': self.outward_entry_id.id,
                'target': 'current',
               }
        
