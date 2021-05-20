/**************************************************************************************************\
 *** 
 *** Simulink model       : BionicHand_r
 *** TargetLink subsystem : BionicHand_r/wristCtrl
 *** Codefile             : wristCtrl.c
 ***
 *** Generated by TargetLink, the dSPACE production quality code generator
 *** Generation date: 2021-04-15 13:06:22
 ***
 *** CODE GENERATOR OPTIONS:
 *** Code generation mode                     : Standard
 *** Compiler                                 : <unknown>
 *** Target                                   : Generic
 *** ANSI-C compatible code                   : yes
 *** Code Optimization                        : enabled
 *** Constant style                           : decimal
 *** Clean code option                        : enabled
 *** Logging mode                             : Do not log anything
 *** Code Coverage                            : disabled
 *** Generate empty conditional branches      : disabled
 *** Loop unroll threshold                    : 5
 *** Utilize bitwise shift operations         : AvoidPotentiallyUndefinedShiftsBasedOnSignedness
 *** Handle unscaled SF expr. with TL type    : enabled
 *** Assignment of conditions                 : AllBooleanOutputs 
 *** Scope reduction only to function level   : disabled
 *** Exploit ranges if not erasable           : disabled
 *** Exploit Compute Through Overflow         : optimized
 *** Linker sections                          : enabled
 *** Enable Assembler                         : disabled
 *** Variable name length                     : 31 chars
 *** Use global bitfields                     : disabled
 *** Stateflow: use of bitfields              : enabled
 *** State activity encoding limit            : 5
 *** Omit zero inits in restart function      : disabled
 *** Share functions between TL subsystems    : disabled
 *** Generate 64bit functions                 : disabled
 *** Inlining Threshold                       : 6
 *** Line break limit                         : 100
 *** Target optimized boolean data type       : enabled
 *** Keep saturation elements                 : disabled
 *** Extended variable sharing                : disabled
 *** Extended lifetime optimization           : enabled
 *** Style definition file                    : C:\Appl\dSpace\dSPACE TargetLink 5.0\Matlab\Tl\Confi
 ***                                            g\codegen\cconfig.xml
 *** Root style sheet                         : C:\Appl\dSpace\dSPACE TargetLink 5.0\Matlab\Tl\XML\C
 ***                                            odeGen\Stylesheets\TL_CSourceCodeSS.xsl
 ***
 *** SUBSYS         CORRESPONDING SIMULINK SUBSYSTEM
 *** Sb1            wristCtrl
 *** Sb2            wristCtrl/DetectChange_TL
 *** Sb3            wristCtrl/Integrator
 *** Sb4            wristCtrl/KI_reduction
 *** Sb5            wristCtrl/Kraft - Druck Umrechnung
 *** Sb6            wristCtrl/PT1_diskret1
 *** Sb7            wristCtrl/PT1_diskret2
 *** Sb8            wristCtrl/bahnplaner
 *** Sb9            wristCtrl/Integrator/Saturate
 *** Sb10           wristCtrl/bahnplaner/DetectChange_TL
 *** Sb11           wristCtrl/bahnplaner/DetectChange_TL1
 *** Sb12           wristCtrl/bahnplaner/DetectChange_TL2
 *** Sb13           wristCtrl/bahnplaner/Subsystem
 *** Sb14           wristCtrl/bahnplaner/Subsystem1
 *** Sb15           wristCtrl/bahnplaner/Subsystem/Integrator
 *** Sb16           wristCtrl/bahnplaner/Subsystem1/Integrator
 *** 
 *** SUBSYS         CORRESPONDING MODEL BLOCK (REFERENCED MODEL)
 *** 
 *** SF-NODE        CORRESPONDING STATEFLOW NODE                    DESCRIPTION
 *** 
 *** TargetLink version      : 5.0 from 02-Oct-2019
 *** Code generator version  : Build Id 5.0.0.24 from 2019-10-07 12:46:33
\**************************************************************************************************/

#ifndef WRISTCTRL_C
#define WRISTCTRL_C

/*------------------------------------------------------------------------------------------------*\
  DEFINES (OPT)
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  INCLUDES
\*------------------------------------------------------------------------------------------------*/

#include <math.h>
#include "wristCtrl.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------------------------------------------*\
  ENUMS
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  DEFINES
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  TYPEDEFS
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  VARIABLES
\*------------------------------------------------------------------------------------------------*/

/**************************************************************************************************\
   GLOBAL: global variables (RAM) | Width: N.A.
\**************************************************************************************************/
GLOBAL struct wrist_tuning_tag wristCtrl_tuning = {
   3.F, /* P */
   2.F, /* I */
   0.F, /* D */
   0.20000000298023224F, /* FF */
   3615, /* offset_cyl2 */
   870 /* offset_cyl3 */
};

/*------------------------------------------------------------------------------------------------*\
  PARAMETERIZED MACROS
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  FUNCTION PROTOTYPES
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  INLINE FUNCTIONS
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  FUNCTION DEFINITIONS
\*------------------------------------------------------------------------------------------------*/

/**************************************************************************************************\
 ***  FUNCTION:
 ***      wristCtrl
 *** 
 ***  DESCRIPTION:
 ***      
 *** 
 ***  PARAMETERS:
 ***      Type               Name                Description
 ***      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ***      UInt16 *           ActPos_cyl2         sensor signal cylinder 2 in increments
 ***      UInt16 *           ActPos_cyl3         sensor signal cylinder 2 in increments
 ***      Float32 *          desPos_cyl2         desired position cylinder 2 in mm
 ***      Float32 *          desPos_cyl3         desired position cylinder 3 in mm
 ***      Bool *             enable              enable/reset
 ***      Float32 *          p2d_cyl2            desired pressure at port 2 of cylinder 2
 ***      Float32 *          p2d_cyl3            desired pressure at port 2 of cylinder 3
 ***      Float32 *          p4d                 desired pressure at port 4 of cylinders
 ***
 ***  RETURNS:
 ***      void
 ***
 ***  SETTINGS:
 ***
\**************************************************************************************************/
void wristCtrl(UInt16 * ActPos_cyl2, UInt16 * ActPos_cyl3, Float32 * desPos_cyl2, Float32 *
  desPos_cyl3, Bool * enable, Float32 * p2d_cyl2, Float32 * p2d_cyl3, Float32 * p4d)
{
   /* STATIC_LOCAL: static local variables (RAM) | Width: N.A. */
   STATIC_LOCAL struct wrist_const_tag wristCtrl_const = {
      0.018698578700423241F, /* sensor_gain */
      0.000172787593328394F, /* A2 */
      0.00020106193551328033F, /* A4 */
      5.F, /* f_diff_x */
      30.F, /* rateLim */
      10.F, /* limit_I */
      400000.F /* p4 */
   };

   /* SLLocal: Default storage class for local variables | Width: 32 */
   Float32 Sb13_Add1;
   Float32 Sb13_Divide2;
   Float32 Sb14_Add1;
   Float32 Sb14_Divide2;
   Float32 Sb1_Gain[2];
   Float32 Sb1_Subtract[2];
   Float32 Sb3_Add[2];
   Float32 Sb4_Switch;
   Float32 Sb4_Switch1;
   Float32 Sb6_Saturation;
   Float32 Sb7_Saturation;
   Float32 Sb8_vd[2];
   Float32 Sb8_xd[2];
   Float32 Sb9_Gain1;
   Float32 Sb9_MinMax[2];
   Float32 Sb9_MinMax1[2];

   /* SLLocal: Default storage class for local variables | Width: 8 */
   Bool Sb12_Relational_Operator;
   Bool Sb1_OR;
   Bool Sb3_reset[2];

   /* SLLocal: Default storage class for local variables | Width: 32 */
   Float32 Aux_F32;

   /* SLStaticLocal: Default storage class for static local variables | Width: 32 */
   static Float32 X_Sb4_Rate_Limiter = 0.F;
   static Float32 X_Sb4_Rate_Limiter1 = 0.F;

   /* SLStaticLocalInit: Default storage class for static local variables with initvalue | Width: 32
    */
   static Float32 U_Sb6_Discrete_Time_Integrator2;
   static Float32 U_Sb7_Discrete_Time_Integrator2;
   static Float32 X_Sb10_Unit_Delay = 0.F;
   static Float32 X_Sb11_Unit_Delay = 0.F;
   static Float32 X_Sb12_Unit_Delay = 0.F;
   static Float32 X_Sb13_startPos = 0.F;
   static Float32 X_Sb14_startPos = 0.F;
   static Float32 X_Sb15_Unit_Delay = 0.F;
   static Float32 X_Sb16_Unit_Delay = 0.F;
   static Float32 X_Sb2_Unit_Delay = 0.F;
   static Float32 X_Sb3_Unit_Delay[2] = 
   {
      /* [0..1] */ 0.F, 0.F
      /* 0.F, 0.F */
   };
   static Float32 X_Sb6_Discrete_Time_Integrator2; /* MIN/MAX: -3.402823466e+38 .. 3.402823466e+38
   */
   static Float32 X_Sb6_Discrete__ator2_TriggerIn = 3.402823466e+38F;
   static Float32 X_Sb7_Discrete_Time_Integrator2; /* MIN/MAX: -3.402823466e+38 .. 3.402823466e+38
   */
   static Float32 X_Sb7_Discrete__ator2_TriggerIn = 3.402823466e+38F;

   /* SLStaticLocalInit: Default storage class for static local variables with initvalue | Width: 8
   */
   static Bool Sb1_wristCtrl_FirstRun = 1;
   static Int8 Sb6_Discrete_T__ator2_LastEvent = -1;
   static Int8 Sb7_Discrete_T__ator2_LastEvent = -1;

   /* TargetLink outport: wristCtrl/p4d
      # combined # wristCtrl/Kraft - Druck Umrechnung/p4Soll */
   *p4d = wristCtrl_const.p4;

   /* Gain: wristCtrl/Gain
      # combined # Gain: wristCtrl/Gain5
      # combined # Sum: wristCtrl/Add1
      # combined # Rescaler: wristCtrl/Data Type Conversion3
      # combined # Rescaler: wristCtrl/Data Type Conversion2 */
   Sb1_Gain[0] = (((Float32) *ActPos_cyl2) - ((Float32) wristCtrl_tuning.offset_cyl2)) * -1.F *
    wristCtrl_const.sensor_gain;
   Sb1_Gain[1] = (((Float32) *ActPos_cyl3) - ((Float32) wristCtrl_tuning.offset_cyl3)) *
    wristCtrl_const.sensor_gain;

   /* Logical: wristCtrl/OR
      # combined # wristCtrl/DetectChange_TL/Out1
      # combined # Relational: wristCtrl/DetectChange_TL/Relational Operator
      # combined # wristCtrl/DetectChange_TL/In1 */
   Sb1_OR = ((Float32) (((Float32) *enable) != X_Sb2_Unit_Delay)) != 0;

   /* Unit delay: wristCtrl/DetectChange_TL/Unit Delay
      # combined # wristCtrl/DetectChange_TL/In1 */
   X_Sb2_Unit_Delay = (Float32) *enable;

   /* Relational: wristCtrl/bahnplaner/DetectChange_TL2/Relational Operator
      # combined # wristCtrl/bahnplaner/DetectChange_TL2/In1
      # combined # wristCtrl/bahnplaner/ena */
   Sb12_Relational_Operator = ((Float32) Sb1_OR) != X_Sb12_Unit_Delay;

   /* Unit delay: wristCtrl/bahnplaner/DetectChange_TL2/Unit Delay
      # combined # wristCtrl/bahnplaner/DetectChange_TL2/In1
      # combined # wristCtrl/bahnplaner/ena */
   X_Sb12_Unit_Delay = (Float32) Sb1_OR;

   /* Logical: wristCtrl/bahnplaner/OR
      # combined # wristCtrl/Integrator/reset
      # combined # wristCtrl/bahnplaner/DetectChange_TL1/Out1
      # combined # wristCtrl/bahnplaner/DetectChange_TL2/Out1
      # combined # wristCtrl/bahnplaner/DetectChange_TL1/In1
      # combined # wristCtrl/bahnplaner/desPos */
   Sb3_reset[0] = Sb12_Relational_Operator || (*desPos_cyl2 != X_Sb11_Unit_Delay);

   /* Unit delay: wristCtrl/bahnplaner/DetectChange_TL1/Unit Delay
      # combined # wristCtrl/bahnplaner/DetectChange_TL1/In1
      # combined # wristCtrl/bahnplaner/desPos */
   X_Sb11_Unit_Delay = *desPos_cyl2;

   /* Switch: wristCtrl/bahnplaner/Subsystem/Switch1 */
   if (Sb3_reset[0]) {
      /* Switch: wristCtrl/bahnplaner/Subsystem/Switch1
         # combined # wristCtrl/bahnplaner/Subsystem/Pos
         # combined # wristCtrl/bahnplaner/actualPos
         # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/startPos */
      X_Sb13_startPos = Sb1_Gain[0];
   }

   /* Sum: wristCtrl/bahnplaner/Subsystem/Add1
      # combined # wristCtrl/bahnplaner/Subsystem/desPos
      # combined # wristCtrl/bahnplaner/desPos
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/startPos */
   Sb13_Add1 = *desPos_cyl2 - X_Sb13_startPos;

   /* Product: wristCtrl/bahnplaner/Subsystem/Integrator/Product
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/Integrator/Unit Delay
      # combined # Saturation: wristCtrl/bahnplaner/Subsystem/Integrator/Saturation
      # combined # Sum: wristCtrl/bahnplaner/Subsystem/Integrator/Add
      # combined # Logical: wristCtrl/bahnplaner/Subsystem/Integrator/Logical Operator
      # combined # wristCtrl/bahnplaner/Subsystem/Integrator/reset
      # combined # Gain: wristCtrl/bahnplaner/Subsystem/Integrator/Gain */
   X_Sb15_Unit_Delay = ((Float32) (!(Sb3_reset[0]))) * (0.005F + X_Sb15_Unit_Delay);

   /* Logical: wristCtrl/bahnplaner/OR1
      # combined # wristCtrl/Integrator/reset
      # combined # wristCtrl/bahnplaner/DetectChange_TL/Out1
      # combined # wristCtrl/bahnplaner/DetectChange_TL2/Out1
      # combined # wristCtrl/bahnplaner/DetectChange_TL/In1
      # combined # wristCtrl/bahnplaner/desPos */
   Sb3_reset[1] = Sb12_Relational_Operator || (*desPos_cyl3 != X_Sb10_Unit_Delay);

   /* Unit delay: wristCtrl/bahnplaner/DetectChange_TL/Unit Delay
      # combined # wristCtrl/bahnplaner/DetectChange_TL/In1
      # combined # wristCtrl/bahnplaner/desPos */
   X_Sb10_Unit_Delay = *desPos_cyl3;

   /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch1 */
   if (Sb3_reset[1]) {
      /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch1
         # combined # wristCtrl/bahnplaner/Subsystem1/Pos
         # combined # wristCtrl/bahnplaner/actualPos
         # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/startPos */
      X_Sb14_startPos = Sb1_Gain[1];
   }

   /* Sum: wristCtrl/bahnplaner/Subsystem1/Add1
      # combined # wristCtrl/bahnplaner/Subsystem1/desPos
      # combined # wristCtrl/bahnplaner/desPos
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/startPos */
   Sb14_Add1 = *desPos_cyl3 - X_Sb14_startPos;

   /* Product: wristCtrl/bahnplaner/Subsystem1/Divide2
      # combined # wristCtrl/bahnplaner/Subsystem1/rateLim */
   if (wristCtrl_const.rateLim != 0.F) {
      /* # combined # Abs: wristCtrl/bahnplaner/Subsystem/Abs1
         # combined # wristCtrl/bahnplaner/Subsystem/rateLim */
      Sb13_Divide2 = ((Float32) fabs((Float64) Sb13_Add1)) / wristCtrl_const.rateLim;

      /* # combined # Abs: wristCtrl/bahnplaner/Subsystem1/Abs1
         # combined # wristCtrl/bahnplaner/Subsystem1/rateLim */
      Sb14_Divide2 = ((Float32) fabs((Float64) Sb14_Add1)) / wristCtrl_const.rateLim;
   }
   else {
      /* wristCtrl/bahnplaner/Subsystem/Divide2: Numerator always greater than or equal to zero. */
      Sb13_Divide2 = 3.402823466e+38F;

      /* wristCtrl/bahnplaner/Subsystem1/Divide2: Numerator always greater than or equal to zero. */
      Sb14_Divide2 = 3.402823466e+38F;
   }

   /* Product: wristCtrl/bahnplaner/Subsystem1/Integrator/Product
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/Integrator/Unit Delay
      # combined # Saturation: wristCtrl/bahnplaner/Subsystem1/Integrator/Saturation
      # combined # Sum: wristCtrl/bahnplaner/Subsystem1/Integrator/Add
      # combined # Logical: wristCtrl/bahnplaner/Subsystem1/Integrator/Logical Operator
      # combined # wristCtrl/bahnplaner/Subsystem1/Integrator/reset
      # combined # Gain: wristCtrl/bahnplaner/Subsystem1/Integrator/Gain */
   X_Sb16_Unit_Delay = ((Float32) (!(Sb3_reset[1]))) * (0.005F + X_Sb16_Unit_Delay);

   /* Switch: wristCtrl/bahnplaner/Subsystem/Switch2
      wristCtrl/bahnplaner/Subsystem/Switch2: Omitted comparison with constant.
      # combined # Relational: wristCtrl/bahnplaner/Subsystem/LessThanOrEqual
      # combined # wristCtrl/bahnplaner/Subsystem/Integrator/out
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/Integrator/Unit Delay */
   if (X_Sb15_Unit_Delay <= Sb13_Divide2) {
      /* SLLocal: Default storage class for local variables | Width: 32 */
      Float32 Sb13_Divide;

      /* Product: wristCtrl/bahnplaner/Subsystem/Divide */
      if (Sb13_Divide2 != 0.F) {
         /* # combined # Switch: wristCtrl/bahnplaner/Subsystem/Switch3
            # combined # wristCtrl/bahnplaner/vd
            # combined # wristCtrl/bahnplaner/Subsystem/v */
         Sb8_vd[0] = Sb13_Add1 / Sb13_Divide2;

         /* # combined # wristCtrl/bahnplaner/Subsystem/Integrator/out
            # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/Integrator/Unit Delay */
         Sb13_Divide = X_Sb15_Unit_Delay / Sb13_Divide2;
      }
      else {
         if (Sb13_Add1 < 0.F) {
            /* # combined # Switch: wristCtrl/bahnplaner/Subsystem/Switch3
               # combined # wristCtrl/bahnplaner/vd
               # combined # wristCtrl/bahnplaner/Subsystem/v */
            Sb8_vd[0] = -3.402823466e+38F;
         }
         else {
            /* # combined # Switch: wristCtrl/bahnplaner/Subsystem/Switch3
               # combined # wristCtrl/bahnplaner/vd
               # combined # wristCtrl/bahnplaner/Subsystem/v */
            Sb8_vd[0] = 3.402823466e+38F;
         }

         /* # combined # wristCtrl/bahnplaner/Subsystem/Integrator/out
            # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/Integrator/Unit Delay */
         if (X_Sb15_Unit_Delay < 0.F) {
            Sb13_Divide = -3.402823466e+38F;
         }
         else {
            Sb13_Divide = 3.402823466e+38F;
         }
      }
      Sb13_Divide = Sb13_Divide * Sb13_Add1;

      /* Switch: wristCtrl/bahnplaner/Subsystem/Switch2
         # combined # wristCtrl/bahnplaner/xd
         # combined # wristCtrl/bahnplaner/Subsystem/y
         # combined # Sum: wristCtrl/bahnplaner/Subsystem/Add
         # combined # Unit delay: wristCtrl/bahnplaner/Subsystem/startPos */
      Sb8_xd[0] = Sb13_Divide + X_Sb13_startPos;
   }
   else {
      /* Switch: wristCtrl/bahnplaner/Subsystem/Switch3
         # combined # wristCtrl/bahnplaner/vd
         # combined # wristCtrl/bahnplaner/Subsystem/v */
      Sb8_vd[0] = 0.F;

      /* Switch: wristCtrl/bahnplaner/Subsystem/Switch2
         # combined # wristCtrl/bahnplaner/xd
         # combined # wristCtrl/bahnplaner/Subsystem/y
         # combined # wristCtrl/bahnplaner/Subsystem/desPos
         # combined # wristCtrl/bahnplaner/desPos */
      Sb8_xd[0] = *desPos_cyl2;
   }

   /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch2
      wristCtrl/bahnplaner/Subsystem1/Switch2: Omitted comparison with constant.
      # combined # Relational: wristCtrl/bahnplaner/Subsystem1/LessThanOrEqual
      # combined # wristCtrl/bahnplaner/Subsystem1/Integrator/out
      # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/Integrator/Unit Delay */
   if (X_Sb16_Unit_Delay <= Sb14_Divide2) {
      /* SLLocal: Default storage class for local variables | Width: 32 */
      Float32 Sb14_Divide;

      /* Product: wristCtrl/bahnplaner/Subsystem1/Divide */
      if (Sb14_Divide2 != 0.F) {
         /* # combined # Switch: wristCtrl/bahnplaner/Subsystem1/Switch3
            # combined # wristCtrl/bahnplaner/vd
            # combined # wristCtrl/bahnplaner/Subsystem1/v */
         Sb8_vd[1] = Sb14_Add1 / Sb14_Divide2;

         /* # combined # wristCtrl/bahnplaner/Subsystem1/Integrator/out
            # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/Integrator/Unit Delay */
         Sb14_Divide = X_Sb16_Unit_Delay / Sb14_Divide2;
      }
      else {
         if (Sb14_Add1 < 0.F) {
            /* # combined # Switch: wristCtrl/bahnplaner/Subsystem1/Switch3
               # combined # wristCtrl/bahnplaner/vd
               # combined # wristCtrl/bahnplaner/Subsystem1/v */
            Sb8_vd[1] = -3.402823466e+38F;
         }
         else {
            /* # combined # Switch: wristCtrl/bahnplaner/Subsystem1/Switch3
               # combined # wristCtrl/bahnplaner/vd
               # combined # wristCtrl/bahnplaner/Subsystem1/v */
            Sb8_vd[1] = 3.402823466e+38F;
         }

         /* # combined # wristCtrl/bahnplaner/Subsystem1/Integrator/out
            # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/Integrator/Unit Delay */
         if (X_Sb16_Unit_Delay < 0.F) {
            Sb14_Divide = -3.402823466e+38F;
         }
         else {
            Sb14_Divide = 3.402823466e+38F;
         }
      }
      Sb14_Divide = Sb14_Divide * Sb14_Add1;

      /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch2
         # combined # wristCtrl/bahnplaner/xd
         # combined # wristCtrl/bahnplaner/Subsystem1/y
         # combined # Sum: wristCtrl/bahnplaner/Subsystem1/Add
         # combined # Unit delay: wristCtrl/bahnplaner/Subsystem1/startPos */
      Sb8_xd[1] = Sb14_Divide + X_Sb14_startPos;
   }
   else {
      /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch3
         # combined # wristCtrl/bahnplaner/vd
         # combined # wristCtrl/bahnplaner/Subsystem1/v */
      Sb8_vd[1] = 0.F;

      /* Switch: wristCtrl/bahnplaner/Subsystem1/Switch2
         # combined # wristCtrl/bahnplaner/xd
         # combined # wristCtrl/bahnplaner/Subsystem1/y
         # combined # wristCtrl/bahnplaner/Subsystem1/desPos
         # combined # wristCtrl/bahnplaner/desPos */
      Sb8_xd[1] = *desPos_cyl3;
   }

   /* Sum: wristCtrl/Subtract */
   Sb1_Subtract[0] = Sb8_xd[0] - Sb1_Gain[0];
   Sb1_Subtract[1] = Sb8_xd[1] - Sb1_Gain[1];

   /* Switch: wristCtrl/KI_reduction/Switch
      wristCtrl/KI_reduction/Switch: Omitted comparison with constant.
      # combined # Relational: wristCtrl/KI_reduction/Less Than
      # combined # Abs: wristCtrl/KI_reduction/Abs
      # combined # wristCtrl/KI_reduction/e_cyl */
   if (((Float32) fabs((Float64) Sb1_Subtract[0])) < 1.F) {
      /* Switch: wristCtrl/KI_reduction/Switch */
      Sb4_Switch = 0.1F;
   }
   else {
      /* Switch: wristCtrl/KI_reduction/Switch */
      Sb4_Switch = 1.F;
   }

   /* Switch: wristCtrl/KI_reduction/Switch1
      wristCtrl/KI_reduction/Switch1: Omitted comparison with constant.
      # combined # Relational: wristCtrl/KI_reduction/Less Than1
      # combined # Abs: wristCtrl/KI_reduction/Abs1
      # combined # wristCtrl/KI_reduction/e_cyl */
   if (((Float32) fabs((Float64) Sb1_Subtract[1])) < 1.F) {
      /* Switch: wristCtrl/KI_reduction/Switch1 */
      Sb4_Switch1 = 0.1F;
   }
   else {
      /* Switch: wristCtrl/KI_reduction/Switch1 */
      Sb4_Switch1 = 1.F;
   }

   /* wristCtrl/KI_reduction/Rate Limiter1: First run initialization */
   if (Sb1_wristCtrl_FirstRun) {
      X_Sb4_Rate_Limiter = 0.F;
      X_Sb4_Rate_Limiter1 = 0.F;
   }

   /* wristCtrl/KI_reduction/Rate Limiter: deviation */
   Aux_F32 = Sb4_Switch - X_Sb4_Rate_Limiter;
   if (Aux_F32 > 0.025F) {
      /* wristCtrl/KI_reduction/Rate Limiter: limit rising rate  */
      X_Sb4_Rate_Limiter += 0.025F;
   }
   else {
      if (Aux_F32 < -0.025F) {
         /* wristCtrl/KI_reduction/Rate Limiter: limit falling rate  */
         X_Sb4_Rate_Limiter += -0.025F;
      }
      else {
         X_Sb4_Rate_Limiter = Sb4_Switch;
      }
   }

   /* wristCtrl/KI_reduction/Rate Limiter1: deviation */
   Aux_F32 = Sb4_Switch1 - X_Sb4_Rate_Limiter1;
   if (Aux_F32 > 0.025F) {
      /* wristCtrl/KI_reduction/Rate Limiter1: limit rising rate  */
      X_Sb4_Rate_Limiter1 += 0.025F;
   }
   else {
      if (Aux_F32 < -0.025F) {
         /* wristCtrl/KI_reduction/Rate Limiter1: limit falling rate  */
         X_Sb4_Rate_Limiter1 += -0.025F;
      }
      else {
         X_Sb4_Rate_Limiter1 = Sb4_Switch1;
      }
   }

   /* Sum: wristCtrl/Integrator/Add
      # combined # Gain: wristCtrl/Integrator/Gain
      # combined # wristCtrl/Integrator/in
      # combined # Product: wristCtrl/Product1
      # combined # Gain: wristCtrl/Gain1
      # combined # wristCtrl/KI_reduction/kI
      # combined # wristCtrl/KI_reduction/Rate Limiter: output  */
   Sb3_Add[0] = (X_Sb4_Rate_Limiter * (Sb1_Subtract[0] * wristCtrl_tuning.I) * 0.005F) +
    X_Sb3_Unit_Delay[0];

   /* Sum: wristCtrl/Integrator/Add
      # combined # Gain: wristCtrl/Integrator/Gain
      # combined # wristCtrl/Integrator/in
      # combined # Product: wristCtrl/Product1
      # combined # Gain: wristCtrl/Gain1
      # combined # wristCtrl/KI_reduction/kI
      # combined # wristCtrl/KI_reduction/Rate Limiter1: output  */
   Sb3_Add[1] = (X_Sb4_Rate_Limiter1 * (Sb1_Subtract[1] * wristCtrl_tuning.I) * 0.005F) +
    X_Sb3_Unit_Delay[1];

   /* MinMax: wristCtrl/Integrator/Saturate/MinMaxMinMax: wristCtrl/Integrator/Saturate/MinMax
      # combined # wristCtrl/Integrator/Saturate/In1 */
   if (Sb3_Add[0] < wristCtrl_const.limit_I) {
      /* # combined # wristCtrl/Integrator/Saturate/In1 */
      Sb9_MinMax[0] = Sb3_Add[0];
   }
   else {
      Sb9_MinMax[0] = wristCtrl_const.limit_I;
   }
   if (Sb3_Add[1] < wristCtrl_const.limit_I) {
      /* # combined # wristCtrl/Integrator/Saturate/In1 */
      Sb9_MinMax[1] = Sb3_Add[1];
   }
   else {
      Sb9_MinMax[1] = wristCtrl_const.limit_I;
   }

   /* Gain: wristCtrl/Integrator/Saturate/Gain1 */
   Sb9_Gain1 = wristCtrl_const.limit_I * -1.F;

   /* MinMax: wristCtrl/Integrator/Saturate/MinMax1MinMax: wristCtrl/Integrator/Saturate/MinMax1 */
   if (Sb9_MinMax[0] > Sb9_Gain1) {
      Sb9_MinMax1[0] = Sb9_MinMax[0];
   }
   else {
      Sb9_MinMax1[0] = Sb9_Gain1;
   }

   /* Product: wristCtrl/Integrator/Product
      # combined # Unit delay: wristCtrl/Integrator/Unit Delay
      # combined # wristCtrl/Integrator/Saturate/Out1
      # combined # Logical: wristCtrl/Integrator/Logical Operator */
   X_Sb3_Unit_Delay[0] = ((Float32) (!(Sb3_reset[0]))) * Sb9_MinMax1[0];

   /* MinMax: wristCtrl/Integrator/Saturate/MinMax1MinMax: wristCtrl/Integrator/Saturate/MinMax1 */
   if (Sb9_MinMax[1] > Sb9_Gain1) {
      Sb9_MinMax1[1] = Sb9_MinMax[1];
   }
   else {
      Sb9_MinMax1[1] = Sb9_Gain1;
   }

   /* Product: wristCtrl/Integrator/Product
      # combined # Unit delay: wristCtrl/Integrator/Unit Delay
      # combined # wristCtrl/Integrator/Saturate/Out1
      # combined # Logical: wristCtrl/Integrator/Logical Operator */
   X_Sb3_Unit_Delay[1] = ((Float32) (!(Sb3_reset[1]))) * Sb9_MinMax1[1];

   /* Discrete Integrator: wristCtrl/PT1_diskret1/Discrete-Time Integrator2: Condition for either ed
      ge trigger
      # combined # wristCtrl/PT1_diskret1/reset */
   if (Sb1_OR && (X_Sb6_Discrete__ator2_TriggerIn <= 0.F) && ((((Float32) Sb1_OR) !=
    X_Sb6_Discrete__ator2_TriggerIn) && (Sb6_Discrete_T__ator2_LastEvent != 1))) {
      Sb6_Discrete_T__ator2_LastEvent = 1;
   }
   else {
      /* # combined # wristCtrl/PT1_diskret1/reset */
      if ((!(Sb1_OR)) && (X_Sb6_Discrete__ator2_TriggerIn > 0.F) && ((((Float32) Sb1_OR) !=
       X_Sb6_Discrete__ator2_TriggerIn) && (Sb6_Discrete_T__ator2_LastEvent != -1))) {
         Sb6_Discrete_T__ator2_LastEvent = -1;
      }
      else {
         Sb6_Discrete_T__ator2_LastEvent = 0;
      }
   }

   /* Discrete Integrator: wristCtrl/PT1_diskret1/Discrete-Time Integrator2: Trigger update code
      # combined # wristCtrl/PT1_diskret1/reset */
   X_Sb6_Discrete__ator2_TriggerIn = (Float32) Sb1_OR;

   /* Discrete Integrator: wristCtrl/PT1_diskret1/Discrete-Time Integrator2: Condition for either ed
      ge trigger */
   if (Sb6_Discrete_T__ator2_LastEvent != 0) {
      /* # combined # wristCtrl/PT1_diskret1/u */
      X_Sb6_Discrete_Time_Integrator2 = Sb1_Subtract[0];
   }
   else {
      /* Discrete Integrator: wristCtrl/PT1_diskret1/Discrete-Time Integrator2 */
      if (Sb1_wristCtrl_FirstRun) {
         /* Discrete Integrator: first run initialization
            # combined # wristCtrl/PT1_diskret1/u */
         X_Sb6_Discrete_Time_Integrator2 = Sb1_Subtract[0];
      }
      else {
         /* Discrete Integrator: integration */
         X_Sb6_Discrete_Time_Integrator2 += (U_Sb6_Discrete_Time_Integrator2 * 0.005F);
      }
   }

   /* Saturation: wristCtrl/PT1_diskret2/Saturation
      # combined # wristCtrl/PT1_diskret2/f */
   if (wristCtrl_const.f_diff_x > 100000.F) {
      Sb6_Saturation = 100000.F;
      Sb7_Saturation = 100000.F;
   }
   else {
      /* # combined # wristCtrl/PT1_diskret2/f */
      if (wristCtrl_const.f_diff_x < 0.1F) {
         Sb6_Saturation = 0.1F;
         Sb7_Saturation = 0.1F;
      }
      else {
         /* # combined # wristCtrl/PT1_diskret1/f */
         Sb6_Saturation = wristCtrl_const.f_diff_x;

         /* # combined # wristCtrl/PT1_diskret2/f */
         Sb7_Saturation = wristCtrl_const.f_diff_x;
      }
   }

   /* Gain: wristCtrl/PT1_diskret1/Gain
      # combined # Product: wristCtrl/PT1_diskret1/Product
      # combined # Sum: wristCtrl/PT1_diskret1/Add
      # combined # Discrete Integrator: wristCtrl/PT1_diskret1/Discrete-Time Integrator2
      # combined # wristCtrl/PT1_diskret1/u */
   U_Sb6_Discrete_Time_Integrator2 = Sb6_Saturation * (Sb1_Subtract[0] -
    X_Sb6_Discrete_Time_Integrator2) * 6.2831853071795862F;

   /* Discrete Integrator: wristCtrl/PT1_diskret2/Discrete-Time Integrator2: Condition for either ed
      ge trigger
      # combined # wristCtrl/PT1_diskret2/reset */
   if (Sb1_OR && (X_Sb7_Discrete__ator2_TriggerIn <= 0.F) && ((((Float32) Sb1_OR) !=
    X_Sb7_Discrete__ator2_TriggerIn) && (Sb7_Discrete_T__ator2_LastEvent != 1))) {
      Sb7_Discrete_T__ator2_LastEvent = 1;
   }
   else {
      /* # combined # wristCtrl/PT1_diskret2/reset */
      if ((!(Sb1_OR)) && (X_Sb7_Discrete__ator2_TriggerIn > 0.F) && ((((Float32) Sb1_OR) !=
       X_Sb7_Discrete__ator2_TriggerIn) && (Sb7_Discrete_T__ator2_LastEvent != -1))) {
         Sb7_Discrete_T__ator2_LastEvent = -1;
      }
      else {
         Sb7_Discrete_T__ator2_LastEvent = 0;
      }
   }

   /* Discrete Integrator: wristCtrl/PT1_diskret2/Discrete-Time Integrator2: Trigger update code
      # combined # wristCtrl/PT1_diskret2/reset */
   X_Sb7_Discrete__ator2_TriggerIn = (Float32) Sb1_OR;

   /* Discrete Integrator: wristCtrl/PT1_diskret2/Discrete-Time Integrator2: Condition for either ed
      ge trigger */
   if (Sb7_Discrete_T__ator2_LastEvent != 0) {
      /* # combined # wristCtrl/PT1_diskret2/u */
      X_Sb7_Discrete_Time_Integrator2 = Sb1_Subtract[1];
   }
   else {
      /* Discrete Integrator: wristCtrl/PT1_diskret2/Discrete-Time Integrator2 */
      if (Sb1_wristCtrl_FirstRun) {
         /* Discrete Integrator: first run initialization
            # combined # wristCtrl/PT1_diskret2/u */
         X_Sb7_Discrete_Time_Integrator2 = Sb1_Subtract[1];
      }
      else {
         /* Discrete Integrator: integration */
         X_Sb7_Discrete_Time_Integrator2 += (U_Sb7_Discrete_Time_Integrator2 * 0.005F);
      }
   }

   /* Gain: wristCtrl/PT1_diskret2/Gain
      # combined # Product: wristCtrl/PT1_diskret2/Product
      # combined # Sum: wristCtrl/PT1_diskret2/Add
      # combined # Discrete Integrator: wristCtrl/PT1_diskret2/Discrete-Time Integrator2
      # combined # wristCtrl/PT1_diskret2/u */
   U_Sb7_Discrete_Time_Integrator2 = Sb7_Saturation * (Sb1_Subtract[1] -
    X_Sb7_Discrete_Time_Integrator2) * 6.2831853071795862F;

   /* Switch: wristCtrl/Switch
      wristCtrl/Switch: Omitted comparison with constant. */
   if (*enable) {
      /* SLLocal: Default storage class for local variables | Width: 32 */
      Float32 Sb5_Product;
      Float32 Sb5_Product1;
      Float32 Sb5_Subtract2[2];

      /* Product: wristCtrl/Kraft - Druck Umrechnung/Product1 */
      Sb5_Product1 = wristCtrl_const.p4 * wristCtrl_const.A4;

      /* Product: wristCtrl/Kraft - Druck Umrechnung/Product
         # combined # Sum: wristCtrl/Kraft - Druck Umrechnung/Add */
      Sb5_Product = 100000.F * (wristCtrl_const.A4 - wristCtrl_const.A2);

      /* Sum: wristCtrl/Kraft - Druck Umrechnung/Subtract2
         # combined # wristCtrl/Kraft - Druck Umrechnung/FpSoll
         # combined # Sum: wristCtrl/Add
         # combined # Gain: wristCtrl/Gain3
         # combined # wristCtrl/Integrator/out
         # combined # Unit delay: wristCtrl/Integrator/Unit Delay
         # combined # Gain: wristCtrl/Gain2
         # combined # Gain: wristCtrl/Gain4
         # combined # wristCtrl/PT1_diskret1/dy */
      Sb5_Subtract2[0] = Sb5_Product1 - ((Sb8_vd[0] * wristCtrl_tuning.FF) + (Sb1_Subtract[0] *
       wristCtrl_tuning.P) + X_Sb3_Unit_Delay[0] + (U_Sb6_Discrete_Time_Integrator2 *
       wristCtrl_tuning.D)) - Sb5_Product;

      /* Sum: wristCtrl/Kraft - Druck Umrechnung/Subtract2
         # combined # wristCtrl/Kraft - Druck Umrechnung/FpSoll
         # combined # Sum: wristCtrl/Add
         # combined # Gain: wristCtrl/Gain3
         # combined # wristCtrl/Integrator/out
         # combined # Unit delay: wristCtrl/Integrator/Unit Delay
         # combined # Gain: wristCtrl/Gain2
         # combined # Gain: wristCtrl/Gain4
         # combined # wristCtrl/PT1_diskret2/dy */
      Sb5_Subtract2[1] = Sb5_Product1 - ((Sb8_vd[1] * wristCtrl_tuning.FF) + (Sb1_Subtract[1] *
       wristCtrl_tuning.P) + X_Sb3_Unit_Delay[1] + (U_Sb7_Discrete_Time_Integrator2 *
       wristCtrl_tuning.D)) - Sb5_Product;

      /* Product: wristCtrl/Kraft - Druck Umrechnung/Divide */
      if (wristCtrl_const.A2 != 0.F) {
         /* # combined # Switch: wristCtrl/Switch
            # combined # TargetLink outport: wristCtrl/p2d_cyl2
            # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll */
         *p2d_cyl2 = Sb5_Subtract2[0] / wristCtrl_const.A2;

         /* # combined # Switch: wristCtrl/Switch1
            # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll
            # combined # TargetLink outport: wristCtrl/p2d_cyl3 */
         *p2d_cyl3 = Sb5_Subtract2[1] / wristCtrl_const.A2;
      }
      else {
         if (Sb5_Subtract2[0] < 0.F) {
            /* # combined # Switch: wristCtrl/Switch
               # combined # TargetLink outport: wristCtrl/p2d_cyl2
               # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll */
            *p2d_cyl2 = -3.402823466e+38F;
         }
         else {
            /* # combined # Switch: wristCtrl/Switch
               # combined # TargetLink outport: wristCtrl/p2d_cyl2
               # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll */
            *p2d_cyl2 = 3.402823466e+38F;
         }
         if (Sb5_Subtract2[1] < 0.F) {
            /* # combined # Switch: wristCtrl/Switch1
               # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll
               # combined # TargetLink outport: wristCtrl/p2d_cyl3 */
            *p2d_cyl3 = -3.402823466e+38F;
         }
         else {
            /* # combined # Switch: wristCtrl/Switch1
               # combined # wristCtrl/Kraft - Druck Umrechnung/p2Soll
               # combined # TargetLink outport: wristCtrl/p2d_cyl3 */
            *p2d_cyl3 = 3.402823466e+38F;
         }
      }
   }
   else {
      /* Switch: wristCtrl/Switch1
         # combined # TargetLink outport: wristCtrl/p2d_cyl3 */
      *p2d_cyl3 = 0.F;

      /* Switch: wristCtrl/Switch
         # combined # TargetLink outport: wristCtrl/p2d_cyl2 */
      *p2d_cyl2 = 0.F;
   }

   /* wristCtrl: Reset of the first run state */
   Sb1_wristCtrl_FirstRun = 0;
}

/*------------------------------------------------------------------------------------------------*\
  MODULE LOCAL FUNCTION DEFINITIONS
\*------------------------------------------------------------------------------------------------*/
#ifdef __cplusplus
}
#endif

#endif /* WRISTCTRL_C */
/*------------------------------------------------------------------------------------------------*\
  END OF FILE
\*------------------------------------------------------------------------------------------------*/
