# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import time


class AllDashboard(models.Model):
    _name = 'all.dashboard'
    _description = 'All Dashboard'

    name = fields.Char("")
    
    
    @api.model
    def get_info(self):
        uid = request.session.uid
        purchase_id = self.env['purchase.order'].sudo().search_read([('user_id', '=', uid)])
        rfq_count = self.env['purchase.order'].sudo().search_count([('state', 'in', ['draft', 'sent','to approve'])])
        purchase_count = self.env['purchase.order'].sudo().search_count([('state', 'in', ['purchase', 'done'])])
        
        rfq_id = self.env['purchase.order'].search([('state', 'in', ['draft', 'sent','to approve'])])
        rfq_sum = 0
        for rec in rfq_id:
            rfq_sum += rec.amount_total
        purchase_sum_id = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        purchase_sum = 0
        for rec in purchase_sum_id:
            purchase_sum += rec.amount_total
        
        shipments_count = self.env['stock.picking'].sudo().search_count([('state', 'not in', ['cancel', 'done']),
                                                                         ('picking_type_id.code','=','incoming'),
                                                                         ('origin','ilike','PO')])
        shipments_id = self.env['stock.picking'].sudo().search([('state', 'not in', ['cancel', 'done']),
                                                                         ('picking_type_id.code','=','incoming'),
                                                                         ('origin','ilike','PO')])
        shipment_total = 0
        for shipment in shipments_id:
            purchase_shipment_id = self.env['purchase.order'].search([('name','=',shipment.origin)])
            if purchase_shipment_id:
                shipment_total += purchase_shipment_id.amount_total
#         shipments_pending_id = self.env['stock.picking'].sudo().search([('state', 'not in', ['cancel', 'done']),
#                                                                          ('picking_type_id.code','=','incoming'),
#                                                                          ('origin','ilike','PO')])
#         shipment_total = 0
#         for shipment in shipments_pending_id:
#             shipment_total += shipment.amount_total
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
        query = """
                select count(sp.id)
                from stock_picking sp
                inner join stock_picking_type spt on spt.id = sp.picking_type_id
                WHERE origin LIKE '%%%s%%' and
                CAST(sp.scheduled_date AS date) BETWEEN '%s' and '%s'""" % ('PO', first_day, last_day)
        cr = self._cr
        cr.execute(query)
        month_shipments_count = cr.fetchall()
        stock_id = self.env['stock.picking'].search([('picking_type_id.code','=','incoming'),('origin','!=',False)])
        month_shipments_total = 0
        for stock in stock_id:
            if stock.scheduled_date.date() > first_day and stock.scheduled_date.date() < last_day: 
                purchase_stock_id = self.env['purchase.order'].search([('name','=',stock.origin)])
                if purchase_stock_id:
                    month_shipments_total += purchase_stock_id.amount_total
        
#         query = """
#                 select sum(sp.amount_total)
#                 from stock_picking sp
#                 inner join stock_picking_type spt on spt.id = sp.picking_type_id
#                 WHERE origin LIKE '%%%s%%' and
#                 CAST(sp.scheduled_date AS date) BETWEEN '%s' and '%s'""" % ('PO', first_day, last_day)
#         cr = self._cr
#         cr.execute(query)
#         month_shipments_total = cr.fetchall()
        bill_search_id = self.env.ref('account.view_account_invoice_filter')
        purchase_search_view_id = self.env.ref('purchase.view_purchase_order_filter')
        shipments_search_view_id = self.env.ref('stock.view_picking_internal_search')
        
        query = """
                select sum(p.amount_total) as amount, pn.name as partner
                from purchase_order p
                inner join res_partner pn on pn.id = p.partner_id
                WHERE p.state in ('purchase', 'done') AND
                p.invoice_status in ('to invoice', 'no')
                group by pn.name
        """
        cr.execute(query)
        purchase_data = cr.dictfetchall()
        purchase_label = []
        purchase_dataset = []
        for data in purchase_data:
            purchase_label.append(data['partner'])
            purchase_dataset.append(data['amount'])
            
        bill_id_done = self.env['account.invoice'].search_count([('state','=','paid'),('type','=','in_invoice')])
        bill_id_pending = self.env['account.invoice'].search_count([('state','=','open'),('type','=','in_invoice')])
        bill_id_today = self.env['account.invoice'].search_count([('date_invoice','=',date.today()),('type','=','in_invoice')])
        bill_id_refund = self.env['account.invoice'].search_count([('state','=','open'),('type','=','in_refund')])
        bill_id = self.env['account.invoice'].search([('state','=','open'),('type','=','in_invoice')])
        bill_refund_id = self.env['account.invoice'].search([('state','=','open'),('type','=','in_refund')])
        bill_done_id = self.env['account.invoice'].search([('state','=','paid'),('type','=','in_invoice')])
        today = date.today()
        from_date_last_30 = today - relativedelta(days=30)
        from_date_last_180 = today - relativedelta(days=180)
        from_date_last_90 = today - relativedelta(days=90)
        bill_total = 0
        bill_done_total = 0
        bill_refund_total = 0
        bill_due_30_total = 0
        bill_due_30_count = 0
        bill_due_180_count = 0
        bill_due_180_total = 0
        bill_due_90_total = 0
        bill_due_90_count = 0
        bill_due_30_done_total = 0
        bill_due_30_done_count = 0
        bill_due_180_done_count = 0
        bill_due_180_done_total = 0
        bill_due_90_done_total = 0
        bill_due_90_done_count = 0
        bill_due_30_refund_total = 0
        bill_due_30_refund_count = 0
        bill_due_180_refund_count = 0
        bill_due_180_refund_total = 0
        bill_due_90_refund_total = 0
        bill_due_90_refund_count = 0
        bill_today_due_count = 0
        bill_today_due_total = 0
        bill_today_due_done_count = 0
        bill_today_due_done_total = 0
        bill_today_refund_count = 0
        bill_today_refund_total = 0
        for invoice in bill_id:
            bill_total = bill_total + invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                bill_due_30_count = bill_due_30_count + 1
                bill_due_30_total = bill_due_30_total + invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
                bill_due_180_count += 1
                bill_due_180_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                bill_due_90_count += 1
                bill_due_90_total += invoice.amount_total
            if today == invoice.date_due:
                bill_today_due_count += 1
                bill_today_due_total += invoice.amount_total
        for invoice in bill_refund_id:
            bill_refund_total = bill_refund_total + invoice.amount_total  
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                bill_due_30_refund_count += 1
                bill_due_30_refund_total += invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
                bill_due_180_refund_count += 1
                bill_due_180_refund_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                bill_due_90_refund_count += 1
                bill_due_90_refund_total += invoice.amount_total  
            if today == invoice.date_due:
                bill_today_refund_count += 1
                bill_today_refund_total += invoice.amount_total
        for invoice in bill_done_id:
            bill_done_total += invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                bill_due_30_done_count += 1
                bill_due_30_done_total += invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
                bill_due_180_done_count += 1
                bill_due_180_done_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                bill_due_90_done_count += 1
                bill_due_90_done_total += invoice.amount_total
            if today == invoice.date_due:
                bill_today_due_done_count += 1
                bill_today_due_done_total += invoice.amount_total
        bill_today_due = bill_today_due_count + bill_today_due_done_count
        bill_today_total = bill_today_due_done_total + bill_today_due_total
        bill_due_30 = bill_due_30_count + bill_due_30_done_count
        bill_due_30_final = bill_due_30_total + bill_due_30_done_total
        bill_due_90 = bill_due_90_count + bill_due_90_done_count
        bill_due_90_final = bill_due_90_total + bill_due_90_done_total
        bill_due_180 = bill_due_180_count + bill_due_180_done_count
        bill_due_180_final =  bill_due_180_total + bill_due_180_done_total
        
        
        
        if purchase_id:
            data = {
                'rfq_count': rfq_count,
                'purchase_count': purchase_count,
                'shipments_count': shipments_count,
                'shipment_total':shipment_total,
                'month_shipments_count': month_shipments_count,
                'month_shipments_total':month_shipments_total,
                'rfq_sum': rfq_sum,
                'purchase_sum': purchase_sum,
                'purchase_label': purchase_label,
                'purchase_dataset': purchase_dataset,
                'purchase_search_view_id':purchase_search_view_id.id,
                'shipments_search_view_id':shipments_search_view_id.id,
                'bill_search_id':bill_search_id.id,
                'bill_done':bill_id_done,
                'bill_pending':bill_id_pending,
                'bill_today':bill_id_today,
                'bill_refund':bill_id_refund,
                'total_bill':bill_total,
                'total_refund':bill_refund_total,
                'bill_today_due':bill_today_due,
                'bill_due_30':bill_due_30,
                'bill_due_30_final':bill_due_30_final,
                'bill_due_90':bill_due_90,
                'bill_due_90_final':bill_due_90_final,
                'bill_due_180':bill_due_180,
                'bill_due_180_final':bill_due_180_final,
                'bill_today_total':bill_today_total,
                'bill_due_30_count':bill_due_30_count,
                'bill_due_30_total':bill_due_30_total,
                'bill_due_180_count':bill_due_180_count,
                'bill_due_180_total':bill_due_180_total,
                'bill_due_90_count':bill_due_90_count,
                'bill_due_90_total':bill_due_90_total,
                'bill_due_30_refund_count':bill_due_30_refund_count,
                'bill_due_30_refunf_total':bill_due_30_refund_total,
                'bill_due_180_refund_count':bill_due_180_refund_count,
                'bill_due_180_refund_total':bill_due_180_refund_total,
                'bill_due_90_refund_count':bill_due_90_refund_count,
                'bill_due_90_refund_total':bill_due_90_refund_total,
                'bill_due_30_done_count':bill_due_30_done_count,
                'bill_due_30_done_total':bill_due_30_done_total,
                'bill_due_180_done_count':bill_due_180_done_count,
                'bill_due_180_done_total':bill_due_30_done_total,
                'bill_due_90_done_count':bill_due_90_done_count,
                'bill_due_90_done_total':bill_due_90_done_total,
                'bill_today_due_count':bill_today_due_count,
                'bill_today_due_total':bill_today_due_total,
                'bill_today_refund_count':bill_today_refund_count,
                'bill_today_refund_total':bill_today_refund_total,
                'bill_today_due_done_count':bill_today_due_done_count,
                'bill_today_due_done_total':bill_today_due_done_total,
            }
            purchase_id[0].update(data)
        return purchase_id 
    
