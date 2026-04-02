# 主子循环块报表示例

主子循环块：主表每条记录循环渲染一个"卡片块"，块内包含主表信息 + 子表明细列表。

---

## 一、核心规则

### 与普通主子表的区别

| 对比项 | 普通主子表 | 主子循环块 |
|-------|----------|----------|
| 主表绑定 | `${db.field}` 单值 | `#{db.field}` 列表（循环） |
| 显示方式 | 一条主表记录 + 子表列表 | 多条主表记录，每条一个卡片 |
| URL传参 | 需要 `?id=1` 指定 | 不需要，自动循环所有 |
| loopBlockList | 不需要 | **必须配置** |
| loopBlock标记 | 不需要 | **每个单元格必须加** `"loopBlock": 1` |
| isPage | 主表可分页 | 主表 `"0"`（不分页） |

### 关键配置

1. **loopBlockList** — 定义循环块的行列范围和驱动数据集
2. **每个单元格** — 必须加 `"loopBlock": 1`
3. **间隔行** — 循环块末尾需要足够的空行作为卡片间隔
4. **主子表联动** — 仍然需要 `link/saveAndEdit` 配置 linkType=4

---

## 二、完整创建流程

### Step 1-2: 创建空报表 + 数据集

与普通主子表相同，区别：
- 主表 SQL 不需要 WHERE 条件（循环所有记录）
- 主表 `isPage: "0"`（不分页）
- 子表 SQL 需要 `WHERE order_fk_id = '${order_fk_id}'`
- 子表 paramList 必须有参数（`searchFlag: 0`）

```python
# 主表 - 查全部，不分页
main_db = {
    "dbCode": "mainOrder", "dbChName": "订单主表",
    "dbType": "0", "isPage": "0",
    "dbDynSql": "select * from rep_demo_order_main",
    "paramList": []  # 不需要参数
}

# 子表 - 按外键过滤
sub_db = {
    "dbCode": "subProduct", "dbChName": "订单商品",
    "dbType": "0", "isPage": "0",
    "dbDynSql": "select * from rep_demo_order_product where order_fk_id = '${order_fk_id}'",
    # 子表参数必须有，searchFlag=0 不勾选查询
    "paramList": [
        {"paramName": "order_fk_id", "paramTxt": "订单外键", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 0, "searchMode": 1}
    ]
}
```

### Step 3: 配置主子表联动

```python
parameter = json.dumps({
    "main": "mainOrder", "sub": "subProduct",
    "subReport": [{"mainField": "id", "subParam": "order_fk_id", "tableIndex": 1}]
}, ensure_ascii=False)

link_data = {
    "mainReport": "mainOrder", "subReport": "subProduct",
    "linkName": "订单主子循环块", "parameter": parameter,
    "linkType": "4", "reportId": report_id
}
api_request('/jmreport/link/saveAndEdit', link_data)
```

### Step 4: 构造循环块 jsonStr

**布局结构（每条主表记录循环渲染）：**

```
Row 1:  标题"订单信息"（合并6列）
Row 2:  订单编号：#{主.code}  |  订单日期：#{主.date}
Row 3:  创建人：#{主.by}      |  创建时间：#{主.time}
Row 4:  描述：#{主.descc}
Row 5:  空行分隔（5px）
Row 6:  子标题"商品明细"
Row 7:  子表表头（商品名称|数量|单价|类型|...）
Row 8:  子表数据行 #{子.product_name} #{子.num} ...
Row 9-30: 间隔空行（22行 x 25px = 550px间距）
```

**循环块内每个单元格必须加 `"loopBlock": 1`：**

```python
LB = 1  # loopBlock 标记

rows_data = {
    "1": {"cells": {
        "1": {"text": "订单信息", "style": 5, "merge": [0, 5], "loopBlock": LB}
    }, "height": 40},
    "2": {"cells": {
        "1": {"text": "订单编号：", "style": 6, "loopBlock": LB},
        "2": {"text": "#{mainOrder.order_code}", "style": 7, "merge": [0, 1], "loopBlock": LB},
        "4": {"text": "订单日期：", "style": 6, "loopBlock": LB},
        "5": {"text": "#{mainOrder.order_date}", "style": 7, "merge": [0, 1], "loopBlock": LB}
    }, "height": 30},
    # ... 主表其他行（都加 loopBlock: LB）
    "6": {"cells": {
        "1": {"text": "商品明细", "style": 8, "merge": [0, 5], "loopBlock": LB}
    }, "height": 34},
    "7": {"cells": {
        "1": {"text": "商品名称", "style": 4, "loopBlock": LB},
        "2": {"text": "数量", "style": 4, "loopBlock": LB},
        # ...
    }, "height": 34},
    "8": {"cells": {
        "1": {"text": "#{subProduct.product_name}", "style": 2, "loopBlock": LB},
        "2": {"text": "#{subProduct.num}", "style": 2, "loopBlock": LB},
        # ...
    }},
    # 间隔空行（Row 9-30，每行25px）
    **{str(i): {"cells": {
        "1": {"text": " ", "loopBlock": LB}, "2": {"text": " ", "loopBlock": LB},
        "3": {"text": " ", "loopBlock": LB}, "4": {"text": " ", "loopBlock": LB},
        "5": {"text": " ", "loopBlock": LB}, "6": {"text": " ", "loopBlock": LB}
    }, "height": 25} for i in range(9, 31)},
    "len": 200
}
```

### loopBlockList 配置

```python
# sci/eci: 列范围（0-based），sri/eri: 行范围（0-based），db: 主数据集code
loop_block_list = [
    {"sci": 1, "eci": 6, "sri": 1, "eri": 30, "index": 1, "db": "mainOrder"}
]
```

| 字段 | 说明 |
|------|------|
| `sci` | 起始列（0-based），通常为1（B列） |
| `eci` | 结束列（0-based） |
| `sri` | 起始行（0-based），循环块第一行 |
| `eri` | 结束行（0-based），**必须包含所有间隔空行** |
| `index` | 循环块序号（从1开始） |
| `db` | 驱动循环的**主表**数据集 dbCode |

> **间隔行数决定卡片间距：** 参考示例用 20+ 行空行（每行25px）。`eri` 必须覆盖所有间隔行，否则间距不生效。

### save 请求体关键字段

```python
save_data = {
    # ... 标准字段 ...
    "loopBlockList": loop_block_list,  # 循环块配置
    "area": False,                     # 让系统自动计算
    # ...
}
```

---

## 三、循环块 vs 普通主子表选择

| 场景 | 推荐方式 |
|------|---------|
| 查看单条订单详情（URL传参） | 普通主子表（`${}`单值 + `#{}`列表） |
| 打印所有订单（每条一页/一块） | **主子循环块**（loopBlock循环） |
| 批量打印发货单/收据 | **主子循环块** |
| 数据卡片式展示 | **主子循环块** |
