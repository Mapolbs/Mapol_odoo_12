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
        
        sale_sum_id = self.env['sale.order'].search([('state', '=', 'sale')])
        sale_sum = 0
        for rec in sale_sum_id:
            sale_sum += rec.amount_total
        
        quotations_sum_id = self.env['sale.order'].search([('state', 'in', ['draft','sent'])])
        quotations_sum = 0
        for rec in quotations_sum_id:
            quotations_sum += rec.amount_total
                
        sale_search_view_id = self.env.ref('sale.view_sales_order_filter')
        
        query = """
                select sum(s.amount_total) as amount, 
                date_trunc('month', s.confirmation_date)::date AS month_date
                from sale_order s
                WHERE state = 'sale' AND date_part('year', s.confirmation_date) = date_part('year', CURRENT_DATE)
                group by date_trunc('month', s.confirmation_date)::date
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
        for data in sale_data:
#             sale_label.append(data['date'])
            sale_label.append(data['month_date'])
            sale_dataset.append(data['amount'])
        
        if sale_id:
            sale_data = {
                'total_sales_count': total_sales_count,
                'total_quotations_count': total_quotations_count,
                'month_quotations_count': month_quotations_count,
                'to_invoice': to_invoice,
                'sale_search_view_id':sale_search_view_id.id,
                'sale_sum': sale_sum,
                'quotations_sum': quotations_sum,
                'sale_label': sale_label,
                'sale_dataset': sale_dataset,
            }
            sale_id[0].update(sale_data)
        return sale_id
    
    
    
     