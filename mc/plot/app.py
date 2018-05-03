from bokeh.io import curdoc
from bokeh.plotting import figure 
from bokeh.transform import dodge
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource, ranges, LabelSet
from bokeh.models import DatetimeTickFormatter

from datetime import datetime
from utils import *

formatter = DatetimeTickFormatter(
	hours=["%H:%M:%S"],
	minutes=["%H:%M:%S"],
	minsec=["%H:%M:%S"],
	seconds=["H:%M:%S"]
)

# Plot Temperature
sourceTemp = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figTemp = figure(x_axis_type="datetime", plot_width=1000, plot_height=500,
			x_axis_label = "@timestamp per 30 seconds", y_axis_label = "NUMA Node Temperature",
			y_range=(-5, 40), title="Temperature", tools=TOOLS)

figTemp.circle_cross(source=sourceTemp, x="x", y="trident1", legend=value("trident1"), size=7, alpha=.85, color="peru")
figTemp.line(source=sourceTemp, x="x", y="trident1", legend=value("trident1"), alpha=.85, color="peru")

figTemp.asterisk(source=sourceTemp, x="x", y="trident2", legend=value("trident2"), size=7, alpha=.85, color="blue")
figTemp.line(source=sourceTemp, x="x", y="trident2", legend=value("trident2"), alpha=.85, color="blue")

figTemp.inverted_triangle(source=sourceTemp, x="x", y="trident3", legend=value("trident3"), size=7, alpha=.85, color="red")
figTemp.line(source=sourceTemp, x="x", y="trident3", legend=value("trident3"), alpha=.85, color="red")

figTemp.xaxis.formatter = formatter
figTemp.legend.orientation = "horizontal"
figTemp.legend.location = "top_left"

# Plot VMs Numbers
sourceVms = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figVms = figure(x_axis_type="datetime", plot_width=1000, plot_height=400,
			x_axis_label = "@timestamp per 30 seconds", y_axis_label = "VM numbers",
			y_range=(-5, 32), title="Number Of VMs", tools=TOOLS)

figVms.circle_cross(source=sourceVms, x="x", y="trident1", legend=value("trident1"), size=7, alpha=.85, color="peru")
figVms.line(source=sourceVms, x="x", y="trident1", legend=value("trident1"), alpha=.85, color="peru")

figVms.asterisk(source=sourceVms, x="x", y="trident2", legend=value("trident2"), size=7, alpha=.85, color="blue")
figVms.line(source=sourceVms, x="x", y="trident2", legend=value("trident2"), alpha=.85, color="blue")

figVms.inverted_triangle(source=sourceVms, x="x", y="trident3", legend=value("trident3"), size=7, alpha=.85, color="red")
figVms.line(source=sourceVms, x="x", y="trident3", legend=value("trident3"), alpha=.85, color="red")

figVms.xaxis.formatter = formatter
figVms.legend.orientation = "horizontal"
figVms.legend.location = "top_left"

# Plot VM Loads
# https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html
loads = ['25', '50', '75', '100']
data = {
	'loads'    : loads,
    'trident1' : [0, 0, 0, 0],
    'trident2' : [0, 0, 0, 0],
    'trident3' : [0, 0, 0, 0]
}
sourceLoads = ColumnDataSource(data=data)
figLoads = figure(x_range=loads, y_range=(0, 20), 
			plot_width=1000, plot_height=400, 
			x_axis_label = "CPU Load (%)", y_axis_label = "Number of Loads",
			title="VM Load Count", tools=TOOLS)

tr1labels = LabelSet(x=dodge('loads', -0.25, range=figLoads.x_range), y='trident1', text='trident1', level='glyph',
        x_offset=5, y_offset=0, source=sourceLoads, render_mode='canvas')
figLoads.add_layout(tr1labels)
figLoads.vbar(x=dodge('loads', -0.25, range=figLoads.x_range), top='trident1', 
			width=0.2, source=sourceLoads, color="peru", legend=value("trident1"))

tr2labels = LabelSet(x=dodge('loads', -0.25, range=figLoads.x_range), y='trident2', text='trident2', level='glyph',
        x_offset=47, y_offset=0, source=sourceLoads, render_mode='canvas')
figLoads.add_layout(tr2labels)
figLoads.vbar(x=dodge('loads',  0.0,  range=figLoads.x_range), top='trident2', 
			width=0.2, source=sourceLoads, color="blue", legend=value("trident2"))

tr3labels = LabelSet(x=dodge('loads', -0.25, range=figLoads.x_range), y='trident3', text='trident3', level='glyph',
        x_offset=89, y_offset=0, source=sourceLoads, render_mode='canvas')
figLoads.add_layout(tr3labels)
figLoads.vbar(x=dodge('loads',  0.25, range=figLoads.x_range), top='trident3', 
			width=0.2, source=sourceLoads, color="red", legend=value("trident3"))

figLoads.x_range.range_padding = 0.1
figLoads.xgrid.grid_line_color = None
figLoads.legend.location = "top_left"
figLoads.legend.orientation = "horizontal"			

# Periodic callback
def update():
	print("------------------------ Update -------------------")
	
	# Request data
	data = getPlotData()
	
	if data:
		# x-axis data
		x = datetime.now()

		# Update Temperature
		trident1Temp = data["trident1.vlab.cs.hioa.no"]["hostTemp"] if "trident1.vlab.cs.hioa.no" in data else 0.0
		trident2Temp = data["trident2.vlab.cs.hioa.no"]["hostTemp"] if "trident2.vlab.cs.hioa.no" in data else 0.0
		trident3Temp = data["trident3.vlab.cs.hioa.no"]["hostTemp"] if "trident3.vlab.cs.hioa.no" in data else 0.0

		temp_data = dict(x=[x], trident1=[trident1Temp], trident2=[trident2Temp], trident3=[trident3Temp])
		sourceTemp.stream(temp_data, rollover=200)

		# Update VMs Number
		trident1numVms = data["trident1.vlab.cs.hioa.no"]["numVms"] if "trident1.vlab.cs.hioa.no" in data else 0	
		trident2numVms = data["trident2.vlab.cs.hioa.no"]["numVms"] if "trident2.vlab.cs.hioa.no" in data else 0
		trident3numVms = data["trident3.vlab.cs.hioa.no"]["numVms"] if "trident3.vlab.cs.hioa.no" in data else 0
		
		vms_data = dict(x=[x], trident1=[trident1numVms], trident2=[trident2numVms], trident3=[trident3numVms])
		sourceVms.stream(vms_data, rollover=200)

		# Update VM loads
		trident1VMloads = data["trident1.vlab.cs.hioa.no"]["vmLoads"] if "trident1.vlab.cs.hioa.no" in data else SERVER_PLOT_DATA["vmLoads"]	
		trident2VMloads = data["trident2.vlab.cs.hioa.no"]["vmLoads"] if "trident2.vlab.cs.hioa.no" in data else SERVER_PLOT_DATA["vmLoads"]
		trident3VMloads = data["trident3.vlab.cs.hioa.no"]["vmLoads"] if "trident3.vlab.cs.hioa.no" in data else SERVER_PLOT_DATA["vmLoads"]

		load_data = {
			'loads'    : loads,
			'trident1' : [trident1VMloads["25"], trident1VMloads["50"], trident1VMloads["75"], trident1VMloads["100"]],
			'trident2' : [trident2VMloads["25"], trident2VMloads["50"], trident2VMloads["75"], trident2VMloads["100"]],
			'trident3' : [trident3VMloads["25"], trident3VMloads["50"], trident3VMloads["75"], trident3VMloads["100"]]
		}
		sourceLoads.stream(load_data, rollover=len(loads))

# Add a periodic callback to be run every 15 second
curdoc().add_root(figTemp)
curdoc().add_root(figVms)
curdoc().add_root(figLoads)
curdoc().add_periodic_callback(update, 30000)
