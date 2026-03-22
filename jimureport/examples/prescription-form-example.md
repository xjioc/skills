# 处方笺模板示例（表单+列表混合）

## 场景说明

一个医院处方笺模板，包含：
- **单条数据**（患者信息）：使用 `${yonghu.字段名}` 绑定
- **列表数据**（药品明细）：使用 `#{yaopin.字段名}` 绑定
- 外边框用 **thick**（粗线），内部用 **thin**（细线）
- 自定义列宽，多处单元格合并
- 隐藏行（`-1` 行）存放辅助字段

## 数据绑定语法对比

| 语法 | 数据类型 | 说明 | 示例 |
|------|---------|------|------|
| `${dbCode.field}` | 单条记录 | 直接取值，不循环 | `${yonghu.yphone}` |
| `#{dbCode.field}` | 列表数据 | 自动循环展开 | `#{yaopin.name}` |

## 布局结构（行分布）

| 行号 | 内容 | 高度 | 说明 |
|------|------|------|------|
| 0 | 顶部留白 | 96px | 预留logo/印章区域 |
| 1 | 上边框线 | 18px | thick边框顶边 |
| 2 | 标题"智能医学院处方笺" | 124px | 合并C3:L3，style 38（14号加粗居中） |
| 3 | 姓名/性别/年龄 | 默认 | `${yonghu.yphone}` `${yonghu.ysex}` `${yonghu.yage}` |
| 4 | 单位/电话 | 29px | `${yonghu.danwei}` `${yonghu.yphone}` |
| 5 | 初步诊断 | 34px | `${yonghu.yjieguo}` 合并7列 |
| 6 | RP：标记 | 79px | 处方开始标志 |
| 7 | **药品列表行** | 37px | `#{yaopin.name}` `#{yaopin.percent}` — 自动循环 |
| 8 | 空行间隔 | 27px | |
| 9 | 医嘱 | 默认 | `${yonghu.yizhu}` 合并8列 |
| 10-12 | 费用明细 | 默认 | 药品费/中成药费/治疗费/检查费等 |
| 13 | 合计 | 默认 | `${yonghu.ytotal}` |
| 14 | 空行 | 17px | |
| 15 | 医师/日期 | 43px | `${yonghu.yishe}` `${yonghu.kdata}` |
| 16 | 空行 | 17px | |
| 17 | 下边框线 | 默认 | thick边框底边 |
| -1 | **隐藏行** | — | `#{yaopin.key1}` `#{yaopin.key2}` 辅助数据 |

## 关键特性

### 1. 隐藏行（-1行）

```json
"-1": {
    "cells": {
        "0": { "text": "#{yaopin.key2}" },
        "-1": { "text": "#{yaopin.key1}" }
    },
    "isDrag": true
}
```

用于存放不需要显示但参与数据处理的字段，行号为 `-1`，列号可以为 `-1`。

### 2. 粗细边框方案

外框用 `thick`，内部用 `thin`，通过不同 style 组合实现：

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ← 行1: thick top + thick left/right
┃  标题                          ┃  ← 行2-16: thick left + thick right
┃  ──────────────────────────── ┃  ← 内部分隔: thin border
┃  内容                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ← 行17: thick bottom + thick left/right
```

边框样式索引分类：

| 索引范围 | 边框类型 | 用途 |
|---------|---------|------|
| 24-26 | thick top + left/right | 顶部边框行 |
| 27, 31 | thick left | 左边框列 |
| 28 | thick right | 右边框列 |
| 32-34 | thick bottom + left/right | 底部边框行 |
| 6-7 | thin 四边 | 内部费用格子 |

### 3. 自定义列宽

```json
"cols": {
    "0": { "width": 35 },
    "1": { "width": 14 },
    "2": { "width": 56 },
    "3": { "width": 54 },
    "4": { "width": 156 },
    "5": { "width": 41 },
    "6": { "width": 31 },
    "7": { "width": 113 },
    "8": { "width": 58 },
    "9": { "width": 20 },
    "10": { "width": 23 },
    "11": { "width": 81 },
    "12": { "width": 12 },
    "len": 50
}
```

### 4. 合并单元格

```json
"merges": [
    "C3:L3",       // 标题横跨10列
    "C4:D4",       // 姓名标签
    "C5:D5",       // 单位标签
    "C6:D6",       // 初步诊断标签
    "E6:L6",       // 诊断结果跨8列
    "B7:D7",       // RP标记
    "C7:E7",       // 药品名称
    "H7:I7",       // 药品规格
    "D10:L10",     // 医嘱跨9列
    "C11:D11",     // 药品费
    "F11:G11",     // 中成药费
    "I11:K11",     // 治疗费
    "E13:H13",     // 合计金额
    "J16:L16",     // 日期
    ...
]
```

### 5. isDrag 属性

```json
"3": { "cells": {...}, "isDrag": true }
```

`isDrag: true` 表示该行的高度曾被用户手动拖拽调整过。

### 6. toolPrintSizeObj（打印尺寸）

```json
"toolPrintSizeObj": {
    "printType": "A4",
    "widthPx": 718,
    "heightPx": 1047
}
```

A4纸张的像素尺寸，用于打印预览。

## 对应的数据集配置

### 数据集1：yonghu（患者信息，单条）

```json
{
    "dbCode": "yonghu",
    "dbChName": "患者信息",
    "dbType": "0",
    "isList": "0",
    "isPage": "0",
    "dbDynSql": "select yphone, ysex, yage, danwei, yjieguo, yizhu, yprice, yzhenliao, ytotal, yishe, kdata from yonghu_table where id = '${id}'"
}
```

### 数据集2：yaopin（药品明细，列表）

```json
{
    "dbCode": "yaopin",
    "dbChName": "药品明细",
    "dbType": "0",
    "isList": "1",
    "isPage": "0",
    "dbDynSql": "select name, percent, key1, key2 from yaopin_table where chufang_id = '${id}'"
}
```

## 与普通列表的区别

| 特性 | 普通列表 | 处方笺（表单混合） |
|------|---------|-------------------|
| 数据集数量 | 通常1个 | 多个（yonghu + yaopin） |
| 绑定语法 | 全部用 `#{}` | 单条用 `${}`，列表用 `#{}` |
| 布局 | 表头+数据行 | 自由布局，多区域 |
| 边框 | 统一thin | 外粗内细 |
| 列宽 | 默认均匀 | 自定义不等宽 |
| 合并单元格 | 少/无 | 大量合并 |
| 隐藏行 | 无 | `-1` 行存辅助数据 |
