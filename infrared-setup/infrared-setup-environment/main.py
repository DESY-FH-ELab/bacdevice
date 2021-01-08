#!/usr/bin/env python3

# Main program to broadcast data points to the DESY BACNet
# --------------------------------------------------------

# running bokeh server:
# bokeh serve cabinet-monitor --address fhlcleangate.desy.de --port 5002 --allow-websocket-origin=fhlcleangate.desy.de:5002

import sys
import pathlib
import os
from os import path

pwd = str(pathlib.Path().absolute())
wd = pwd
proj_name = pwd.split('/')[-1]
if proj_name != 'bacdevice':
    wd = pwd+'/..'
sys.path.append(wd)

logsdir = wd+'/logs'


import configparser
from sys import exit, version_info
import threading
import time
import pytz
from uuid import getnode

import csv
import sys
from datetime import datetime
from datetime import date
import time
from collections import OrderedDict
from math import pi

from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
from bokeh.models import DatetimeTickFormatter
from bokeh.models.widgets import Div,PreText
from bokeh.layouts import column,row
from bokeh.application.handlers.directory import DirectoryHandler

from bokeh.layouts import gridplot
from bokeh.models import CheckboxGroup
from bokeh.models import Slider
from bokeh.models import TextInput
from bokeh.models import DatePicker

from bokeh.models import Button

import random

import pandas as pd
import numpy as np

global periodic_callback_id

def initial_date(attr,old,new):
    date_picker_i.value = new

def final_date(attr,old,new):
    date_picker_f.value = new

def get_history():
    sdata = {}
    sel_data = {}
    for l in location:
        sdata[sensor[l]] = pd.read_hdf('/home/walsh/data/infrared-setup/raspberryX.h5', sensor[l].replace('-','_'))
        last_ts = sdata[sensor[l]].iloc[-1].name
        first_ts = sdata[sensor[l]].iloc[0].name
        first_ts = last_ts-72*3600
        sel_data[l] = sdata[sensor[l]].loc[first_ts:last_ts]
        
        sdates = [datetime.fromtimestamp(ts) for ts in list(seldata[l].index)]
        for key in observables:
            ds[l][key].data = {'x':sdates, 'y':list(seldata[l][key])}
            ds[l][key].trigger('data', ds[l][key].data, ds[l][key].data)


@linear()
def update(step):
    readdata()

def readdata():
    sdata = {}
    sel_data = {}
    for l in location:
        mycsv = '{0}/{1}.csv'.format(directory,sensor[l])
        if not path.exists(mycsv):
            continue
            
        sdata[sensor[l]] = pd.read_csv(mycsv,names=("datetime","temperature","pressure","humidity"),parse_dates=[0],infer_datetime_format=True)
        # select only every n-th row
#        sdata[sensor[l]] = sdata[sensor[l]].iloc[::50, :]
        # convert datetime to unix timestamp (FIXME: check timezone)
        sdata[sensor[l]]["timestamp"] = pd.DatetimeIndex ( sdata[sensor[l]]["datetime"] ).astype ( np.int64 )/1000000000
        sdata[sensor[l]]["timestamp"] = sdata[sensor[l]]["timestamp"].astype(int)
        sdata[sensor[l]].set_index("timestamp",inplace=True)
        
        # remove possible duplicates (not sure why there are duplicates)
        sdata[sensor[l]] = sdata[sensor[l]].loc[~sdata[sensor[l]].index.duplicated(keep='first')]
        # reindex
        sdata[sensor[l]] = sdata[sensor[l]].sort_index()
 
## MOVED TO INITIALDATA        
#         # index of the last timestamp
# #        last_ts = sdata[sensor[l]].iloc[-1].name
#         now_ts = int(time.time())
#         last_idx = sdata[sensor[l]].index.get_loc(now_ts, method='nearest')
#         last_ts = sdata[sensor[l]].iloc[last_idx].name
#         if now_ts-last_ts > max_hours*3600:
#             continue
#             
#         # get the nearest index max_hours before
#         first_idx = sdata[sensor[l]].index.get_loc(last_ts-max_hours*3600, method='nearest')
#         # get the first timestamp
#         first_ts = sdata[sensor[l]].iloc[first_idx].name
#         # get selected data
#         sel_data[l] = sdata[sensor[l]].loc[first_ts:last_ts]
        
        sel_data[l] = sdata[sensor[l]]
        
    return sel_data


def initialdata():
    # FIXME: check if alldata is available, otherwise readdata
    sel_data = {}
    for l in location:
        now_ts = int(time.time())
        last_idx = alldata[l].index.get_loc(now_ts, method='nearest')
        last_ts = alldata[l].iloc[last_idx].name
        if now_ts-last_ts > max_hours*3600:
            continue
            
        # get the nearest index max_hours before
        first_idx = alldata[l].index.get_loc(last_ts-max_hours*3600, method='nearest')
        # get the first timestamp
        first_ts = alldata[l].iloc[first_idx].name
        # get selected data
        sel_data[l] = alldata[l].loc[first_ts:last_ts]
        
    return sel_data
        

def main () :
    print('This is a bokeh server application')

### GLOBAL ###

if __name__ == "__main__" :
    main ()
    
elif __name__.startswith('bokeh_app') or __name__.startswith('bk_script'):
    # name starts with bk_script (__name__ = bk_script_<some number>)
    
    # read data from the files
    directory = '/home/walsh/data/infrared-setup'

    max_hours = 36
    plot = {}
    r = {}
    ds = {}
    color = {}
    sensor = {}
    # FIX ME! Need more colors
    colors = ['firebrick','navy','green','lightblue','magenta','lightgreen','red','blue','black']
    sensors = ['raspberry7_bus1_ch1','raspberry7_bus4_ch1','raspberry7_bus5_ch1','raspberry7_bus6_ch1','raspberry8_bus1_ch1','raspberry8_bus4_ch1','raspberry8_bus5_ch1','raspberry8_bus6_ch1','raspberry9_bus1_ch1']
    location = ['sensor #1','sensor #2','sensor #3','sensor #4','sensor #5','sensor #6','sensor #7','sensor #8','ref sensor']
    observables = ['temperature','pressure','humidity']
    for i, l in enumerate(location):
        color[l] = colors[i]
        sensor[l] = sensors[i]
        r[l]  = {}
        ds[l] = {}
        
    alldata = readdata()
    inidata = initialdata()
    print(inidata)
        
    plot[observables[0]] = figure(plot_width=500, plot_height=500,x_axis_type="datetime",toolbar_location="above")
    plot[observables[1]] = figure(plot_width=500, plot_height=500,x_axis_type="datetime",x_range=plot[observables[0]].x_range,toolbar_location="above")
    plot[observables[2]] = figure(plot_width=500, plot_height=500,x_axis_type="datetime",x_range=plot[observables[0]].x_range,toolbar_location="above")
    date_format = ['%d %b %Y %H:%M:%S']
    for key, p in plot.items():
        p.xaxis.formatter=DatetimeTickFormatter(
               microseconds=date_format,
               milliseconds=date_format,
               seconds=date_format,
               minsec=date_format,
               minutes=date_format,
               hourmin=date_format,
               hours=date_format,
               days=date_format,
               months=date_format,
               years=date_format
              )
        p.xaxis.major_label_orientation = pi/3
        p.xaxis.axis_label = "Local time"

        for l in location:
            try:
                sdates = [datetime.fromtimestamp(ts) for ts in list(inidata[l].index)]
            except KeyError as e:
                continue
            #r[l][key] = p.line(sdates, list(inidata[l][key]), color=color[l], line_width=2,legend_label=l)
            r[l][key] = p.circle(sdates, list(inidata[l][key]), fill_color=color[l], line_color=color[l], size=3,legend_label=l)
            ds[l][key] = r[l][key].data_source
        p.legend.location = "top_left"
        p.legend.orientation = "vertical"
        p.legend.click_policy="hide"

        

    plot['temperature'].yaxis.axis_label = "Temperature (C)"
    plot['pressure'].yaxis.axis_label = "Pressure (hPa)"
    plot['humidity'].yaxis.axis_label = "Relative Humidity (%RH)"
    
#    sys.exit()
    
    # pick a date
    date_picker_i = DatePicker(value=date.today(),max_date=date.today(), title='Inital date:', width=150, disabled=False)
    mydate_i=date_picker_i.value
    date_picker_f = DatePicker(value=date.today(),max_date=date.today(), title='Final date:' , width=150, disabled=False)
    mydate_f=date_picker_f.value
    date_picker_i.on_change('value',initial_date)
    date_picker_f.on_change('value',final_date)

    hist_button = Button(label="Plot date selection", button_type="default", width=310)
    hist_button.on_click(get_history)
    
    
    pre_head = PreText(text="N.B.: Readout every 10 seconds. Be patient!",width=500, height=50)
    pre_head2 = PreText(text="",width=400, height=25)
    pre_temp_top = PreText(text="",width=400, height=20)
    pre_temp_mid = PreText(text="",width=400, height=20)
    pre_temp_bot = PreText(text="",width=400, height=20)
    
    h_space = PreText(text="",width=50, height=1)
    v_space = PreText(text="",width=1, height=50)
    
    
    curdoc().add_root(column(row(h_space,pre_head),row(h_space, date_picker_i, date_picker_f), row(h_space, hist_button),v_space,row(h_space,plot['temperature'],h_space,plot['humidity'],h_space,plot['pressure']), v_space))
    
#    readdata()
#    main()
#    time.sleep ( 10 )
#    periodic_callback_id = curdoc().add_periodic_callback(update, 10000)
else:
    pass    