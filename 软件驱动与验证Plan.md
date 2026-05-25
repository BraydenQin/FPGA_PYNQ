# 软件驱动与全流程验证代码部署 Plan

> 适用分工：软件驱动与全流程验证。目标是先在 VS Code 中完成可维护的 Python 驱动、测试数据生成、CPU golden result、PYNQ 调用封装和 benchmark 脚本；Jupyter Notebook 只作为板端调试和答辩演示入口，不作为核心代码唯一载体。

## 0. 代码生成总任务

请创建一个 PYNQ-Z2 量化矩阵乘加速器的软件驱动与验证代码框架。代码应支持：

1. 在 PC 或 PYNQ 板端生成 INT8 测试矩阵和 CPU golden result。
2. 在 PYNQ 板端加载 Vivado 导出的 `.bit/.hwh` overlay。
3. 使用 PYNQ Python API 分配连续物理内存 buffer。
4. 通过 AXI Lite 寄存器配置 HLS IP 的输入输出地址、矩阵尺寸和 shift。
5. 启动 IP，轮询完成状态，读回输出矩阵。
6. 对比 FPGA 输出和 CPU golden result。
7. 输出 CPU 时间、FPGA kernel 时间、端到端总时间。
8. 保留 Notebook 演示入口，但核心逻辑必须放在 `.py` 模块中，方便 VS Code 开发和复用。

第一版不要接入 `llama2.c`。先完成量化矩阵乘最小闭环。

## 1. 已确定技术路线

- 开发板：PYNQ-Z2。
- 软件路线：普通 Python 模块为主，PYNQ Notebook 为演示层。
- 硬件输入：Vivado 同学提供 `matmul_overlay.bit` 和 `matmul_overlay.hwh`。
- 硬件 IP：HLS 导出的 `matmul_accel`，通过 AXI Lite 控制，通过 AXI Master 访问 DDR。
- 数据类型：`A` 为 INT8，`B` 为 INT8，`C` 第一版按 INT32 输出处理。
- 默认矩阵尺寸：`M=16, K=64, N=16`。
- 默认缩放：`shift=7`。
- 存储顺序：row-major。
- 正确性标准：FPGA 输出必须与 Python CPU golden result 完全一致。

## 2. 推荐目录结构

代码生成 agent 请按下面结构创建文件：

```text
quant_mma_accel/
  README.md
  requirements.txt
  configs/
    default.json
    register_map.example.json
  software/
    __init__.py
    cpu_ref.py
    quantize.py
    test_vectors.py
  pynq_driver/
    __init__.py
    register_map.py
    overlay_driver.py
    matmul_accel.py
    benchmark.py
    demo_notebook.ipynb
  scripts/
    generate_vectors.py
    run_cpu_check.py
    run_pynq_once.py
    run_benchmark.py
  tests/
    test_cpu_ref.py
    test_quantize.py
  test_vectors/
    .gitkeep
  overlays/
    README.md
```

说明：

- `software/`：不依赖 PYNQ，PC 上也能运行。
- `pynq_driver/`：只在 PYNQ 板端运行，依赖 `pynq` 包。
- `scripts/`：命令行入口，方便 VS Code terminal 和板端 SSH 运行。
- `test_vectors/`：保存 `.npy` 输入和 golden result。
- `overlays/`：放 `.bit/.hwh`，不强制提交大文件。

## 3. 配置文件要求

### `configs/default.json`

用于保存默认矩阵尺寸、shift、overlay 路径和 IP 名称。

```json
{
  "M": 16,
  "K": 64,
  "N": 16,
  "shift": 7,
  "seed": 0,
  "overlay_bitfile": "overlays/matmul_overlay.bit",
  "ip_name": "matmul_accel_0",
  "register_map": "configs/register_map.example.json"
}
```

### `configs/register_map.example.json`

先使用占位 offset。真实 offset 必须以后续 HLS 导出的 driver/header 为准。

```json
{
  "CTRL": "0x00",
  "GIE": "0x04",
  "IER": "0x08",
  "ISR": "0x0c",
  "A_ADDR": "0x10",
  "B_ADDR": "0x1c",
  "C_ADDR": "0x28",
  "M": "0x34",
  "K": "0x3c",
  "N": "0x44",
  "SHIFT": "0x4c"
}
```

代码里必须允许用户替换 register map，不要把 offset 写死在驱动逻辑里。

## 4. 各文件详细实现要求

### `software/cpu_ref.py`

实现 CPU 参考矩阵乘，不能依赖 PYNQ。

必须提供函数：

```python
def matmul_int8_ref(input_a: np.ndarray, input_b: np.ndarray, shift: int) -> np.ndarray:
    """Return INT32 golden result for C = (A @ B) >> shift."""
```

要求：

- 检查 `input_a` 和 `input_b` 必须是二维矩阵。
- 检查 `input_a.shape[1] == input_b.shape[0]`。
- 计算前将输入转换为 `np.int32`，避免 INT8 溢出。
- 输出 dtype 为 `np.int32`。
- 使用 NumPy 的矩阵乘法实现，不要手写三重循环作为主实现。

### `software/quantize.py`

实现最简单的对称量化工具。

必须提供函数：

```python
def quantize_to_int8(values: np.ndarray, scale: float) -> np.ndarray:
    """Quantize float array to INT8 with round, clip, and cast."""

def dequantize_from_int8(values: np.ndarray, scale: float) -> np.ndarray:
    """Convert INT8 values back to float32."""
```

要求：

- `quantize_to_int8` 使用 `np.round(values * scale)`。
- clip 到 `[-128, 127]`。
- 输出 dtype 为 `np.int8`。
- `dequantize_from_int8` 输出 dtype 为 `np.float32`。

### `software/test_vectors.py`

负责生成、保存和加载测试数据。

必须提供函数：

```python
def generate_int8_matrices(M: int, K: int, N: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Generate deterministic INT8 matrices A[M,K] and B[K,N]."""

def save_test_vectors(output_dir: str | Path, input_a: np.ndarray, input_b: np.ndarray, golden_c: np.ndarray, metadata: dict) -> None:
    """Save input_a.npy, input_b.npy, golden_c.npy, and metadata.json."""

def load_test_vectors(vector_dir: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Load vectors and metadata."""
```

保存文件：

```text
test_vectors/
  input_a.npy
  input_b.npy
  golden_c.npy
  metadata.json
```

`metadata.json` 至少包含：`M`、`K`、`N`、`shift`、`seed`、`a_dtype`、`b_dtype`、`c_dtype`、`layout`。

### `pynq_driver/register_map.py`

封装寄存器表读取和 offset 转换。

必须提供：

```python
@dataclass
class RegisterMap:
    CTRL: int
    A_ADDR: int
    B_ADDR: int
    C_ADDR: int
    M: int
    K: int
    N: int
    SHIFT: int

    @classmethod
    def from_json(cls, path: str | Path) -> "RegisterMap":
        ...
```

要求：

- 支持 JSON 中的 offset 写成 `"0x10"` 或整数。
- 如果缺少关键字段，应抛出清晰异常。
- `CTRL` 默认可为 `0x00`，但仍允许配置覆盖。

### `pynq_driver/overlay_driver.py`

负责加载 overlay 和获取 IP。

必须提供：

```python
class OverlayDriver:
    def __init__(self, bitfile: str, ip_name: str):
        ...

    def get_ip(self):
        ...

    def print_ip_dict(self) -> None:
        ...
```

要求：

- 延迟导入 `pynq`，避免 PC 端 import 整个项目时报错。
- 加载 overlay 后检查 `ip_name` 是否存在于 `overlay.ip_dict`。
- 如果找不到 IP，错误信息里打印可用 IP 名称。

### `pynq_driver/matmul_accel.py`

这是核心驱动类。

必须提供：

```python
class MatmulAccel:
    def __init__(self, bitfile: str, ip_name: str, register_map: RegisterMap):
        ...

    def run(self, input_a: np.ndarray, input_b: np.ndarray, shift: int) -> np.ndarray:
        """Run hardware matmul and return INT32 output matrix."""

    def run_with_timing(self, input_a: np.ndarray, input_b: np.ndarray, shift: int) -> tuple[np.ndarray, dict]:
        """Run hardware matmul and return result plus timing dict."""
```

驱动流程必须按顺序实现：

1. 检查 `input_a`、`input_b` 是二维矩阵。
2. 检查 dtype 为 `np.int8`，必要时给出清晰错误。
3. 计算 `M, K, N`。
4. 使用 `pynq.allocate` 分配：
   - `a_buf`: shape `(M * K,)`, dtype `np.int8`
   - `b_buf`: shape `(K * N,)`, dtype `np.int8`
   - `c_buf`: shape `(M * N,)`, dtype `np.int32`
5. 将输入矩阵按 row-major 展平写入 buffer。
6. 将 `c_buf` 清零。
7. 必要时调用 buffer flush。
8. 写 AXI Lite 寄存器：
   - `A_ADDR = a_buf.physical_address`
   - `B_ADDR = b_buf.physical_address`
   - `C_ADDR = c_buf.physical_address`
   - `M = M`
   - `K = K`
   - `N = N`
   - `SHIFT = shift`
9. 写 `CTRL` 的 bit0 启动 IP，即 `ap_start`。
10. 轮询 `CTRL` 的 bit1，即 `ap_done`。
11. 设置超时，避免硬件异常时无限卡死。
12. 必要时 invalidate 输出 buffer。
13. 将输出 reshape 为 `(M, N)` 并返回普通 NumPy 数组。
14. 释放 buffer，避免重复运行后内存泄露。

控制寄存器常见含义：

```text
CTRL bit0: ap_start
CTRL bit1: ap_done
CTRL bit2: ap_idle
CTRL bit3: ap_ready
```

注意：真实 HLS IP 可能对 64-bit 地址使用低 32 位和高 32 位两个寄存器。如果 HLS header 显示地址寄存器被拆成 `a_1` / `a_2`，驱动需要支持写低 32 位和高 32 位。

### `pynq_driver/benchmark.py`

负责批量测试。

必须提供函数：

```python
def run_benchmark(cases: list[dict], accel: MatmulAccel) -> list[dict]:
    """Run multiple M/K/N/shift cases and return result rows."""
```

每个结果 row 至少包含：

```text
M, K, N, shift, pass, max_abs_error, cpu_time_ms, fpga_kernel_time_ms, total_time_ms
```

### `scripts/generate_vectors.py`

命令行生成测试数据。

示例命令：

```bash
python scripts/generate_vectors.py --M 16 --K 64 --N 16 --shift 7 --seed 0 --out test_vectors/default
```

### `scripts/run_cpu_check.py`

只运行 CPU 参考实现，用于 PC 端提前验证。

示例命令：

```bash
python scripts/run_cpu_check.py --vectors test_vectors/default
```

### `scripts/run_pynq_once.py`

在 PYNQ 板端运行一次硬件验证。

示例命令：

```bash
python scripts/run_pynq_once.py \
  --bitfile overlays/matmul_overlay.bit \
  --ip-name matmul_accel_0 \
  --register-map configs/register_map.example.json \
  --vectors test_vectors/default
```

输出示例：

```text
PASS
M=16 K=64 N=16 shift=7
max_abs_error=0
cpu_time_ms=...
fpga_kernel_time_ms=...
total_time_ms=...
```

### `scripts/run_benchmark.py`

运行多组尺寸并输出 CSV 或 Markdown 表格。

默认测试组合：

```text
tiny:   M=2,  K=4,   N=2,  shift=7
small:  M=16, K=64,  N=16, shift=7
medium: M=32, K=128, N=32, shift=7
shift:  M=16, K=64,  N=16, shift=3
```

## 5. Notebook 要求

Notebook 不是核心驱动，只负责演示。Notebook 中不要复制大量驱动逻辑，只调用 `.py` 模块。

Notebook 建议 cell：

1. 项目说明和当前 overlay 文件。
2. 导入模块。
3. 加载配置。
4. 打印 `overlay.ip_dict`。
5. 加载测试数据。
6. 运行 CPU golden result。
7. 调用 `MatmulAccel.run_with_timing`。
8. 检查 `np.testing.assert_array_equal`。
9. 输出 benchmark 表格。

如果让 agent 生成 `.ipynb`，必须使用标准 notebook JSON，并且每个 cell 的 metadata 中包含 `language` 字段。

## 6. PC 端开发流程

在没有 PYNQ 板和 overlay 之前，可以先完成这些：

```bash
python -m venv .venv
pip install numpy pytest
python scripts/generate_vectors.py --M 16 --K 64 --N 16 --shift 7 --seed 0 --out test_vectors/default
python scripts/run_cpu_check.py --vectors test_vectors/default
pytest
```

PC 端不应强制安装 `pynq`。所有 PYNQ 相关 import 都应延迟到 PYNQ 板端运行时。

## 7. PYNQ 板端部署流程

在 PYNQ-Z2 上建议部署到：

```text
/home/xilinx/jupyter_notebooks/matmul_accel/
```

需要复制：

```text
quant_mma_accel/
  configs/
  software/
  pynq_driver/
  scripts/
  test_vectors/
  overlays/matmul_overlay.bit
  overlays/matmul_overlay.hwh
```

板端验证命令：

```bash
cd /home/xilinx/jupyter_notebooks/matmul_accel/quant_mma_accel
python scripts/run_pynq_once.py --bitfile overlays/matmul_overlay.bit --ip-name matmul_accel_0 --register-map configs/register_map.example.json --vectors test_vectors/default
python scripts/run_benchmark.py --bitfile overlays/matmul_overlay.bit --ip-name matmul_accel_0 --register-map configs/register_map.example.json
```

如果 Notebook 打开方便，也可以在浏览器里打开 `pynq_driver/demo_notebook.ipynb`，但 Notebook 应该只调用上述模块。

## 8. 和硬件同学必须对齐的接口表

代码生成前先保留这张表，等硬件输出后填真实值。

| 项目 | 当前约定 | 需要谁确认 |
|---|---|---|
| overlay 文件名 | `matmul_overlay.bit/.hwh` | Vivado 同学 |
| IP 名称 | `matmul_accel_0` | Vivado 同学 |
| A 类型 | INT8 | HLS 同学 |
| B 类型 | INT8 | HLS 同学 |
| C 类型 | INT32 | HLS 同学 |
| A shape | `M x K` | 三方确认 |
| B shape | `K x N` | 三方确认 |
| C shape | `M x N` | 三方确认 |
| 存储顺序 | row-major | HLS 同学 |
| 缩放方式 | arithmetic right shift | HLS 同学 |
| 默认 shift | `7` | 三方确认 |
| 地址寄存器宽度 | 32-bit 或 64-bit | HLS/Vivado 同学 |
| `A_ADDR` offset | 待确认 | HLS 同学 |
| `B_ADDR` offset | 待确认 | HLS 同学 |
| `C_ADDR` offset | 待确认 | HLS 同学 |
| `M/K/N/SHIFT` offset | 待确认 | HLS 同学 |

你可以直接发给硬件同学：

```text
请给我 HLS 导出的 control register map，最好是 xmatmul_accel_hw.h 或 driver header。
我需要 a/b/c 指针、M、K、N、shift、ap_start、ap_done 的 offset，以及地址寄存器是 32-bit 还是 64-bit。
```

## 9. 验收标准

### PC 端验收

- 能生成固定随机种子的测试数据。
- `cpu_ref.py` 输出 dtype 为 `np.int32`。
- 单元测试通过。
- PC 端 import 项目时不会因为没有 `pynq` 包而失败。

### PYNQ 端验收

- `Overlay(bitfile)` 能成功加载。
- `overlay.ip_dict` 中能看到目标 IP。
- 单次 `run_pynq_once.py` 输出 `PASS`。
- `max_abs_error=0`。
- benchmark 能输出至少 3 组矩阵尺寸的结果。
- 程序异常时不会无限卡死，有 timeout 错误信息。

### 汇报材料验收

- 有 CPU vs FPGA 表格。
- 有正确性截图。
- 有 `overlay.ip_dict` 或 IP 地址映射截图。
- 能说明 Notebook 只是演示入口，核心驱动是 Python 模块。

## 10. 常见问题处理策略

### 找不到 IP

处理：打印 `overlay.ip_dict.keys()`，确认 `.bit` 和 `.hwh` 同名，确认 `ip_name` 是否和 Vivado 导出一致。

### 程序卡在轮询完成

处理：检查 `ap_start` 是否写入，AXI Master 是否连到 DDR，地址寄存器是否需要拆成高低 32 位，矩阵尺寸是否超过 HLS 支持上限。

### 结果不一致

处理：检查 row-major 展平顺序、INT8 是否按 signed 解释、累加是否为 INT32、shift 是否一致、输出 dtype 是否为 INT32。

### 小矩阵性能不快

处理：报告中解释小矩阵被 Python 调用和 AXI 控制开销影响，用 medium 或 larger case 展示趋势。

## 11. 可以直接发给代码生成 Agent 的 Prompt

```text
请根据以下要求生成一个 PYNQ-Z2 量化矩阵乘加速器的软件驱动与验证代码框架。

背景：硬件同学会提供 matmul_overlay.bit 和 matmul_overlay.hwh，其中包含 HLS IP matmul_accel_0。IP 通过 AXI Lite 配置寄存器，通过 AXI Master 访问 DDR。矩阵乘公式为 C = (A @ B) >> shift。A/B 是 INT8，C 是 INT32，矩阵按 row-major 展平。

请创建目录 quant_mma_accel，并实现以下文件：
- configs/default.json
- configs/register_map.example.json
- software/cpu_ref.py
- software/quantize.py
- software/test_vectors.py
- pynq_driver/register_map.py
- pynq_driver/overlay_driver.py
- pynq_driver/matmul_accel.py
- pynq_driver/benchmark.py
- scripts/generate_vectors.py
- scripts/run_cpu_check.py
- scripts/run_pynq_once.py
- scripts/run_benchmark.py
- tests/test_cpu_ref.py
- tests/test_quantize.py
- README.md
- requirements.txt

重要要求：
1. PC 端不安装 pynq，因此所有 pynq import 必须延迟到板端运行时。
2. CPU golden result 必须使用 np.int32 累加，输出 np.int32。
3. register map 从 JSON 读取，不能把 offset 写死在驱动里。
4. MatmulAccel.run() 要分配 PYNQ buffer，写 AXI Lite 寄存器，启动 IP，轮询 ap_done，读取输出并释放 buffer。
5. 轮询必须有 timeout，不能无限 while。
6. 支持 64-bit 物理地址拆成低 32 位和高 32 位写寄存器的情况，可以通过配置或 helper 函数实现。
7. scripts/generate_vectors.py 可以在 PC 上生成 input_a.npy、input_b.npy、golden_c.npy、metadata.json。
8. scripts/run_pynq_once.py 在 PYNQ 板端运行，输出 PASS/FAIL、max_abs_error、cpu_time_ms、fpga_kernel_time_ms、total_time_ms。
9. tests 只测试不依赖 PYNQ 的软件部分。
10. 代码要清晰、模块化，README 写明 PC 端和 PYNQ 端如何运行。

默认参数：M=16, K=64, N=16, shift=7, seed=0, ip_name=matmul_accel_0。

第一版不要接入 llama2.c，不要实现 HLS/Vivado 代码，只完成软件驱动与验证部分。
```

## 12. 你的最近执行顺序

1. 先让 agent 生成上面的 Python 项目框架。
2. 在 PC 端运行 `generate_vectors.py` 和 `pytest`。
3. 等硬件同学给 `.bit/.hwh` 和 register map。
4. 修改 `configs/register_map.example.json` 为真实 offset。
5. 把项目复制到 PYNQ-Z2。
6. 先运行 `run_pynq_once.py`，再运行 `run_benchmark.py`。
7. 最后再补 Notebook 演示和汇报截图。