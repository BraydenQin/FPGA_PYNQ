//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2024.2 (win64) Build 5239630 Fri Nov 08 22:35:27 MST 2024
//Date        : Wed Jun  3 05:23:46 2026
//Host        : LAPTOP-SV114DSC running 64-bit major release  (build 9200)
//Command     : generate_target system.bd
//Design      : system
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CORE_GENERATION_INFO = "system,IP_Integrator,{x_ipVendor=xilinx.com,x_ipLibrary=BlockDiagram,x_ipName=system,x_ipVersion=1.00.a,x_ipLanguage=VERILOG,numBlks=4,numReposBlks=4,numNonXlnxBlks=0,numHierBlks=0,maxHierDepth=0,numSysgenBlks=0,numHlsBlks=1,numHdlrefBlks=0,numPkgbdBlks=0,bdsource=USER,da_axi4_cnt=5,da_ps7_cnt=1,synth_mode=Hierarchical}" *) (* HW_HANDOFF = "system.hwdef" *) 
module system
   (DDR_addr,
    DDR_ba,
    DDR_cas_n,
    DDR_ck_n,
    DDR_ck_p,
    DDR_cke,
    DDR_cs_n,
    DDR_dm,
    DDR_dq,
    DDR_dqs_n,
    DDR_dqs_p,
    DDR_odt,
    DDR_ras_n,
    DDR_reset_n,
    DDR_we_n,
    FIXED_IO_ddr_vrn,
    FIXED_IO_ddr_vrp,
    FIXED_IO_mio,
    FIXED_IO_ps_clk,
    FIXED_IO_ps_porb,
    FIXED_IO_ps_srstb);
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ADDR" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME DDR, AXI_ARBITRATION_SCHEME TDM, BURST_LENGTH 8, CAN_DEBUG false, CAS_LATENCY 11, CAS_WRITE_LATENCY 11, CS_ENABLED true, DATA_MASK_ENABLED true, DATA_WIDTH 8, MEMORY_TYPE COMPONENTS, MEM_ADDR_MAP ROW_COLUMN_BANK, SLOT Single, TIMEPERIOD_PS 1250" *) inout [14:0]DDR_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR BA" *) inout [2:0]DDR_ba;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CAS_N" *) inout DDR_cas_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_N" *) inout DDR_ck_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CK_P" *) inout DDR_ck_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CKE" *) inout DDR_cke;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR CS_N" *) inout DDR_cs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DM" *) inout [3:0]DDR_dm;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQ" *) inout [31:0]DDR_dq;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_N" *) inout [3:0]DDR_dqs_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR DQS_P" *) inout [3:0]DDR_dqs_p;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR ODT" *) inout DDR_odt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RAS_N" *) inout DDR_ras_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR RESET_N" *) inout DDR_reset_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:ddrx:1.0 DDR WE_N" *) inout DDR_we_n;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRN" *) (* X_INTERFACE_MODE = "Master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME FIXED_IO, CAN_DEBUG false" *) inout FIXED_IO_ddr_vrn;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO DDR_VRP" *) inout FIXED_IO_ddr_vrp;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO MIO" *) inout [53:0]FIXED_IO_mio;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_CLK" *) inout FIXED_IO_ps_clk;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_PORB" *) inout FIXED_IO_ps_porb;
  (* X_INTERFACE_INFO = "xilinx.com:display_processing_system7:fixedio:1.0 FIXED_IO PS_SRSTB" *) inout FIXED_IO_ps_srstb;

  wire [14:0]DDR_addr;
  wire [2:0]DDR_ba;
  wire DDR_cas_n;
  wire DDR_ck_n;
  wire DDR_ck_p;
  wire DDR_cke;
  wire DDR_cs_n;
  wire [3:0]DDR_dm;
  wire [31:0]DDR_dq;
  wire [3:0]DDR_dqs_n;
  wire [3:0]DDR_dqs_p;
  wire DDR_odt;
  wire DDR_ras_n;
  wire DDR_reset_n;
  wire DDR_we_n;
  wire FIXED_IO_ddr_vrn;
  wire FIXED_IO_ddr_vrp;
  wire [53:0]FIXED_IO_mio;
  wire FIXED_IO_ps_clk;
  wire FIXED_IO_ps_porb;
  wire FIXED_IO_ps_srstb;
  wire [63:0]matmul_accel_0_m_axi_gmem0_ARADDR;
  wire [1:0]matmul_accel_0_m_axi_gmem0_ARBURST;
  wire [3:0]matmul_accel_0_m_axi_gmem0_ARCACHE;
  wire [0:0]matmul_accel_0_m_axi_gmem0_ARID;
  wire [7:0]matmul_accel_0_m_axi_gmem0_ARLEN;
  wire [1:0]matmul_accel_0_m_axi_gmem0_ARLOCK;
  wire [2:0]matmul_accel_0_m_axi_gmem0_ARPROT;
  wire [3:0]matmul_accel_0_m_axi_gmem0_ARQOS;
  wire matmul_accel_0_m_axi_gmem0_ARREADY;
  wire [2:0]matmul_accel_0_m_axi_gmem0_ARSIZE;
  wire matmul_accel_0_m_axi_gmem0_ARVALID;
  wire [31:0]matmul_accel_0_m_axi_gmem0_RDATA;
  wire [0:0]matmul_accel_0_m_axi_gmem0_RID;
  wire matmul_accel_0_m_axi_gmem0_RLAST;
  wire matmul_accel_0_m_axi_gmem0_RREADY;
  wire [1:0]matmul_accel_0_m_axi_gmem0_RRESP;
  wire matmul_accel_0_m_axi_gmem0_RVALID;
  wire [63:0]matmul_accel_0_m_axi_gmem1_ARADDR;
  wire [1:0]matmul_accel_0_m_axi_gmem1_ARBURST;
  wire [3:0]matmul_accel_0_m_axi_gmem1_ARCACHE;
  wire [0:0]matmul_accel_0_m_axi_gmem1_ARID;
  wire [7:0]matmul_accel_0_m_axi_gmem1_ARLEN;
  wire [1:0]matmul_accel_0_m_axi_gmem1_ARLOCK;
  wire [2:0]matmul_accel_0_m_axi_gmem1_ARPROT;
  wire [3:0]matmul_accel_0_m_axi_gmem1_ARQOS;
  wire matmul_accel_0_m_axi_gmem1_ARREADY;
  wire [2:0]matmul_accel_0_m_axi_gmem1_ARSIZE;
  wire matmul_accel_0_m_axi_gmem1_ARVALID;
  wire [31:0]matmul_accel_0_m_axi_gmem1_RDATA;
  wire [0:0]matmul_accel_0_m_axi_gmem1_RID;
  wire matmul_accel_0_m_axi_gmem1_RLAST;
  wire matmul_accel_0_m_axi_gmem1_RREADY;
  wire [1:0]matmul_accel_0_m_axi_gmem1_RRESP;
  wire matmul_accel_0_m_axi_gmem1_RVALID;
  wire [63:0]matmul_accel_0_m_axi_gmem2_AWADDR;
  wire [1:0]matmul_accel_0_m_axi_gmem2_AWBURST;
  wire [3:0]matmul_accel_0_m_axi_gmem2_AWCACHE;
  wire [0:0]matmul_accel_0_m_axi_gmem2_AWID;
  wire [7:0]matmul_accel_0_m_axi_gmem2_AWLEN;
  wire [1:0]matmul_accel_0_m_axi_gmem2_AWLOCK;
  wire [2:0]matmul_accel_0_m_axi_gmem2_AWPROT;
  wire [3:0]matmul_accel_0_m_axi_gmem2_AWQOS;
  wire matmul_accel_0_m_axi_gmem2_AWREADY;
  wire [2:0]matmul_accel_0_m_axi_gmem2_AWSIZE;
  wire matmul_accel_0_m_axi_gmem2_AWVALID;
  wire [0:0]matmul_accel_0_m_axi_gmem2_BID;
  wire matmul_accel_0_m_axi_gmem2_BREADY;
  wire [1:0]matmul_accel_0_m_axi_gmem2_BRESP;
  wire matmul_accel_0_m_axi_gmem2_BVALID;
  wire [31:0]matmul_accel_0_m_axi_gmem2_WDATA;
  wire matmul_accel_0_m_axi_gmem2_WLAST;
  wire matmul_accel_0_m_axi_gmem2_WREADY;
  wire [3:0]matmul_accel_0_m_axi_gmem2_WSTRB;
  wire matmul_accel_0_m_axi_gmem2_WVALID;
  wire [0:0]proc_sys_reset_0_peripheral_aresetn;
  wire processing_system7_0_FCLK_CLK0;
  wire processing_system7_0_FCLK_RESET0_N;
  wire [31:0]processing_system7_0_M_AXI_GP0_ARADDR;
  wire [1:0]processing_system7_0_M_AXI_GP0_ARBURST;
  wire [3:0]processing_system7_0_M_AXI_GP0_ARCACHE;
  wire [11:0]processing_system7_0_M_AXI_GP0_ARID;
  wire [3:0]processing_system7_0_M_AXI_GP0_ARLEN;
  wire [1:0]processing_system7_0_M_AXI_GP0_ARLOCK;
  wire [2:0]processing_system7_0_M_AXI_GP0_ARPROT;
  wire [3:0]processing_system7_0_M_AXI_GP0_ARQOS;
  wire processing_system7_0_M_AXI_GP0_ARREADY;
  wire [2:0]processing_system7_0_M_AXI_GP0_ARSIZE;
  wire processing_system7_0_M_AXI_GP0_ARVALID;
  wire [31:0]processing_system7_0_M_AXI_GP0_AWADDR;
  wire [1:0]processing_system7_0_M_AXI_GP0_AWBURST;
  wire [3:0]processing_system7_0_M_AXI_GP0_AWCACHE;
  wire [11:0]processing_system7_0_M_AXI_GP0_AWID;
  wire [3:0]processing_system7_0_M_AXI_GP0_AWLEN;
  wire [1:0]processing_system7_0_M_AXI_GP0_AWLOCK;
  wire [2:0]processing_system7_0_M_AXI_GP0_AWPROT;
  wire [3:0]processing_system7_0_M_AXI_GP0_AWQOS;
  wire processing_system7_0_M_AXI_GP0_AWREADY;
  wire [2:0]processing_system7_0_M_AXI_GP0_AWSIZE;
  wire processing_system7_0_M_AXI_GP0_AWVALID;
  wire [11:0]processing_system7_0_M_AXI_GP0_BID;
  wire processing_system7_0_M_AXI_GP0_BREADY;
  wire [1:0]processing_system7_0_M_AXI_GP0_BRESP;
  wire processing_system7_0_M_AXI_GP0_BVALID;
  wire [31:0]processing_system7_0_M_AXI_GP0_RDATA;
  wire [11:0]processing_system7_0_M_AXI_GP0_RID;
  wire processing_system7_0_M_AXI_GP0_RLAST;
  wire processing_system7_0_M_AXI_GP0_RREADY;
  wire [1:0]processing_system7_0_M_AXI_GP0_RRESP;
  wire processing_system7_0_M_AXI_GP0_RVALID;
  wire [31:0]processing_system7_0_M_AXI_GP0_WDATA;
  wire [11:0]processing_system7_0_M_AXI_GP0_WID;
  wire processing_system7_0_M_AXI_GP0_WLAST;
  wire processing_system7_0_M_AXI_GP0_WREADY;
  wire [3:0]processing_system7_0_M_AXI_GP0_WSTRB;
  wire processing_system7_0_M_AXI_GP0_WVALID;
  wire [6:0]smartconnect_0_M01_AXI_ARADDR;
  wire smartconnect_0_M01_AXI_ARREADY;
  wire smartconnect_0_M01_AXI_ARVALID;
  wire [6:0]smartconnect_0_M01_AXI_AWADDR;
  wire smartconnect_0_M01_AXI_AWREADY;
  wire smartconnect_0_M01_AXI_AWVALID;
  wire smartconnect_0_M01_AXI_BREADY;
  wire [1:0]smartconnect_0_M01_AXI_BRESP;
  wire smartconnect_0_M01_AXI_BVALID;
  wire [31:0]smartconnect_0_M01_AXI_RDATA;
  wire smartconnect_0_M01_AXI_RREADY;
  wire [1:0]smartconnect_0_M01_AXI_RRESP;
  wire smartconnect_0_M01_AXI_RVALID;
  wire [31:0]smartconnect_0_M01_AXI_WDATA;
  wire smartconnect_0_M01_AXI_WREADY;
  wire [3:0]smartconnect_0_M01_AXI_WSTRB;
  wire smartconnect_0_M01_AXI_WVALID;

  system_matmul_accel_0_0 matmul_accel_0
       (.ap_clk(processing_system7_0_FCLK_CLK0),
        .ap_rst_n(proc_sys_reset_0_peripheral_aresetn),
        .m_axi_gmem0_ARADDR(matmul_accel_0_m_axi_gmem0_ARADDR),
        .m_axi_gmem0_ARBURST(matmul_accel_0_m_axi_gmem0_ARBURST),
        .m_axi_gmem0_ARCACHE(matmul_accel_0_m_axi_gmem0_ARCACHE),
        .m_axi_gmem0_ARID(matmul_accel_0_m_axi_gmem0_ARID),
        .m_axi_gmem0_ARLEN(matmul_accel_0_m_axi_gmem0_ARLEN),
        .m_axi_gmem0_ARLOCK(matmul_accel_0_m_axi_gmem0_ARLOCK),
        .m_axi_gmem0_ARPROT(matmul_accel_0_m_axi_gmem0_ARPROT),
        .m_axi_gmem0_ARQOS(matmul_accel_0_m_axi_gmem0_ARQOS),
        .m_axi_gmem0_ARREADY(matmul_accel_0_m_axi_gmem0_ARREADY),
        .m_axi_gmem0_ARSIZE(matmul_accel_0_m_axi_gmem0_ARSIZE),
        .m_axi_gmem0_ARVALID(matmul_accel_0_m_axi_gmem0_ARVALID),
        .m_axi_gmem0_AWREADY(1'b0),
        .m_axi_gmem0_BID(1'b0),
        .m_axi_gmem0_BRESP({1'b0,1'b0}),
        .m_axi_gmem0_BVALID(1'b0),
        .m_axi_gmem0_RDATA(matmul_accel_0_m_axi_gmem0_RDATA),
        .m_axi_gmem0_RID(matmul_accel_0_m_axi_gmem0_RID),
        .m_axi_gmem0_RLAST(matmul_accel_0_m_axi_gmem0_RLAST),
        .m_axi_gmem0_RREADY(matmul_accel_0_m_axi_gmem0_RREADY),
        .m_axi_gmem0_RRESP(matmul_accel_0_m_axi_gmem0_RRESP),
        .m_axi_gmem0_RVALID(matmul_accel_0_m_axi_gmem0_RVALID),
        .m_axi_gmem0_WREADY(1'b0),
        .m_axi_gmem1_ARADDR(matmul_accel_0_m_axi_gmem1_ARADDR),
        .m_axi_gmem1_ARBURST(matmul_accel_0_m_axi_gmem1_ARBURST),
        .m_axi_gmem1_ARCACHE(matmul_accel_0_m_axi_gmem1_ARCACHE),
        .m_axi_gmem1_ARID(matmul_accel_0_m_axi_gmem1_ARID),
        .m_axi_gmem1_ARLEN(matmul_accel_0_m_axi_gmem1_ARLEN),
        .m_axi_gmem1_ARLOCK(matmul_accel_0_m_axi_gmem1_ARLOCK),
        .m_axi_gmem1_ARPROT(matmul_accel_0_m_axi_gmem1_ARPROT),
        .m_axi_gmem1_ARQOS(matmul_accel_0_m_axi_gmem1_ARQOS),
        .m_axi_gmem1_ARREADY(matmul_accel_0_m_axi_gmem1_ARREADY),
        .m_axi_gmem1_ARSIZE(matmul_accel_0_m_axi_gmem1_ARSIZE),
        .m_axi_gmem1_ARVALID(matmul_accel_0_m_axi_gmem1_ARVALID),
        .m_axi_gmem1_AWREADY(1'b0),
        .m_axi_gmem1_BID(1'b0),
        .m_axi_gmem1_BRESP({1'b0,1'b0}),
        .m_axi_gmem1_BVALID(1'b0),
        .m_axi_gmem1_RDATA(matmul_accel_0_m_axi_gmem1_RDATA),
        .m_axi_gmem1_RID(matmul_accel_0_m_axi_gmem1_RID),
        .m_axi_gmem1_RLAST(matmul_accel_0_m_axi_gmem1_RLAST),
        .m_axi_gmem1_RREADY(matmul_accel_0_m_axi_gmem1_RREADY),
        .m_axi_gmem1_RRESP(matmul_accel_0_m_axi_gmem1_RRESP),
        .m_axi_gmem1_RVALID(matmul_accel_0_m_axi_gmem1_RVALID),
        .m_axi_gmem1_WREADY(1'b0),
        .m_axi_gmem2_ARREADY(1'b0),
        .m_axi_gmem2_AWADDR(matmul_accel_0_m_axi_gmem2_AWADDR),
        .m_axi_gmem2_AWBURST(matmul_accel_0_m_axi_gmem2_AWBURST),
        .m_axi_gmem2_AWCACHE(matmul_accel_0_m_axi_gmem2_AWCACHE),
        .m_axi_gmem2_AWID(matmul_accel_0_m_axi_gmem2_AWID),
        .m_axi_gmem2_AWLEN(matmul_accel_0_m_axi_gmem2_AWLEN),
        .m_axi_gmem2_AWLOCK(matmul_accel_0_m_axi_gmem2_AWLOCK),
        .m_axi_gmem2_AWPROT(matmul_accel_0_m_axi_gmem2_AWPROT),
        .m_axi_gmem2_AWQOS(matmul_accel_0_m_axi_gmem2_AWQOS),
        .m_axi_gmem2_AWREADY(matmul_accel_0_m_axi_gmem2_AWREADY),
        .m_axi_gmem2_AWSIZE(matmul_accel_0_m_axi_gmem2_AWSIZE),
        .m_axi_gmem2_AWVALID(matmul_accel_0_m_axi_gmem2_AWVALID),
        .m_axi_gmem2_BID(matmul_accel_0_m_axi_gmem2_BID),
        .m_axi_gmem2_BREADY(matmul_accel_0_m_axi_gmem2_BREADY),
        .m_axi_gmem2_BRESP(matmul_accel_0_m_axi_gmem2_BRESP),
        .m_axi_gmem2_BVALID(matmul_accel_0_m_axi_gmem2_BVALID),
        .m_axi_gmem2_RDATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .m_axi_gmem2_RID(1'b0),
        .m_axi_gmem2_RLAST(1'b0),
        .m_axi_gmem2_RRESP({1'b0,1'b0}),
        .m_axi_gmem2_RVALID(1'b0),
        .m_axi_gmem2_WDATA(matmul_accel_0_m_axi_gmem2_WDATA),
        .m_axi_gmem2_WLAST(matmul_accel_0_m_axi_gmem2_WLAST),
        .m_axi_gmem2_WREADY(matmul_accel_0_m_axi_gmem2_WREADY),
        .m_axi_gmem2_WSTRB(matmul_accel_0_m_axi_gmem2_WSTRB),
        .m_axi_gmem2_WVALID(matmul_accel_0_m_axi_gmem2_WVALID),
        .s_axi_control_ARADDR(smartconnect_0_M01_AXI_ARADDR),
        .s_axi_control_ARREADY(smartconnect_0_M01_AXI_ARREADY),
        .s_axi_control_ARVALID(smartconnect_0_M01_AXI_ARVALID),
        .s_axi_control_AWADDR(smartconnect_0_M01_AXI_AWADDR),
        .s_axi_control_AWREADY(smartconnect_0_M01_AXI_AWREADY),
        .s_axi_control_AWVALID(smartconnect_0_M01_AXI_AWVALID),
        .s_axi_control_BREADY(smartconnect_0_M01_AXI_BREADY),
        .s_axi_control_BRESP(smartconnect_0_M01_AXI_BRESP),
        .s_axi_control_BVALID(smartconnect_0_M01_AXI_BVALID),
        .s_axi_control_RDATA(smartconnect_0_M01_AXI_RDATA),
        .s_axi_control_RREADY(smartconnect_0_M01_AXI_RREADY),
        .s_axi_control_RRESP(smartconnect_0_M01_AXI_RRESP),
        .s_axi_control_RVALID(smartconnect_0_M01_AXI_RVALID),
        .s_axi_control_WDATA(smartconnect_0_M01_AXI_WDATA),
        .s_axi_control_WREADY(smartconnect_0_M01_AXI_WREADY),
        .s_axi_control_WSTRB(smartconnect_0_M01_AXI_WSTRB),
        .s_axi_control_WVALID(smartconnect_0_M01_AXI_WVALID));
  system_proc_sys_reset_0_0 proc_sys_reset_0
       (.aux_reset_in(1'b1),
        .dcm_locked(1'b1),
        .ext_reset_in(processing_system7_0_FCLK_RESET0_N),
        .mb_debug_sys_rst(1'b0),
        .peripheral_aresetn(proc_sys_reset_0_peripheral_aresetn),
        .slowest_sync_clk(processing_system7_0_FCLK_CLK0));
  system_processing_system7_0_0 processing_system7_0
       (.DDR_Addr(DDR_addr),
        .DDR_BankAddr(DDR_ba),
        .DDR_CAS_n(DDR_cas_n),
        .DDR_CKE(DDR_cke),
        .DDR_CS_n(DDR_cs_n),
        .DDR_Clk(DDR_ck_p),
        .DDR_Clk_n(DDR_ck_n),
        .DDR_DM(DDR_dm),
        .DDR_DQ(DDR_dq),
        .DDR_DQS(DDR_dqs_p),
        .DDR_DQS_n(DDR_dqs_n),
        .DDR_DRSTB(DDR_reset_n),
        .DDR_ODT(DDR_odt),
        .DDR_RAS_n(DDR_ras_n),
        .DDR_VRN(FIXED_IO_ddr_vrn),
        .DDR_VRP(FIXED_IO_ddr_vrp),
        .DDR_WEB(DDR_we_n),
        .FCLK_CLK0(processing_system7_0_FCLK_CLK0),
        .FCLK_RESET0_N(processing_system7_0_FCLK_RESET0_N),
        .MIO(FIXED_IO_mio),
        .M_AXI_GP0_ACLK(processing_system7_0_FCLK_CLK0),
        .M_AXI_GP0_ARADDR(processing_system7_0_M_AXI_GP0_ARADDR),
        .M_AXI_GP0_ARBURST(processing_system7_0_M_AXI_GP0_ARBURST),
        .M_AXI_GP0_ARCACHE(processing_system7_0_M_AXI_GP0_ARCACHE),
        .M_AXI_GP0_ARID(processing_system7_0_M_AXI_GP0_ARID),
        .M_AXI_GP0_ARLEN(processing_system7_0_M_AXI_GP0_ARLEN),
        .M_AXI_GP0_ARLOCK(processing_system7_0_M_AXI_GP0_ARLOCK),
        .M_AXI_GP0_ARPROT(processing_system7_0_M_AXI_GP0_ARPROT),
        .M_AXI_GP0_ARQOS(processing_system7_0_M_AXI_GP0_ARQOS),
        .M_AXI_GP0_ARREADY(processing_system7_0_M_AXI_GP0_ARREADY),
        .M_AXI_GP0_ARSIZE(processing_system7_0_M_AXI_GP0_ARSIZE),
        .M_AXI_GP0_ARVALID(processing_system7_0_M_AXI_GP0_ARVALID),
        .M_AXI_GP0_AWADDR(processing_system7_0_M_AXI_GP0_AWADDR),
        .M_AXI_GP0_AWBURST(processing_system7_0_M_AXI_GP0_AWBURST),
        .M_AXI_GP0_AWCACHE(processing_system7_0_M_AXI_GP0_AWCACHE),
        .M_AXI_GP0_AWID(processing_system7_0_M_AXI_GP0_AWID),
        .M_AXI_GP0_AWLEN(processing_system7_0_M_AXI_GP0_AWLEN),
        .M_AXI_GP0_AWLOCK(processing_system7_0_M_AXI_GP0_AWLOCK),
        .M_AXI_GP0_AWPROT(processing_system7_0_M_AXI_GP0_AWPROT),
        .M_AXI_GP0_AWQOS(processing_system7_0_M_AXI_GP0_AWQOS),
        .M_AXI_GP0_AWREADY(processing_system7_0_M_AXI_GP0_AWREADY),
        .M_AXI_GP0_AWSIZE(processing_system7_0_M_AXI_GP0_AWSIZE),
        .M_AXI_GP0_AWVALID(processing_system7_0_M_AXI_GP0_AWVALID),
        .M_AXI_GP0_BID(processing_system7_0_M_AXI_GP0_BID),
        .M_AXI_GP0_BREADY(processing_system7_0_M_AXI_GP0_BREADY),
        .M_AXI_GP0_BRESP(processing_system7_0_M_AXI_GP0_BRESP),
        .M_AXI_GP0_BVALID(processing_system7_0_M_AXI_GP0_BVALID),
        .M_AXI_GP0_RDATA(processing_system7_0_M_AXI_GP0_RDATA),
        .M_AXI_GP0_RID(processing_system7_0_M_AXI_GP0_RID),
        .M_AXI_GP0_RLAST(processing_system7_0_M_AXI_GP0_RLAST),
        .M_AXI_GP0_RREADY(processing_system7_0_M_AXI_GP0_RREADY),
        .M_AXI_GP0_RRESP(processing_system7_0_M_AXI_GP0_RRESP),
        .M_AXI_GP0_RVALID(processing_system7_0_M_AXI_GP0_RVALID),
        .M_AXI_GP0_WDATA(processing_system7_0_M_AXI_GP0_WDATA),
        .M_AXI_GP0_WID(processing_system7_0_M_AXI_GP0_WID),
        .M_AXI_GP0_WLAST(processing_system7_0_M_AXI_GP0_WLAST),
        .M_AXI_GP0_WREADY(processing_system7_0_M_AXI_GP0_WREADY),
        .M_AXI_GP0_WSTRB(processing_system7_0_M_AXI_GP0_WSTRB),
        .M_AXI_GP0_WVALID(processing_system7_0_M_AXI_GP0_WVALID),
        .PS_CLK(FIXED_IO_ps_clk),
        .PS_PORB(FIXED_IO_ps_porb),
        .PS_SRSTB(FIXED_IO_ps_srstb),
        .USB0_VBUS_PWRFAULT(1'b0));
  system_smartconnect_0_0 smartconnect_0
       (.M00_AXI_arready(1'b0),
        .M00_AXI_awready(1'b0),
        .M00_AXI_bresp({1'b0,1'b0}),
        .M00_AXI_bvalid(1'b0),
        .M00_AXI_rdata({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .M00_AXI_rresp({1'b0,1'b0}),
        .M00_AXI_rvalid(1'b0),
        .M00_AXI_wready(1'b0),
        .M01_AXI_araddr(smartconnect_0_M01_AXI_ARADDR),
        .M01_AXI_arready(smartconnect_0_M01_AXI_ARREADY),
        .M01_AXI_arvalid(smartconnect_0_M01_AXI_ARVALID),
        .M01_AXI_awaddr(smartconnect_0_M01_AXI_AWADDR),
        .M01_AXI_awready(smartconnect_0_M01_AXI_AWREADY),
        .M01_AXI_awvalid(smartconnect_0_M01_AXI_AWVALID),
        .M01_AXI_bready(smartconnect_0_M01_AXI_BREADY),
        .M01_AXI_bresp(smartconnect_0_M01_AXI_BRESP),
        .M01_AXI_bvalid(smartconnect_0_M01_AXI_BVALID),
        .M01_AXI_rdata(smartconnect_0_M01_AXI_RDATA),
        .M01_AXI_rready(smartconnect_0_M01_AXI_RREADY),
        .M01_AXI_rresp(smartconnect_0_M01_AXI_RRESP),
        .M01_AXI_rvalid(smartconnect_0_M01_AXI_RVALID),
        .M01_AXI_wdata(smartconnect_0_M01_AXI_WDATA),
        .M01_AXI_wready(smartconnect_0_M01_AXI_WREADY),
        .M01_AXI_wstrb(smartconnect_0_M01_AXI_WSTRB),
        .M01_AXI_wvalid(smartconnect_0_M01_AXI_WVALID),
        .S00_AXI_araddr(processing_system7_0_M_AXI_GP0_ARADDR),
        .S00_AXI_arburst(processing_system7_0_M_AXI_GP0_ARBURST),
        .S00_AXI_arcache(processing_system7_0_M_AXI_GP0_ARCACHE),
        .S00_AXI_arid(processing_system7_0_M_AXI_GP0_ARID),
        .S00_AXI_arlen(processing_system7_0_M_AXI_GP0_ARLEN),
        .S00_AXI_arlock(processing_system7_0_M_AXI_GP0_ARLOCK),
        .S00_AXI_arprot(processing_system7_0_M_AXI_GP0_ARPROT),
        .S00_AXI_arqos(processing_system7_0_M_AXI_GP0_ARQOS),
        .S00_AXI_arready(processing_system7_0_M_AXI_GP0_ARREADY),
        .S00_AXI_arsize(processing_system7_0_M_AXI_GP0_ARSIZE),
        .S00_AXI_arvalid(processing_system7_0_M_AXI_GP0_ARVALID),
        .S00_AXI_awaddr(processing_system7_0_M_AXI_GP0_AWADDR),
        .S00_AXI_awburst(processing_system7_0_M_AXI_GP0_AWBURST),
        .S00_AXI_awcache(processing_system7_0_M_AXI_GP0_AWCACHE),
        .S00_AXI_awid(processing_system7_0_M_AXI_GP0_AWID),
        .S00_AXI_awlen(processing_system7_0_M_AXI_GP0_AWLEN),
        .S00_AXI_awlock(processing_system7_0_M_AXI_GP0_AWLOCK),
        .S00_AXI_awprot(processing_system7_0_M_AXI_GP0_AWPROT),
        .S00_AXI_awqos(processing_system7_0_M_AXI_GP0_AWQOS),
        .S00_AXI_awready(processing_system7_0_M_AXI_GP0_AWREADY),
        .S00_AXI_awsize(processing_system7_0_M_AXI_GP0_AWSIZE),
        .S00_AXI_awvalid(processing_system7_0_M_AXI_GP0_AWVALID),
        .S00_AXI_bid(processing_system7_0_M_AXI_GP0_BID),
        .S00_AXI_bready(processing_system7_0_M_AXI_GP0_BREADY),
        .S00_AXI_bresp(processing_system7_0_M_AXI_GP0_BRESP),
        .S00_AXI_bvalid(processing_system7_0_M_AXI_GP0_BVALID),
        .S00_AXI_rdata(processing_system7_0_M_AXI_GP0_RDATA),
        .S00_AXI_rid(processing_system7_0_M_AXI_GP0_RID),
        .S00_AXI_rlast(processing_system7_0_M_AXI_GP0_RLAST),
        .S00_AXI_rready(processing_system7_0_M_AXI_GP0_RREADY),
        .S00_AXI_rresp(processing_system7_0_M_AXI_GP0_RRESP),
        .S00_AXI_rvalid(processing_system7_0_M_AXI_GP0_RVALID),
        .S00_AXI_wdata(processing_system7_0_M_AXI_GP0_WDATA),
        .S00_AXI_wid(processing_system7_0_M_AXI_GP0_WID),
        .S00_AXI_wlast(processing_system7_0_M_AXI_GP0_WLAST),
        .S00_AXI_wready(processing_system7_0_M_AXI_GP0_WREADY),
        .S00_AXI_wstrb(processing_system7_0_M_AXI_GP0_WSTRB),
        .S00_AXI_wvalid(processing_system7_0_M_AXI_GP0_WVALID),
        .S01_AXI_araddr(matmul_accel_0_m_axi_gmem0_ARADDR),
        .S01_AXI_arburst(matmul_accel_0_m_axi_gmem0_ARBURST),
        .S01_AXI_arcache(matmul_accel_0_m_axi_gmem0_ARCACHE),
        .S01_AXI_arid(matmul_accel_0_m_axi_gmem0_ARID),
        .S01_AXI_arlen(matmul_accel_0_m_axi_gmem0_ARLEN),
        .S01_AXI_arlock(matmul_accel_0_m_axi_gmem0_ARLOCK[0]),
        .S01_AXI_arprot(matmul_accel_0_m_axi_gmem0_ARPROT),
        .S01_AXI_arqos(matmul_accel_0_m_axi_gmem0_ARQOS),
        .S01_AXI_arready(matmul_accel_0_m_axi_gmem0_ARREADY),
        .S01_AXI_arsize(matmul_accel_0_m_axi_gmem0_ARSIZE),
        .S01_AXI_arvalid(matmul_accel_0_m_axi_gmem0_ARVALID),
        .S01_AXI_rdata(matmul_accel_0_m_axi_gmem0_RDATA),
        .S01_AXI_rid(matmul_accel_0_m_axi_gmem0_RID),
        .S01_AXI_rlast(matmul_accel_0_m_axi_gmem0_RLAST),
        .S01_AXI_rready(matmul_accel_0_m_axi_gmem0_RREADY),
        .S01_AXI_rresp(matmul_accel_0_m_axi_gmem0_RRESP),
        .S01_AXI_rvalid(matmul_accel_0_m_axi_gmem0_RVALID),
        .S02_AXI_araddr(matmul_accel_0_m_axi_gmem1_ARADDR),
        .S02_AXI_arburst(matmul_accel_0_m_axi_gmem1_ARBURST),
        .S02_AXI_arcache(matmul_accel_0_m_axi_gmem1_ARCACHE),
        .S02_AXI_arid(matmul_accel_0_m_axi_gmem1_ARID),
        .S02_AXI_arlen(matmul_accel_0_m_axi_gmem1_ARLEN),
        .S02_AXI_arlock(matmul_accel_0_m_axi_gmem1_ARLOCK[0]),
        .S02_AXI_arprot(matmul_accel_0_m_axi_gmem1_ARPROT),
        .S02_AXI_arqos(matmul_accel_0_m_axi_gmem1_ARQOS),
        .S02_AXI_arready(matmul_accel_0_m_axi_gmem1_ARREADY),
        .S02_AXI_arsize(matmul_accel_0_m_axi_gmem1_ARSIZE),
        .S02_AXI_arvalid(matmul_accel_0_m_axi_gmem1_ARVALID),
        .S02_AXI_rdata(matmul_accel_0_m_axi_gmem1_RDATA),
        .S02_AXI_rid(matmul_accel_0_m_axi_gmem1_RID),
        .S02_AXI_rlast(matmul_accel_0_m_axi_gmem1_RLAST),
        .S02_AXI_rready(matmul_accel_0_m_axi_gmem1_RREADY),
        .S02_AXI_rresp(matmul_accel_0_m_axi_gmem1_RRESP),
        .S02_AXI_rvalid(matmul_accel_0_m_axi_gmem1_RVALID),
        .S03_AXI_awaddr(matmul_accel_0_m_axi_gmem2_AWADDR),
        .S03_AXI_awburst(matmul_accel_0_m_axi_gmem2_AWBURST),
        .S03_AXI_awcache(matmul_accel_0_m_axi_gmem2_AWCACHE),
        .S03_AXI_awid(matmul_accel_0_m_axi_gmem2_AWID),
        .S03_AXI_awlen(matmul_accel_0_m_axi_gmem2_AWLEN),
        .S03_AXI_awlock(matmul_accel_0_m_axi_gmem2_AWLOCK[0]),
        .S03_AXI_awprot(matmul_accel_0_m_axi_gmem2_AWPROT),
        .S03_AXI_awqos(matmul_accel_0_m_axi_gmem2_AWQOS),
        .S03_AXI_awready(matmul_accel_0_m_axi_gmem2_AWREADY),
        .S03_AXI_awsize(matmul_accel_0_m_axi_gmem2_AWSIZE),
        .S03_AXI_awvalid(matmul_accel_0_m_axi_gmem2_AWVALID),
        .S03_AXI_bid(matmul_accel_0_m_axi_gmem2_BID),
        .S03_AXI_bready(matmul_accel_0_m_axi_gmem2_BREADY),
        .S03_AXI_bresp(matmul_accel_0_m_axi_gmem2_BRESP),
        .S03_AXI_bvalid(matmul_accel_0_m_axi_gmem2_BVALID),
        .S03_AXI_wdata(matmul_accel_0_m_axi_gmem2_WDATA),
        .S03_AXI_wlast(matmul_accel_0_m_axi_gmem2_WLAST),
        .S03_AXI_wready(matmul_accel_0_m_axi_gmem2_WREADY),
        .S03_AXI_wstrb(matmul_accel_0_m_axi_gmem2_WSTRB),
        .S03_AXI_wvalid(matmul_accel_0_m_axi_gmem2_WVALID),
        .aclk(processing_system7_0_FCLK_CLK0),
        .aresetn(proc_sys_reset_0_peripheral_aresetn));
endmodule
