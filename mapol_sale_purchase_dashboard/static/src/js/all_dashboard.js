odoo.define('mapol_sale_purchase_dashboard.dashboard', function (require) {
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
		//purchase dashboard events
    	'click .rfq-count': 'action_rfq_count',
    	'click .purchase-count': 'action_purchase_count',
    	'click .month-shipments': 'action_get_month_shipments',
    	'click .shipments': 'action_get_shipments',
    	//pdf
    	'click #generate_purchase_pdf': function(){this.generate_purchase_pdf("bar");},
    	'click #generate_purchase_pie_pdf': function(){this.generate_purchase_pdf("pie")},
	},
	init: function(parent, context) {
        this._super(parent, context);
        var data = [];
        var self = this;
        if (context.tag == 'mapol_sale_purchase_dashboard.dashboard') {
            self._rpc({
                model: 'all.dashboard',
                method: 'get_info',
            }, []).then(function(result){
                self.data = result[0]
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
        var all_dashboard = QWeb.render( 'mapol_sale_purchase_dashboard.dashboard', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(all_dashboard).prependTo(self.$el);
        self.graph();
        return all_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },
    //purchase event action
    action_rfq_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Purchase Requests Quotation"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            src_model: 'purchase.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['draft','sent','to approve']]],
            search_view_id: self.data.purchase_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_purchase_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("Total Purchase Orders"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            src_model: 'purchase.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','in',['purchase','done']]],
            search_view_id: self.data.purchase_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_get_month_shipments: function(event) {
        var self = this;
        var date = new Date();
    	//var s = date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate() + " " +  date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
        var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        var fday = firstDay.toJSON().slice(0,10).replace(/-/g,'-');
        var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("THIS MONTH INCOMING SHIPMENTS"),
            type: 'ir.actions.act_window',
            res_model: 'stock.picking',
            src_model: 'purchase.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['picking_type_id.code','=','incoming'],
            		 ['origin','ilike','PO'],
            		 ['scheduled_date','>', fday],
            		 ['scheduled_date','<', lday]
            		 //['scheduled_date','&gt;=',[self.data.today_datetime]],
            		 ],
            search_view_id: self.data.shipments_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_get_shipments: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return self.do_action({
            name: _t("PENDING SHIPMENTS"),
            type: 'ir.actions.act_window',
            res_model: 'stock.picking',
            src_model: 'purchase.order',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {'search_default_origin': [self.data.name],
                    'default_origin': self.data.name,
                    },
            domain: [['picking_type_id.code','=','incoming'],
            		 ['state','not in',['done','cancel']],
            		 ['origin','ilike','PO']],
            search_view_id: self.data.shipments_search_view_id,
            target: 'current'
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
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                 labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                 "October", "November", "December"],
                 labels: self.data.purchase_label,
                datasets: [{
                    label: 'Purchase Graph',
                    data: self.data.purchase_dataset,
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
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.data.purchase_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.data.
                            purchase_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.data.purchase_dataset.length
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
                        fontColor: 'black'
                    }
                },
            },
        });
        
        //Pie Chart
        var piectx = this.$el.find('#pieChart');
        bg_color_list = []
        for (var i=0;i<=self.data.purchase_dataset.length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.data.purchase_dataset,
                    backgroundColor: bg_color_list,
                    label: 'Purchase Pie'
                }],
                labels:self.data.purchase_label,
            },
            options: {
                responsive: true
            }
        });
        

    },
    generate_purchase_pdf: function(chart) {
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChart');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#pieChart');
        }
        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('purchase_report.pdf');
    },


});
core.action_registry.add('mapol_sale_purchase_dashboard.dashboard', DashboardView);
return DashboardView
});
