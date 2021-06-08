/**************************************************************************************************\
 *** 
 *** Simulink model       : BionicHand_r
 *** TargetLink subsystem : BionicHand_r/fingerCtrl
 *** Codefile             : fingerCtrl.h
 ***
 *** Generated by TargetLink, the dSPACE production quality code generator
 *** Generation date: 2021-06-08 10:57:06
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
 *** Style definition file                    : C:\Appl\dSpace\dSPACE TargetLink 5.1\Matlab\Tl\Confi
 ***                                            g\codegen\cconfig.xml
 *** Root style sheet                         : C:\Appl\dSpace\dSPACE TargetLink 5.1\Matlab\Tl\XML\C
 ***                                            odeGen\Stylesheets\TL_CSourceCodeSS.xsl
 ***
 *** TargetLink version      : 5.1 from 28-Oct-2020
 *** Code generator version  : Build Id 5.1.0.29 from 2020-10-22 12:32:14
\**************************************************************************************************/

#ifndef FINGERCTRL_H
#define FINGERCTRL_H

/*------------------------------------------------------------------------------------------------*\
  DEFINES (OPT)
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  INCLUDES
\*------------------------------------------------------------------------------------------------*/

#include "tl_defines_e.h"
#include "tl_basetypes.h"
#include "udt_e.h"

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
   CAL: global calibratable parameters (ROM) | Width: N.A.
\**************************************************************************************************/
extern CAL struct finger_tuning_tag fingerCtrl_tuning_a;

/*------------------------------------------------------------------------------------------------*\
  PARAMETERIZED MACROS
\*------------------------------------------------------------------------------------------------*/
/*------------------------------------------------------------------------------------------------*\
  FUNCTION PROTOTYPES
\*------------------------------------------------------------------------------------------------*/

/**************************************************************************************************\
   GlobalStep: Default function class for not static model step functions
\**************************************************************************************************/
extern void fingerCtrl(Float32 Se1_TopFingerSensors[5], Float32 Se1_BotFingerSensors[5], Float32
    Se1_desFingerPos[7], Bool * Se1_reset, UInt16 * ActPos_cyl1, UInt16 * ActPos_DRVS, Float32 *
    desPos_cyl1, Float32 * desPos_DRVS, Bool * enable, Float32 Se1_pFinger_des[7], Float32 *
    p2d_cyl1, Float32 * p2d_DRVS, const struct finger_tuning_tag * fingerCtrl_tuning);

#ifdef __cplusplus
}
#endif

#endif /* FINGERCTRL_H */
/*------------------------------------------------------------------------------------------------*\
  END OF FILE
\*------------------------------------------------------------------------------------------------*/
