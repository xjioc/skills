# 分栏报表示例

分栏：同一数据集的循环块横向重复 N 次展示，通过 `loopBlockList` 的 `loopTime` 控制栏数。

---

## 一、核心规则

### 分栏 vs 分版

| 对比项 | 分栏（loopBlock + loopTime） | 分版（zonedEdition） |
|-------|---------------------------|---------------------|
| 数据集 | **同一数据集**横向重复 | 不同数据集各自独立 |
| 配置 | `loopBlockList` + `loopTime:N` + `"loopBlock":1` | `zonedEditionList` + `"zonedEdition":N` |
| 场景 | 员工卡片分2栏/3栏 | 用户表+部门表并排 |

### 关键配置

1. **loopBlockList** — 加 `loopTime: N` 指定横向重复次数
2. **循环块内所有单元格** — 必须加 `"loopBlock": 1`
3. **间隔列** — 循环块最后一列留空作为栏间距
4. **标题与循环块之间** — 加一行空行（height=15px）避免紧贴

---

## 二、完整创建流程

### Step 1: 数据集

```python
db_data = {
    "dbCode": "staff", "dbChName": "职员信息",
    "dbType": "0",
    "isPage": "0",  # 分栏不分页
    "dbDynSql": "select name, sex, update_by, jphone from rep_demo_dxtj",
    "fieldList": [...], "paramList": []
}
```

### Step 2: 构造 jsonStr

**布局结构（loopTime=2，分2栏）：**

```
Row 1: 职员信息分栏报表（标题，合并覆盖2栏宽度）
Row 2: （空行 15px 间距）
Row 3: 职员信息（子标题，循环块开始，合并4列）  ← loopBlock
Row 4: 姓名│性别│职务│联系方式│(间隔列)        ← loopBlock
Row 5: #{staff.name}│...│...│...│              ← loopBlock
Row 6: （间隔行 20px）                          ← loopBlock（循环块结束）
       ↑ 横向自动复制一份到右侧 →
```

```python
LB = 1  # loopBlock 标记

rows_data = {
    # 标题（不在循环块内）
    "1": {"cells": {
        "1": {"text": "职员信息分栏报表", "style": 5, "merge": [0, 8]}
    }, "height": 40},
    # 空行间距
    "2": {"cells": {}, "height": 15},
    # 子标题（循环块内，合并4列）
    "3": {"cells": {
        "1": {"text": "职员信息", "style": 1, "merge": [0, 3], "loopBlock": LB},
        "5": {"text": "", "loopBlock": LB}  # 间隔列
    }, "height": 34},
    # 表头
    "4": {"cells": {
        "1": {"text": "姓名", "style": 4, "loopBlock": LB},
        "2": {"text": "性别", "style": 4, "loopBlock": LB},
        "3": {"text": "职务", "style": 4, "loopBlock": LB},
        "4": {"text": "联系方式", "style": 4, "loopBlock": LB},
        "5": {"text": "", "loopBlock": LB}
    }, "height": 34},
    # 数据行
    "5": {"cells": {
        "1": {"text": "#{staff.name}", "style": 2, "loopBlock": LB},
        "2": {"text": "#{staff.sex}", "style": 2, "loopBlock": LB},
        "3": {"text": "#{staff.update_by}", "style": 2, "loopBlock": LB},
        "4": {"text": "#{staff.jphone}", "style": 2, "loopBlock": LB},
        "5": {"text": "", "loopBlock": LB}
    }},
    # 间隔行
    "6": {"cells": {
        "1": {"text": "", "loopBlock": LB},
        "5": {"text": "", "loopBlock": LB}
    }, "height": 20},
    "len": 200
}
```

### loopBlockList 配置

```python
# loopTime=2 → 横向分2栏
loop_block_list = [
    {"sci": 1, "sri": 3, "eci": 5, "eri": 6, "index": 1, "db": "staff", "loopTime": 2}
]
```

| 字段 | 说明 |
|------|------|
| `sci`/`eci` | 列范围（包含间隔列） |
| `sri`/`eri` | 行范围（循环块区域，不含标题） |
| `db` | 数据集 dbCode |
| `loopTime` | **横向重复次数**（2=分2栏，3=分3栏） |
| `index` | 循环块序号 |

### 列配置

```python
cols_data = {
    "1": {"width": 80},   # 姓名
    "2": {"width": 60},   # 性别
    "3": {"width": 80},   # 职务
    "4": {"width": 110},  # 联系方式
    "5": {"width": 30},   # 间隔列（栏间距）
    "len": 100
}
```

> **间隔列**（第5列 width=30px）在循环块最后一列，横向复制时自动成为两栏之间的空白。

### save 请求体

```python
save_data = {
    # ... 标准字段 ...
    "loopBlockList": loop_block_list,
    "area": False,
    # ...
}
```

---

## 三、预览效果

```
        职员信息分栏报表

    职员信息              职员信息
┌────┬──┬──┬──────┐  ┌────┬──┬──┬──────┐
│姓名│性│职│联系方式│  │姓名│性│职│联系方式│
├────┼──┼──┼──────┤  ├────┼──┼──┼──────┤
│张三│1 │1 │1803...│  │小哲│1 │2 │1803...│
└────┴──┴──┴──────┘  └────┴──┴──┴──────┘

    职员信息              职员信息
┌────┬──┬──┬──────┐  ┌────┬──┬──┬──────┐
│闫妮│1 │2 │1803...│  │陌生│1 │2 │1803...│
└────┴──┴──┴──────┘  └────┴──┴──┴──────┘
```

---

## 四、注意事项

- **标题不在循环块内**，不加 `loopBlock`，位于循环块上方
- **标题和循环块之间加空行**（height=15px），避免紧贴
- **标题合并范围**要覆盖 `loopTime` 倍的列宽（如2栏 = 列数x2+间隔列）
- **子标题合并范围**只在循环块内的数据列（不含间隔列），横向复制时自动复制
- `isPage: "0"` — 分栏不分页
- 分3栏只需改 `loopTime: 3`

### 关键踩坑经验

#### 1. 左边距列必须在循环块外部

要实现左侧缩进，**col 0 (A列) 不加入循环块**，循环块从 col 1 开始（`sci: 1`）。这样 A 列作为固定左边距，不会被横向复制。

```python
# 正确：col 0 在循环块外
cols_data = {
    "0": {"width": 72},  # A列 左边距，不在循环块内
    "1": {"width": 80},  # B列 数据列开始
    ...
}
loop_block_list = [{"sci": 1, "eci": 7, ...}]  # 从 col 1 开始

# 错误：col 0 在循环块内 → 左边距也被复制，右栏多出一列空白
loop_block_list = [{"sci": 0, "eci": 7, ...}]
```

#### 2. 右栏复制列必须显式定义宽度

`loopTime=2` 横向复制时，右栏的列（如 col 8~14）**不会继承左栏列宽**，会使用默认100px，导致右栏比左栏宽。**必须在 cols 中显式为右栏列设置与左栏相同的宽度。**

```python
cols_data = {
    # 左栏 col 1~7
    "1": {"width": 80},
    "2": {"width": 60},
    ...
    "7": {"width": 50},   # 间隔列
    # 右栏 col 8~14（必须显式设置！）
    "8": {"width": 80},   # = col 1
    "9": {"width": 60},   # = col 2
    ...
    "14": {"width": 50},  # = col 7
    "len": 100
}
```

> **通用公式：** 如果循环块有 N 列（sci 到 eci），loopTime=K，则需要为 col `eci+1` 到 `sci + N*K - 1` 都设置宽度。

#### 3. 分栏/分版标题样式不要背景色和边框

**仅限分栏和分版报表**：标题横跨多栏，如果有背景色和边框会显得过宽，推荐无背景无边框。

**其他报表类型（普通列表、分组、循环块、主子表、多源等）仍使用标准标题样式（有背景色+边框）。**

```python
# 分栏/分版标题样式（无背景无边框）
{"align": "center", "valign": "middle", "font": {"bold": True, "size": 14}, "color": "#0066CC"}

# 其他报表标题样式（标准，有背景+边框）
{"border": {"bottom": ["thin","#d8d8d8"], ...}, "align": "center", "valign": "middle", "font": {"bold": True, "size": 14}, "bgcolor": "#E6F2FF", "color": "#0066CC"}
```

#### 4. dataRectWidth 需匹配总宽度

设置 `dataRectWidth` 为所有列宽之和（含左边距和两栏），防止列被浏览器自动拉伸：

```python
# 左边距72 + 左栏(80+60+60+100+80+80+50) + 右栏(同) = 72 + 510 + 510 = 1092
save_data = {
    "dataRectWidth": 1100,
    ...
}
```
