# 蓝桥杯单片机踩坑知识库

按 C51 模块整理蓝桥杯单片机答疑数据库，保留筛选后的 C51 原始周报并提供模块化归档入口。

---

## 当前结构

- 模块页：按功能模块汇总踩坑与答疑记录
- 原始周报：完整保留在 [weekly-index.md](./weekly-index.md) 与 [单片机答疑数据库](./单片机答疑数据库/)
- 格式规范：新补充内容仍可参考 [example.md](./example.md)

---

## 模块索引

| 模块 | 文件 | 条目数 |
|---|---|---:|
| LED | [led.md](./led.md) | 32 |
| 数码管 | [seg.md](./seg.md) | 55 |
| 按键 | [key.md](./key.md) | 64 |
| EEPROM | [eeprom.md](./eeprom.md) | 15 |
| DA 输出 | [da.md](./da.md) | 18 |
| AD 采集 | [ad.md](./ad.md) | 13 |
| 定时 / 计数 | [timer.md](./timer.md) | 46 |
| 超声波 | [ultrasonic.md](./ultrasonic.md) | 15 |
| 串口 | [uart.md](./uart.md) | 10 |
| 温度 / 时钟 / 传感器 | [sensor.md](./sensor.md) | 47 |
| 工具链 / 环境 | [toolchain.md](./toolchain.md) | 45 |
| C51 语法 / 基础逻辑 | [programming.md](./programming.md) | 55 |
| 综合赛题 / 系统 | [system.md](./system.md) | 37 |

---

## 原始资料

- 原始周报索引：[weekly-index.md](./weekly-index.md)
- 原始周报目录：[单片机答疑数据库](./单片机答疑数据库/)
- 当前保留周报：70 篇

---

## 使用说明

1. 先从模块页进入，按功能定位问题。
2. 需要看原始上下文时，再跳转到对应周报原文。
3. 新内容优先补充到对应模块页，保持按模块归档。

---

## 本地预览

在仓库根目录执行：

```powershell
.\scripts\preview_docs.ps1
```

常用参数：

```powershell
.\scripts\preview_docs.ps1 -Open
.\scripts\preview_docs.ps1 -HostName 0.0.0.0 -Port 3010
```

脚本会把仓库根目录作为静态站点目录启动本地预览服务，默认优先使用 `http://127.0.0.1:3000`。
