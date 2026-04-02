# 分版报表示例（多表格并排）

分版报表：左右并排多个独立表格，各自绑定不同数据集，独立循环展开。

---

## 一、核心规则

### 什么是分版

左侧已有一个表格（主数据集），右侧需要另一个独立表格时，使用分版。每个分版区域有独立的数据集和循环逻辑。

### 关键配置

1. **zonedEditionList** — 定义分版区域的行列范围和数据集
2. **分版区域单元格** — 必须加 `"zonedEdition": N`（N=分版编号，从1开始）
3. **左侧主表格** — 普通 `#{}` 绑定，不需要任何标记
4. **数据集** — 分版区域的数据集 `isPage: "0"`（不分页），与主数据集独立

### zonedEditionList 结构

```python
zoned_edition_list = [
    {"sci": 7, "sri": 3, "eci": 9, "eri": 4, "db": "depts", "index": 1},
    # 可以有多个分版区域
    {"sci": 11, "sri": 3, "eci": 12, "eri": 4, "db": "other", "index": 2}
]
```

| 字段 | 说明 |
|------|------|
| `sci` | 起始列（rows中的列key，从0或1开始取决于布局） |
| `eci` | 结束列 |
| `sri` | 起始行（rows中的行key） |
| `eri` | 结束行（包含表头+数据行） |
| `db` | 分版区域绑定的数据集 dbCode |
| `index` | 分版编号（从1开始，与单元格 `zonedEdition` 值对应） |

---

## 二、完整创建流程（SQL 数据集）

### Step 1: 创建数据集

```python
# 左侧主数据集（用户信息）- 可分页
user_db = {
    "dbCode": "users", "dbChName": "用户信息",
    "dbType": "0", "isPage": "1",
    "dbDynSql": "select username, realname, sex, email, phone from sys_user",
    "fieldList": [...], "paramList": []
}

# 右侧分版数据集（部门信息）- 不分页
dept_db = {
    "dbCode": "depts", "dbChName": "部门信息",
    "dbType": "0", "isPage": "0",  # 分版区域不分页
    "dbDynSql": "select depart_name, org_code, description from sys_depart",
    "fieldList": [...], "paramList": []
}
```

> **分版区域数据集类型不限**：SQL、API、JavaBean、JSON 均可使用，配置方式与普通数据集一致。

### Step 2: 构造 jsonStr

**布局结构（标题和内容之间加空行间距）：**

```
     B    C    D    E    F   G   H    I    J
  1: ──────── 分版报表示例 ──────────────────
  2: （空行 15px 间距）
  3: ── 用户信息 ──              ── 部门信息 ──
  4: 账号│姓名│性别│邮箱│电话│ │部门名│编码│描述
  5: #{} │#{} │#{} │#{} │#{} │ │#{}  │#{} │#{}
     ←── 主数据集 ──→          ←─ zonedEdition=1 ─→
```

> **标题与内容之间加一行空行**（height=15px），避免标题紧贴表格。分栏/循环块同理。

```python
rows_data = {
    "1": {"cells": {
        "1": {"text": "分版报表示例", "style": 5, "merge": [0, 8]}
    }, "height": 40},
    "2": {"cells": {
        "1": {"text": "用户信息", "style": 6, "merge": [0, 4]},
        "7": {"text": "部门信息", "style": 6, "merge": [0, 2]}
    }, "height": 34},
    # 左侧表头（普通，不加 zonedEdition）
    # 右侧表头（加 zonedEdition: 1）
    "3": {"cells": {
        "1": {"text": "用户账号", "style": 4},
        "2": {"text": "真实姓名", "style": 4},
        "3": {"text": "性别", "style": 4},
        "4": {"text": "邮箱", "style": 4},
        "5": {"text": "电话", "style": 4},
        "7": {"text": "部门名称", "style": 4, "zonedEdition": 1},
        "8": {"text": "机构编码", "style": 4, "zonedEdition": 1},
        "9": {"text": "描述", "style": 4, "zonedEdition": 1}
    }, "height": 34},
    # 左侧数据行 + 右侧数据行
    "4": {"cells": {
        "1": {"text": "#{users.username}", "style": 2},
        "2": {"text": "#{users.realname}", "style": 2},
        "3": {"text": "#{users.sex}", "style": 2},
        "4": {"text": "#{users.email}", "style": 2},
        "5": {"text": "#{users.phone}", "style": 2},
        "7": {"text": "#{depts.depart_name}", "style": 2, "zonedEdition": 1},
        "8": {"text": "#{depts.org_code}", "style": 2, "zonedEdition": 1},
        "9": {"text": "#{depts.description}", "style": 2, "zonedEdition": 1}
    }},
    "len": 200
}

# 分版配置：右侧部门区域
zoned_edition_list = [
    {"sci": 7, "sri": 3, "eci": 9, "eri": 4, "db": "depts", "index": 1}
]
```

### Step 3: save 请求体

```python
save_data = {
    # ... 标准字段 ...
    "zonedEditionList": zoned_edition_list,  # 分版配置
    "area": False,
    # ...
}
```

---

## 三、多个分版区域

可同时定义多个分版，每个用不同的 index：

```python
zoned_edition_list = [
    {"sci": 5, "sri": 3, "eci": 7, "eri": 4, "db": "datasetA", "index": 1},
    {"sci": 9, "sri": 3, "eci": 10, "eri": 4, "db": "datasetB", "index": 2}
]

# 单元格标记对应的 index
"5": {"text": "#{datasetA.field}", "zonedEdition": 1}  # 分版1
"9": {"text": "#{datasetB.field}", "zonedEdition": 2}  # 分版2
```

---

## 四、分版 vs 分栏

| 对比项 | 分版（zonedEdition） | 分栏（loopBlock + loopTime） |
|-------|---------------------|---------------------------|
| 用途 | 左右并排不同表格 | 同一数据横向重复展示 |
| 数据集 | 每个区域不同数据集 | 同一数据集 |
| 配置 | `zonedEditionList` + `"zonedEdition":N` | `loopBlockList` + `"loopTime":N` + `"loopBlock":1` |
| 循环 | 各区域独立循环 | 整个块横向重复N次 |
| 场景 | 用户表+部门表并排 | 员工卡片分2栏/3栏展示 |
