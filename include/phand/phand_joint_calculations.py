#!\usr\bin\env python3

import numpy as np
import math as m

class JointCalculations:
    
    def __init__(self):
        self.l1 = 27.63e-3
        self.l2 = 26.63e-3
        self.l3 = 158e-3
        self.l4 = 27.02e-3
        self.l5 = 26.95e-3

        self.l9     = 76.41e-3
        self.l10    = 18.81e-3
        self.l11_0  = self.l9-self.l10

        self.theta3 = np.deg2rad(18.6)

    # Matlab theta 4
    def calculate_wristBase_cylinderR(self, theta1, theta2):

        return -m.atan2(- m.cos(self.theta3)*(self.l4 - self.l1*m.cos(theta1)) - m.sin(self.theta3)*(self.l2*m.cos(theta2) - self.l5
               + self.l1*m.sin(theta1)*m.sin(theta2)),
                        m.sqrt(
                            m.pow(abs(self.l3 - self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)),2)
                         + m.pow(abs(self.l2*m.cos(theta2) - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)),2)
                            + m.pow(abs(self.l4 - self.l1*m.cos(theta1)),2)
                        ))

    # Matlab theta5
    def calculate_horizontal_R_vertical_R(self,theta1, theta2):

        return m.atan2(
            m.cos(self.theta3)*(self.l2*m.cos(theta2) - self.l5 +
            self.l1*m.sin(theta1)*m.sin(theta2)) -
            m.sin(self.theta3)*(self.l4 - self.l1*m.cos(theta1)),
            self.calculate_rigthcylinder_rod(theta1,theta2) # L6
        )

    # Matlab theta 6
    def calculate_wristBase_cylinderL(self, theta1, theta2):

        return -m.atan2(
            -m.cos(-self.theta3)*(self.l4 - self.l1*m.cos(theta1))
            -m.sin(-self.theta3)*(self.l2*m.cos(theta2)
            -self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)),
            self.calculate_leftcylinder_rod(theta1, theta2))

    # Matlab theta7
    def calculate_horizontal_L_vertical_L(self,theta1, theta2):

        return m.atan2(
            m.cos(-self.theta3)*(self.l2*m.cos(theta2)
            - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2))
            - m.sin(-self.theta3)*(self.l4 - self.l1*m.cos(theta1)),
            self.calculate_leftcylinder_rod(theta1, theta2))

    def calculate_l0(self):
        return self.calculate_leftcylinder_rod(0,0)

    # Matlab L6
    def calculate_rigthcylinder_rod(self,theta1, theta2):

        return m.sqrt(
            m.pow(abs(self.l4 - self.l1*m.cos(theta1)), 2) +
            m.pow(abs(self.l3 + self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)), 2) +
            m.pow(abs(self.l5 - self.l2*m.cos(theta2) + self.l1*m.sin(theta1)*m.sin(theta2)), 2)
        )

    # Matlab L7
    def calculate_leftcylinder_rod(self, theta1, theta2):

        return m.sqrt(
            m.pow(abs(self.l2*m.cos(theta2) - self.l5 + self.l1*m.sin(theta1)*m.sin(theta2)), 2) +
            m.pow(abs(self.l4 - self.l1*m.cos(theta1)), 2) +
            m.pow(abs(self.l3 - self.l2*m.sin(theta2) + self.l1*m.cos(theta2)*m.sin(theta1)), 2)
                  )

    def calculate_index_angles(self, cylinder_rod ):

        self.l11 = self.l11_0+cylinder_rod

        ph1 =  2*m.atan(((self.l9*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/( m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11) - (self.l10*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11) + (self.l11*m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt(((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow((self.l9 + self.l10 - self.l11),3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11))/(self.l9 + self.l10 - self.l11))

        ph2 = 2*m.atan(m.pow((self.l9 + self.l10 - self.l11),2)*m.sqrt((((self.l9 - self.l10 + self.l11)*(self.l10 - self.l9 + self.l11))/(m.pow( (self.l9 + self.l10 - self.l11), 3)*(self.l9 + self.l10 + self.l11))))/(self.l9 - self.l10 + self.l11))

        #print([cylinder_rod, ph1, ph1])

        return [ph1, ph2]

    def calculate_theta1_theta2(self, l1_in, l2_in):
        
        l0 = self.calculate_l0()
        # for t1 in np.arange(np.deg2rad(-30.0), np.deg2rad(30.0),  0.05,):
        t1 = np.deg2rad(-40.0)
        t2 = np.deg2rad(-30.0)
        counter = 0
        big_inc = 0.15
        small_inc = 0.010
        old_error = [100,100]
        while t1 < np.deg2rad(40.0):

            # print([t1, t2])
            # for t2 in np.arange(np.deg2rad(-30.0), np.deg2rad(30.0),  0.05):
            l1 = 0
            l2 = 0
            t2 = np.deg2rad(-30.0)

            while t2 < np.deg2rad(30.0):
                counter += 1
                l1 = self.calculate_leftcylinder_rod(theta1=t1, theta2=t2) - l0
                l2 = l0 - self.calculate_rigthcylinder_rod(theta1=t1, theta2=t2)
                # print([abs(l1 - l1_in), abs(l2 - l2_in)])
                error_l1 = abs(l1 - l1_in)
                error_l2 = abs(l2 - l2_in)

                if l1 < l1_in:
                    break
                if l2 < l2_in:
                    break

                old_error[0] = error_l1
                old_error[1] = error_l2


                if error_l2 > 0.007:
                    t2 += big_inc*1.5
                elif error_l2 > 0.002:
                    t2 += small_inc*2
                else:
                    t2 += small_inc

                if error_l1 < 0.002 and error_l2 < 0.002:
                    # logging.debug("Found after: %i iterations"%counter)
                    # print([abs(l1-l1_in), abs(l2-l2_in)])
                    return [t1, t2, True]

            if abs(l1 - l1_in) > 0.007:
                t1 += big_inc
            elif abs(l1 - l1_in) > 0.002:
                t1 += small_inc*2
            else:
                t1 += small_inc

        # logging.error("Not found %f %f"%(l1_in, l2_in))
        # print([l1_in, l2_in])
        return [0,0, False]
        # raise LookupError("No solution found")
