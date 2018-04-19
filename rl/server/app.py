from bokeh.io import curdoc
from bokeh.plotting import figure 
from bokeh.models import ColumnDataSource

import sys
from datetime import datetime
from utils import *

TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"
SERVER_COLOR = {
	"trident1" : "peru",
	"trident2" : "blue",
	"trident3" : "red"
}

# Plot Temperature
host = getHostName().split(".")[0]
sourceTemp = ColumnDataSource(data=dict(x=[], y=[]))
figTemp = figure(x_axis_type="datetime", title="%s Temperature"%(host), tools=TOOLS, plot_width=600, plot_height=500)
figTemp.xaxis.axis_label = "time(sec)"
figTemp.yaxis.axis_label = "NUMA Node Temperature"
figTemp.y_range.start = 0
figTemp.y_range.end = 60
figTemp.line(source=sourceTemp, x="x", y="y", line_width=2, alpha=.85, color=SERVER_COLOR[host])

# Plot VMs Numbers
sourceVms = ColumnDataSource(data=dict(x=[], y=[]))
figVms = figure(x_axis_type="datetime", title="%s Number Of VMs"%(host), tools=TOOLS, plot_width=600, plot_height=300)
figVms.xaxis.axis_label = "time(sec)"
figVms.yaxis.axis_label = "VM numbers"
figVms.y_range.start = 0
figVms.y_range.end = 60
figVms.line(source=sourceVms, x="x", y="y", line_width=2, alpha=.85, color=SERVER_COLOR[host])

# Get calibration temperature
calibrationTemp = float(sys.argv[1]) #calibrate.Calibrate(600).getCalibrationTemp()

def update():
	x = datetime.now()	

	# Update Temperature
	temp = getHostTemp() - calibrationTemp
	numaNode = getNumberOfNodes()
	nodeTemp = temp/numaNode if temp >= 0 else 0
	temp_data = dict(x=[x], y=[nodeTemp])
	sourceTemp.stream(temp_data, rollover=100)

	# Update Temperature
	numVms = getNumberOfVms()
	vms_data = dict(x=[x], y=[numVms])
	sourceVms.stream(vms_data, rollover=100)

# Add a periodic callback to be run every 1 second
curdoc().add_root(figTemp)
curdoc().add_root(figVms)
curdoc().add_periodic_callback(update, 1000)
