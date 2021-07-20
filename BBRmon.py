# -*- coding: utf-8 -*-
#
# BBRMom
# Copyright (C) 2021  Marco Pizzocaro - Istituto Nazionale di Ricerca Metrologica (INRIM)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT



import pyvisa as visa
import time
from datetime import date, datetime
import os
from collections import deque

from numpy import *

from matplotlib.pyplot import *
ioff()
import matplotlib.dates as mdates


import __main__

rm = visa.ResourceManager()
instr = rm.open_resource('ASRL33::INSTR', parity=visa.constants.Parity.none, data_bits=8, stop_bits=visa.constants.StopBits.one, baud_rate=57600, flow_control=visa.constants.VI_ASRL_FLOW_NONE)
instr.query_dealy=0.1


# note the sleeps to avoid writing commands too quickly :(
instr.write('abort'); time.sleep(0.1)
instr.write('*rst'); time.sleep(0.1)
instr.write('conf:temp frtd, (@101:110)'); time.sleep(0.1) #add here new sensors
instr.write('sens:temp:tran:frtd:res 1000, (@101:110)'); time.sleep(0.1) #add here new sensors
instr.write('rout:scan (@101:110)'); time.sleep(0.1) #add here new sensors
instr.write('unit:temp c'); time.sleep(0.1)
instr.write('sens:temp:nplc 200, (@101:110)'); time.sleep(0.1) #add here new sensors
instr.write('sens:zero:auto off, (@101:110)'); time.sleep(0.1) #add here new sensors
instr.write('format:read:alarm off'); time.sleep(0.1)
instr.write('format:read:unit off'); time.sleep(0.1)
instr.write('format:read:time off'); time.sleep(0.1)
instr.write('format:read:channel off'); time.sleep(0.1)
instr.write('*ese 0'); time.sleep(0.1)




# timeto wait for new data
wait = 79.


fig, (ax1, ax2, ax3) = subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [2.5, 1., 1.]})
fig.canvas.set_window_title('BBRMon')
fig.tight_layout()
fig.subplots_adjust(right=0.75, left=0.12, bottom=0.12) 

#locator = mdates.HourLocator(interval=4)# mdates.AutoDateLocator(minticks=3, maxticks=12)
#formatter = mdates.DateFormatter('%H:%M')#mdates.ConciseDateFormatter(locator)

locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
formatter = mdates.ConciseDateFormatter(locator)

ax3.set_ylabel('Uncertainty /°C')
ax3.yaxis.set_label_coords(-0.14, 0.5)
ax3.set_xlabel('Time (UTC)')
ax3.grid()
# this is needed for every axis
ax3.xaxis.set_major_locator(locator)
ax3.xaxis.set_major_formatter(formatter)
ax3twin = ax3.twinx()
ax3twin.set_ylabel('Freq. Unc.')
ax3twin.yaxis.set_label_coords(1.14, 0.5)

ax2.set_ylabel('Average /°C')
ax2.yaxis.set_label_coords(-0.14, 0.5)
ax2.grid()
# this is needed for every axis
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)

ax2twin = ax2.twinx()
ax2twin.set_ylabel('Freq. Shift')
ax2twin.yaxis.set_label_coords(1.14, 0.5)

ax1.set_ylabel('Recorded Temp. /°C')
ax1.yaxis.set_label_coords(-0.14, 0.5)
ax1.grid()
#ax1.set_title('2019-02-07')
# this is needed for every axis
ax1.xaxis.set_major_locator(locator)
ax1.xaxis.set_major_formatter(formatter)

fig.canvas.manager.window.move(3500, 25)
fig.show()
fig.canvas.draw()


# output
path = os.path.join("..","Temperature Data")
path = path
today = date.today()

if not os.path.exists(path):
	os.makedirs(path)


# THEBUFFER
N = int(86400//wait)
tbuffer  = deque([], N)
buffer = deque([], N)
newdata = False


mlabels = ['below-north', 'below-east', 'over-east', 'over-south', 'below-south', 'below-west', 'over-west', 'over-north', 'far-from-oven', 'close-to-oven']
labels = ['#time'] + mlabels

def new_file(today):
	filo_name = os.path.join(path, str(today) + '.dat')
	# later in with
	filo = open(filo_name, 'a')
	
	# file out
	filo.write("# File generated on: " + str(datetime.now()) + "\n")		
	filo.write('# By the program: ' +  os.path.basename(__main__.__file__) + '\n')
	#filo.write("# Version: " +  __version__ + '\n')
	filo.write('# Temperatures / degree C \n')
	
	header= '\t'.join(labels)
	filo.writelines([header + '\n'])
	
	return filo

filo = new_file(today)



fYb = 518295836590863.6



# preliminary BBR setup
# =====================

alpha = 3.62612e-6# ufloat(3.62612,0.00007, 'alpha')*1e-6 # Hz/(V/m) from sherman2012
eta1 = 0.01745 #ufloat(0.01745, 0.00038, 'eta1')	# from Beloy2014
eta2 = 0.000593 #ufloat(0.000593, 0.000016, 'eta2')
sigma = 8.319430e2 # ufloat(8.319430, 0.000015, 'sigma')*1e2 # V/m 



def eta(T):
	return eta1*(T/300.)**2 + eta2*(T/300.)**4

def bbr(T):
	T = T+273.15
	dn = -0.5*alpha*sigma**2*(T/300.)**4*(1+eta(T))
	return dn/fYb

def bbrdelta(T, u):
	return (bbr(T-u)-bbr(T+u))/2


is_running = True

# clear the buffer (?)
try:
	temp = instr.query_ascii_values('fetc?', container=array)
except visa.errors.VisaIOError:
	pass


while is_running:
	try:
		instr.write('init')
	except visa.errors.VisaIOError:
		print('Failed to init. Retrying.')
		continue
	
	t0 = time.time()
	while time.time() < t0 + wait:
		if not fignum_exists(1):
			break
		pause(0.2) # this is plt.pause -- time.sleep() does not work because it is blocking and messes up with the live plot
		#time.sleep(0.2)
	
	if not fignum_exists(1):
		break

	try:
		temp = instr.query_ascii_values('fetc?', container=array)
	except visa.errors.VisaIOError:
		print('Cannot read temp. Continuing.')
		continue
	
	if temp.size != 10:
		print('No data. Continuing.')
		continue
	
	t = time.time()
		
	tbuffer.append(t)
	buffer.append(temp)
		
	fmt = "{:.3f}\t"*10 #number of sensors
	tempstring = "{:.3f}\t".format(t) + fmt.format(*temp)
	#print(temp)
	if filo:
		filo.writelines(tempstring + '\n')
		# force the buffer to be written to disk
		filo.flush()
		os.fsync(filo.fileno())
		print(tempstring)


			
	# inspired by pyablab.scope
	# extract all data in buffer in a fast way (with a temprary conversion in list)
	# and with a proper shape (see later)
	data = list(buffer)			
	data = array(data).T
	tt = list(tbuffer)
	tt = array(tt).astype('datetime64[s]')


	Tmax = amax(data, axis=0)
	Tmin = amin(data, axis=0)
	T = (Tmax+Tmin)/2
	uncT = (Tmax-Tmin)/sqrt(12.)
	uncT = sqrt(uncT**2+0.21**2) # add thermistors accuracy
	meanT = mean(T)

	if fignum_exists(1):
		if ax1.lines:
			for l, y in zip(ax1.lines, data):
				l.set_xdata(tt)
				l.set_ydata(y)
				
			if ax1.lines:
				# set autoscale from new data!!!
				ax1.relim()
				ax1.autoscale_view(tight=True)
				
		else:
			ax1.plot(tt, data.T)
			ax1.legend(labels= mlabels, loc='upper left', bbox_to_anchor=(1.02, 1),  bbox_transform=ax1.transAxes, fontsize=9)

		
		if ax2.lines:
			for l, y in zip(ax2.lines, [T+uncT,T-uncT,T]):
				l.set_xdata(tt)
				l.set_ydata(y)
				
			if ax2.lines:
				# set autoscale from new data!!!
				ax2.relim()
				ax2.autoscale_view()
				
			
		else:
			ax2.plot(tt, T+uncT, color='C0')
			ax2.plot(tt, T-uncT, color='C0')
			ax2.plot(tt, T, color='C1')
			
		xmin, xmax = ax2.get_ylim()
		ax2twin.set_ylim((bbr(xmin),bbr(xmax)))


		if ax3.lines:
				for l, y in zip(ax3.lines, [uncT]):
					l.set_xdata(tt)
					l.set_ydata(y)
				if ax3.lines:
					# set autoscale from new data!!!
					ax3.relim()
					ax3.autoscale_view()
		else:
			ax3.plot(tt, uncT)
			
		xmin, xmax = ax3.get_ylim()
		ax3twin.set_ylim(bbrdelta(meanT, xmin), bbrdelta(meanT, xmax))


		fig.canvas.draw()
	else:
		break
			
	if date.today() != today:
		fig.savefig(filo.name[:-3] + 'png')
		filo.close()
		today = date.today()
		filo = new_file(today)
	
		
print('Closing BBRMon. Goodbye.')
fig.savefig(filo.name[:-3] + 'png')
is_running = False
filo.close()
instr.close()





