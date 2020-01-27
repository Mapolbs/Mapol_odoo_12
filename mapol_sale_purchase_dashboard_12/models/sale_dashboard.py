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
        sale_id = self.env['sale.order'].sudo().search_read([('user_id', '=', uid)])
        total_sales_count = self.env['sale.order'].sudo().search_count([('state', '=', 'sale')])
        total_quotations_count = self.env['sale.order'].sudo().search_count([('state', 'in', ['draft','sent'])])
        to_invoice = self.env['sale.order'].sudo().search_count([('state', '=', 'sale'),
                                                                 ('invoice_status', '=', 'to invoice')])
        invoice_total_id = self.env['sale.order'].sudo().search([('state', '=', 'sale'),('invoice_status', '=', 'to invoice')])
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
                select sum(amount_total)
                from sale_order
                WHERE CAST(date_order AS date) BETWEEN '%s' and '%s'
                and  state in ('draft','sent')""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        month_quotations_total = cr.fetchall()
        
        
        sale_sum_id = self.env['sale.order'].search([('state', '=', 'sale')])
        sale_sum = 0
        for rec in sale_sum_id:
            sale_sum += rec.amount_total
        
        quotations_sum_id = self.env['sale.order'].search([('state', 'in', ['draft','sent'])])
        quotations_sum = 0
        for rec in quotations_sum_id:
            quotations_sum += rec.amount_total
                
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
        for invoice in invoice_id:
            invoice_total = invoice_total + invoice.amount_total
            if from_date_last_30 <= invoice.date_due and today >= invoice.date_due:
                due_30_count = due_30_count + 1
                due_30_total = due_30_total + invoice.amount_total
            if from_date_last_180 <= invoice.date_due and today >= invoice.date_due:
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
        if sale_id:
            sale_data = {
                'total_sales_count': total_sales_count,
                'total_quotations_count': total_quotations_count,
                'month_quotations_count': month_quotations_count,
                'month_quotations_total':month_quotations_total,
                'to_invoice': to_invoice,
                'sale_invoice_total':sale_invoice_total,
                'sale_search_view_id':sale_search_view_id.id,
                'invoice_search_id':invoice_search_id.id,
                'sale_sum': sale_sum,
                'quotations_sum': quotations_sum,
                'sale_label': sale_label,
                'sale_dataset': sale_dataset,
                'invoice_done':invoice_id_done,
                'invoice_pending':invoice_id_pending,
                'invoice_today':invoice_id_today,
                'invoice_refund':invoice_id_refund,
                'total_invoice':invoice_total,
                'total_refund':invoice_refund_total,
                'today_due':today_due,
                'due_30':due_30,
                'due_30_final':due_30_final,
                'due_90':due_90,
                'due_90_final':due_90_final,
                'due_180':due_180,
                'due_180_final':due_180_final,
                'today_total':today_total,
                'due_30_count':due_30_count,
                'due_30_total':due_30_total,
                'due_180_count':due_180_count,
                'due_180_total':due_180_total,
                'due_90_count':due_90_count,
                'due_90_total':due_90_total,
                'due_30_refund_count':due_30_refund_count,
                'due_30_refunf_total':due_30_refund_total,
                'due_180_refund_count':due_180_refund_count,
                'due_180_refund_total':due_180_refund_total,
                'due_90_refund_count':due_90_refund_count,
                'due_90_refund_total':due_90_refund_total,
                'due_30_done_count':due_30_done_count,
                'due_30_done_total':due_30_done_total,
                'due_180_done_count':due_180_done_count,
                'due_180_done_total':due_30_done_total,
                'due_90_done_count':due_90_done_count,
                'due_90_done_total':due_90_done_total,
                'today_due_count':today_due_count,
                'today_due_total':today_due_total,
                'today_refund_count':today_refund_count,
                'today_refund_total':today_refund_total,
                'today_due_done_count':today_due_done_count,
                'today_due_done_total':today_due_done_total,
            }
            sale_id[0].update(sale_data)
        
        return sale_id
    
    
    
     