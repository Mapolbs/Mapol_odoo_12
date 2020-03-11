# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import time
from collections import OrderedDict
from operator import itemgetter



class SaleDashboard(models.Model):
    _name = 'sale.dashboard'
    _description = 'Sale Dashboard'

    name = fields.Char("")
    
    @api.model
    def get_info_data(self):
        uid = request.session.uid
        sale_id = self.env['sale.order'].search_read([('user_id', '=', uid)])
#         total_sales_count = self.env['sale.order'].sudo().search_count([('state', '=', 'sale')])
        total_quotations_count = self.env['sale.order'].search_count([('state', 'in', ['draft','sent'])])
        to_invoice = self.env['sale.order'].search_count([('state', '=', 'sale'),
                                                                 ('invoice_status', '=', 'to invoice')])
        invoice_total_id = self.env['sale.order'].search([('state', '=', 'sale'),('invoice_status', '=', 'to invoice')])
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
        query = """
                select count(id)
                from sale_order
                WHERE CAST(date_order AS date) BETWEEN '%s' and '%s'
                and  state in ('draft','sent')""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        month_quotations_count = cr.fetchall()
        
        query = """
                select round(sum(amount_total),2)
                from sale_order
                WHERE CAST(date_order AS date) BETWEEN '%s' and '%s'
                and  state in ('draft','sent')""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        month_quotations_total = cr.fetchall()
        
        
        sale_sum_id = self.env['sale.order'].search([('state', '=', 'sale')])
        sale_sum = 0
        total_sales_count = 0
        for rec in sale_sum_id:
            if rec.confirmation_date.year == date.today().year:
                sale_sum += rec.amount_total
                total_sales_count += 1
        
        product_records = {}
        top_prod_label = []
        top_prod_count = []
        for o in sale_sum_id:
            for po in o.order_line:
                if po.product_id:
                    if po.product_id not in product_records:
                        product_records.update({po.product_id:0})
                    product_records[po.product_id] += po.qty_delivered
        for product_id, qty_delivered in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True):
            if len(top_prod_label)<5:
                top_prod_label.append(product_id.name)
                top_prod_count.append(qty_delivered)
                
        
        quotations_sum_id = self.env['sale.order'].search([('state', 'in', ['draft','sent'])])
        quotations_sum = 0
        for rec in quotations_sum_id:
            quotations_sum += rec.amount_total
            
        cancel_sale_id = self.env['sale.order'].search([('state','=','cancel')])
        cancel_sum = 0
        cancel_count = 0
        for rec in cancel_sale_id:
            if rec.confirmation_date.year == date.today().year:
                cancel_count += 1
                cancel_sum += rec.amount_total
            
        fully_invoice_id = self.env['sale.order'].search([('invoice_status','=','invoiced')])
        fully_count = 0
        fully_sum = 0
        for rec in fully_invoice_id:
            if rec.confirmation_date.year == date.today().year:
                fully_count += 1
                fully_sum += rec.amount_total
                
        sale_search_view_id = self.env.ref('sale.view_sales_order_filter')
        invoice_search_id = self.env.ref('account.view_account_invoice_filter')
        
        query = """
                select sum(s.amount_total) as amount, 
                date_trunc('month', s.confirmation_date)::date AS month_date
                from sale_order s
                WHERE state = 'sale' AND date_part('year', s.confirmation_date) = date_part('year', CURRENT_DATE)
                group by month_date
        """
#         query = """
#                 select sum(s.amount_total) as amount,
#                 date_trunc('month', s.confirmation_date)::date AS month_date,
#                 DATE(s.confirmation_date) as date
#                 from sale_order s
#                 WHERE state = 'sale' AND date_part('year', s.confirmation_date) = date_part('year', CURRENT_DATE)
#                 group by date_trunc('month', s.confirmation_date)::date, DATE(s.confirmation_date)
#         """
        cr.execute(query)
        sale_data = cr.dictfetchall()
        sale_label = []
        sale_dataset = []
        sale_invoice_total = 0
        for invoice in invoice_total_id:
            sale_invoice_total += invoice.amount_total
        for data in sale_data:
#             sale_label.append(data['date'])
#             date_new = datetime.strptime(data['month_date'], "%d %b %Y")
            sale_label.append(str(data['month_date'].month) + '-' + str(data['month_date'].year))
            sale_dataset.append(data['amount'])
            
            
        #stock product count
        
        product_id = self.env['product.product'].search([('bom_ids','!=',False)])
        prod_label = []
        prod_count = []
        product_records = {}
        for o in product_id:
            if o not in product_records:
                product_records.update({o.name:0})
            product_records[o.name] += o.qty_available
        for product_id, product_qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True):
            if len(prod_label)<5:
                prod_label.append(product_id)
                prod_count.append(product_qty)
        
        
#         for product in product_id:
#             
#             prod_label.append(product.name)
#             prod_count.append(product.qty_available)
        
        
        query = """
            SELECT partner.name as partner_ids,count(partner_id),sum(amount_total) FROM sale_order sale LEFT JOIN res_partner partner on partner.id = sale.partner_id where state='sale' group by partner_ids order by sum(amount_total) desc limit 5
        """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        amt = []
        for value in partner_data:
            amt.append(value['sum'])
#         customer_sale_id = self.env['sale.order'].search([('state','!=','draft')])
        
        
        invoice_id_done = self.env['account.invoice'].search_count([('state','=','paid'),('type','=','out_invoice')])
        invoice_id_pending = self.env['account.invoice'].search_count([('state','=','open'),('type','=','out_invoice')])
        invoice_id_today = self.env['account.invoice'].search_count([('date_invoice','=',date.today()),('type','=','out_invoice')])
        invoice_id_refund = self.env['account.invoice'].search_count([('state','=','open'),('type','=','out_refund')])
        invoice_id = self.env['account.invoice'].search([('state','=','open'),('type','=','out_invoice')])
        invoice_refund_id = self.env['account.invoice'].search([('state','=','open'),('type','=','out_refund')])
        invoice_done_id = self.env['account.invoice'].search([('state','=','paid'),('type','=','out_invoice')])
        today = date.today()
        from_date_last_30 = today - relativedelta(days=30)
        from_date_last_180 = today - relativedelta(days=180)
        to_date_last_180 = today + relativedelta(days=180)
        from_date_last_90 = today - relativedelta(days=90)
        invoice_total = 0
        invoice_done_total = 0
        invoice_refund_total = 0
        due_30_total = 0
        due_30_count = 0
        due_180_count = 0
        due_180_total = 0
        due_90_total = 0
        due_90_count = 0
        due_30_done_total = 0
        due_30_done_count = 0
        due_180_done_count = 0
        due_180_done_total = 0
        due_90_done_total = 0
        due_90_done_count = 0
        due_30_refund_total = 0
        due_30_refund_count = 0
        due_180_refund_count = 0
        due_180_refund_total = 0
        due_90_refund_total = 0
        due_90_refund_count = 0
        today_due_count = 0
        today_due_total = 0
        today_due_done_count = 0
        today_due_done_total = 0
        today_refund_count = 0
        today_refund_total = 0
        overdue_180_count = 0
        overdue_180_total = 0
        for invoice in invoice_id:
            invoice_total = invoice_total + invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                due_30_count = due_30_count + 1
                due_30_total = due_30_total + invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today > invoice.date_due:
                overdue_180_count += 1
                overdue_180_total += invoice.amount_total
            if to_date_last_180 >= invoice.date_due and today <= invoice.date_due:
                due_180_count += 1
                due_180_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                due_90_count += 1
                due_90_total += invoice.amount_total
            if today == invoice.date_due:
                today_due_count += 1
                today_due_total += invoice.amount_total
        for invoice in invoice_refund_id:
            invoice_refund_total = invoice_refund_total + invoice.amount_total  
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                due_30_refund_count += 1
                due_30_refund_total += invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
                due_180_refund_count += 1
                due_180_refund_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                due_90_refund_count += 1
                due_90_refund_total += invoice.amount_total  
            if today == invoice.date_due:
                today_refund_count += 1
                today_refund_total += invoice.amount_total
        for invoice in invoice_done_id:
            invoice_done_total += invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                due_30_done_count += 1
                due_30_done_total += invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
                due_180_done_count += 1
                due_180_done_total += invoice.amount_total
            if from_date_last_90 <= invoice.date_due and today >= invoice.date_due:
                due_90_done_count += 1
                due_90_done_total += invoice.amount_total
            if today == invoice.date_due:
                today_due_done_count += 1
                today_due_done_total += invoice.amount_total
        today_due = today_due_count + today_due_done_count
        today_total = today_due_done_total + today_due_total
        due_30 = due_30_count + due_30_done_count
        due_30_final = due_30_total + due_30_done_total
        due_90 = due_90_count + due_90_done_count
        due_90_final = due_90_total + due_90_done_total
        due_180 = due_180_count + due_180_done_count
        due_180_final =  due_180_total + due_180_done_total

        if not sale_id:
            sale_id = [{}]
        
        if sale_id or not sale_id:
            sale_data = {
                'total_sales_count': total_sales_count,
                'total_quotations_count': total_quotations_count,
                'month_quotations_count': month_quotations_count,
                'month_quotations_total':month_quotations_total,
                'to_invoice': to_invoice,
                'sale_invoice_total':round(sale_invoice_total,2),
                'sale_search_view_id':sale_search_view_id.id,
                'invoice_search_id':invoice_search_id.id,
                'sale_sum': round(sale_sum,2),
                'quotations_sum': round(quotations_sum,2),
                'cancel_count':cancel_count,
                'cancel_sum': round(cancel_sum,2),
                'fully_sum': round(fully_sum,2),
                'fully_count': fully_count,
                'sale_label': sale_label,
                'sale_dataset': sale_dataset,
                'top_prod_label': top_prod_label,
                'top_prod_count': top_prod_count,
                'prod_label':prod_label,
                'prod_count':prod_count,
                'partner_data':partner_data,
                'customer_min_amt':min(amt),
                'invoice_done':round(invoice_id_done,2),
                'invoice_pending':round(invoice_id_pending,2),
                'invoice_today':round(invoice_id_today,2),
                'invoice_refund':round(invoice_id_refund,2),
                'total_invoice':round(invoice_total,2),
                'total_refund':round(invoice_refund_total,2),
                'today_due':round(today_due,2),
                'due_30':round(due_30,2),
                'due_30_final':round(due_30_final,2),
                'due_90':round(due_90,2),
                'due_90_final':round(due_90_final,2),
                'due_180':round(due_180,2),
                'due_180_final':round(due_180_final,2),
                'today_total':round(today_total,2),
                'due_30_count':due_30_count,
                'due_30_total':round(due_30_total,2),
                'overdue_180_count':overdue_180_count,
                'overdue_180_total':round(overdue_180_total,2),
                'due_180_count':due_180_count,
                'due_180_total':round(due_180_total,2),
                'due_90_count':due_90_count,
                'due_90_total':round(due_90_total,2),
                'due_30_refund_count':due_30_refund_count,
                'due_30_refunf_total':round(due_30_refund_total,2),
                'due_180_refund_count':due_180_refund_count,
                'due_180_refund_total':round(due_180_refund_total,2),
                'due_90_refund_count':due_90_refund_count,
                'due_90_refund_total':round(due_90_refund_total,2),
                'due_30_done_count':due_30_done_count,
                'due_30_done_total':round(due_30_done_total,2),
                'due_180_done_count':due_180_done_count,
                'due_180_done_total':round(due_30_done_total,2),
                'due_90_done_count':due_90_done_count,
                'due_90_done_total':round(due_90_done_total,2),
                'today_due_count':today_due_count,
                'today_due_total':round(today_due_total,2),
                'today_refund_count':today_refund_count,
                'today_refund_total':round(today_refund_total,2),
                'today_due_done_count':today_due_done_count,
                'today_due_done_total':round(today_due_done_total,2),
            }
            sale_id[0].update(sale_data)
        return sale_id
    
    
    
     