# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Demonstrating a single scene that is shown in four different viewboxes,
each with a different camera.

Note:
    This example just creates four scenes using the same visual.
    Multiple views are currently not available. See #1124 how this could
    be achieved.
"""

import sys
import numpy as np
from vispy import app, scene, io


canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()


# Create four ViewBoxes
vb1 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb3 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb4 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)

scenes = vb1.scene, vb2.scene, vb3.scene, vb4.scene

# Put viewboxes in a grid
grid = canvas.central_widget.add_grid()


grid.padding = 6
grid.add_widget(vb1, 0, 0)
grid.add_widget(vb2, 0, 1)
grid.add_widget(vb3, 1, 0)
grid.add_widget(vb4, 1, 1)


grid2 = grid.add_grid()
vvvv = grid2.add_view(row=0, col=1, name='vvvv', border_color='green')
vvvv.camera = scene.PanZoomCamera()


# add some axes
x_axis = scene.AxisWidget(orientation='bottom')
x_axis.stretch = (1, 0.1)
grid2.add_widget(x_axis, row=1, col=1)
x_axis.link_view(vvvv)
y_axis = scene.AxisWidget(orientation='left')
y_axis.stretch = (0.1, 1)
grid2.add_widget(y_axis, row=0, col=0)
y_axis.link_view(vvvv)

# First a plot line:
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down
line1 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vvvv.scene)


grid.add_widget(grid2, 1, 3)




# Create some visuals to show
im1 = io.load_crate().astype('float32') / 255
for par in scenes:
    image = scene.visuals.Image(im1, grid=(20, 20), parent=par)

# Assign cameras
vb1.camera = scene.BaseCamera()
vb2.camera = scene.PanZoomCamera()
vb3.camera = scene.TurntableCamera()
vb4.camera = scene.FlyCamera()


if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()
