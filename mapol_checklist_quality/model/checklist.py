from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# class ChecklistCategory(models.Model):
#     _name = 'checklist.category'
#     _description = "Quality Checklist"
#     
#     name = fields.Char('Name',required=True)
#     code = fields.Char('code')
    
class ChecklistSet(models.Model):
    _name = 'checklist.set'
    _descriptio = 'Quality Checklist Set'
    
    name = fields.Char('Name',required=True)
    type = fields.Selection([('descriptive','Descriptive'),('image','Image'),('numeric','Numeric Type')],default="descriptive")
    max_value = fields.Float('Max Value')
    min_value = fields.Float('Min Value')
#     product_value = fields.Float('Value')
    image = fields.Binary()
#     image_value = fields.Selection([('yes','Yes'),('no','No')])
    description = fields.Char('Description')
#     remarks = fields.Text('Remarks')
    product_id = fields.Many2one('product.product','Product',required=True)
#     checklist_category_id = fields.Many2one('checklist.category','Checklist Category',required=True)
    
    @api.onchange('min_value','max_value')
    def onchange_min_max(self):
        if self.min_value:
            if self.max_value < self.min_value:
                raise ValidationError('Max value should be greater than Min Value')
        if self.max_value:
            if self.min_value > self.max_value:
                raise ValidationError('Min Value should be less than Max Value')
    
    
class Product(models.Model):
    _inherit = 'product.template'
    
    is_quality_required = fields.Boolean('Quality Required')
    
    #     checklist_category_id = fields.Many2one('checklist.category','Checklist Category')
    
class ChecklistMain(models.Model):
    _name = 'checklist.main'
    _description = 'Quality Checklist'
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('checklist.main') or _('New')
        return super(ChecklistMain,self).create(vals)
    
    _sql_constraints = [
        ('Stock_unique', 'unique(stock_id)', "Checklist is already created for this Stock."),
    ]
    name = fields.Char('Name')
    stock_id = fields.Many2one('stock.move','Stock',required=True)
    product_id = fields.Many2one('product.product','Product',required=True)
#     checklist_category_id = fields.Many2one('checklist.category','Checklist Category',required=True)
    checklist_line_ids = fields.One2many('checklist.main.line','checklist_main_id')
    state = fields.Selection([
        ('draft','Draft'),
        ('partial', 'Partial'),
        ('pass', 'Passed'),
        ('fail', 'Failed'),
    ], 'Status', copy=False, default='draft')
    purchase_id = fields.Many2one('purchase.order','Purchase')
#     @api.depends('checklist_line_ids.checklist_test')
#     def onchange_state(self):
#         line_count = 0
#         yes_count = 0
#         no_count = 0
#         for line in self.checklist_line_ids:
#             line_count += 1
#             if line.checklist_test == 'yes':
#                 yes_count += 1
#             elif line.checklist_test == 'no':
#                 no_count += 1
#         if line_count == yes_count:
#             self.state = 'pass'
#         elif line_count == no_count:
#             self.state = 'fail'
#         else:
#             self.state = 'partial'
        
    def chg_done(self):
        self.state = "pass"
    def chg_fail(self):
        self.state = 'fail'
#                    
    

class ChecklistLine(models.Model):
    _name = 'checklist.main.line'
    
    checklist_main_id = fields.Many2one('checklist.main','Checklist Main')
    product_id = fields.Many2one('product.product','Product')
#     checklist_category_id = fields.Many2one('checklist.category','Checklist Category',required=True)
    checklist_set_id = fields.Many2one('checklist.set','Checklist Set',domain="[('product_id','=',product_id)]",required=True)
    type = fields.Selection([('descriptive','Descriptive'),('image','Image'),('numeric','Numeric Type')],default="descriptive")
    max_value = fields.Float('Max Value')
    min_value = fields.Float('Min Value')
    image = fields.Binary()
    product_value = fields.Float('Value')
    description = fields.Char('Description')
    checklist_test = fields.Selection([('yes','Yes'),('no',"No")],'Test',default='yes')
    remarks = fields.Text('Remarks')
#     
#     @api.onchange('product_value')
#     def onchange_product_value(self):
#         for rec in self:
#             if rec:
#                 if rec.product_value > rec.max_value:
#                     raise ValidationError('Value greater than Max value')
#                 elif rec.product_value < rec.min_value:
#                     raise ValidationError('Value lesser than Max value')
    
class stock(models.Model):
    _inherit = 'stock.move'
    
    checklist_main_id = fields.Many2one('checklist.main','Quality Checklist')
#     is_quality_required = fields.Boolean('Quality Required')
    
    @api.multi
    def quality_checklist(self):
        for rec in self:
            quality = self.env['checklist.main'].search([('stock_id','=',rec.id)])
            if quality:
                raise ValidationError('Already Checklist Completed')
            if rec.quantity_done <= 0:
                raise ValidationError('Provide Done Quantity')
            if rec.product_id.is_quality_required == True:
#                 self.is_quality_required = True
                checklist_line = []
                if rec:
                    checklist = self.env['checklist.set'].search([])
                    if not checklist:
                        raise ValidationError('Checklist not found. Create checklist for this Product..!!')
                    for check in checklist:
                        if rec.product_id.id == check.product_id.id:
                            checklist_line.append((0,0,{'product_id':check.product_id.id,'checklist_set_id':check.id,
                                                        'type':check.type,'max_value':check.max_value,'min_value':check.min_value,
                                                        'image':check.image,'description':check.description}))
                            
#                         else:
#                             raise ValidationError('Checklist not added')
                    return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'checklist.main',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [[self.env.ref('mapol_checklist_quality.view_checklist_main_form').id, 'form']],
                    'target': 'new',
                    'context':{
                        'default_stock_id':rec.id,
                        'default_product_id':rec.product_id.id,
    #                     'default_checklist_category_id':rec.product_id.checklist_category_id.id,
                        'default_checklist_line_ids':checklist_line,
                        'default_purchase_id':rec.purchase_id.id,
                        }
                   }
            else:
                raise ValidationError('Product not required to check quality')
    
class Picking(models.Model):
    _inherit = 'stock.picking'
    
    
    @api.multi
    def quality_checked(self):
        for rec in self:
            if rec:
                for line in rec.move_ids_without_package:
                    checklist = self.env['checklist.main'].search([('stock_id','=',line.id)],limit=1)
                    if checklist:
                        line.checklist_main_id = checklist.id
                    else:
                        raise ValidationError('Quality Check not Completed')
    
    @api.multi
    def button_validate(self):
        for rec in self:
            res = super(Picking, self).button_validate()
            for line in rec.move_ids_without_package:
                if line.product_id.is_quality_required == True:
                    if line.checklist_main_id:
                        return res
                    if rec.picking_type_id.name == 'Delivery Orders':
                        return res
                    else:
                        raise ValidationError('Stock need to clear all the checklist')
                else:
                    return res
    
    

    