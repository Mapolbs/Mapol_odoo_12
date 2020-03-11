# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import time
from scipy.constants.constants import pt


class AllDashboard(models.Model):
    _name = 'all.dashboard'
    _description = 'All Dashboard'

    name = fields.Char("")
    
    
    @api.model
    def get_info(self):
        uid = request.session.uid
        purchase_id = self.env['purchase.order'].search_read([('user_id', '=', uid)])
        rfq_count = self.env['purchase.order'].search_count([('state', 'in', ['draft', 'sent','to approve'])])
        purchase_count = self.env['purchase.order'].search_count([('state', 'in', ['purchase', 'done'])])
        
        rfq_id = self.env['purchase.order'].search([('state', 'in', ['draft', 'sent','to approve'])])
        rfq_sum = 0
        for rec in rfq_id:
            rfq_sum += rec.amount_total
        print(rfq_sum)
        purchase_sum_id = self.env['purchase.order'].search([('state', 'in', ['purchase', 'done'])])
        purchase_sum = 0
        for rec in purchase_sum_id:
            purchase_sum += rec.amount_total
        
        shipments_count = self.env['stock.picking'].search_count([('state', 'not in', ['cancel', 'done']),
                                                                         ('picking_type_id.code','=','incoming'),
                                                                         ('origin','ilike','PO')])
        shipments_id = self.env['stock.picking'].search([('state', 'not in', ['cancel', 'done']),
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
            
        order = self.env['purchase.order'].search([('state','in',('purchase','done'))])  
        product_records = {}
        prod_label = []
        prod_count = []
        for o in order:
            for po in o.order_line:
                if po.product_id:
                    if po.product_id not in product_records:
                        product_records.update({po.product_id:0})
                    product_records[po.product_id] += po.product_qty
        for product_id, product_qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True):
            if len(prod_label)<5:
                prod_label.append(product_id.name)
                prod_count.append(product_qty)
                
                
        query = """
            SELECT partner.name as partner_ids,count(partner_id),sum(amount_total) FROM purchase_order purchase LEFT JOIN res_partner partner on partner.id = purchase.partner_id where state='purchase' group by partner_ids order by sum(amount_total) desc limit 5
        """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        
        general_id = self.env['purchase.order'].search([('is_production_purchase','=',False),('state','!=','cancel')])
        general_count = 0
        general_total = 0
        for general in general_id:
            if general.date_order.year == date.today().year:
                general_count += 1
                general_total += general.amount_total
            
        production_id = self.env['purchase.order'].search([('is_production_purchase','=',True),('state','!=','cancel')])
        production_count = 0
        production_total = 0
        for production in production_id:
            if production.date_order.year == date.today().year:
                production_count += 1
                production_total += production.amount_total
            
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
        to_date_last_180 = today + relativedelta(days=180)
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
        bill_overdue_180_count = 0
        bill_overdue_180_total = 0
        for invoice in bill_id:
            bill_total = bill_total + invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                bill_due_30_count = bill_due_30_count + 1
                bill_due_30_total = bill_due_30_total + invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today > invoice.date_due:
                bill_overdue_180_count += 1
                bill_overdue_180_total += invoice.amount_total
            if to_date_last_180 >= invoice.date_due and today <= invoice.date_due:
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
        
        if not purchase_id:
            purchase_id = [{}]
        
        if purchase_id or not purchase_id:
            data = {
                'rfq_count': rfq_count,
                'purchase_count': purchase_count,
                'shipments_count': shipments_count,
                'shipment_total':round(shipment_total,2),
                'month_shipments_count': month_shipments_count,
                'month_shipments_total':round(month_shipments_total,2),
                'rfq_sum': round(rfq_sum,2),
                'prod_label':prod_label,
                'general_count':general_count,
                'general_total':round(general_total,2),
                'production_count':production_count,
                'production_total':round(production_total,2),
                'prod_count':prod_count,
                'partner_data':partner_data,
                'purchase_sum': round(purchase_sum,2),
                'purchase_label': purchase_label,
                'purchase_dataset': purchase_dataset,
                'purchase_search_view_id':purchase_search_view_id.id,
                'shipments_search_view_id':shipments_search_view_id.id,
                'bill_search_id':bill_search_id.id,
                'bill_done':round(bill_id_done,2),
                'bill_pending':round(bill_id_pending,2),
                'bill_today':round(bill_id_today,2),
                'bill_refund':round(bill_id_refund,2),
                'total_bill':round(bill_total,2),
                'total_refund':round(bill_refund_total,2),
                'bill_today_due':round(bill_today_due,2),
                'bill_due_30':round(bill_due_30,2),
                'bill_due_30_final':round(bill_due_30_final,2),
                'bill_due_90':round(bill_due_90,2),
                'bill_due_90_final':round(bill_due_90_final,2),
                'bill_due_180':round(bill_due_180,2),
                'bill_due_180_final':round(bill_due_180_final,2),
                'bill_today_total':round(bill_today_total,2),
                'bill_due_30_count':bill_due_30_count,
                'bill_due_30_total':round(bill_due_30_total,2),
                'bill_due_180_count':bill_due_180_count,
                'bill_due_180_total':round(bill_due_180_total,2),
                'bill_overdue_180_count':bill_overdue_180_count,
                'bill_overdue_180_total':round(bill_overdue_180_total,2),
                'bill_due_90_count':bill_due_90_count,
                'bill_due_90_total':round(bill_due_90_total,2),
                'bill_due_30_refund_count':bill_due_30_refund_count,
                'bill_due_30_refunf_total':round(bill_due_30_refund_total,2),
                'bill_due_180_refund_count':bill_due_180_refund_count,
                'bill_due_180_refund_total':round(bill_due_180_refund_total,2),
                'bill_due_90_refund_count':bill_due_90_refund_count,
                'bill_due_90_refund_total':round(bill_due_90_refund_total,2),
                'bill_due_30_done_count':bill_due_30_done_count,
                'bill_due_30_done_total':round(bill_due_30_done_total,2),
                'bill_due_180_done_count':bill_due_180_done_count,
                'bill_due_180_done_total':round(bill_due_30_done_total,2),
                'bill_due_90_done_count':bill_due_90_done_count,
                'bill_due_90_done_total':round(bill_due_90_done_total,2),
                'bill_today_due_count':bill_today_due_count,
                'bill_today_due_total':round(bill_today_due_total,2),
                'bill_today_refund_count':bill_today_refund_count,
                'bill_today_refund_total':round(bill_today_refund_total,2),
                'bill_today_due_done_count':bill_today_due_done_count,
                'bill_today_due_done_total':round(bill_today_due_done_total,2),
            }
            purchase_id[0].update(data)
        return purchase_id 
    
