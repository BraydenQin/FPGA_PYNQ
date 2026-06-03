# TinyLlama / LLaMA 推理软件实施计划

生成日期：2026-06-03

## 1. 目标定位

目标是在现有 PYNQ + FPGA INT8 矩阵乘加速器基础上，逐步实现 LLaMA 类模型推理演示。当前硬件只覆盖 INT8 GEMM/linear，因此软件计划应按“先可运行，再逐步加速”的方式推进：

1. 先完成纯软件 LLaMA/TinyLlama 推理最小闭环。
2. 再把权重线性层映射到现有 `matmul_accel_0`。
3. 通过 profiling 找出真实瓶颈。
4. 决定是否继续改 FPGA kernel。

当前不建议一开始承诺完整 TinyLlama 全模型都由 FPGA 推理。更合理的表述是：FPGA 先作为 INT8 linear/GEMM 协处理器，CPU 负责控制流、非线性算子、KV cache、采样和文件加载。

## 2. 模型可行性判断

### 2.1 TinyLlama 1.1B 的容量风险

如果这里的 TinyLlama 指常见的 TinyLlama-1.1B，它虽然比 7B/13B 小很多，但对 PYNQ-Z2 这类板仍然很大：

- FP16 权重大约 2.2 GB 以上，不适合 512 MB DDR。
- INT8 权重大约 1.1 GB 以上，仍然超过 PYNQ-Z2 常见内存容量。
- 4-bit 权重大约 550 MB 左右，还没有算 runtime buffer、KV cache、Python/PYNQ 运行环境和操作系统开销。
- 自回归推理还需要 KV cache，context length 越长内存压力越大。

因此，若目标板是 PYNQ-Z2，TinyLlama-1.1B 不应作为第一阶段板端闭环目标。它可以作为 PC 端参考目标，或作为后续在更大 DDR 板卡上的目标。

### 2.2 更稳妥的第一阶段模型

建议先选择以下之一作为板端目标：

| 方案 | 说明 |
| --- | --- |
| tiny random LLaMA | 用很小 hidden size/layer 数搭一个结构正确的 LLaMA，用于验证算子和调度 |
| TinyStories 小模型 | 体量比 TinyLlama-1.1B 更容易进入嵌入式板端 |
| llama2.c 风格小模型 | 文件格式和推理代码简单，适合移植和验证 |
| 自定义 toy transformer | 最可控，适合先打通 FPGA linear offload |

建议路线：PC 端保留 TinyLlama 兼容思路，PYNQ 板端第一版使用小模型，避免项目卡在内存容量上。

## 3. 当前软件和硬件基础

当前 `quant_mma_accel` 已经具备以下能力：

- 生成 INT8 测试矩阵。
- NumPy CPU golden result：`C = (A @ B) >> shift`。
- PYNQ buffer 分配和 cache flush/invalidate。
- 通过 AXI-Lite 写入 A/B/C 地址、M/K/N、shift。
- 启动 IP 并轮询 `ap_done`。
- 输出 FPGA kernel 时间和端到端时间。

当前软件默认使用硬件工程导出的 XSA：

- `../fpga_hardware/accelerator_hardware/AI_accelerator.xsa`
- `configs/register_map.fpga_hardware.json`

软件驱动会把 XSA 中的 `.bit/.hwh` 提取到运行缓存：

```text
quant_mma_accel/overlays/generated/AI_accelerator/AI_accelerator.bit
quant_mma_accel/overlays/generated/AI_accelerator/AI_accelerator.hwh
```

不再从 `pynq_delivery` 复制 `.bit/.hwh` 作为默认运行来源。

## 4. 总体软件架构

建议在 `quant_mma_accel` 下新增 LLM 相关模块，保持 Python 3.6.5 兼容：

```text
quant_mma_accel/
  llm/
    __init__.py
    config.py              # 模型配置：hidden size、层数、head 数等
    tokenizer.py           # 第一阶段可简化，后续再兼容 SentencePiece/BPE
    weights.py             # 权重加载、量化、重排、分块
    ops_cpu.py             # CPU/NumPy RMSNorm、RoPE、softmax、SwiGLU 等
    linear_backend.py      # CPU linear 与 FPGA linear 的统一接口
    llama_model.py         # LLaMA block 和自回归 decode
    generate.py            # 文本生成入口
  scripts/
    run_llm_cpu.py
    run_llm_pynq.py
    export_llm_weights.py
```

设计原则：

- `llm` 模块不在 import 时强制依赖 `pynq`。
- PYNQ 相关 import 继续延迟到板端运行时。
- 所有代码兼容 Python 3.6.5，避免 `list[str]`、`A | B`、`dataclasses` 强依赖和 `from __future__ import annotations`。
- 先使用 NumPy 实现清晰正确的参考路径，再把 linear backend 替换为 FPGA。

## 5. 推理拆分方案

LLaMA decoder layer 可以拆成以下模块：

| 模块 | 第一阶段执行位置 | FPGA 适配性 |
| --- | --- | --- |
| Token embedding | CPU/NumPy | 可选，不急 |
| RMSNorm | CPU/NumPy | 暂不适配当前 GEMM IP |
| Q/K/V projection | FPGA linear | 高 |
| RoPE | CPU/NumPy | 暂不适配当前 GEMM IP |
| Attention score | CPU/NumPy 或后续 FPGA | 中，当前 IP 可做部分 GEMM，但 softmax 和 cache 管理仍在 CPU |
| Softmax | CPU/NumPy | 低，当前 IP 不覆盖 |
| Attention output projection | FPGA linear | 高 |
| MLP gate/up/down projection | FPGA linear | 高 |
| SiLU/SwiGLU | CPU/NumPy | 暂不适配当前 GEMM IP |
| LM head | FPGA linear 或 CPU | 高，但输出词表可能较大 |
| Sampling | CPU | 低 |

第一版最有价值的 FPGA 接入点是所有 `x @ W` 的 linear 层。

## 6. FPGA Linear Backend 设计

当前硬件接口是：

```text
C = (A @ B) >> shift
A: int8[M, K]
B: int8[K, N]
C: int32[M, N]
```

因此可以定义统一接口：

```python
class LinearBackend(object):
    def matmul(self, input_a, weight_b, shift):
        raise NotImplementedError
```

实现两个 backend：

- `CpuLinearBackend`：调用 NumPy，作为 golden reference。
- `FpgaLinearBackend`：调用现有 `MatmulAccel.run_with_timing()`。

### 6.1 Prefill 阶段

Prompt prefill 时一次处理多个 token，输入 shape 可以是：

```text
A = activations: [seq_len, hidden]
B = weight:      [hidden, out]
C = output:      [seq_len, out]
```

这与当前 GEMM IP 比较匹配，能减少 kernel 启动次数，也更容易体现 FPGA 吞吐。

### 6.2 Decode 阶段

逐 token decode 时通常是：

```text
A = current token activation: [1, hidden]
B = weight:                   [hidden, out]
C = output:                   [1, out]
```

这可以映射为 `M=1` 的 GEMM，但当前 IP 可能因为启动开销、DDR 权重读取和低并行度导致加速比不明显。后续若主要展示生成速度，应考虑专门的 GEMV kernel。

## 7. 权重量化与布局计划

### 7.1 第一版量化格式

为了匹配当前硬件，第一版使用 per-tensor 或 per-channel INT8 权重：

```text
float_weight -> int8_weight
float_activation -> int8_activation
int32_accum -> shift -> int32/float dequant
```

当前 IP 只支持一个整数 `shift`，没有内建 scale/zero-point。因此第一版可以采用对称量化：

- zero point 固定为 0；
- scale 在 CPU 侧维护；
- FPGA 输出 INT32 后，CPU 侧做 dequant 或继续定点流转。

### 7.2 权重布局

现有 IP 要求 B 是 `[K, N]` row-major。HLS 报告显示 `input_b` 有 stride incompatible，说明当前访问 B 的模式可能不是最优。

软件侧可以先准备两份布局：

- 逻辑布局：便于和 PyTorch/NumPy 对齐。
- FPGA 布局：便于当前硬件读取。

后续如果硬件改为读取转置权重或 packed 权重，软件只需要改 `weights.py` 的导出和 `linear_backend.py` 的调用约定。

## 8. 分阶段实施计划

### 阶段 0：硬件交付文件整理

目标：让当前 PYNQ 驱动能用真实交付文件跑通。

任务：

- 使用 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa` 作为 overlay source。
- 运行时从 XSA 提取 PYNQ 需要的 `.bit/.hwh`。
- 使用 `configs/register_map.fpga_hardware.json`。
- 保持 `configs/default.json` 指向硬件工程 XSA。
- 在 PYNQ 板端运行 `scripts/run_pynq_once.py`。
- 记录 PASS/FAIL 和 timing。

验收标准：

- FPGA 输出与 CPU golden result 完全一致。
- `overlay.ip_dict` 中能看到 `matmul_accel_0`。
- 没有 `ap_done` 超时。

### 阶段 1：纯软件 LLaMA 最小闭环

目标：不接 FPGA，先跑通小模型 forward/generate。

任务：

- 实现模型配置读取。
- 实现 RMSNorm、RoPE、attention、MLP、LM head。
- 使用极小 toy 权重做 deterministic test。
- 实现 `run_llm_cpu.py`，支持 prompt -> token 输出。
- 对每个算子写小尺寸单元测试。

验收标准：

- toy model 可以稳定生成 token。
- 每个算子 shape 正确，数值与 NumPy reference 对齐。
- PC 端测试通过。

### 阶段 2：INT8 linear 后端抽象

目标：把 LLaMA 中所有 linear 调用统一接到 backend。

任务：

- 实现 `CpuLinearBackend`。
- 实现 `FpgaLinearBackend`。
- 为 Q/K/V、O projection、MLP projection、LM head 替换调用路径。
- 增加 backend 选择参数：`--backend cpu|fpga`。

验收标准：

- 同一组 INT8 输入和权重下，CPU backend 与 FPGA backend 输出一致。
- 可以统计每个 linear 层的 FPGA kernel 时间。

### 阶段 3：权重导出与量化

目标：把模型权重转换为当前硬件能消费的 INT8 矩阵。

任务：

- 编写 `export_llm_weights.py`。
- 支持从小模型权重导出 `.npy` 或 `.npz`。
- 保存每层 scale、shift、shape 和布局 metadata。
- 第一版先支持小模型，后续再兼容 TinyLlama 权重。

验收标准：

- 权重文件可在 Python 3.6.5 + NumPy 环境加载。
- 每层 linear shape 与模型配置一致。
- CPU INT8 路径与 FP32/FP16 reference 的误差在可解释范围内。

### 阶段 4：PYNQ 板端小模型推理

目标：在板端完成小模型 prefill/decode 演示。

任务：

- 限制 seq_len、hidden size、层数，保证内存可控。
- 把权重分层加载，避免一次性占满 DDR。
- 对 prefill linear 使用 FPGA backend。
- decode 阶段先可选 CPU/FPGA backend 对比。
- 输出 token/s、每层耗时、FPGA kernel 总耗时、端到端耗时。

验收标准：

- 板端可以生成一段固定长度 token。
- 不发生内存不足。
- profiling 能显示 FPGA linear 的耗时占比。

### 阶段 5：评估 TinyLlama-1.1B

目标：决定是否继续推进真实 TinyLlama。

任务：

- 计算目标板 DDR 可用容量。
- 计算 8-bit/4-bit 权重、KV cache、activation buffer 总需求。
- 如果容量不足，评估分层流式加载或外部存储 streaming。
- 如果 streaming 过慢，转向更小模型或更大板卡。

验收标准：

- 有明确容量表和性能估算。
- 明确 TinyLlama-1.1B 是板端目标、PC 端目标，还是仅作为论文/报告中的扩展目标。

## 9. `.xsa` 到 `.hwh` 的使用计划

你的理解需要稍微修正：PYNQ 软件运行通常不是直接加载 `.xsa`，而是加载 `.bit`，并依赖同名 `.hwh` 解析 overlay 元数据。

但你朋友说的关键点是对的：`.xsa` 包里通常已经包含 `.hwh`，所以可以从 `.xsa` 提取 `.hwh`。

本项目后续默认使用 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa`。软件驱动会从这个 XSA 中提取 PYNQ 需要的 `.bit/.hwh` 到 `quant_mma_accel/overlays/generated/AI_accelerator/`。

硬件工程 XSA 中包含：

```text
AI_accelerator.bit
system.hwh
drivers/matmul_accel_v1_0/src/xmatmul_accel_hw.h
```

查看 XSA 内容：

```powershell
tar -tf fpga_hardware/accelerator_hardware/AI_accelerator.xsa
```

正常运行不需要手工复制 `pynq_delivery` 的 `.bit/.hwh`。

## 10. 风险清单

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| TinyLlama-1.1B 权重太大 | 板端无法加载 | 先用小模型；TinyLlama 放 PC 或更大板卡 |
| 当前 GEMM IP 并行度低 | FPGA 加速比不明显 | 先做 correctness，再基于 profiling 改硬件 |
| B 矩阵访存 burst 不理想 | 权重读取慢 | 权重重排、转置、tile、packed layout |
| Python/PYNQ 开销大 | decode 阶段慢 | 合并 linear、减少 kernel 启动次数、后续写 C 扩展或专用 kernel |
| 量化误差影响生成 | 输出质量下降 | 先做小模型逐层误差分析，再扩展 |
| Python 3.6.5 限制依赖 | 新版库不可用 | 固定旧版 NumPy，避免 transformers 等重依赖直接上板 |

## 11. 推荐近期任务顺序

1. 先在板端用现有矩阵乘验证真实 FPGA overlay。
2. 把 `register_map.actual.json` 纳入 `quant_mma_accel/configs/`，让软件不再用 example map。
3. 做一个 toy LLaMA 配置，例如 2 层、hidden 64/128、少量 head。
4. 完成纯 NumPy forward。
5. 把 toy LLaMA 的 linear 层切到 FPGA backend。
6. 记录 prefill 与 decode 的耗时差异。
7. 再决定是否投入硬件改造：优先解决 B 访存和并行度。

## 12. 最小演示目标

建议最终 demo 先定义为：

```text
在 PYNQ 板端加载 matmul_overlay.bit/hwh，运行一个小型 LLaMA-like decoder。
模型中的 linear 层通过 FPGA INT8 GEMM 加速，其余算子由 ARM/NumPy 完成。
程序输出生成 token、正确性对比、每层耗时和 FPGA kernel 总耗时。
```

这个目标和当前硬件能力匹配，也能自然引出后续优化方向：更宽访存、更高并行度、GEMV kernel、权重重排和更多 transformer 算子硬化。
