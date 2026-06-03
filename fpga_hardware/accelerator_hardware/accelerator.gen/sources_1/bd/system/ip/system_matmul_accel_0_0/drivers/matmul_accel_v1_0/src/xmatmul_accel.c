// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2024.2 (64-bit)
// Tool Version Limit: 2024.11
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
/***************************** Include Files *********************************/
#include "xmatmul_accel.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XMatmul_accel_CfgInitialize(XMatmul_accel *InstancePtr, XMatmul_accel_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Control_BaseAddress = ConfigPtr->Control_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XMatmul_accel_Start(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL) & 0x80;
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XMatmul_accel_IsDone(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XMatmul_accel_IsIdle(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XMatmul_accel_IsReady(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XMatmul_accel_EnableAutoRestart(XMatmul_accel *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL, 0x80);
}

void XMatmul_accel_DisableAutoRestart(XMatmul_accel *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_AP_CTRL, 0);
}

void XMatmul_accel_Set_input_a(XMatmul_accel *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_A_DATA, (u32)(Data));
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_A_DATA + 4, (u32)(Data >> 32));
}

u64 XMatmul_accel_Get_input_a(XMatmul_accel *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_A_DATA);
    Data += (u64)XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_A_DATA + 4) << 32;
    return Data;
}

void XMatmul_accel_Set_input_b(XMatmul_accel *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_B_DATA, (u32)(Data));
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_B_DATA + 4, (u32)(Data >> 32));
}

u64 XMatmul_accel_Get_input_b(XMatmul_accel *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_B_DATA);
    Data += (u64)XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_INPUT_B_DATA + 4) << 32;
    return Data;
}

void XMatmul_accel_Set_output_c(XMatmul_accel *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_OUTPUT_C_DATA, (u32)(Data));
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_OUTPUT_C_DATA + 4, (u32)(Data >> 32));
}

u64 XMatmul_accel_Get_output_c(XMatmul_accel *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_OUTPUT_C_DATA);
    Data += (u64)XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_OUTPUT_C_DATA + 4) << 32;
    return Data;
}

void XMatmul_accel_Set_M(XMatmul_accel *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_M_DATA, Data);
}

u32 XMatmul_accel_Get_M(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_M_DATA);
    return Data;
}

void XMatmul_accel_Set_K(XMatmul_accel *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_K_DATA, Data);
}

u32 XMatmul_accel_Get_K(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_K_DATA);
    return Data;
}

void XMatmul_accel_Set_N(XMatmul_accel *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_N_DATA, Data);
}

u32 XMatmul_accel_Get_N(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_N_DATA);
    return Data;
}

void XMatmul_accel_Set_shift(XMatmul_accel *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_SHIFT_DATA, Data);
}

u32 XMatmul_accel_Get_shift(XMatmul_accel *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_SHIFT_DATA);
    return Data;
}

void XMatmul_accel_InterruptGlobalEnable(XMatmul_accel *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_GIE, 1);
}

void XMatmul_accel_InterruptGlobalDisable(XMatmul_accel *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_GIE, 0);
}

void XMatmul_accel_InterruptEnable(XMatmul_accel *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_IER);
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_IER, Register | Mask);
}

void XMatmul_accel_InterruptDisable(XMatmul_accel *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_IER);
    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_IER, Register & (~Mask));
}

void XMatmul_accel_InterruptClear(XMatmul_accel *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XMatmul_accel_WriteReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_ISR, Mask);
}

u32 XMatmul_accel_InterruptGetEnabled(XMatmul_accel *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_IER);
}

u32 XMatmul_accel_InterruptGetStatus(XMatmul_accel *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XMatmul_accel_ReadReg(InstancePtr->Control_BaseAddress, XMATMUL_ACCEL_CONTROL_ADDR_ISR);
}

