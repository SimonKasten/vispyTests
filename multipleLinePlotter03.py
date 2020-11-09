# -*- coding: utf-8 -*-

import sys
import numpy as np
from vispy import app, scene, io

import collections
import threading
import time
import random


startTime = time.time()
daqDeque = collections.deque()
count = 0.

def fillDeque():
    global count
    while True:        
        daqDeque.append( (time.time(), count+1) )
        daqDeque.append( (time.time(), count+2) )
        daqDeque.append( (time.time(), count+3) )
        daqDeque.append( (time.time(), count+4) )
        count += 0.0000001
        time.sleep(0.0025)


randomDataCreator = threading.Thread(target=fillDeque)
randomDataCreator.setDaemon(True)
randomDataCreator.start()


canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 1200, 800
canvas.show()

grid = canvas.central_widget.add_grid()
grid.spacing = 0


class LinePlot:
    def __init__(self, parentgrid, cam='base'):
        self.subgrid = parentgrid.add_grid()
        self.subgrid.border_color = 'yellow'
        self.vb = self.subgrid.add_view(row=1, col=1, col_span=2, name='vb', border_color='green')
        self.vb.camera = cam

        # add some axes
        self.title = scene.Label("Plot Title", color='white', method='gpu')
        self.title.height_max = 40
        self.title.border_color = 'green'
        self.subgrid.add_widget(self.title, row=0, col=0, col_span=3)

        self.x_axis = scene.AxisWidget(orientation='bottom',
                                tick_label_margin=15,
                                axis_label='X Axis',
                                axis_font_size=12,
                                axis_label_margin=40)
        self.x_axis.height_min = 60
        self.x_axis.height_max = 60
        self.x_axis.border_color = 'red'
        # self.x_axis.height_max = 80   
        self.subgrid.add_widget(self.x_axis, row=2, col=1, col_span=2)
        self.x_axis.link_view(self.vb)
        
        self.y_axis = scene.AxisWidget(orientation='left',
                        tick_label_margin=5,
                        axis_label='Y Axis',
                        axis_font_size=12,
                        axis_label_margin=50)
        self.y_axis.width_min = 80
        self.y_axis.width_max = 80
        self.y_axis.border_color = 'purple'
        #self.y_axis.stretch = (0.1, 1)
        # self.y_axis.width_max = 80
        self.subgrid.add_widget(self.y_axis, row=1, col=0)
        self.y_axis.link_view(self.vb)

        self.right_padding = self.subgrid.add_widget(row=0, col=3, row_span=3)
        self.right_padding.width_max = 50
        self.right_padding.border_color = 'orange'


lPlot1 = LinePlot(grid, cam='panzoom')
grid.add_widget(lPlot1.subgrid, row=0, col=0)

lPlot2 = LinePlot(grid, cam='panzoom')
grid.add_widget(lPlot2.subgrid, row=1, col=0)

lPlot3 = LinePlot(grid, cam='panzoom')
grid.add_widget(lPlot3.subgrid, row=2, col=0)




len_buff = 10000
first = 0
valid_data = 0
len_data = len_buff

pos = np.empty((len_buff, 2), np.float32)

empty_plot = np.zeros((1, 2), np.float32)

line = scene.visuals.Line(pos=empty_plot.copy(), method='gl',
                        antialias=False, name='line1', parent=lPlot1.vb.scene)
line2 = scene.visuals.Line(pos=empty_plot.copy(), color='green', method='gl',
                        antialias=False, name='line2', parent=lPlot2.vb.scene)
line3 = scene.visuals.Line(pos=empty_plot.copy(), method='gl',
                        antialias=False, name='line3', parent=lPlot3.vb.scene)



def shoveler(ev):
    global valid_data, first, pos, startTime, len_data
    if daqDeque:
        daq = daqDeque.popleft()

        if valid_data >= len_data:
            # more buffer
            pos = np.append(pos, np.empty((len_buff, 2), np.float32), axis=0)
            len_data = np.size(pos, 0)

        pos[valid_data, 0] = daq[0] - startTime
        pos[valid_data, 1] = daq[1]

        valid_data += 1
        if valid_data > len_buff:
            first += 1



def update(ev):
    global valid_data, first, pos, line, line2, line3, lPlot1
    print(len(daqDeque))

    line.set_data(pos=pos[first:valid_data])
    line2.set_data(pos=pos[first:valid_data])
    line3.set_data(pos=pos[first:valid_data])

    lPlot1.vb.camera.set_range(x=(0, pos[valid_data-1, 0]))



timer = app.Timer()
timer.connect(update)
timer.start(0.05)

shovel = app.Timer()
shovel.connect(shoveler)
shovel.start(0)

if sys.flags.interactive != 1:
    app.run()
