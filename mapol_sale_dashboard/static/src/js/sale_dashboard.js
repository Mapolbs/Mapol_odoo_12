odoo.define('mapol_sale_dashboard.sale_dashboard', function (require) {
"use strict";

var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var DashboardView = AbstractAction.extend(ControlPanelMixin, {
	events: {
    	//sale dashboard events
    	'click .total-sales-count': 'action_total_sales_count',
    	'click .total-quotations-count': 'action_total_quotations_count',
    	'click .month-quotations': 'action_month_quotations',
    	'click .to-invoice': 'action_to_invoice',
        'click .fully-invoice': 'action_fully_invoice',
        'click .cancel-order': 'action_cancel_order',
    	'click .due_1_month': 'action_due_1_month',
    	'click .due_3_month': 'action_due_3_month',
    	'click .due_6_month': 'action_due_6_month',
    	'click .due_today': 'action_due_today',
        'click .due_pending': 'action_due_pending',
        'click .top-sale-customer': 'action_top_sale_customer',
    	//pdf
    	'click #generate_sale_pdf': function(){this.generate_sale_pdf("bar");},
    	'click #generate_sale_pie_pdf': function(){this.generate_sale_pdf("pie")},
	},
	init: function(parent, context) {
        this._super(parent, context);
        var sale_data = [];
        var self = this;
        this.dashboards_templates = ['mapol_sale_dashboard.sale_dashboard'];
        if (context.tag == 'mapol_sale_dashboard.sale_dashboard') {
            //Sale rpc
            self._rpc({
                model: 'sale.dashboard',
                method: 'get_info_data',
            }, []).then(function(result){
                self.sale_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var sale_dashboard = QWeb.render( 'mapol_sale_dashboard.sale_dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(sale_dashboard).prependTo(self.$el);
        self.graph();
       //self.render_dashboards();
       // self.previewTable();
        return sale_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    
	//Sale event action
	
    action_top_sale_customer: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("TOP SALE CUSTOMERS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            search_view_id: self.sale_data.sale_search_view_id,
            context:{'group_by': 'partner_id','create':false,'search_default_order': 'amount_total'},
            domain: [['state','=','sale']],
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },


	action_total_sales_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("TOTAL SALE ORDERS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','sale']],
            context: {'create':false},
            search_view_id: self.sale_data.sale_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },

    action_fully_invoice: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("FULLY INVOICED ORDERS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['invoice_status','=','invoiced']],
            search_view_id: self.sale_data.sale_search_view_id,
            context: {'create':false},
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_cancel_order: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("CANCEL SALE ORDERS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','cancel']],
            search_view_id: self.sale_data.sale_search_view_id,
            context: {'create':false},
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    
    action_total_quotations_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("TOTAL QUOTATIONS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','sent']]],
            search_view_id: self.sale_data.sale_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_month_quotations: function(event) {
        var self = this;
        var date = new Date();
        var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        var fday = firstDay.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("THIS MONTH QUOTATIONS"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','sent']],
            		 ['date_order','>', fday],
            		 ['date_order','<', lday]
            		 ],
            search_view_id: self.sale_data.sale_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_due_1_month: function(event) {
    	var self = this;
        var date = new Date();
        var lastDay = new Date(date.getFullYear(), date.getMonth() - 1, 0);
        var fday = date.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Due for Last 1month"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','open','paid']],
            		 ['date_due','<=', fday],
            		 ['date_due','>=', lday],
            		 ['type','=','out_invoice']
            		 ],
            search_view_id: self.sale_data.invoice_search_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_due_3_month: function(event) {
    	var self = this;
        var date = new Date();
        var lastDay = new Date(date.getFullYear(), date.getMonth() - 3, 0);
        var fday = date.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Due For Last 3 Months"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','open','paid']],
            		 ['date_due','<=', fday],
            		 ['date_due','>=', lday],
            		 ['type','=','out_invoice']
            		 ],
            search_view_id: self.sale_data.invoice_search_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_due_6_month: function(event) {
    	var self = this;
        var date = new Date();
        var lastDay = new Date(date.getFullYear(),date.getMonth() - 6, 0);
        var fday = date.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Over Due"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['open']],
            		 ['date_due','<=', fday],
            		 ['date_due','>=', lday],
            		 ['type','=','out_invoice']
            		 ],
            search_view_id: self.sale_data.invoice_search_id,
            context: {'create':false},
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_due_pending: function(event) {
        var self = this;
        var date = new Date();
        var lastDay = new Date(date.getFullYear(),date.getMonth() + 6, 0);
        var fday = date.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Due"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['open']],
                     ['date_due','>=', fday],
                     ['date_due','<=', lday],
                     ['type','=','out_invoice']
                     ],
            search_view_id: self.sale_data.invoice_search_id,
            context: {'create':false},
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_due_today: function(event) {
    	var self = this;
        var date = new Date().toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Today Due"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            src_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','open','paid']],
            		 ['date_due','=', date],
            		 ['type','=','out_invoice']
            		 ],
            search_view_id: self.sale_data.invoice_search_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    action_to_invoice: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("TO BE INVOICED"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            src_model: 'sale.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=','sale'],
            		['invoice_status','=','to invoice']
            		],
            search_view_id: self.sale_data.sale_search_view_id,
            target: 'current',
            context: {'create':false},
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    // Here we are plotting chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#myChart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var types = ['doughnut','line','pie','bar','horizontalBar'];
        var myChart = new Chart(ctx, {
            type: types[Math.floor(Math.random()*5)],
            data: {
                 //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                 //"October", "November", "December"],
                 labels: self.sale_data.sale_label,
                datasets: [{
                    label: 'Sales Graph',
                    data: self.sale_data.sale_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]

            },
            
        });
        var piectx = this.$el.find('#salepieChart');
        var pieChart = new Chart(piectx, {
            type: 'line',
            data: {
                 //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                 //"October", "November", "December"],
                 labels: self.sale_data.prod_label,
                datasets: [{
                    label: 'Product Onhand',
                    data: self.sale_data.prod_count,
                    backgroundColor :['rgba(255, 99, 132, 0.2)', 
                'rgba(54, 162, 235, 0.2)', 
                'rgba(255, 206, 86, 0.2)', 
                'rgba(75, 192, 192, 0.2)', 
                'rgba(153, 102, 255, 0.2)', 
                'rgba(255, 159, 64, 0.2)' 
], 
                    borderColor: [ 
                'rgba(255,99,132,1)', 
                'rgba(54, 162, 235, 1)', 
                'rgba(255, 206, 86, 1)', 
                'rgba(75, 192, 192, 1)', 
                'rgba(153, 102, 255, 1)', 
                'rgba(255, 159, 64, 1)' 
            ], 
                    //borderColor: bg_color_list,
                    //barPercentage: 0.5,
        //barThickness: 6,
        //maxBarThickness: 8,
        //minBarLength: 2,
                    pointStyle: 'rectRounded',
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.sale_data.prod_count),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.sale_data.
                            prod_count.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.sale_data.prod_count.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black',
                    }
                },
            },
        });
    


        //Pie Chart
       /** var piectx = this.$el.find('#salepieChart');
        bg_color_list = []
        for (var i=0;i<=self.sale_data.sale_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: self.sale_data.sale_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Sale Pie'
                }],
                labels:self.sale_data.sale_label,
            },
            options: {
                responsive: true
            }
        });*/
        

    },

    //stock product charts
    render_dashboards: function() {
        alert('hjhsh');
           
            var self = this;
            _.each(this.dashboards_templates, function() {
                self._rpc({
                    model: 'sale.dashboard',
                    method: 'get_info_data',
                    args:[],
                                })
            .then(
             function(){          
                    console.log('sgh')
                     google.charts.load('current', {'packages':['corechart']});
                     google.charts.setOnLoadCallback(drawChart);
           
                    function drawChartss() {
                            console.log('enter');
                           var data = google.visualization.arrayToDataTable([
               ['Year', 'Asia', { role: 'annotation'} ,'Europe', { role: 'annotation'}],
               ['2012',  900,'900',      390, '390'],
               ['2013',  1000,'1000',      400,'400'],
               ['2014',  1170,'1170',      440,'440'],
               ['2015',  1250,'1250',       480,'480'],
               ['2016',  1530,'1530',      540,'540']
            ]);

            var options = {title: 'Population (in millions)', isStacked:'percent'};  

            // Instantiate and draw the chart.
            var chart = new google.visualization.BarChart(document.getElementById('container'));
            chart.draw(data, options);
                                };
                                
                    
                           //  setInterval(function(){self.render_dashboards();}, 1000);
                //}
                      self.$('.chart-pie').append(QWeb.render(template, {widget: self,values: result}));
                    
             });
        });
                     
          //  });
       },


    previewTable: function() {
        $('#emp_details').DataTable( {
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Employee Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },
                {
                    extend: 'print',
                    exportOptions: {
                    columns: ':visible'
                    }
                },
            'colvis'
            ],
            columnDefs: [ {
                targets: -1,
                visible: false
            } ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 15,
        } );
    },
    generate_sale_pdf: function(chart) {
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#salepieChart');
        }
        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('sale_report.pdf');
    },


});
core.action_registry.add('mapol_sale_dashboard.sale_dashboard', DashboardView);
return DashboardView
});
