"""
The data assimilation system:OI
Load:
  x_a_init.txt
Save:
  x_b_oi.txt
  x_a_oi.txt
"""
import numpy as np
from scipy.integrate import ode
import lorenz96
from settings import *
import math

def getDis(pointX,pointY):
    a=39. - 1.          #lineY2-lineY1
    b=1. - 39.          #lineX1-lineX2
    c=39.*1. - 1.*39. #lineX2*lineY1-lineX1*lineY2
    dis=(math.fabs(a*pointX+b*pointY+c))/(math.pow(a*a+b*b,0.5))
    return dis

# load initial condition
x_a_init = np.genfromtxt('x_a_init.txt')

# load observations
y_o_save = np.genfromtxt('x_o_save.txt')

# load truth
x_t_save = np.genfromtxt('x_t.txt')

#load initial BEC
Pb = np.genfromtxt('Pb.txt')    #initial BEC

# load H
#H = np.genfromtxt('H2.txt')
H = np.eye(N)

# calculate for obs. error covariance(R)
R = np.zeros((N,N))
for i in range(N):
     R[i,i] = (std_obs_err)**2.
"""
# density obs. err 
R = np.zeros((19,19))
for i in range(19):
     R[i,i] = (std_obs_err)**2.
"""

# DA process:OI
tt = 1    
# initial x_b: no values at the initial time (assign NaN)
x_b_save = np.full((1,N), np.nan, dtype='f8')
# initial x_a: from x_a_init
x_a_save = np.array([x_a_init])
while tt <= nT:
    print('DA process...')
    tts = tt - 1
    Ts = tts * dT  # forecast start time
    Ta = tt  * dT  # forecast end time (DA analysis time)
#        print('Cycle =', tt, ', Ts =', round(Ts, 10), ', Ta =', round(Ta, 10))
    
    #--------------
    # forecast step
    #--------------

    solver = ode(lorenz96.f).set_integrator('dopri5')
    solver.set_initial_value(x_a_save[tts], Ts).set_f_params(F)
    solver.integrate(Ta)
    x_b_save = np.vstack([x_b_save, [solver.y]])

    #--------------
    # analysis step
    #--------------
    
    #truth
    x_t = x_t_save[tt].transpose()
    # background
    x_b = x_b_save[tt].transpose()
    
    # observation
    y_o = y_o_save[tt].transpose()
    
    # obs. err
    #obs_err = y_o-x_t
    
    # innovation
    y_b = np.dot(H, x_b)
    d = y_o - y_b
    
    #Kalmen Gain
    K_OI = np.dot((np.dot(Pb,np.transpose(H))),(np.linalg.inv((np.dot(H,np.dot(Pb,np.transpose(H))))+R)))

    # analysis scheme
    x_a = x_b + np.dot(K_OI,d)

    x_a_save = np.vstack([x_a_save, x_a.transpose()])
    tt += 1

# save OI background and analysis data
np.savetxt('x_b_oi.txt', x_b_save)
np.savetxt('x_a_oi.txt', x_a_save)
"""
# save OI background and analysis data
np.savetxt('x_b_oi_obs1.txt', x_b_save)
np.savetxt('x_a_oi_obs1.txt', x_a_save)
"""
