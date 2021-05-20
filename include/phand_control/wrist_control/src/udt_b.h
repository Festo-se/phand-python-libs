/**************************************************************************************************\
 *** 
 *** Simulink model       : BionicHand_r
 *** TargetLink subsystem : BionicHand_r/wristCtrl
 *** Codefile             : udt_b.h
 ***
 *** Generation date: 2021-04-15 13:06:22
 ***
 *** TargetLink version      : 5.0 from 02-Oct-2019
 *** Code generator version  : Build Id 5.0.0.24 from 2019-10-07 12:46:33
\**************************************************************************************************/

#ifndef UDT_B_H
#define UDT_B_H

#include "tl_basetypes.h"

#ifdef __cplusplus
extern "C" {
#endif

struct wrist_const_tag {
   Float32 sensor_gain;
   Float32 A2;
   Float32 A4;
   Float32 f_diff_x;
   Float32 rateLim;
   Float32 limit_I;
   Float32 p4;
};

struct wrist_tuning_tag {
   Float32 P;
   Float32 I;
   Float32 D;
   Float32 FF;
   UInt16 offset_cyl2;
   UInt16 offset_cyl3;
};

#ifdef __cplusplus
}
#endif

#endif /* UDT_B_H */
/*------------------------------------------------------------------------------------------------*\
  END OF FILE
\*------------------------------------------------------------------------------------------------*/
