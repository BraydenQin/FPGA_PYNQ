# FPGA 矩阵乘加速器硬件层分析报告

生成日期：2026-06-03

## 1. 结论摘要

当前工程中 `fpga_hardware/accelerator_hardware` 是完整 Vivado 硬件工程，`pynq_delivery` 是面向 PYNQ 软件侧使用的交付包。两者功能有重合，但定位不同：

- `fpga_hardware/accelerator_hardware`：硬件源工程和 Vivado 生成结果，适合作为后续继续改硬件、重新综合实现、导出 XSA/bitstream 的主线。
- `pynq_delivery`：把同一个硬件设计整理成 PYNQ 侧易用的 `.bit/.hwh/.xsa/register_map` 交付文件，适合作为软件驱动集成和板端验证入口。

当前硬件实现的是一个 HLS 生成的 INT8 矩阵乘加速 IP，实例名为 `matmul_accel_0`，计算合同是：

```text
A: int8[M, K], row-major
B: int8[K, N], row-major
C: int32[M, N], row-major
C = (A @ B) >> shift
```

硬件已经完成综合、实现、布线和 bitstream 导出。系统时钟为 100 MHz，routed timing 已满足约束，WNS 为 2.460 ns，WHS 为 0.036 ns，路由错误为 0。

## 2. 硬件目录与交付目录的关系

### 2.1 `fpga_hardware/accelerator_hardware`

该目录包含 Vivado 工程和生成产物：

- `accelerator.xpr`：Vivado 工程入口。
- `AI_accelerator.xsa`：硬件平台导出文件。
- `system_wrapper.bit`：顶层 bitstream。
- `accelerator.srcs/sources_1/bd/system/system.bd`：block design。
- `accelerator.gen/sources_1/bd/system/hw_handoff/system.hwh`：Vivado 生成的硬件 handoff 元数据。
- `accelerator.runs/.../*.rpt`：综合、实现、资源、时序、功耗、路由等报告。

因此，如果后续要“尽量用 FPGA hardware 部分去做”，建议以此目录作为硬件开发源头。

### 2.2 `pynq_delivery`

该目录是给 PYNQ 软件侧使用的整理版交付物：

- `matmul_overlay.bit`
- `matmul_overlay.hwh`
- `matmul_overlay.xsa`
- `register_map.actual.json`
- `xmatmul_accel_hw.h`
- `csynth.rpt`
- `overlay_metadata.json`

其中 `.bit/.hwh` 已重命名为同一基础名 `matmul_overlay`，这符合 PYNQ `Overlay("matmul_overlay.bit")` 自动寻找同名 `.hwh` 的习惯。

## 3. 顶层硬件架构

从 Vivado HWH 和交付元数据看，系统由以下模块组成：

| 模块 | 作用 |
| --- | --- |
| `processing_system7_0` | Zynq PS，负责 ARM、DDR、固定 IO、AXI 主控等 |
| `matmul_accel_0` | HLS 生成的 INT8 GEMM 加速 IP |
| `smartconnect_0` | AXI interconnect，连接 PS、控制接口和数据访问路径 |
| `proc_sys_reset_0` | 复位控制 |

数据流可以概括为：

```text
Python/PYNQ software
  -> AXI-Lite 写寄存器：A/B/C 物理地址、M/K/N、shift、ap_start
  -> matmul_accel_0 通过 m_axi 从 DDR 读取 A/B
  -> matmul_accel_0 在 PL 中完成 INT8 MAC 和 shift
  -> matmul_accel_0 通过 m_axi 把 INT32 C 写回 DDR
  -> Python/PYNQ invalidate buffer 后读取结果
```

这说明当前设计没有单独的 CDMA/VDMA 搬运阶段，IP 本身通过 AXI master 直接访问 DDR。软件侧只负责分配连续物理 buffer、写寄存器和轮询完成状态。

## 4. IP 接口与寄存器

### 4.1 AXI master 数据接口

HLS 报告显示该 IP 有 3 个 `m_axi` 端口：

| 接口 | 方向 | 数据用途 | 软件数据宽度 | 地址宽度 | 最大 burst 长度 | Outstanding |
| --- | --- | --- | --- | --- | --- | --- |
| `m_axi_gmem0` | read only | `input_a` | 8 bit | 64 bit | 16 | 16 |
| `m_axi_gmem1` | read only | `input_b` | 8 bit | 64 bit | 16 | 16 |
| `m_axi_gmem2` | write only | `output_c` | 32 bit | 64 bit | 16 | 16 |

HWH 中对应 AXI data width 参数为 32 bit，HLS 报告里的 8/32 bit 是从 C 类型角度看到的软件数据宽度。实际总线侧会经由 HLS AXI 适配逻辑访问 DDR。

### 4.2 AXI-Lite 控制接口

控制接口为 `s_axi_control`，数据宽度 32 bit，地址宽度 7 bit。寄存器表如下：

| 逻辑名 | Offset | 作用 |
| --- | --- | --- |
| `CTRL` | `0x00` | `ap_start/ap_done/ap_idle/ap_ready/auto_restart/interrupt` |
| `GIE` | `0x04` | 全局中断使能 |
| `IER` | `0x08` | IP 中断使能 |
| `ISR` | `0x0c` | IP 中断状态 |
| `A_ADDR` | `0x10` | `input_a` 地址低 32 位 |
| `A_ADDR_HIGH` | `0x14` | `input_a` 地址高 32 位 |
| `B_ADDR` | `0x1c` | `input_b` 地址低 32 位 |
| `B_ADDR_HIGH` | `0x20` | `input_b` 地址高 32 位 |
| `C_ADDR` | `0x28` | `output_c` 地址低 32 位 |
| `C_ADDR_HIGH` | `0x2c` | `output_c` 地址高 32 位 |
| `M` | `0x34` | A/C 行数 |
| `K` | `0x3c` | 归约维度 |
| `N` | `0x44` | B/C 列数 |
| `SHIFT` | `0x4c` | 累加后右移量 |

这个寄存器表已经在 `pynq_delivery/register_map.actual.json` 中整理好，可直接给现有 Python 驱动使用。

## 5. 已有 FPGA 加速逻辑

当前 HLS 顶层函数参数为：

| 参数 | 方向 | 类型 |
| --- | --- | --- |
| `input_a` | in | `signed char const *` |
| `input_b` | in | `signed char const *` |
| `output_c` | out | `int *` |
| `M` | in | `int` |
| `K` | in | `int` |
| `N` | in | `int` |
| `shift` | in | `int` |

从综合报告可以判断，核心运算是 INT8 x INT8 乘法、INT32 累加，并在输出前执行算术右移。HLS bind report 中出现 `mac_muladd_8s_8s_32s_32_4_1`，说明乘加被绑定为有符号 8 bit 输入、32 bit 累加的数据路径。

对 LLaMA/TinyLlama 这类模型来说，当前硬件最直接能服务的是线性层：

- token embedding 后的矩阵乘；
- Q/K/V projection；
- attention output projection；
- MLP gate/up/down projection；
- prompt prefill 阶段的批量 GEMM；
- decode 阶段的 batch=1 GEMV，可映射为 `M=1` 的 GEMM。

它暂时不覆盖 RMSNorm、RoPE、softmax、KV cache 管理、采样等非 GEMM 逻辑，这些应先放在 ARM/NumPy/C 侧实现，再逐步评估是否值得硬化到 FPGA。

## 6. 已有 FPGA 优化点

### 6.1 使用 INT8 输入和 INT32 输出

输入 A/B 采用 INT8，输出 C 采用 INT32，适合量化神经网络中的线性层。INT8 能显著降低 DDR 带宽和片上运算资源压力；INT32 累加可以避免短 K 维度以外的严重溢出风险。

### 6.2 MAC 循环 pipeline

HLS pragma report 显示核心 multiply-accumulate 循环使用了：

```text
pipeline II=1
```

综合摘要里 `matmul_accel_Pipeline_VITIS_LOOP_15_1` 的 iteration interval 为 1，说明最内层 MAC 循环已经做到每周期接收一次迭代。这是当前设计最关键的 FPGA 加速点。

### 6.3 多 AXI master bundle

A、B、C 分别使用不同 AXI bundle：

```text
input_a  -> m_axi_gmem0
input_b  -> m_axi_gmem1
output_c -> m_axi_gmem2
```

这比把所有访存混在同一 bundle 更利于读写通道并发，也方便 SmartConnect 做事务调度。

### 6.4 支持 burst 和 outstanding

HLS 接口报告显示每个 `m_axi` 接口配置了最大 read/write burst length 16，read/write outstanding 16。当前 `input_a` 和 `output_c` 有 inferred variable burst，说明顺序访问部分已能形成 burst。

### 6.5 控制与数据解耦

AXI-Lite 只传控制参数和物理地址，矩阵数据走 DDR + AXI master。这种设计比通过 AXI-Lite 逐字写矩阵更合理，也更适合以后接入大模型权重和激活 buffer。

## 7. 当前资源、时序和实现状态

### 7.1 HLS 估算

`pynq_delivery/csynth.rpt` 中 HLS 对 `matmul_accel` 的估算：

| 资源 | 使用量 | 占比 |
| --- | --- | --- |
| BRAM | 4 | 1% |
| DSP | 5 | 2% |
| FF | 3882 | 3% |
| LUT | 4065 | 7% |

### 7.2 IP OOC 综合结果

`system_matmul_accel_0_0_utilization_synth.rpt` 中 IP 级综合结果：

| 资源 | 使用量 | 占比 |
| --- | --- | --- |
| Slice LUTs | 2975 | 5.59% |
| Slice Registers | 4335 | 4.07% |
| Block RAM Tile | 1.5 | 1.07% |
| DSP48E1 | 4 | 1.82% |

### 7.3 顶层 placed 结果

`system_wrapper_utilization_placed.rpt` 中系统级 placed 结果：

| 资源 | 使用量 | 占比 |
| --- | --- | --- |
| Slice LUTs | 2045 | 3.84% |
| Slice Registers | 2219 | 2.09% |
| Block RAM Tile | 1 | 0.71% |
| BUFG | 1 | 3.13% |

注意：系统级 placed 报告中的 DSP 显示为 0，而 IP OOC/HLS 报告中显示 IP 使用 DSP。这是不同报告口径造成的差异，硬件分析时应保留 IP 级报告作为加速器内部资源使用依据。

### 7.4 时序与路由

时序报告结果：

| 指标 | 数值 |
| --- | --- |
| 时钟 | `clk_fpga_0` |
| 周期 | 10.000 ns |
| 频率 | 100 MHz |
| WNS | 2.460 ns |
| TNS | 0.000 ns |
| WHS | 0.036 ns |
| THS | 0.000 ns |
| 失败 endpoint | 0 |

路由报告结果：

| 指标 | 数值 |
| --- | --- |
| routable nets | 3690 |
| fully routed nets | 3690 |
| routing errors | 0 |

结论：当前设计实现质量足够进入板端正确性验证和性能测试阶段。

## 8. 当前瓶颈与优化空间

### 8.1 `input_b` 访问模式不理想

HLS burst report 中 `input_b` 出现：

```text
Burst Status: Fail
Problem: Stride is incompatible
```

这说明当前 B 矩阵访问在某些循环中不是连续地址模式，HLS 无法推导成理想 burst。对于大模型线性层，权重矩阵 B 很大，B 侧访存通常会成为主要瓶颈。

建议优化方向：

- 改变 B 的存储布局，例如预转置权重，让内层 K 循环访问连续地址。
- 使用 tile/blocking，把 A/B 子块搬到 BRAM 后复用。
- 对 B 做 packed INT8 布局，配合更宽 AXI 数据位宽读取。
- 对 LLaMA 权重离线预处理，生成硬件友好的 row/column major 版本。

### 8.2 AXI 数据宽度较窄

HWH 参数显示 `m_axi_gmem*` data width 为 32 bit。对于 INT8 矩阵乘，32 bit 一次只能承载 4 个 INT8，DDR 带宽利用率有限。

建议优化方向：

- 在 HLS 中使用 `ap_int<32>`、`ap_int<64>` 或 `ap_int<128>` 打包读取多个 INT8。
- 调整 `max_widen_bitwidth` 或使用显式 vectorized load，避免 HLS 报告里的 widen fail。
- 让计算内核一次展开多个 MAC lane，与更宽访存匹配。

### 8.3 DSP 和 BRAM 使用率很低

Zynq-7020 有 220 个 DSP，当前 IP 级只使用约 4 个 DSP48E1，说明计算并行度还很保守。若目标是 LLM 推理，当前单 MAC pipeline 只能作为功能闭环，性能上不会充分利用 FPGA。

建议优化方向：

- 展开 N 维或 K 维，形成多 lane dot-product。
- 用 BRAM 缓存 A tile 和 B tile，提高数据复用。
- 为 decode 阶段设计专门的 GEMV kernel，减少 `M=1` 时的启动开销和低利用率。
- 在资源允许时做 systolic/tiled GEMM，而不是单一内层 MAC。

### 8.4 缺少大模型相关算子

当前硬件只覆盖 GEMM/linear。TinyLlama 推理还需要：

- RMSNorm；
- RoPE；
- Q/K/V cache 读写；
- attention score；
- softmax；
- SiLU/SwiGLU；
- logits 采样。

短期建议只把 GEMM/linear 交给 FPGA，其他算子留在 CPU；中期再根据 profiling 选择 attention 或 norm 的硬化优先级。

## 9. `.xsa`、`.hwh` 和 `.bit` 的关系

底层 PYNQ `Overlay` 运行时仍然加载 `.bit`：

```python
Overlay("AI_accelerator.bit")
```

PYNQ 会寻找同目录下同基础名的 `.hwh`，即：

```text
AI_accelerator.bit
AI_accelerator.hwh
```

`.hwh` 的作用是告诉 PYNQ overlay 内有哪些 IP、层级名、寄存器和地址信息。没有 `.hwh` 时，bitstream 可能仍能下载，但 Python 侧很难可靠地通过 `overlay.ip_dict` 和属性访问 IP。

`.xsa` 是 Vivado/Vitis 导出的硬件平台归档，里面可以包含 bitstream、HWH、driver header、PS 初始化文件等。当前软件默认以 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa` 为来源，并在运行时提取 PYNQ 需要的 `.bit/.hwh` 到软件目录缓存。

本项目的硬件工程 XSA 中包含：

```text
AI_accelerator.bit
system.hwh
drivers/matmul_accel_v1_0/src/xmatmul_accel_hw.h
...
```

因此，“`.xsa` 可以转成/提取 `.hwh`”这个说法在本项目里是成立的。更精确地说：不是把 XSA 重新综合成 HWH，而是从 XSA 归档中提取 Vivado 已经导出的 HWH。

在 PowerShell 中可以查看 XSA 内容：

```powershell
tar -tf fpga_hardware/accelerator_hardware/AI_accelerator.xsa
```

软件驱动会自动完成提取。手工排查时，也可以把 XSA 中的 `.bit/.hwh` 提取到软件缓存目录并保持同名：

```powershell
mkdir quant_mma_accel\overlays\generated\AI_accelerator
tar -xf fpga_hardware/accelerator_hardware/AI_accelerator.xsa -C quant_mma_accel\overlays\generated\AI_accelerator system.hwh AI_accelerator.bit
copy quant_mma_accel\overlays\generated\AI_accelerator\system.hwh quant_mma_accel\overlays\generated\AI_accelerator\AI_accelerator.hwh
```

关键是 PYNQ 侧最终仍建议保持 `.bit` 与 `.hwh` 同目录、同基础名。

## 10. 后续硬件路线建议

### 阶段 1：保留当前硬件，完成板端闭环

目标：证明 PYNQ 软件驱动能从硬件工程导出的 XSA 调用 FPGA IP。

- 使用 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa` 作为 overlay 来源。
- 软件运行时从 XSA 提取 `.bit/.hwh` 到 `quant_mma_accel/overlays/generated/`。
- 使用 `configs/register_map.fpga_hardware.json`。
- 在 PYNQ-Z2 上跑 `run_pynq_once.py`。
- 验证 FPGA 输出与 CPU golden result 完全一致。
- 记录不同 M/K/N 下的 kernel 时间和端到端时间。

### 阶段 2：针对 LLM linear 层优化数据布局

目标：让当前 GEMM 更适合权重矩阵长期驻留/重复读取。

- 明确 LLaMA linear 的 shape。
- 离线量化并重排权重 B。
- 优先解决 `input_b` stride incompatible。
- 对比重排前后的 burst、带宽和 kernel 时间。

### 阶段 3：提高并行度和带宽

目标：从功能型 GEMM 变成可展示加速比的 GEMM/GEMV。

- 扩宽 AXI 读取数据位宽。
- 打包 INT8，单周期处理多个乘加。
- 增加 N/K 维展开。
- 使用 BRAM tile 缓存权重或激活。
- 在资源和时序之间做 design space exploration。

### 阶段 4：为 decode 阶段设计专用 GEMV

目标：适配自回归推理中 batch=1 的主场景。

- 设计 `y = x @ W` 专用 kernel。
- 降低每次 kernel 启动和 buffer 搬运开销。
- 支持分块输出，避免一次性输出维度过大导致 DDR 压力。
- 和 CPU 侧 KV cache/attention 调度配合。

## 11. 本报告引用的关键文件

- `fpga_hardware/accelerator_hardware/AI_accelerator.xsa`
- `fpga_hardware/accelerator_hardware/system_wrapper.bit`
- `fpga_hardware/accelerator_hardware/accelerator.gen/sources_1/bd/system/hw_handoff/system.hwh`
- `fpga_hardware/accelerator_hardware/accelerator.runs/system_matmul_accel_0_0_synth_1/system_matmul_accel_0_0_utilization_synth.rpt`
- `fpga_hardware/accelerator_hardware/accelerator.runs/impl_1/system_wrapper_utilization_placed.rpt`
- `fpga_hardware/accelerator_hardware/accelerator.runs/impl_1/system_wrapper_timing_summary_routed.rpt`
- `fpga_hardware/accelerator_hardware/accelerator.runs/impl_1/system_wrapper_route_status.rpt`
- `pynq_delivery/csynth.rpt`
- `pynq_delivery/overlay_metadata.json`
- `pynq_delivery/register_map.actual.json`
- `pynq_delivery/xmatmul_accel_hw.h`
