#!/usr/bin/env python3
from phand_core_lib.phand import *
from timeit import default_timer as timer
import matplotlib.pyplot as plt

jc = JointCalculations()



num_found = 0
notfound = 0
avg_time = 0
total_calc = 0

jc.calculate_theta1_theta2(0, 0.02)
exit(0)

for l1 in np.arange(-0.02, 0.01, 0.001):

    for l2 in np.arange(-0.02, 0.01, 0.001):

        start = timer()
        [_,_,found, cal] = jc.calculate_theta1_theta2(l1, l2)
        total_calc += cal
        if found:
            num_found+=1
        else:
            # print([l1,l2])
            notfound+=1

        end = timer()

        if avg_time == 0:
            avg_time = end-start
        else:
            avg_time = (avg_time + end-start)/2

print("|  0.1/0.01 | 0.01 | %i | %i | %i | %f | %i |" % (num_found+notfound,num_found,notfound,avg_time, total_calc))
