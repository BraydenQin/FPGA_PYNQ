# 线性层加速实验记录

生成日期：2026-06-03

## 已完成

- 新增线性层实验入口：`scripts/run_linear_layer_experiment.py`。
- 新增合成线性层 NPZ 生成入口：`scripts/generate_linear_case.py`。
- 新增 HuggingFace 单层权重导出入口：`scripts/export_hf_linear_layer.py`。
- 默认 FPGA overlay 来源仍为 `fpga_hardware/accelerator_hardware/AI_accelerator.xsa`，运行时自动提取 `.bit/.hwh`。

## 当前本机实验结果

当前 Windows/PC 环境没有 PYNQ 包，不能直接跑 FPGA backend：

```text
pynq_available=False
```

已生成一个 LLM-like INT8 线性层实验包：

```text
test_vectors/linear/synthetic_m16_k512_n512.npz
M=16, K=512, N=512, shift=7
```

CPU 基线实验结果：

```text
cpu_time_ms=5.735200
```

结果 JSON：

```text
test_vectors/linear/synthetic_m16_k512_n512_cpu_result.json
```

## TinyLlama 权重加载状态

已安装 PC 端导出依赖：`torch==2.4.1`、`transformers==4.45.2`、`accelerate==0.33.0`、`safetensors==0.4.5`。

尝试从 HuggingFace 导出：

```bash
python scripts/export_hf_linear_layer.py \
  --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --layer-name model.layers.0.mlp.down_proj.weight \
  --M 1 \
  --out test_vectors/linear/tinyllama_layer0_down_proj.npz
```

当前失败原因是网络代理链路无法连接 HuggingFace：

```text
ProxyError: Unable to connect to proxy
```

因此本轮先使用合成 INT8 线性层完成实验代码闭环。等 HuggingFace 网络或本地模型缓存可用时，导出的 TinyLlama `.npz` 可以直接替换合成 `.npz`，不需要改 FPGA 驱动。

## PYNQ 板端实验命令

把项目复制到 PYNQ 后，在 `quant_mma_accel` 目录运行：

```bash
python scripts/run_linear_layer_experiment.py \
  --backend both \
  --case-npz test_vectors/linear/synthetic_m16_k512_n512.npz \
  --cpu-repeats 3 \
  --fpga-repeats 5 \
  --json-out test_vectors/linear/synthetic_m16_k512_n512_fpga_result.json
```

验收口径：

- `pass=True` 且 `max_abs_error=0`。
- `fpga_kernel_time_ms < cpu_time_ms` 时，可以说明 FPGA 在该 INT8 linear kernel 上快于 CPU 参考实现。
- `total_time_ms` 需要单独解释，因为它包含 PYNQ buffer 分配、cache flush/invalidate 和 Python 调用开销。
