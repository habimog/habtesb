from bokeh.io import curdoc
from bokeh.plotting import figure 
from bokeh.models import ColumnDataSource

import socket
import json
from datetime import datetime
from copy import deepcopy
from utils import *

# Plot Temperature
sourceTemp = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figTemp = figure(x_axis_type="datetime", title="Temperature", tools=TOOLS, plot_width=1500, plot_height=500)
figTemp.xaxis.axis_label = "time(min)"
figTemp.yaxis.axis_label = "NUMA Node Temperature"
figTemp.y_range.start = -5
figTemp.y_range.end = 50
figTemp.circle_cross(source=sourceTemp, x="x", y="trident1", legend="tr1", size=7, alpha=.85, color="peru")
figTemp.line(source=sourceTemp, x="x", y="trident1", legend="tr1", alpha=.85, color="peru")

figTemp.asterisk(source=sourceTemp, x="x", y="trident2", legend="tr2", size=7, alpha=.85, color="blue")
figTemp.line(source=sourceTemp, x="x", y="trident2", legend="tr2", alpha=.85, color="blue")

figTemp.inverted_triangle(source=sourceTemp, x="x", y="trident3", legend="tr3", size=7, alpha=.85, color="red")
figTemp.line(source=sourceTemp, x="x", y="trident3", legend="tr3", alpha=.85, color="red")
figTemp.legend.location = "top_left"

# Plot VMs Numbers
sourceVms = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figVms = figure(x_axis_type="datetime", title="Number Of VMs", tools=TOOLS, plot_width=1500, plot_height=400)
figVms.xaxis.axis_label = "time(min)"
figVms.yaxis.axis_label = "VM numbers"
figVms.y_range.start = -5
figVms.y_range.end = 35
figVms.circle_cross(source=sourceVms, x="x", y="trident1", legend="tr1", size=7, alpha=.85, color="peru")
figVms.line(source=sourceVms, x="x", y="trident1", legend="tr1", alpha=.85, color="peru")

figVms.asterisk(source=sourceVms, x="x", y="trident2", legend="tr2", size=7, alpha=.85, color="blue")
figVms.line(source=sourceVms, x="x", y="trident2", legend="tr2", alpha=.85, color="blue")

figVms.inverted_triangle(source=sourceVms, x="x", y="trident3", legend="tr3", size=7, alpha=.85, color="red")
figVms.line(source=sourceVms, x="x", y="trident3", legend="tr3", alpha=.85, color="red")
figVms.legend.location = "top_left"

# Plot VM Loads
loads = ['25%', '50%', '75%', '100%']
figLoads = figure(x_range=loads, plot_width=1500, plot_height=400, title="VM Load Count")
figLoads.vbar(x=loads, top=[0, 0, 0, 0], width=0.5)
figLoads.xgrid.grid_line_color = None
figLoads.xaxis.axis_label = "CPU Load (%)"
figLoads.yaxis.axis_label = "Number of Loads"
figLoads.y_range.start = 0

# Get Plot Data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 10002
def _getPlotData():
	server_message = {}
	for host, ip in SERVERS.items():
		server_message[host] = deepcopy(SERVER_PLOT_DATA)
		try:
			# Request server plot data 
			sock.sendto(json.dumps(SERVER_PLOT_DATA).encode('utf-8'), (ip, port))
			print("sent server plot data request to {}".format((ip, port)))

			# Receive response
			print("waiting to receive")
			sock.settimeout(5.0)
			data, address = sock.recvfrom(512)
			sock.settimeout(None)
			server_message[host] = json.loads(data.decode('utf-8'))
			print("received: {} from {}".format(server_message[host], address))
		except:
			print("Socket timeout for {}".format((ip, port)))

	return server_message
			

def update():
	print("------------------------ Update -------------------")
	
	# Request data
	data = _getPlotData()
	
	if data:
		# x-axis data
		x = datetime.now()	

		# Update Temperature
		trident1Temp = data["trident1.vlab.cs.hioa.no"]["hostTemp"] if "trident1.vlab.cs.hioa.no" in data else 0.0
		trident2Temp = data["trident2.vlab.cs.hioa.no"]["hostTemp"] if "trident2.vlab.cs.hioa.no" in data else 0.0
		trident3Temp = data["trident3.vlab.cs.hioa.no"]["hostTemp"] if "trident3.vlab.cs.hioa.no" in data else 0.0

		temp_data = dict(x=[x], trident1=[trident1Temp], trident2=[trident2Temp], trident3=[trident3Temp])
		sourceTemp.stream(temp_data, rollover=1000)

		# Update VMs Number
		trident1numVms = data["trident1.vlab.cs.hioa.no"]["numVms"] if "trident1.vlab.cs.hioa.no" in data else 0.0	
		trident2numVms = data["trident2.vlab.cs.hioa.no"]["numVms"] if "trident2.vlab.cs.hioa.no" in data else 0.0
		trident3numVms = data["trident3.vlab.cs.hioa.no"]["numVms"] if "trident3.vlab.cs.hioa.no" in data else 0.0
		
		vms_data = dict(x=[x], trident1=[trident1numVms], trident2=[trident2numVms], trident3=[trident3numVms])
		sourceVms.stream(vms_data, rollover=1000)

		# Update VM loads
		trident1VMloads = data["trident1.vlab.cs.hioa.no"]["vmLoads"] if "trident1.vlab.cs.hioa.no" in data else 0	
		trident2VMloads = data["trident2.vlab.cs.hioa.no"]["vmLoads"] if "trident2.vlab.cs.hioa.no" in data else 0
		trident3VMloads = data["trident3.vlab.cs.hioa.no"]["vmLoads"] if "trident3.vlab.cs.hioa.no" in data else 0

		vmLoads = {}
		vmLoads["25"] = trident1VMloads["25"] + trident2VMloads["25"] + trident3VMloads["25"]
		vmLoads["50"] = trident1VMloads["50"] + trident2VMloads["50"] + trident3VMloads["50"]
		vmLoads["75"] = trident1VMloads["75"] + trident2VMloads["75"] + trident3VMloads["75"]
		vmLoads["100"] = trident1VMloads["100"] + trident2VMloads["100"] + trident3VMloads["100"]

		figLoads.vbar(x=loads, top=[vmLoads["25"], vmLoads["50"], vmLoads["75"], vmLoads["100"]], width=0.5)

# Add a periodic callback to be run every 15 second
curdoc().add_root(figTemp)
curdoc().add_root(figVms)
curdoc().add_root(figLoads)
curdoc().add_periodic_callback(update, 15000)
