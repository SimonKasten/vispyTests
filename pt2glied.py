import numpy as np
import control
from control.matlab import *
import matplotlib.pyplot as plt
for ii in range(0, 11): # Liste von 0 bis kk-1
    d = 1.2 - 0.1*ii
    den  = np.array([1,2*d, 1])
    print("d = %3.2f, Pole = %s " %(d,str(np.roots(den))) )
    pt2 = tf(1,den)
    y, t = control.matlab.step(pt2)
    plt.plot(t,y)
plt.title('P-T2s Batch')
plt.xlabel('t [s]'); plt.ylabel('h(t)')    
plt.grid()
plt.figure()
pzmap(pt2)
plt.grid()
#mag, phase, w = control.matlab.bode(pt2)
plt.show()