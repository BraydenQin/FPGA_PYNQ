# 软件适配简短计划

生成日期：2026-06-03

## 目标

后续不再使用 `pynq_delivery` 中的 `.bit/.hwh` 作为运行来源。软件驱动统一以 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa` 为 overlay 源；运行时从 XSA 提取 PYNQ 需要的同名 `.bit/.hwh` 到软件目录缓存，再加载到板端。

## 边界

- 不修改 Vivado 工程、不重新综合、不调整 HLS pragma。
- 只做 Python/PYNQ 软件适配、配置整理和 benchmark 流程更新。
- 全量 TinyLlama 暂不作为 Zynq 板端第一目标，避免权重和 KV cache 超出 DDR。

## 推理策略

第一版只演示 LLaMA/TinyLlama 中最适合当前硬件的线性层：Q/K/V projection、attention output projection、MLP projection 和 LM head。CPU 负责 RMSNorm、RoPE、softmax、KV cache 和采样；FPGA 负责 INT8 linear：

```text
C = (A @ B) >> shift
```

这样能体现明确的加速策略：把常规 CPU/NumPy 的矩阵乘替换成 PL 侧 INT8 GEMM，并用 benchmark 同时报告 `cpu_time_ms`、`fpga_kernel_time_ms` 和 `total_time_ms`。验收时优先看大一点的 linear case 或 prefill case，因为它们更能摊薄 PYNQ 调用开销。

## 实施步骤

1. 驱动支持 `.xsa`：传入 `AI_accelerator.xsa` 时自动提取 `.bit/.hwh` 并加载。
2. 默认配置改为硬件工程来源：`../fpga_hardware/accelerator_hardware/AI_accelerator.xsa`。
3. 寄存器表改为硬件工程导出的 64-bit 地址版本。
4. 先运行矩阵乘正确性和 benchmark，确认 FPGA 输出等于 CPU golden。
5. 再新增 LLaMA-like 小模型或 toy linear 层，把其中的 linear 调到 FPGA backend。

## 当前实验命令

PC 端如果已安装 `torch/transformers`，先从 HuggingFace 导出 TinyLlama 的一个线性层权重。导出脚本只抽取一层并保存成 INT8 `.npz`，避免在 PYNQ 板端加载完整模型：

```bash
python scripts/export_hf_linear_layer.py \
	--model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
	--layer-name model.layers.0.mlp.down_proj.weight \
	--M 16 \
	--out test_vectors/linear/tinyllama_layer0_down_proj.npz
```

如果暂时没有 HuggingFace 依赖，可以先跑合成线性层：

```bash
python scripts/generate_linear_case.py \
	--M 16 \
	--K 512 \
	--N 512 \
	--out test_vectors/linear/synthetic_m16_k512_n512.npz

python scripts/run_linear_layer_experiment.py \
	--backend cpu \
	--case-npz test_vectors/linear/synthetic_m16_k512_n512.npz
```

PYNQ 板端运行 FPGA/CPU 对比：

```bash
python scripts/run_linear_layer_experiment.py \
	--backend both \
	--case-npz test_vectors/linear/synthetic_m16_k512_n512.npz \
	--cpu-repeats 3 \
	--fpga-repeats 5
```

如果 HuggingFace 网络可用，把 `--case-npz` 换成 `test_vectors/linear/tinyllama_layer0_down_proj.npz` 即可跑真实 TinyLlama 单层线性权重。

实验报告里优先使用 `fpga_kernel_time_ms` 对比 `cpu_time_ms`，因为它反映线性层 kernel 本身的加速；同时保留 `total_time_ms` 用于说明 PYNQ buffer 分配、cache flush/invalidate 和 Python 调用开销。

## 验收

- `run_pynq_once.py` 输出 `PASS`。
- `run_linear_layer_experiment.py --backend both` 至少给出一组 `fpga_kernel_time_ms < cpu_time_ms` 的线性层 case。
- 文档和命令都不再要求使用 `pynq_delivery` 的 `.bit/.hwh`。