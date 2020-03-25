from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class Planning(models.Model):
    _name = 'mrp.plan'
    _description = 'MRP Planning'
    
    
    def change_color_on_kanban(self):
        for record in self:
            color = 0
            if record.state == 'draft':
                color = 4
            elif record.state == 'approve':
                color = 10
            elif record.state == 'cancel':
                color = 9
            record.color = color
    
    
    
    name = fields.Char('Name',readonly=True)
#     location_dest_id = fields.Many2one('stock.location','Destination Loaction')
    product_id = fields.Many2one('product.product','Product',domain="[('bom_ids','!=',False)]") 
    plan_date = fields.Datetime('Plan Date',default=datetime.today())
    production_date = fields.Datetime('Production Date')
    plan_qty = fields.Float('Plan Quantity')
    uom_id = fields.Many2one('uom.uom','Product Uom')
    bom_id = fields.Many2one('mrp.bom','Bom',domain="[('product_tmpl_id','=',product_id)]")
    user_id = fields.Many2one('res.users','Responsible')
    is_subcontract = fields.Boolean('Subcontract',default=False,compute="onchange_subcontract")
    state = fields.Selection([('draft','Draft'),('approve','Approve'),('cancel','Cancel')],copy=False,default="draft")
    production_id = fields.Many2one('mrp.production','Production',readonly=True)
    color = fields.Integer('Color Index', compute="change_color_on_kanban")
    progress = fields.Integer('Production Progress',default=10,compute="onchange_widget")
    max_progress = fields.Integer(default=100)
    
    @api.depends('production_id')
    def onchange_widget(self):
        for rec in self:
            if rec.production_id:
                if rec.production_id.state == 'confirmed':
                    rec.progress = 25
                elif rec.production_id.state == 'planned':
                    rec.progress = 50
                elif rec.production_id.state == 'progress':
                    rec.progress = 75
                elif rec.production_id.state == 'done':
                    rec.progress = 100
                elif rec.production_id.state == 'cancel':
                    rec.progress = 0
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mrp.plan') or _('New')
        return super(Planning,self).create(vals)  
    
    @api.onchange('product_id')
    def onchange_bom(self):
        if self.product_id:
            print(self.product_id)
            product_id = self.env['product.template'].search([('name','=',self.product_id.name)],limit=1)
            print(product_id)
            bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_id.id)],limit=1)
            self.bom_id = bom
            self.uom_id = self.product_id.uom_id.id
            self.plan_qty = 1
    
    
    @api.onchange('production_date')
    def onchange_date(self):
        if self.production_date and self.plan_date:
            if self.production_date < self.plan_date:
                raise ValidationError('Production Date should be greater than Plan Date...!!')
    
    
    @api.depends('bom_id')
    def onchange_subcontract(self):
        for rec in self:
            if rec.bom_id:
                rec.is_subcontract = rec.bom_id.is_subcontract

#     def confirm(self):
#         if self.state:
#             self.ensure_one()
#             template = self.env['ir.model.data'].get_object('mrp_plan', 'email_template_mrp_plan')
#             self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
#             self.state = 'confirm'
        
    def cancel(self):
        if self.state:
            self.state = 'cancel'
    
    def approve(self):
        if self.product_id:
            picking_type_id = self.env['stock.picking.type'].search([('code','=','mrp_operation'),('warehouse_id.partner_id','=',self.env.user.company_id.id)])
#             product_id = self.env['product.product'].search([('name','=','')])
            mrp_order = {
                    'product_id':self.product_id.id,
                    'planned_date':self.plan_date,
                    'product_qty':self.plan_qty,
                    'product_uom_id':self.uom_id.id,
                    'date_planned_start':self.production_date,
                    'bom_id':self.bom_id.id,
                    'user_id':self.user_id.id,
#                     'location_dest_id':self.location_dest_id.id,
                    'is_subcontract':self.is_subcontract,
                    'partner_id':self.bom_id.partner_id.id,
                    'picking_type_id':picking_type_id.id,
                    'location_src_id':picking_type_id.default_location_src_id.id,
                    'planned_id':self.id or '',
                }
            mrp = self.env['mrp.production'].create(mrp_order)
            self.production_id = mrp
            template = self.env['ir.model.data'].get_object('mrp_plan', 'email_template_mrp_plan')
            self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
            self.state = 'approve'
            
            
    def manufacture_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': self.production_id.id,
            'view_type': 'form',
            'view_mode': 'form',
#             'context': self.env.context,
            'target': 'current',
        }
        
     
class Production(models.Model):
    _inherit = 'mrp.production'
     
    planned_date = fields.Char('Planned Date')
    planned_id = fields.Many2one('mrp.plan','Production Plan')
    
    
    
       
     