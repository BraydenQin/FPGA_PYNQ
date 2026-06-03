# PYNQ 交付包

本目录包含 PYNQ 侧同学可直接使用的 INT8 矩阵乘法 Overlay 相关文件。

## 推荐交付的文件

- `matmul_overlay.bit`
- `matmul_overlay.hwh`
- `register_map.actual.json`
- `PYNQ_Delivery_Guide.docx`

## 附加参考文件

- `matmul_overlay.xsa`
- `xmatmul_accel_hw.h`
- `csynth.rpt`
- `overlay_metadata.json`

## 硬件信息

- Overlay 基础名称：`matmul_overlay`
- IP 实例名称：`matmul_accel_0`
- AXI Lite 基地址：`0x40000000`
- AXI Lite 高地址：`0x4000FFFF`
- 数据契约：
  - `A`：`int8[M, K]`，行优先
  - `B`：`int8[K, N]`，行优先
  - `C`：`int32[M, N]`，行优先
  - 计算规则：`C = (A @ B) >> shift`
- 数据搬移路径：PS 通过 AXI Lite 配置 IP，IP 通过 `m_axi` 直接读写 DDR。

## PYNQ 使用说明

- 将 `matmul_overlay.bit` 和 `matmul_overlay.hwh` 放在同一目录下，且保持相同的基础名称。PYNQ Overlay 加载依赖此命名规则。
- 使用 `matmul_accel_0` 作为 `ip_name`。
- 提供的 `register_map.actual.json` 兼容本地 PYNQ 驱动中的 `RegisterMap.from_json(...)`。

## 最小软件示例

```python
from pynq_driver.matmul_accel import MatmulAccel
from pynq_driver.register_map import RegisterMap

register_map = RegisterMap.from_json("register_map.actual.json")
accel = MatmulAccel(
    bitfile="matmul_overlay.bit",
    ip_name="matmul_accel_0",
    register_map=register_map,
)

output = accel.run(input_a, input_b, shift=0)
```

## 命名说明

matmul_overlay.* 文件是为 PYNQ 使用而导出的设计文件的便捷副本。它们与对应的 design_1_wrapper.* 文件字节完全相同，但经过重命名，使得 .bit 和 .hwh 明确共享同一个 Overlay 基础名称。
