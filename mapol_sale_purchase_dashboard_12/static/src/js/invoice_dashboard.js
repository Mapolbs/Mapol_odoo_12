odoo.define('invoice_homepage', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var session = require('web.session');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
//var NotificationManager = require('web.notification').NotificationManager;
var rpc = require('web.rpc');

var _t = core._t;
var QWeb = core.qweb;



var DashboardView = AbstractAction.extend(ControlPanelMixin, {
	template: "mapol_sale_purchase_dashboard_12.HomePage",
    searchview_hidden: true,
    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['mapol_sale_purchase_dashboard_12.invoice'];
    },
    
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dashboards();
        });
    },
    render_dashboards: function() {
    		var team =localStorage.getItem("team");
			var self = this;
	        _.each(this.dashboards_templates, function(template) {
	        	
	        	self._rpc({
		    	    model: 'account.invoice',
		    	    method: 'get_info',
		    	    args:[team],
		    	    	    	})    
    		.then(
		     function(result){ 	    	
	        	     
	            	 google.charts.load('current', {'packages':['corechart']});
	                 google.charts.setOnLoadCallback(drawChart);
					function drawChart() {
	                 var data = google.visualization.arrayToDataTable([
					  ['Task', 'Hours per Day'],
					  ['Work', 8],
					  ['Eat', 2],
					  ['TV', 4],
					  ['Gym', 2],
					  ['Sleep', 8],
					  ['Game',5]
					]);
					
					  var options = {'title':'My Average Day', 'width':600, 'height':400, is3D: true,};
					
					  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
					  var charts = new google.visualization.PieChart(document.getElementById('piechart_3d'));
					  chart.draw(data, options);
					  charts.draw(data, options);
					  }
					  self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result}));
		     });
	                 
	        });
	    }
});
core.action_registry.add('invoice_homepage', DashboardView);
return DashboardView
});
