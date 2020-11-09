import sys
import numpy as np
from vispy import gloo, app, scene, io

import collections
import threading
import time
import random

N = 1000

class LineBuffer:
    def __init__(self, blocksize):
        self.pos = np.empty((blocksize, 2), np.float32)
        self.blocksize = blocksize
        self.first = 0
        self.last = blocksize
        self.valid = 0

    def append(self, newpos):
        # if buffer full append new block
        if self.valid >= self.last:
            self.pos = np.append(self.pos, np.empty((self.blocksize, 2), np.float32), axis=0)
            self.last += self.blocksize

        self.pos[self.valid, 0] = newpos[0]
        self.pos[self.valid, 1] = newpos[1]

        self.valid += 1
        if self.valid > self.blocksize:
            self.first += 1

    def valid_buffer(self):
        return self.pos[self.first:self.valid]

    def cam_range(self):
        return (self.pos[self.first, 0], self.pos[self.valid - 1, 0])






class LinePlot:
    def __init__(self, parentgrid, cam='base'):
        # organize grid and cam
        self.subgrid = parentgrid.add_grid()
        self.subgrid.border_color = 'yellow'
        self.vb = self.subgrid.add_view(row=1, col=1, col_span=2, name='vb', border_color='green')
        self.vb.camera = cam

        # add some axes and empty spaces
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
        self.subgrid.add_widget(self.y_axis, row=1, col=0)
        self.y_axis.link_view(self.vb)

        self.right_padding = self.subgrid.add_widget(row=0, col=3, row_span=3)
        self.right_padding.width_max = 50
        self.right_padding.border_color = 'orange'

        # create Line for Plot
        self.line = scene.visuals.Line( pos=np.zeros((1, 2), np.float32),
                                        method='gl',
                                        antialias=False,
                                        parent=self.vb.scene)
        self.linebuff = LineBuffer(N)
    

    def update_line(self):
        """ updates Line of LinePlot with LineBuffer """
        self.line.set_data(pos=self.linebuff.valid_buffer())


    def cam_range(self, y=(0,1), x=None):
        """ set cam range, if x=None then auto range"""
        if x is None:
            validXrange = self.linebuff.cam_range()
            self.vb.camera.set_range(x=validXrange, y=y)
        else:
            self.vb.camera.set_range(x=x, y=y)




class Canvas(scene.SceneCanvas):

    def __init__(self, *args, **kwargs):
        scene.SceneCanvas.__init__(self, *args, **kwargs)

    # def on_close(self, event):
    #     print('closing!')

    # def on_resize(self, event):
    #     print('Resize %r' % (event.size, ))

    # def on_key_press(self, event):
    #     modifiers = [key.name for key in event.modifiers]
    #     print('Key pressed - text: %r, key: %s, modifiers: %r' % (
    #         event.text, event.key.name, modifiers))

    # def on_key_release(self, event):
    #     modifiers = [key.name for key in event.modifiers]
    #     print('Key released - text: %r, key: %s, modifiers: %r' % (
    #         event.text, event.key.name, modifiers))

    # def on_mouse_press(self, event):
    #     self.print_mouse_event(event, 'Mouse press')

    # def on_mouse_release(self, event):
    #     self.print_mouse_event(event, 'Mouse release')

    # def on_mouse_move(self, event):
    #     self.print_mouse_event(event, 'Mouse move')

    # def on_mouse_wheel(self, event):
    #     self.print_mouse_event(event, 'Mouse wheel')

    # def print_mouse_event(self, event, what):
    #     modifiers = ', '.join([key.name for key in event.modifiers])
    #     print('%s - pos: %r, button: %s, modifiers: %s, delta: %r' %
    #           (what, event.pos, event.button, modifiers, event.delta))

    # def on_draw(self, event):
    #     gloo.clear(color=True, depth=True)



class Frontend:

    def __init__(self, *args, **kwargs):
        self.canvas = Canvas(keys='interactive', *args, **kwargs)
        self.grid = self.canvas.central_widget.add_grid()
        self.grid.spacing = 0
        self.line_plots = []

        self.lineUpdater = app.Timer()
        self.lineUpdater.connect(self.update)
        self.lineUpdater.start(0.1)


    def show(self):
        self.canvas.show()

    def add_line_plot(self, row, col):
        _lPlot = LinePlot(self.grid, cam='panzoom') 
        self.line_plots.append(_lPlot)
        self.grid.add_widget(_lPlot.subgrid, row=row, col=col)
        return _lPlot

    def update(self, ev):
        for plot in self.line_plots:
            plot.update_line()
            plot.cam_range(y=(0,10))



startTime = time.time()
daqDeque = collections.deque()

def fillDeque():
    global count
    while True:        
        daqDeque.append( (time.time(), random.random()*5) )
        daqDeque.append( (time.time(), random.random()*5) )
        daqDeque.append( (time.time(), random.random()*5) )
        daqDeque.append( (time.time(), random.random()*5) )
        time.sleep(0.0025)


randomDataCreator = threading.Thread(target=fillDeque)
randomDataCreator.setDaemon(True)
randomDataCreator.start()


frontend = Frontend(size=(1200, 800), title="a gschmeidiger Blod")
frontend.show()

lPlot1 = frontend.add_line_plot(0,0)
lPlot2 = frontend.add_line_plot(1,0)
lPlot3 = frontend.add_line_plot(2,0)

def shoveler(ev):
    global startTime
    if daqDeque:
        daq = daqDeque.popleft()
        lPlot1.linebuff.append((daq[0] - startTime, daq[1]))
        lPlot2.linebuff.append((daq[0] - startTime, daq[1]))
        lPlot3.linebuff.append((daq[0] - startTime, daq[1]))

shovel = app.Timer()
shovel.connect(shoveler)
shovel.start(0)

if sys.flags.interactive != 1:
    app.run()