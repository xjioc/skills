# 自定义分组排序示例

## 场景说明

纵向分组报表，按「区域→城市」两级分组，区域使用自定义排序：华北 → 华南 → 华东（而非数据原始顺序）。使用 JSON 数据集。

**核心属性：** 在分组单元格上添加 `"textOrders": "华北|华南|华东"`，多个值用 `|` 分隔。

## textOrders 属性说明

| 项目 | 说明 |
|------|------|
| 属性名 | `textOrders` |
| 值格式 | `"值1\|值2\|值3"`，用 `\|` 分隔 |
| 适用范围 | 任何分组（纵向 group、横向 groupRight、customGroup） |
| 放置位置 | 分组单元格（含 `aggregate: "group"` 的 cell） |
| 效果 | 分组按指定顺序排列，不在列表中的值排在最后 |

## 数据集配置

JSON 数据集（dbType="3"），12条数据，3个区域 × 2个城市 × 2条记录：

```json
{
    "data": [
        {"region": "华东", "city": "上海", "product": "产品A", "amount": 15000},
        {"region": "华东", "city": "上海", "product": "产品B", "amount": 8000},
        {"region": "华东", "city": "杭州", "product": "产品B", "amount": 12000},
        {"region": "华东", "city": "杭州", "product": "产品A", "amount": 9500},
        {"region": "华南", "city": "广州", "product": "产品C", "amount": 18000},
        {"region": "华南", "city": "广州", "product": "产品A", "amount": 7000},
        {"region": "华南", "city": "深圳", "product": "产品A", "amount": 16000},
        {"region": "华南", "city": "深圳", "product": "产品B", "amount": 11000},
        {"region": "华北", "city": "北京", "product": "产品B", "amount": 20000},
        {"region": "华北", "city": "北京", "product": "产品C", "amount": 13000},
        {"region": "华北", "city": "天津", "product": "产品C", "amount": 11000},
        {"region": "华北", "city": "天津", "product": "产品A", "amount": 9000}
    ]
}
```

saveDb 参数：
```json
{
    "dbCode": "ds",
    "dbChName": "区域销售数据",
    "dbType": "3",
    "jsonData": "{\"data\":[...]}",
    "isList": "1",
    "isPage": "0"
}
```

> **注意：** 分组报表 `isPage` 设为 `"0"`（不分页），确保分组合并完整。

## 数据绑定行配置

```json
{
    "cells": {
        "1": {
            "text": "#{ds.group(region)}",
            "style": 2,
            "aggregate": "group",
            "subtotal": "groupField",
            "funcname": "-1",
            "subtotalText": "合计",
            "textOrders": "华北|华南|华东"
        },
        "2": {
            "text": "#{ds.group(city)}",
            "style": 2,
            "aggregate": "group",
            "subtotal": "groupField",
            "funcname": "-1",
            "subtotalText": "小计"
        },
        "3": {
            "text": "#{ds.product}",
            "style": 2
        },
        "4": {
            "text": "#{ds.amount}",
            "style": 2,
            "subtotal": "-1",
            "funcname": "SUM"
        }
    }
}
```

## save 请求体顶层分组配置

```python
save_data = {
    ...
    "isGroup": True,
    "groupField": "ds.region",   # 指向一级分组字段
    ...
}
```

## 预览效果

数据原始顺序为华东→华南→华北，但因 `textOrders` 设置，预览时按华北→华南→华东显示：

```
┌────────┬────────┬────────┬──────────┐
│ 区域    │ 城市    │ 产品    │ 金额      │
├────────┼────────┼────────┼──────────┤
│        │        │ 产品B   │ 20000    │
│        │ 北京    │ 产品C   │ 13000    │
│        │        │         │ 小计 33000│
│ 华北    ├────────┼────────┼──────────┤
│        │        │ 产品C   │ 11000    │
│        │ 天津    │ 产品A   │ 9000     │
│        │        │         │ 小计 20000│
│        │        │         │ 合计 53000│
├────────┼────────┼────────┼──────────┤
│        │        │ 产品C   │ 18000    │
│        │ 广州    │ 产品A   │ 7000     │
│ 华南    │        │         │ 小计 25000│
│        ├────────┼────────┼──────────┤
│        │ 深圳    │ ...     │ ...      │
│        │        │         │ 合计 52000│
├────────┼────────┼────────┼──────────┤
│ 华东    │ ...    │ ...     │ ...      │
│        │        │         │ 合计 44500│
└────────┴────────┴────────┴──────────┘
```

## 更多用法

### 横向分组自定义排序

`textOrders` 同样适用于 `groupRight` 横向分组：

```json
{
    "text": "#{ds.groupRight(quarter)}",
    "aggregate": "group",
    "direction": "right",
    "textOrders": "Q4|Q1|Q2|Q3"
}
```

### 多级都自定义排序

一级和二级分组可以各自设置 `textOrders`：

```json
// 一级分组
"1": {
    "text": "#{ds.group(region)}",
    "textOrders": "华北|华南|华东",
    ...
},
// 二级分组
"2": {
    "text": "#{ds.group(city)}",
    "textOrders": "北京|天津|广州|深圳|上海|杭州",
    ...
}
```
