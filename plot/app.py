from bokeh.io import curdoc
from bokeh.plotting import figure 
from bokeh.models import ColumnDataSource

import socket
import json
from datetime import datetime
from utils import *

# Plot Temperature
sourceTemp = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figTemp = figure(x_axis_type="datetime", title="Temperature", tools=TOOLS, plot_width=800, plot_height=500)
figTemp.xaxis.axis_label = "time(sec)"
figTemp.yaxis.axis_label = "NUMA Node Temperature"
#figTemp.y_range.start = 0
#figTemp.y_range.end = 60
figTemp.circle_cross(source=sourceTemp, x="x", y="trident1", legend="tr1", size=7, alpha=.85, color="peru")
figTemp.line(source=sourceTemp, x="x", y="trident1", legend="tr1", alpha=.85, color="peru")

figTemp.asterisk(source=sourceTemp, x="x", y="trident2", legend="tr2", size=7, alpha=.85, color="blue")
figTemp.line(source=sourceTemp, x="x", y="trident2", legend="tr2", alpha=.85, color="blue")

figTemp.inverted_triangle(source=sourceTemp, x="x", y="trident3", legend="tr3", size=7, alpha=.85, color="red")
figTemp.line(source=sourceTemp, x="x", y="trident3", legend="tr3", alpha=.85, color="red")
figTemp.legend.location = "top_left"

# Plot VMs Numbers
sourceVms = ColumnDataSource(data=dict(x=[], trident1=[], trident2=[], trident3=[]))
figVms = figure(x_axis_type="datetime", title="Number Of VMs", tools=TOOLS, plot_width=800, plot_height=400)
figVms.xaxis.axis_label = "time(sec)"
figVms.yaxis.axis_label = "VM numbers"
#figVms.y_range.start = 0
#figVms.y_range.end = 60
figVms.circle_cross(source=sourceVms, x="x", y="trident1", legend="tr1", size=7, alpha=.85, color="peru")
figVms.line(source=sourceVms, x="x", y="trident1", legend="tr1", alpha=.85, color="peru")

figVms.asterisk(source=sourceVms, x="x", y="trident2", legend="tr2", size=7, alpha=.85, color="blue")
figVms.line(source=sourceVms, x="x", y="trident2", legend="tr2", alpha=.85, color="blue")

figVms.inverted_triangle(source=sourceVms, x="x", y="trident3", legend="tr3", size=7, alpha=.85, color="red")
figVms.line(source=sourceVms, x="x", y="trident3", legend="tr3", alpha=.85, color="red")
figVms.legend.location = "top_left"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 10002
def _getPlotData():
	server_message = {}

	for host, ip in SERVERS.items():
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
	
	# x-axis data
	x = datetime.now()	

	# Update Temperature
	trident1Temp = data["trident1.vlab.cs.hioa.no"]["hostTemp"] if data else 0.0
	trident2Temp = data["trident2.vlab.cs.hioa.no"]["hostTemp"] if data else 0.0
	trident3Temp = data["trident3.vlab.cs.hioa.no"]["hostTemp"] if data else 0.0

	temp_data = dict(x=[x], trident1=[trident1Temp], trident2=[trident2Temp], trident3=[trident3Temp])
	sourceTemp.stream(temp_data, rollover=100)

	# Update VMs Number
	trident1numVms = data["trident1.vlab.cs.hioa.no"]["numVms"] if data else 0.0	
	trident2numVms = data["trident2.vlab.cs.hioa.no"]["numVms"] if data else 0.0
	trident3numVms = data["trident3.vlab.cs.hioa.no"]["numVms"] if data else 0.0

	vms_data = dict(x=[x], trident1=[trident1numVms], trident2=[trident2numVms], trident3=[trident3numVms])
	sourceVms.stream(vms_data, rollover=100)

# Add a periodic callback to be run every 15 second
curdoc().add_root(figTemp)
curdoc().add_root(figVms)
curdoc().add_periodic_callback(update, 15000)
