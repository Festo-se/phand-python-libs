/**************************************************************************************************\
 *** 
 *** Simulink model       : BionicHand_r
 *** TargetLink subsystem : BionicHand_r/fingerCtrl
 *** Codefile             : udt_e.h
 ***
 *** Generation date: 2021-06-08 10:57:06
 ***
 *** TargetLink version      : 5.1 from 28-Oct-2020
 *** Code generator version  : Build Id 5.1.0.29 from 2020-10-22 12:32:14
\**************************************************************************************************/

#ifndef UDT_E_H
#define UDT_E_H

#include "tl_basetypes.h"

#ifdef __cplusplus
extern "C" {
#endif

struct finger_const_tag {
   Float32 useMean; /* Description: 1= use mean of Top and Bottom Sensors; 0 = use Bottom Sensor */
   Float32 ctrlGain; /* Description: Scaling Gain for Ctrl Parameters */
   Float32 rateLim_finger; /* Description: rateLimit for finger Movement */
   Float32 A2_cyl1_DRVS[2]; /* Description: Effective surface of Port 2 of index-cylinder and DRVS
   */
   Float32 A4_cyl1_DRVS[2]; /* Description: Effective surface of Port 4 of index-cylinder and DRVS
   */
   Float32 limit_I; /* Description: Limit for Integrator for index_cylinder and DRVS */
   Float32 rateLim_cyl1; /* Description: rate Limit for movement of index-cylinder */
   Float32 rateLim_DRVS; /* Description: rateLimit for movement of DRVS */
   Float32 p4; /* Description: pressure A4 (3bar) */
};

struct finger_tuning_tag {
   Float32 P_big; /* Description: P Gain for full fingers */
   Float32 P_small; /* Description: P Gain for half fingers */
   Float32 I_big; /* Description: I Gain for full fingers */
   Float32 I_small; /* Description: I Gain for half fingers */
   Float32 FF_big; /* Description: Feed-Forward for full fingers */
   Float32 FF_small; /* Description: Feed-Forward for half dingers */
   UInt16 minTopFingerPos[5]; /* Description: TopSensor Values for stretched Fingers (p=0) */
   UInt16 minBotFingerPos[5]; /* Description: BotSensor Values for stretched Fingers (p=0) */
   UInt16 maxTopFingerPos[5]; /* Description: TopSensor Values for flexed Fingers (p=max) */
   UInt16 maxBotFingerPos[5]; /* Description: BotSensor Values for flexed Fingers (p=0) */
   Float32 P_cyl_drvs[2]; /* Description: P Gains for index-Cylinder and DRVS */
   Float32 I_cyl_drvs[2]; /* Description: I Gains for index-cylinder and DRVS */
   Float32 FF_cyl_drvs[2]; /* Description: Feed-Forward Gains for index-cylinder and DRVS */
   UInt16 cyl1_minPos;
   UInt16 cyl1_maxPos;
   UInt16 DRVS_minPos;
   UInt16 DRVS_maxPos;
};

struct wrist_const_tag {
   Float32 sensor_gain;
   Float32 A2;
   Float32 A4;
   Float32 f_diff_x;
   Float32 rateLim;
   Float32 limit_I;
   Float32 p4;
};

#ifdef __cplusplus
}
#endif

#endif /* UDT_E_H */
/*------------------------------------------------------------------------------------------------*\
  END OF FILE
\*------------------------------------------------------------------------------------------------*/
