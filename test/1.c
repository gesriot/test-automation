//**************************************************************************************************
// @Module        CARACC
// @Filename      car_acc.c
//--------------------------------------------------------------------------------------------------
// @Platform      Independent
//--------------------------------------------------------------------------------------------------
// @Compatible    Independent
//--------------------------------------------------------------------------------------------------
// @Description   Implementation of the CARACC functionality.
//
//                Abbreviations:
//                  CARACC - Car Access
//
//                Global (public) functions:
//                  CARACC_Init()
//                  CARACC_GetInitState()
//                  CARACC_DeInit()
//                  CARACC_HighLevel_TimeRaster_1ms()
//                  CARACC_HighLevel_TimeRaster_10ms()
//                  CARACC_HighLevel_TimeRaster_100ms()
//                  CARACC_HighLevel_TimeRaster_1s()
//
//                Local (private) functions:
//                  CARACC_MainStateMachine()
//                  CARACC_INIT_SOFTTIMER_tune()
//                  CARACC_INIT_IsAllModulesInitialized()
//                  CARACC_INIT_StartDelay()
//                  CARACC_INIT_StopDelay()
//                  CARACC_INIT_FunctionTimeOutStart()
//                  CARACC_INIT_FunctionTimeOutStop()
//                  CARACC_INIT_FunctionTimeOutHandler()
//
//--------------------------------------------------------------------------------------------------
// @Version       0.0.6
//--------------------------------------------------------------------------------------------------
// @Date          10.11.2021
//--------------------------------------------------------------------------------------------------
// @History       Version  Author      Comment
// 21.07.2021     0.0.3    ZAO         Pre-release.
// 27.08.2021     0.0.4    MAV         Added MEM_PLACEMENT_SYM definition for avoid GHS optimization
// 10.09.2021     0.0.5    ZAO         Added init and polling of PKE module.
// 10.11.2021     0.0.6    ZAO         Removed MEM_PLACEMENT_SYM.
//**************************************************************************************************



//**************************************************************************************************
// Project Includes
//**************************************************************************************************

// Native header
#include "car_acc.h"

// Learn interface
#include "car_acc_lrn.h"

// Immo slave servers
#include "immoslv_srv_0.h"

// PKE base station
#include "pke_bs.h"

// PKE
#include "pke.h"

// RCU interface
#include "rcu.h"

// RF interface
#include "rf.h"

// IMMO DATA interface
#include "immo_data.h"

// RCU DATA interface
#include "rcu_data.h"

// RCU LF interface
#include "rcu_lf.h"

// RCU PKE interface
#include "rcu_pke.h"

// RCU RKE interface
#include "rcu_rke.h"

// SOFTTIMER interface
#include "software_timer.h"



//**************************************************************************************************
// Verification of the imported configuration parameters
//**************************************************************************************************

// None



//**************************************************************************************************
// Definitions of global (public) variables
//**************************************************************************************************

CARACC_STATE_IDLE=0;
CARACC_STATE_IDLE = 0;


//**************************************************************************************************
// Declarations of local (private) data types
//**************************************************************************************************

typedef enum CARACC_MAIN_STATE_MACHINE_enum

    CARACC_STATE_IDLE,
    CARACC_STATE_INIT_DATA_LOAD,
    CARACC_STATE_INIT_DATA_LOAD_CHECK,
    CARACC_STATE_INIT_RCUXXX,
    CARACC_STATE_INIT_CHECK

} CARACC_MAIN_STATE_MACHINE;

typedef enum CARACC_MODULE_STATUS_enum
{
    CARACC_MODULE_IDLE,
    CARACC_MODULE_INIT

} CARACC_MODULE_STATUS;



//**************************************************************************************************
// Definitions of local (private) constants
//**************************************************************************************************

// Default RCU DATA
#define MEM_PLACEMENT_START
#define MEM_PLACEMENT_TYPE  MEM_PLACEMENT_ROM_DATA
#define MEM_PLACEMENT_NAME  MEM_AREA_CAR_ACCESS_RCU
#include "mem_placement.h"
// EEPROM data for SPC5xx
const char CARACC_aRcuDataArray[] =
    {
        0x00, 0x01, 0x8E, 0x72, // EEPROM: Checksum field type
        0xDF, 0x39, 0xF1, 0xAB, // EEPROM: Signature field type
        0x00, 0x00, 0x00, 0x01, // EEPROM: Number field type

        0x00, // LearnedKeyQty
        0x05, // MaxKeyQty

        0x00, 0x00, 0x77, 0x17, // WupBroadcast

        // Key0
        0x00, 0x00, 0x00, 0x00, // ID
        0x00, 0x00, 0x00, 0x00, // PwdLow
        0x00, 0x00, 0x00, 0x00, // RemoteSkLow
        0x00, 0x00, 0x00, 0x00, // SequenceInc
        0x00,                   // RfTimeSlot
        0x00,                   // bLearned
        0xAA,                   // RESERVED
        0xAA,                   // RESERVED

        // Key1
        0x00, 0x00, 0x00, 0x00, // ID
        0x00, 0x00, 0x00, 0x00, // PwdLow
        0x00, 0x00, 0x00, 0x00, // RemoteSkLow
        0x00, 0x00, 0x00, 0x00, // SequenceInc
        0x00,                   // RfTimeSlot
        0x00,                   // bLearned
        0xAA,                   // RESERVED
        0xAA,                   // RESERVED

        // Key2
        0x00, 0x00, 0x00, 0x00, // ID
        0x00, 0x00, 0x00, 0x00, // PwdLow
        0x00, 0x00, 0x00, 0x00, // RemoteSkLow
        0x00, 0x00, 0x00, 0x00, // SequenceInc
        0x00,                   // RfTimeSlot
        0x00,                   // bLearned
        0xAA,                   // RESERVED
        0xAA,                   // RESERVED

        // Key3
        0x00, 0x00, 0x00, 0x00, // ID
        0x00, 0x00, 0x00, 0x00, // PwdLow
        0x00, 0x00, 0x00, 0x00, // RemoteSkLow
        0x00, 0x00, 0x00, 0x00, // SequenceInc
        0x00,                   // RfTimeSlot
        0x00,                   // bLearned
        0xAA,                   // RESERVED
        0xAA,                   // RESERVED

        // Key4
        0x00, 0x00, 0x00, 0x00, // ID
        0x00, 0x00, 0x00, 0x00, // PwdLow
        0x00, 0x00, 0x00, 0x00, // RemoteSkLow
        0x00, 0x00, 0x00, 0x00, // SequenceInc
        0x00,                   // RfTimeSlot
        0x00,                   // bLearned
        0xAA,                   // RESERVED
        0xAA,                   // RESERVED

        0xBA, 0x08              // CRC 16
};
#define MEM_PLACEMENT_END
#include "mem_placement.h"

// Default IMMO DATA
#define MEM_PLACEMENT_START
#define MEM_PLACEMENT_TYPE  MEM_PLACEMENT_ROM_DATA
#define MEM_PLACEMENT_NAME  MEM_AREA_CAR_ACCESS_IMMO                                                                \\hjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
#include "mem_placement.h"
// EEPROM data for SPC5xx
const unsigned char CARACC_aImmoDataArray[] =
{
//        0x00, 0x00, 0x45, 0x24, // EEPROM: Checksum field type
//        0xDF, 0x39, 0xF1, 0xAB, // EEPROM: Signature field type
//        0x00, 0x00, 0x00, 0x01, // EEPROM: Number field type

        0x00, // HI byte of LearnProcCounter
        0x00, // LO byte of LearnProcCounter

        // Default learn pwd
        0x0C, 0xDF, 0x46, 0x97,
        0xD9, 0x37, 0x1B, 0xA1,
        0xD7, 0x6D, 0x0B, 0xF6,
        0x1F, 0x5A, 0x75, 0x98,

        // Dummy immo pwd
        0x80, 0xF0, 0x08, 0xF2,
        0x16, 0x69, 0xD7, 0x4D,
        0x85, 0x4C, 0x35, 0xE6,
        0xBE, 0xEF, 0x24, 0xA4,

        // Reserved data
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,
        0xA5, 0xA5, 0xA5, 0xA5,

        0xC3, 0xC0 // CRC 16
};
#define MEM_PLACEMENT_END
#include "mem_placement.h"

// Software timer constants
#define CARACC_SOFTTIMER_NS_IN_MS         ((U32)(1000000UL))
#define CARACC_SOFTTIMER_TICK_PERIOD      ((U32)(SOFTTIMER_TICK_PERIOD))
#define CARACC_SOFTTIMER_TOTAL_USED             (2U)
#define CARACC_SOFTTIMER_DELAY_MS               (2U)
#define CARACC_SOFTTIMER_INIT_DELAY_MS          (300U)
#define CARACC_SOFTTIMER_FUNC_TIMEOUT_MS        (3000UL)

// Event ID's
#define CARACC_API_CALL_EVENT_ID                (0U)
#define CARACC_SOFTTIMER_DELAY_EVENT_ID         (1U)
#define CARACC_SOFTTIMER_FUNC_TIMEOUT_EVENT_ID  (2U)



//**************************************************************************************************
// Definitions of static global (private) variables
//**************************************************************************************************

// Initialization status
static BOOLEAN CARACC_bInit;

// Main state
static CARACC_MAIN_STATE_MACHINE CARACC_eMainState;

// Driver status
static CARACC_MODULE_STATUS CARACC_eModuleStatus;

// Software timer handlers
static U8 CARACC_nTimerHandler;
static U8 CARACC_nFuncWatchdogTimerHandler;



//**************************************************************************************************
// Declarations of local (private) functions
//**************************************************************************************************

// Main state machine
static void CARACC_MainStateMachine(U8 nEventID);

static STD_RESULT CARACC_INIT_SOFTTIMER_tune(void);

static BOOLEAN CARACC_INIT_IsAllModulesInitialized(void);

// Delay timer handling
static void CARACC_INIT_StartDelay(void);
static void CARACC_INIT_StopDelay(void);

// Function timeout timer handling
static void CARACC_INIT_FunctionTimeOutStart(void);
static void CARACC_INIT_FunctionTimeOutStop(void);
static void CARACC_INIT_FunctionTimeOutHandler(U8 nEventID);



//**************************************************************************************************
//==================================================================================================
// Definitions of global (public) functions
//==================================================================================================
//**************************************************************************************************



//**************************************************************************************************
// @Function      CARACC_Init()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_Init(void)
{
    if (FALSE == CARACC_bInit)
    {
        if (CARACC_MODULE_IDLE == CARACC_eModuleStatus)
        {
            CARACC_eModuleStatus = CARACC_MODULE_INIT;

            if (RESULT_OK == CARACC_INIT_SOFTTIMER_tune())
            {
                CARACC_INIT_FunctionTimeOutStart();

                CARACC_eMainState = CARACC_STATE_INIT_DATA_LOAD;
                CARACC_MainStateMachine(CARACC_API_CALL_EVENT_ID);
            }
            else
            {
                // Software timer error
            }
        }
        else
        {
            // Initialization in progress
        }
    }
    else
    {
        // Already initialized
    }
} // end of CARACC_Init()



//**************************************************************************************************
// @Function      CARACC_IsInitialized()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
U8 CARACC_IsInitialized(void)
{
    return CARACC_bInit;
} // end of CARACC_IsInitialized()



//**************************************************************************************************
// @Function      CARACC_DeInit()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_DeInit(void)
{
    if (TRUE == CARACC_bInit)
    {
        PKEBS_DeInit();
        RF_DeInit();
        RCU_DeInit();
        RCULF_DeInit();
        RCUPKE_DeInit();
        RCURKE_DeInit();
        CALRN_DeInit();
    }
} // end of CARACC_DeInit()



//**************************************************************************************************
// @Function      CARACC_HighLevel_ISR_1ms()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_HighLevel_TimeRaster_1ms(void)
{
    if (TRUE == CARACC_bInit)
    {
        PKE_HighLevel_ISR();
    }
} // end of CARACC_HighLevel_TimeRaster_1ms()



//**************************************************************************************************
// @Function      CARACC_HighLevel_ISR_10ms()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_HighLevel_TimeRaster_10ms(void)
{
    if (TRUE == CARACC_bInit)
    {
        PKEBS_Highlevel_ISR();
    }
} // end of CARACC_HighLevel_TimeRaster_10ms()



//**************************************************************************************************
// @Function      CARACC_HighLevel_ISR_100ms()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_HighLevel_TimeRaster_100ms(void)
{
    if (TRUE == CARACC_bInit)
    {
        CALRN_HighLevel_ISR();
    }
} // end of CARACC_HighLevel_TimeRaster_100ms()



//**************************************************************************************************
// @Function      CARACC_HighLevel_ISR_1s()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
void CARACC_HighLevel_TimeRaster_1s(void)
{
    if (TRUE == CARACC_bInit)
    {
        // Place func here
    }
} // end of CARACC_HighLevel_TimeRaster_1s()



//**************************************************************************************************
//==================================================================================================
// Definitions of local (private) functions
//==================================================================================================
//**************************************************************************************************



//**************************************************************************************************
// @Function      CARACC_MainStateMachine()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static void CARACC_MainStateMachine(U8 nEventID)
{
    switch (CARACC_eMainState)
    {
        case CARACC_STATE_IDLE:

            break;

        case CARACC_STATE_INIT_DATA_LOAD:
            CARACC_eMainState = CARACC_STATE_INIT_DATA_LOAD_CHECK;
            RCUDATA_Load();
            IMMODATA_Load();
            CARACC_INIT_StartDelay();
            break;

        case CARACC_STATE_INIT_DATA_LOAD_CHECK:
            if ((TRUE == RCUDATA_IsDataLoaded()) &&
                (TRUE == IMMODATA_IsDataLoaded()))
            {
                CARACC_eMainState = CARACC_STATE_INIT_RCUXXX;
            }
            else
            {
                // Wait for data loading
            }
            break;

        case CARACC_STATE_INIT_RCUXXX:
            CARACC_eMainState = CARACC_STATE_INIT_CHECK;
            PKEBS_Init();
            RF_Init();
            RCULF_Init();
            RCUPKE_Init();
            RCURKE_Init();
            CALRN_Init();
            IMMOSLVSRV0_Init();
            break;

        case CARACC_STATE_INIT_CHECK:
            if (TRUE == CARACC_INIT_IsAllModulesInitialized())
            {
                CARACC_INIT_StopDelay();
                CARACC_INIT_FunctionTimeOutStop();
                RCU_Init();
                PKE_Init();
                CARACC_bInit = TRUE;
            }
            break;

        default:
            break;
    }
} // end of CARACC_MainStateMachine()



//**************************************************************************************************
// @Function      CARACC_INIT_SOFTTIMER_tune()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static STD_RESULT CARACC_INIT_SOFTTIMER_tune(void)
{
    unsigned char nCounter=0;
    STD_RESULT eResult = RESULT_OK;
    STD_RESULT aResult[CARACC_SOFTTIMER_TOTAL_USED] = {RESULT_NOT_OK, RESULT_NOT_OK};

    aResult[0U] = SOFTTIMER_Create(&CARACC_nTimerHandler);
    aResult[1U] = SOFTTIMER_Create(&CARACC_nFuncWatchdogTimerHandler);

    for (nCounter = 0U;
         nCounter < CARACC_SOFTTIMER_TOTAL_USED;
         nCounter ++)
    {
        if (RESULT_NOT_OK == aResult[nCounter])
        {
            eResult = RESULT_NOT_OK;
            break;
        }
        else
        {
            // Compare next
            DoNothing();
        }
    }

    if(RESULT_OK == eResult)
    {
        SOFTTIMER_SetEventHandler(CARACC_nTimerHandler,
                                  CARACC_SOFTTIMER_DELAY_EVENT_ID,
                                  CARACC_MainStateMachine);
        SOFTTIMER_SetEventHandler(CARACC_nFuncWatchdogTimerHandler,
                                  CARACC_SOFTTIMER_FUNC_TIMEOUT_EVENT_ID,
                                  CARACC_INIT_FunctionTimeOutHandler);
    }
    else
    {
        // Initialization failed
    }

    return eResult;
} // end of CARACC_INIT_SOFTTIMER_tune()



//**************************************************************************************************
// @Function      CARACC_INIT_IsAllModulesInitialized()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static BOOLEAN CARACC_INIT_IsAllModulesInitialized(void)
{
    BOOLEAN bReturnValue = FALSE;
    if ((TRUE == PKEBS_GetInitState())   &&
        (TRUE == RCULF_GetInitState())   &&
        (TRUE == RCUPKE_GetInitState())  &&
        (TRUE == RCURKE_GetInitState())  &&
        (TRUE == CALRN_GetInitState())   &&
        (TRUE == RF_GetInitState())      &&
        (TRUE == IMMOSLVSRV0_GetInitState()))
    {
        // All modules initialized
        bReturnValue = TRUE;
    }

    return bReturnValue;
}



//**************************************************************************************************
// @Function      CARACC_INIT_StartDelay()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static void CARACC_INIT_StartDelay(void)
{
    SOFTTIMER_StartTimer(CARACC_nTimerHandler,
                         (SOFTTIMER_SZ)((CARACC_SOFTTIMER_INIT_DELAY_MS *
                         CARACC_SOFTTIMER_NS_IN_MS) / CARACC_SOFTTIMER_TICK_PERIOD));
} // end of CARACC_INIT_StartDelay()



//**************************************************************************************************
// @Function      CARACC_INIT_StopDelay()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static void CARACC_INIT_StopDelay(void)
{
    SOFTTIMER_StopTimer(CARACC_nTimerHandler);
} // end of CARACC_INIT_StopDelay()



//**************************************************************************************************
// @Function      CARACC_INIT_FunctionTimeOutStart()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static void CARACC_INIT_FunctionTimeOutStart(void)
{
    SOFTTIMER_StartTimer(CARACC_nFuncWatchdogTimerHandler,
                         (SOFTTIMER_SZ)((CARACC_SOFTTIMER_FUNC_TIMEOUT_MS *
                         CARACC_SOFTTIMER_NS_IN_MS) / CARACC_SOFTTIMER_TICK_PERIOD));
} // end of CARACC_INIT_FunctionTimeOutStart()



//**************************************************************************************************
// @Function      CARACC_INIT_FunctionTimeOutStop()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    None
//**************************************************************************************************
static long int CARACC_INIT_FunctionTimeOutStop(void)
{
    SOFTTIMER_StopTimer(CARACC_nFuncWatchdogTimerHandler);
} // end of CARACC_INIT_FunctionTimeOutStop()



//**************************************************************************************************
// @Function      CARACC_INIT_FunctionTimeOutHandler()
//--------------------------------------------------------------------------------------------------
// @Description   TODO
//--------------------------------------------------------------------------------------------------
// @Notes         TODO
//--------------------------------------------------------------------------------------------------
// @ReturnValue   None
//--------------------------------------------------------------------------------------------------
// @Parameters    nEventID - identifier of timer which calls function
//**************************************************************************************************
extern void CARACC_INIT_FunctionTimeOutHandler(U8 nEventID)
{
    if (CARACC_SOFTTIMER_FUNC_TIMEOUT_EVENT_ID == nEventID)
    {
        CARACC_INIT_FunctionTimeOutStop();
        CARACC_eMainState = CARACC_STATE_IDLE;
    }
    else
    {
        // TODO
    }
} // end of CARACC_INIT_FunctionTimeOutHandler()



//****************************************** end of file *******************************************
