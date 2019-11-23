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
        if purchase_id:
            data = {
                'rfq_count': rfq_count,
                'purchase_count': purchase_count,
                'shipments_count': shipments_count,
                'month_shipments_count': month_shipments_count,
                'rfq_sum': rfq_sum,
                'purchase_sum': purchase_sum,
                'purchase_label': purchase_label,
                'purchase_dataset': purchase_dataset,
                'purchase_search_view_id':purchase_search_view_id.id,
                'shipments_search_view_id':shipments_search_view_id.id
            }
            purchase_id[0].update(data)
        return purchase_id 
    
