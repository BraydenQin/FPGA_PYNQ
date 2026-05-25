# PYNQ-Z2 量化矩阵乘加速器软件驱动

本项目是一个面向 PYNQ-Z2 的 INT8 量化矩阵乘加速器软件框架。核心逻辑放在 Python 模块中，方便在 VS Code 中开发、测试和维护；Jupyter Notebook 只作为板端演示入口，不承担主要业务逻辑。

第一版目标是完成最小闭环：

- 在 PC 或 PYNQ 板端生成确定性的 INT8 输入矩阵。
- 使用 NumPy 计算 INT32 golden result：`C = (A @ B) >> shift`。
- 在 PYNQ 板端加载 Vivado 导出的 `.bit/.hwh` overlay。
- 使用 PYNQ 分配物理连续 buffer。
- 通过 AXI Lite 寄存器配置 HLS IP。
- 启动 IP，轮询 `ap_done`，并设置超时避免程序卡死。
- 读回 FPGA 输出，与 CPU golden result 做逐元素对比。
- 输出 CPU 时间、FPGA kernel 时间和端到端总时间。

PC 端不需要安装 `pynq`。所有 PYNQ 相关 import 都延迟到板端运行时执行。

## 当前状态

当前软件侧框架已经可以在 PC 端完成：

- 测试向量生成。
- CPU golden result 计算。
- CPU 结果自检。
- 单元测试。
- PYNQ 驱动封装。
- benchmark 脚本。
- Notebook 演示入口。

还需要硬件同学提供以下文件和信息后，才能完成真实 FPGA 性能测试：

- `matmul_overlay.bit`
- `matmul_overlay.hwh`
- 真实 HLS/Vivado control register map，例如 `xmatmul_accel_hw.h`
- IP 名称，例如 `matmul_accel_0`
- A/B/C 的数据类型、矩阵形状、row-major 布局和 shift 规则

## 目录结构

```text
quant_mma_accel/
  configs/                  默认配置和寄存器表模板
  software/                 PC 端可运行的 NumPy 参考实现和测试向量工具
  pynq_driver/              PYNQ overlay、AXI Lite 和 benchmark 驱动
  scripts/                  命令行入口
  tests/                    PC 端单元测试
  test_vectors/             生成的 .npy 测试数据
  overlays/                 放置 Vivado 导出的 .bit/.hwh 文件
```

## PC 端开发和验收

在 `quant_mma_accel` 目录下运行：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_vectors.py --M 16 --K 64 --N 16 --shift 7 --seed 0 --out test_vectors/default
python scripts/run_cpu_check.py --vectors test_vectors/default
pytest
```

在 Linux 或 PYNQ 板端，虚拟环境激活命令改为：

```bash
source .venv/bin/activate
```

PC 端验收通过后，说明软件参考实现、测试向量和不依赖 PYNQ 的模块已经可用。

## PYNQ 板端运行流程

把项目复制到 PYNQ-Z2，例如：

```text
/home/xilinx/jupyter_notebooks/matmul_accel/quant_mma_accel
```

把硬件文件放到：

```text
overlays/matmul_overlay.bit
overlays/matmul_overlay.hwh
```

确认 `configs/register_map.example.json` 已经替换为真实寄存器 offset 后，运行单次硬件验证：

```bash
python scripts/run_pynq_once.py \
  --bitfile overlays/matmul_overlay.bit \
  --ip-name matmul_accel_0 \
  --register-map configs/register_map.example.json \
  --vectors test_vectors/default
```

如果输出 `PASS` 且 `max_abs_error=0`，说明 FPGA 输出和 CPU golden result 完全一致。

运行默认 benchmark：

```bash
python scripts/run_benchmark.py \
  --bitfile overlays/matmul_overlay.bit \
  --ip-name matmul_accel_0 \
  --register-map configs/register_map.example.json
```

benchmark 会输出多组矩阵尺寸下的 CPU 时间、FPGA kernel 时间、端到端时间和正确性结果。

## 寄存器表说明

`configs/register_map.example.json` 目前是占位模板。真实 offset 必须以 HLS/Vivado 导出的 driver header 为准，例如 `xmatmul_accel_hw.h`。

必须确认的逻辑寄存器：

- `CTRL`：AXI Lite 控制寄存器。未配置时默认使用 `0x00`。
- `A_ADDR`、`B_ADDR`、`C_ADDR`：输入输出 buffer 的 DDR 物理地址。
- `M`、`K`、`N`、`SHIFT`：矩阵尺寸和右移参数。

offset 可以写成 JSON 整数，也可以写成十六进制字符串，例如：

```json
{
  "A_ADDR": "0x10",
  "B_ADDR": "0x1c",
  "C_ADDR": "0x28"
}
```

如果 HLS 指针地址是 64-bit，需要配置高 32 位寄存器，例如：

```json
{
  "A_ADDR": "0x10",
  "A_ADDR_HIGH": "0x14",
  "B_ADDR": "0x1c",
  "B_ADDR_HIGH": "0x20",
  "C_ADDR": "0x28",
  "C_ADDR_HIGH": "0x2c"
}
```

驱动会把物理地址低 32 位写入 `A_ADDR`，如果配置了 `A_ADDR_HIGH`，会把高 32 位写入对应高位寄存器。

## 和硬件同学对齐的信息

建议直接向硬件同学确认：

```text
请给我 HLS 导出的 control register map，最好是 xmatmul_accel_hw.h 或 driver header。
我需要 a/b/c 指针、M、K、N、shift、ap_start、ap_done 的 offset，以及地址寄存器是 32-bit 还是 64-bit。
```

当前软件侧默认数据约定：

- `A`：INT8，shape 为 `M x K`，row-major。
- `B`：INT8，shape 为 `K x N`，row-major。
- `C`：INT32，shape 为 `M x N`，row-major。
- 计算公式：`C = (A @ B) >> shift`。

## Notebook

`pynq_driver/demo_notebook.ipynb` 是板端演示入口。Notebook 只负责调用 Python 模块，不复制大量驱动逻辑。

建议演示顺序：

- 加载配置。
- 打印 `overlay.ip_dict`。
- 加载测试向量。
- 计算 CPU golden result。
- 调用 `MatmulAccel.run_with_timing`。
- 使用 `np.testing.assert_array_equal` 检查结果。
- 输出 benchmark 表格。

## 完成度说明

如果只看 VS Code / PC 端软件开发，本项目已经具备完整框架和可运行测试。最终验收还需要在 PYNQ-Z2 上加载真实 `.bit/.hwh` 文件，并使用真实寄存器表完成硬件正确性验证和性能测试。