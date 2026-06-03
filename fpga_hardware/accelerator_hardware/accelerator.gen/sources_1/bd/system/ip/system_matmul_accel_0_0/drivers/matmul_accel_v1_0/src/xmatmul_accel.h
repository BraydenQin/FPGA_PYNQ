// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2024.2 (64-bit)
// Tool Version Limit: 2024.11
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
#ifndef XMATMUL_ACCEL_H
#define XMATMUL_ACCEL_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xmatmul_accel_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
#ifdef SDT
    char *Name;
#else
    u16 DeviceId;
#endif
    u64 Control_BaseAddress;
} XMatmul_accel_Config;
#endif

typedef struct {
    u64 Control_BaseAddress;
    u32 IsReady;
} XMatmul_accel;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XMatmul_accel_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XMatmul_accel_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XMatmul_accel_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XMatmul_accel_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
#ifdef SDT
int XMatmul_accel_Initialize(XMatmul_accel *InstancePtr, UINTPTR BaseAddress);
XMatmul_accel_Config* XMatmul_accel_LookupConfig(UINTPTR BaseAddress);
#else
int XMatmul_accel_Initialize(XMatmul_accel *InstancePtr, u16 DeviceId);
XMatmul_accel_Config* XMatmul_accel_LookupConfig(u16 DeviceId);
#endif
int XMatmul_accel_CfgInitialize(XMatmul_accel *InstancePtr, XMatmul_accel_Config *ConfigPtr);
#else
int XMatmul_accel_Initialize(XMatmul_accel *InstancePtr, const char* InstanceName);
int XMatmul_accel_Release(XMatmul_accel *InstancePtr);
#endif

void XMatmul_accel_Start(XMatmul_accel *InstancePtr);
u32 XMatmul_accel_IsDone(XMatmul_accel *InstancePtr);
u32 XMatmul_accel_IsIdle(XMatmul_accel *InstancePtr);
u32 XMatmul_accel_IsReady(XMatmul_accel *InstancePtr);
void XMatmul_accel_EnableAutoRestart(XMatmul_accel *InstancePtr);
void XMatmul_accel_DisableAutoRestart(XMatmul_accel *InstancePtr);

void XMatmul_accel_Set_input_a(XMatmul_accel *InstancePtr, u64 Data);
u64 XMatmul_accel_Get_input_a(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_input_b(XMatmul_accel *InstancePtr, u64 Data);
u64 XMatmul_accel_Get_input_b(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_output_c(XMatmul_accel *InstancePtr, u64 Data);
u64 XMatmul_accel_Get_output_c(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_M(XMatmul_accel *InstancePtr, u32 Data);
u32 XMatmul_accel_Get_M(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_K(XMatmul_accel *InstancePtr, u32 Data);
u32 XMatmul_accel_Get_K(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_N(XMatmul_accel *InstancePtr, u32 Data);
u32 XMatmul_accel_Get_N(XMatmul_accel *InstancePtr);
void XMatmul_accel_Set_shift(XMatmul_accel *InstancePtr, u32 Data);
u32 XMatmul_accel_Get_shift(XMatmul_accel *InstancePtr);

void XMatmul_accel_InterruptGlobalEnable(XMatmul_accel *InstancePtr);
void XMatmul_accel_InterruptGlobalDisable(XMatmul_accel *InstancePtr);
void XMatmul_accel_InterruptEnable(XMatmul_accel *InstancePtr, u32 Mask);
void XMatmul_accel_InterruptDisable(XMatmul_accel *InstancePtr, u32 Mask);
void XMatmul_accel_InterruptClear(XMatmul_accel *InstancePtr, u32 Mask);
u32 XMatmul_accel_InterruptGetEnabled(XMatmul_accel *InstancePtr);
u32 XMatmul_accel_InterruptGetStatus(XMatmul_accel *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
