---
name: jimureport
description: 积木报表生成器 — 自然语言描述报表需求或提供截图，自动生成积木报表（支持数据报表、打印报表、分组报表、循环报表、数据填报等全类型）。Use when user says "积木报表", "jmreport", "Excel报表", "数据填报", "可视化报表", "打印报表", "分组报表", "循环报表", "按照截图生成报表", "创建积木报表", "做一个可视化报表", "积木设计器", "create jimureport", "visual report". Also triggers when user describes report requirements involving Excel-like layouts, data binding with #{}, or multi-sheet reports, or provides a screenshot to generate a report.
---

# JeecgBoot 积木报表 (JiMu Report) AI 自动生成器

自然语言描述报表需求或提供截图，自动生成积木报表配置，并通过 API 在 JeecgBoot 系统中自动创建/编辑报表。支持数据报表、打印报表、分组报表、循环报表、数据填报等全类型。

> **重要：本 skill 处理「积木报表」（可视化 Excel 风格报表设计器），不涉及「Online 报表」（SQL 驱动的 cgreport）或「Online 表单」（cgform）。**

## 与 Online 报表的区别

| 特性 | 积木报表 (jimureport) | Online 报表 (cgreport) |
|------|----------------------|----------------------|
| 设计方式 | 可视化 Excel 设计器 | 配置式（字段列表） |
| 布局能力 | 自由布局、合并单元格、多sheet | 固定表格列 |
| 数据绑定 | `#{数据集编码.字段名}` | 自动列映射 |
| 填报功能 | 支持（submitForm=1） | 不支持 |
| 打印配置 | 精细控制（纸张/边距/方向） | 基础打印 |
| 增强能力 | CSS/JS/Python 增强 | 无 |

## 前置条件

用户必须提供以下信息（或由 AI 引导确认）：

1. **API 地址**：JeecgBoot 后端地址（如 `https://boot3.jeecg.com/jeecgboot`）
2. **X-Access-Token**：JWT 登录令牌（从浏览器 F12 获取）

如果用户未提供，提示：
> 请提供 JeecgBoot 后端地址和 X-Access-Token（从浏览器 F12 → Network → 任意请求的 Request Headers 中复制）。

## 接口签名机制

部分接口标记了 `@JimuSignature` 注解，调用时必须在 Header 中携带 `X-Sign` 和 `X-TIMESTAMP`，否则返回 `code: 1001` 签名校验失败。

**需要签名的接口：** `queryFieldBySql`、`executeSelectApi`、`loadTableData`、`testConnection`、`download/image`、`dictCodeSearch`、`getDataSourceByPage`、`getDataSourceById`

**不需要签名的接口：** `save`、`saveDb`、`get/{id}`、`field/tree/{reportId}`、`loadDbData/{dbId}`、`source/getJmReportSharedDbPageList`、`source/linkJmReportShareDb`、`source/delShareDbByDbId`

### 签名算法

```
1. 收集所有请求参数（URL query + POST body）
2. 所有值转为字符串（数字→str, 布尔→"true"/"false", 对象→JSON字符串）
3. 按 key 字母升序排序
4. 转为紧凑 JSON 字符串（无空格）: json.dumps(sorted_dict, separators=(',', ':'))
5. 拼接密钥: jsonStr + "dd05f1c54d63749eda95f9fa6d49v442a"
6. MD5 并转大写: hashlib.md5(拼接结果.encode()).hexdigest().upper()
```

> **默认签名密钥：** `dd05f1c54d63749eda95f9fa6d49v442a`（注意第29位是字母 `v` 不是数字 `4`）
> 可通过 `jeecg.signatureSecret` 配置覆盖。
> **时间戳有效期：5 分钟。**

详细文档见 `references/api-dataset.md` 签名机制章节。

参考文档（3个合并文件，覆盖所有配置）：
- `references/report-design.md` - 报表设计核心（单元格属性、数据绑定、分组合计、查询配置、循环块、displayConfig）
- `references/chart-binddata.md` - 图表与组件（30+图表类型、ECharts配置模板、图片/条码/二维码组件、Virtual Cell占位）
- `references/api-dataset.md` - API接口与数据集（签名机制、数据源管理、SQL/API/JSON/JavaBean数据集CRUD）
- `references/query-controls.md` - 查询控件完整参考（8种控件类型、默认值、时间控件、下拉树、范围查询、报表参数配置及约束规则）
- `references/print-config.md` - 打印配置完整参考（纸张大小、布局方向、边距、页码显示/位置/起始范围、页眉页脚、水印文本/字号/颜色/角度、表尾固定底部、常用配置模板）
- `references/background-config.md` - 背景图配置参考（background对象结构、repeat可选值、上传接口/jmreport/upload返回message加/jmreport/img/前缀、无背景时为false）
- `references/taodan-config.md` - 套打配置完整参考（imgList背景图数组、virtual虚拟单元格标记、layer_id关联机制、printConfig.isBackend=true、上传接口message直接用无前缀、Python构建示例）
- `references/report-drilling.md` - 报表钻取与联动（linkType=0报表钻取/1网络链接/2图表联动/4主子表联动，单元格linkIds字符串+display:link，图表linkIds放extData内部，联动linkChartId配置，参数映射4种语法）
- `references/db-connection.md` - 数据库连接动态获取（从服务 application-*.yml 读取数据库配置、解析 JDBC URL、环境变量占位符处理、pymysql 连接，用于建表/插数据/数据探查）
- `references/save-api.md` - /jmreport/save 完整请求体结构（designerObj格式、根级sheet字段、chartList/imgList位置、rows写法、最小新建示例）
- `references/cell-format.md` - 单元格格式化完整参考（所有 format key：normal/number/percent/rmb/usd/eur/year/month/yearMonth/date/date2/time/datetime/img/barcode/qrcode，及 AI 选择规则）

示例文档（含完整 JSON）：
- `examples/param-query.md` - 报表参数查询示例（SQL+API+JavaBean数据集、paramList/fieldList查询配置、searchMode值映射、extJson参数配置、JS三级联动、下拉树、字段查询全类型）
- `examples/master-sub-table.md` - 主子表示例（SQL+API+JavaBean三种主子表、联动配置link/saveAndEdit、子表参数searchFlag:0、${}单值+#{}列表绑定）
- `examples/multi-source-table.md` - 多源报表示例（多数据集同行#{}列表绑定、JSON数据集主子关系、linkType=4联动配置、getLinkData查询接口、与主子表报表的区别）
- `examples/master-sub-loopblock.md` - 主子循环块示例（loopBlockList配置、每个单元格loopBlock:1、间隔行间距、循环块vs普通主子表选择）
- `examples/horizontal-group.md` - 横向分组示例（groupRight+dynamic 纯横向、customGroup 自定义横向）
- `examples/multi-level-header.md` - 多级循环表头示例（二级横向表头+斜线表头、纵横组合、纯横向多级）
- `examples/zone-edition.md` - 分版报表示例（zonedEditionList多表格并排、单元格zonedEdition标记、标题空行间距、分版vs分栏对比）
- `examples/column-split.md` - 分栏报表示例（loopBlockList+loopTime横向重复、间隔列、标题空行间距、分栏vs分版对比）
- `examples/fixed-head-tail.md` - 固定表头表尾示例（fixedPrintHeadRows/TailRows配置、fixedHead/fixedTail单元格标记、打印每页重复）
- `examples/report-drilling.md` - 钻取示例（报表钻取报表+图表钻取报表+网络钻取三合一、linkIds字符串格式+display:link、图表linkIds放extData内部、paramValue专用值name/value/seriesName）
- `examples/object-dataset.md` - 对象数据集示例（逮捕证，isList:"0"+isPage:"0"、${}单值绑定、套打/证件/单据场景、与主子表结合）
- `examples/chart-linkage.md` - 联动示例（表格联动图表+图表联动图表、linkType=2统一、extData必须有chartId/id、图表位置计算避免重叠、目标数据集参数需默认值、area=False自动滚动）
- `examples/shared-dataset.md` - 共享数据集示例（izSharedSource=1、jimuReportId空、linkJmReportShareDb关联、saveDb返回完整对象需提取result['id']、完整4步流程）
- `examples/elasticsearch-datasource.md` - ES数据源示例（dbType="es"、SQL需es.前缀、addDataSource+getDataSourceByPage获取ID、ES 9.x Calcite兼容问题需手动构建fieldList）
- `examples/custom-group-sort.md` - 自定义分组排序示例（textOrders属性、多级分组各自排序、适用于纵向group/横向groupRight/customGroup、JSON数据集两级分组合计）
- `examples/follow-exten-multi-summary.md` - 跟随分组扩展示例（rightFollowExten:"follow"、二级横向分组year+month、分组下方多行汇总SUM/MAX/MIN、第2行起需设置rightFollowExten）

## 可用脚本

> 以下脚本均已在训练环境验证可用，直接调用或修改参数后执行。
> **所有脚本统一使用 `session.trust_env = False` 绕过系统代理**（`proxies=None` 不够）。

| 脚本 | 功能 | 关键函数 |
|------|------|---------|
| `scripts/dict_manager.py` | 字典和字典项的增删改查（先查后建）| `get_or_create_dict()`, `batch_add_items()` |
| `scripts/add_chart.py` | 向已有报表追加任意图表组件 | `add_chart(base_url, token, report_id, chart_type, echarts_config, ...)` |
| `scripts/jimureport_creator.py` | 从零创建完整报表（含数据集/绑定） | 参见脚本内注释 |

### add_chart.py 调用示例

```python
from add_chart import add_chart

add_chart(
    base_url="http://192.168.1.6:8085/jmreport",
    token="<X-Access-Token>",
    report_id="<报表雪花ID>",
    chart_type="bar.background",   # extData 中记录的类型，不影响渲染
    echarts_config={ ... },        # 完整 ECharts option dict，见 chart-binddata.md 第8节
    row=1, col=0,                  # 图表左上角（0-based）
    row_end=10, col_end=6,         # virtual cell 占位范围右下角
    width="650", height="350",
)
```

### dict_manager.py 调用示例

```python
from dict_manager import get_or_create_dict, batch_add_items

dict_id = get_or_create_dict("学历", "edu_level", "学历级别")
batch_add_items(dict_id, [
    {"itemText": "大专", "itemValue": "1", "sortOrder": 1},
    {"itemText": "本科", "itemValue": "2", "sortOrder": 2},
])
```

---

## 交互流程

### Step 0: 判断操作类型

| 用户意图关键词 | 操作类型 |
|---------------|---------|
| 创建/新建/做一个积木报表 | **新增报表** → Step 1 |
| 修改积木报表/改字段/加数据集/加查询条件 | **编辑报表** → 需要报表ID，走编辑流程 |
| 创建/新建/修改/删除共享数据集 | **共享数据集管理** → 走共享数据集流程 |
| 查询共享数据集 | **查询共享数据集** → 调用 `getJmReportSharedDbPageList` |

**编辑报表流程：**

#### 增删字段/参数流程

> **核心原则：修改 SQL → 重新解析 → 保存数据集。fieldList 用解析接口返回的，paramList 在解析结果基础上补充查询配置。**

```
1. field/tree/{reportId}         → 获取数据集列表，通过编码或名称匹配目标数据集，拿到 dbId
2. loadDbData/{dbId}             → 获取数据集详情（SQL、fieldList、paramList）
3. 修改 SQL（增删字段/参数）       → 在 select 中增删字段，在 FreeMarker 条件中增删参数
4. queryFieldBySql（修改后的SQL） → 重新解析，获取最新的 fieldList 和 paramList
5. saveDb（传 id = 更新）         → 用解析后的 fieldList + 补充后的 paramList 保存数据集
```

> **fieldList 直接用解析接口返回的结果。**
>
> **paramList 注意：** `queryFieldBySql` **无法识别 FreeMarker `<#if>` 条件中的 `${}` 参数**，paramList 可能返回空。因此参数需要手动构建或从已有数据集的 paramList 中保留，再补充 searchMode、dictCode、searchFormat 等查询配置。

**Python 实现示例（增加字段+参数）：**
```python
# Step 1-2: 查找数据集
tree = api_request(f'/jmreport/field/tree/{report_id}')
for group in tree['result']:
    info = group[0] if isinstance(group, list) else group
    if info.get('code') == 'users':  # 按编码或名称匹配
        db_id = info['dbId']

detail = api_request(f'/jmreport/loadDbData/{db_id}?reportId={report_id}')['result']
report_db = detail['reportDb']
old_sql = report_db['dbDynSql']

# Step 3: 修改 SQL（增加字段 + 增加参数条件）
new_sql = old_sql.replace('select username,', 'select id, username,')
# 如需增加参数，同时在 SQL 中添加 FreeMarker 条件

# Step 4: 重新解析 → fieldList 用解析结果
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": new_sql, "dbSource": report_db.get('dbSource', ''), "type": "0"
})
new_fields = parse_result['result']['fieldList']

# paramList: queryFieldBySql 无法识别 FreeMarker <#if> 中的 ${} 参数
# 需从已有数据集保留，或手动构建。增删参数时在已有 paramList 基础上操作
existing_params = detail['paramList']
# 如需新增参数: existing_params.append({...})
# 如需删除参数: existing_params = [p for p in existing_params if p['paramName'] != 'xxx']

# Step 5: 保存数据集（传 id = 更新）
save_db_data = {
    "id": db_id,
    "jimuReportId": report_id,
    "dbCode": report_db['dbCode'],
    "dbChName": report_db['dbChName'],
    "dbType": report_db['dbType'],
    "dbSource": report_db.get('dbSource', ''),
    "dbDynSql": new_sql,
    "isList": report_db.get('isList', '1'),
    "isPage": report_db.get('isPage', '1'),
    "fieldList": new_fields,       # 解析接口返回的
    "paramList": existing_params   # 从已有数据集保留
}
api_request('/jmreport/saveDb', save_db_data)
```

> **注意：** `field/tree` 返回结构为 `result: [[{code, dbId, children}, ...]]`，嵌套两层数组。数据集字段名是 `code`（不是 `dbCode`）和 `dbId`（不是 `id`）。`loadDbData` 返回的 SQL 在 `result.reportDb.dbDynSql` 中。

#### 修改报表设计（jsonStr）流程

如果还需要同步修改报表表头/数据行（如新增列），在数据集保存后继续：

```
6. get/{reportId}                → 获取当前 jsonStr
7. 修改 rows/cols/merges          → 增删列、调整合并范围
8. save                          → 保存报表设计
```

详见 `references/api-dataset.md` 中的"查询已有数据集"章节。

#### 共享数据集流程

共享数据集的增删改与普通数据集完全一致，区别仅在于 `izSharedSource: 1`，且 `jimuReportId` 为空。

```
1. 查询共享数据集列表:  GET /jmreport/source/getJmReportSharedDbPageList?pageSize=10&pageNo=1&name=
2. 创建共享数据集:     POST /jmreport/saveDb（izSharedSource=1, jimuReportId=""）
3. 修改共享数据集:     POST /jmreport/saveDb（传 id = 更新, izSharedSource=1）
4. 删除共享数据集:     POST /jmreport/source/delShareDbByDbId，请求体: {"id": "共享数据集ID"}
5. 报表引用共享数据集: POST /jmreport/source/linkJmReportShareDb
   请求体: {"jimuReportId": "报表ID", "jimuSharedSourceId": "共享数据集ID"}
```

> **注意：** `getJmReportSharedDbPageList`、`linkJmReportShareDb`、`delShareDbByDbId` 均不需要签名。
> 详见 `references/api-dataset.md` 第11节"共享数据集"。

### Step 0.1: 判断报表类型

| 用户描述关键词 | 报表类型 | 构建方式 |
|--------------|---------|---------|
| 明细表/列表/简单报表 | 普通列表 | 表头行 + 数据绑定行 `#{db.field}` |
| 证件/单据/合同/逮捕证/套打单条记录 | 对象数据集报表 | `isList:"0"` + `isPage:"0"` + `${db.field}` 单值绑定，见 `examples/object-dataset.md` |
| 循环块/卡片/套打/信息表 | 循环块报表 | `loopBlockList` + `loopBlock:1` 单元格，见 `references/report-design.md` 5.2 |
| 分组/合计/小计 | 纵向分组 | `group()` + `subtotal`/`funcname`，见 `references/report-design.md` 4 |
| 横向分组/交叉表/多级表头/动态列 | 横向动态分组 | `groupRight()` + `dynamic()`，见下方决策 |
| 横向统计/每条记录展开一列 | 自定义横向分组 | `customGroup()` + `direction:"right"` |
| 多源/多数据集/订单+明细列表 | 多源报表 | 主子表都用 `#{}` 列表绑定 + `linkType=4` 联动，见 `examples/multi-source-table.md` |

**横向分组决策（当用户需要横向展开时）：**

| 场景 | 推荐方式 | 示例文件 |
|------|---------|---------|
| 1-3行表头 + 下方有数值动态填充 | **groupRight + dynamic** | `examples/multi-level-header.md` |
| 行列交叉（行头纵向+列头横向+值） | **group + groupRight + dynamic** | `examples/multi-level-header.md` 示例2 |
| 每条记录横向展开，每行一个字段 | **customGroup** | `examples/horizontal-group.md` 示例2 |

### Step 1: 解析需求

从用户描述中提取：

| 信息 | 默认值 | 示例 |
|------|--------|------|
| 报表名称 (name) | 用户指定 | "销售统计报表" |
| SQL 语句 | 从需求推导或用户提供 | `SELECT ... FROM ...` |
| 数据源 (dbSource) | 空（默认数据源） | `second_db` |
| 是否集合 (isList) | "1" | "0"=对象数据集（单条记录，用 `${}` 绑定） |
| 是否分页 (isPage) | "1" | "0"=不分页（对象数据集必须为"0"） |
| 是否填报 (submitForm) | 0 | 1=填报模式 |
| 查询条件 | **默认不生成** | 只有用户明确指定时才添加 |

> **数据源规则：**
> - 用户指定了数据源时使用指定的 dbSource；如没有指定任何数据源，则默认读取当前服务环境（dbSource 传空字符串），不需要额外配置。
> - **关键：`dbSource` 必须传数据源的 ID（如 `"1199218436288897024"`），不能传名称（如 `"mongodb"`）。** 传名称不会报错但无法正确关联，设计器中数据源下拉框不会显示。必须先通过 `getDataSourceByPage` 查询数据源列表，按 name 匹配拿到 ID。
>
> **MongoDB 专用规则（详见 `references/datasource-api.md`）：**
> - SQL 必须加 `mongo.` 前缀：`select * from mongo.集合名`，用户不提供时自动拼接
> - 字段名含 `-` 的必须从 fieldList 中过滤掉（FreeMarker 会把 `-` 当减号导致报错）
> - 以 `_` 开头的字段也应过滤（如 `_record_is_locked_`）

> **重要：查询条件默认不生成。** 只有用户明确指定时才添加。有两种配置方式：
>
> **1. 报表参数（paramList）— 优先使用：** SQL 中有 `${param}` 参数时，在 `paramList` 中添加对应条目，fieldList 不设置 searchFlag。
> **2. 报表字段查询（fieldList searchFlag）：** 用户明确说"用字段作为查询条件"时才使用。
>
> **查询模式规则（详见 `references/query-controls.md`）：**
> - **报表参数**：日期/数值类型 → searchMode=1（输入框）；字典字段 → searchMode=4（下拉单选）或 3（下拉多选）；字符串 → searchMode=1
> - **报表字段查询**：日期/数值类型 → searchMode=1（输入框）或 2（范围查询）；字符串 → searchMode=1 或 5（模糊查询）；字典字段 → searchMode=4 或 3

### Step 2: 调用 SQL 解析接口获取字段

**POST** `/jmreport/queryFieldBySql`

```json
{
    "sql": "select * from demo",
    "dbSource": "",
    "type": "0"
}
```

**返回结构：**
```json
{
    "success": true,
    "result": {
        "paramList": [],
        "fieldList": [
            {
                "fieldName": "id",
                "fieldText": "id",
                "widgetType": "String",
                "orderNum": 1
            }
        ]
    }
}
```

### Step 3: 调用数据集保存接口

**POST** `/jmreport/saveDb`

```json
{
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "数据集编码",
    "dbChName": "数据集中文名",
    "dbType": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "SQL语句",
    "fieldList": [],
    "paramList": []
}
```

**关键字段说明：**

| 字段 | 说明 | 示例 |
|------|------|------|
| `jimuReportId` | 关联的报表ID | `"1193766682428530688"` |
| `dbCode` | 数据集编码，在jsonStr中通过 `#{dbCode.fieldName}` 引用 | `"sales"` |
| `dbChName` | 数据集中文名称 | `"销售数据"` |
| `dbType` | 数据源类型："0"=SQL, "1"=API, "2"=JavaBean, "3"=JSON, "4"=共享, "5"=多文件, "6"=单文件 | `"0"` |
| `dbSource` | 数据源标识，空=默认 | `""` |
| `jsonData` | **JSON数据集专用**（dbType="3"）：必须用 `{"data": [...]}` 格式包裹，**禁止**直接传数组 `[...]`，否则 fastjson 解析报错 | `'{"data":[{"name":"张三"}]}'` |
| `isList` | "1"=列表数据 | `"1"` |
| `isPage` | "1"=分页 | `"1"` |
| `dbDynSql` | SQL语句（SQL数据集）；API地址（API数据集，后端拉取数据用） | `"select * from demo"` |
| `apiUrl` | **API数据集专用**（dbType="1"）：API 地址，设计器 UI「Api地址」读取此字段。**必须与 `dbDynSql` 同时设置** | `"http://api.example.com/list"` |
| `apiMethod` | **API数据集专用**（dbType="1"）：请求方式，`"0"`=GET, `"1"`=POST。设计器 UI「请求方式」读取此字段 | `"0"` |

**fieldList 每个字段的结构：**
```json
{
    "fieldName": "id",
    "fieldText": "id",
    "widgetType": "String",
    "orderNum": 0,
    "tableIndex": 0,
    "extJson": "",
    "dictCode": ""
}
```

### Step 4: 构造报表 jsonStr

`jsonStr` 是积木报表的核心设计数据，定义了 Excel 风格的布局。

**根据报表类型选择构建方式：**

| 报表类型 | rows 构建方式 | 标题后空行 | 额外配置 |
|---------|-------------|----------|---------|
| 普通列表 | 标题行 + 表头行 + 数据行 `#{db.field}` | **不加** | — |
| 纵向分组合计 | 标题行 + 表头行 + 数据行含 `group()`/`funcname` | **不加** | `isGroup`, `groupField` |
| 循环块（卡片式） | 标题行 + 空行 + 多行标签-值对 + 间隔行（`loopBlock:1`） | 加(15px) | `loopBlockList` |
| 分版报表 | 标题行 + 空行 + 多表格并排 | 加(15px) | `zonedEditionList` |
| 分栏报表 | 标题行 + 空行 + 循环块横向重复 | 加(15px) | `loopBlockList` + `loopTime` |
| 多级循环表头 | 标题行 + groupRight表头行(1-3行) + 数据行含 `group()`+`dynamic()` | **不加** | `isGroup`, `groupField`，参见下方 |
| 自定义横向分组 | 标题行 + 每行一个 `customGroup()` + `direction:"right"` | **不加** | — |

> **标题空行规则：** 普通列表、纵向分组、横向分组等表格类报表，标题直接接表头，**不加空行**；循环块、分版、分栏等复杂布局，标题和内容之间加一行空行 `{"cells": {}, "height": 15}`。

**多级循环表头 rows 构建模板：**

```
Row 0: 标题（合并多列）
Row 1: [斜线表头(可选)] + #{db.groupRight(一级字段)}  ← aggregate:"group", direction:"right"
Row 2:                   + #{db.groupRight(二级字段)}  ← aggregate:"group", direction:"right"
Row 3: #{db.group(纵向字段1)} + #{db.group(纵向字段2)} + #{db.dynamic(值字段)}  ← aggregate:"dynamic"
Row 4: 总计（合并） + =SUM(D4)
```

注意事项：
- groupRight 列头用蓝底白字表头样式（如 style 8）
- dynamic 值行用普通数据样式（如 style 14），不要用表头样式
- **所有边框颜色保持一致**（统一用 `#d8d8d8` 浅灰，不要混用 `#000`）
- 需要 `isGroup: true` 和 `groupField: "db.纵向分组字段"` 顶层配置
- 完整示例见 `examples/multi-level-header.md`
- **含斜线表头的交叉报表/多级循环表头报表，数据集默认不分页**（`isPage: "0"`），否则分组合并和横向展开可能不完整
- **斜线表头样式禁止 `align`/`valign`**：斜线表头的 style 只能包含 `{border, bgcolor, color}`，**不能有 `align` 或 `valign`**，否则三个标签的定位会错乱（只显示第一个词）。必须为斜线表头单独创建样式，不要复用普通表头样式。

**斜线表头配置模板：**

```json
{
    "rendered": "",
    "lineStart": "lefttop",
    "merge": [1, 1],
    "style": 斜线专用样式索引,
    "text": "左下标签|中间标签|右上标签"
}
```

> - `text` 用 `|` 分隔，最多3个标签（左下、中间、右上）
> - `lineStart: "lefttop"` — 从左上角画斜线
> - `rendered: ""` — 必须设置
> - 斜线专用样式示例：`{"border": {...}, "bgcolor": "#5b9cd6", "color": "#ffffff"}`（无 align/valign）

**横向小计列（compute 表达式）：**

交叉表中每个横向分组需要小计列时，使用 `compute` 表达式：

```
#{dbCode.compute(field1+field2)}
```

> **重要：compute 前缀必须是数据集编码（dbCode），不是 `jm`。** 例如数据集编码为 `qyxs`，则写 `#{qyxs.compute(sales_1+gift_1)}`，不能写 `#{jm.compute(...)}`。

- 支持 `+` `-` `*` `/` 四则运算
- 小计列会跟随 groupRight 横向分组自动循环展开
- groupRight 的 `merge` 需要包含小计列，如有3列（销售额+捐赠+小计），则 `merge: [0, 2]`
- 小计列同样支持 `subtotal: "-1"`, `funcname: "SUM"` 纵向汇总

**交叉表完整布局模板（含横向小计）：**

```
Row 1: 标题（合并所有列）
Row 2: 区域(merge↓2行) | 省份(merge↓2行) | #{db.groupRight(month)} merge→3列(销售+捐赠+小计)
Row 3:                                   | 销售额 | 捐赠 | 小计  ← 二级表头
Row 4: #{db.group(region)} | #{db.group(province)} | #{db.dynamic(sales)} | #{db.dynamic(gift)} | #{db.compute(sales+gift)}
Row 5: 总计(合并2列) | =SUM(C5) | =SUM(D5) | =SUM(E5)
Row 6: 最大值(合并2列) | =MAX(C5) | =MAX(D5) | =MAX(E5)  ← 需要 rightFollowExten
```

**跟随分组扩展（rightFollowExten）：**

当横向分组（groupRight）下方存在**多行**表达式时（如总计行+最大值行），分组展开时只有第一行（数据绑定行）会自动跟随扩展，第二行及之后的行不会自动扩展。需要在这些行的单元格上设置 `rightFollowExten: "follow"`。

**适用场景：** 横向分组、横向纵向组合分组、交叉报表中，分组下方有多行汇总（如总计+最大值+平均值等）。

**配置规则：**
1. 分组下方**第二行起**的单元格需要设置 `rightFollowExten: "follow"`
2. **最后一列不需要设置**（如小计列/compute列）
3. 第一行（数据绑定行或第一个汇总行）不需要设置

**示例（上方布局模板的 Row 6）：**
```json
// Row 6: 最大值行 — 分组下方第二个汇总行
"6": {
    "cells": {
        "1": {"text": "最大值", "merge": [0, 1]},
        "3": {"text": "=MAX(C5)", "rightFollowExten": "follow"},  // 需要
        "4": {"text": "=MAX(D5)", "rightFollowExten": "follow"},  // 需要
        "5": {"text": "=MAX(E5)"}                                  // 最后一列不需要
    }
}
```

> **参考文档：** https://help.jimureport.com/group/followExten
> 完整示例见 `examples/custom-group-sort.md` 中的跟随扩展章节。

#### 4.1 jsonStr 完整结构

```json
{
    "loopBlockList": [],
    "querySetting": {
        "izOpenQueryBar": false,
        "izDefaultQuery": true
    },
    "recordSubTableOrCollection": { "group": [], "record": [], "range": [] },
    "printConfig": {
        "paper": "A4",
        "width": 210,
        "height": 297,
        "definition": 1,
        "isBackend": false,
        "marginX": 10,
        "marginY": 10,
        "layout": "portrait",
        "printCallBackUrl": ""
    },
    "hidden": { "rows": [], "cols": [], "conditions": { "rows": {}, "cols": {} } },
    "queryFormSetting": { "useQueryForm": false, "dbKey": "", "idField": "" },
    "dbexps": [],
    "dicts": [],
    "fillFormToolbar": {
        "show": true,
        "btnList": ["save","subTable_add","verify","subTable_del","print","close","first","prev","next","paging","total","last","exportPDF","exportExcel","exportWord"]
    },
    "freeze": "A1",
    "dataRectWidth": 700,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": { "len": 100 },
    "area": { "sri": 0, "sci": 0, "eri": 0, "eci": 0, "width": 100, "height": 25 },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "1": {
            "cells": {
                "1": { "text": "表头1", "style": 4 },
                "2": { "text": "表头2", "style": 4 }
            },
            "height": 34
        },
        "2": {
            "cells": {    "name": "sheet1",

                "1": { "text": "#{数据集编码.字段1}", "style": 2 },
                "2": { "text": "#{数据集编码.字段2}", "style": 2 }
            }
        },
        "len": 200
    },
    "rpbar": { "show": true, "pageSize": "", "btnList": [] },
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "displayConfig": {},
    "fillFormInfo": { "layout": { "direction": "horizontal", "width": 200, "height": 45 } },
    "background": false,
    "styles": [],
    "fillFormStyle": "default",
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": []
}
```

#### 4.2 行列数据 (rows)

> **所有报表左侧必须留一列空白作为边距。** col 0（A列）为空列，宽度设为较小值（如 20~30px），数据从 col 1（B列）开始。这是通用设计规则，适用于所有报表类型。
>
> ```python
> cols_data = {
>     "0": {"width": 25},  # A列 左边距（空列）
>     "1": {"width": 120}, # B列 第一个数据列
>     ...
> }
> ```
>
> 标题、表头、数据行的 cell 均从 col 1 开始，col 0 不放内容。分栏报表中 col 0 不加入循环块（`sci` 从 1 开始）。

**行和列索引规则（重要）：**

- `rows["0"]` = 设计器第1行（UI第1行）；`rows["1"]` = 第2行，以此类推（**0-indexed**）
- `cells["0"]` = A列（第1列）；`cells["5"]` = F列（第6列）；`cells["6"]` = G列（第7列），以此类推（**0-indexed**）
- 通常 A列（cells["0"]）用作左边距空列，内容从 cells["1"] 开始；但当用户说"第N列"时，直接用 cells[str(N-1)]

```json
"rows": {
    "1": {
        "cells": {
            "1": { "text": "ID", "style": 4 },
            "2": { "text": "名称", "style": 4 },
            "3": { "text": "金额", "style": 4 }
        },
        "height": 34
    },
    "2": {
        "cells": {
            "1": { "text": "#{ds.id}", "style": 2 },
            "2": { "text": "#{ds.name}", "style": 2 },
            "3": { "text": "#{ds.amount}", "style": 2 }
        }
    },
    "len": 200
}
```

- **第1行**：表头行（通常用 style 4，蓝底白字）
- **第2行**：数据绑定行（用 `#{数据集编码.字段名}` 语法）
- `height`：行高（像素）
- `len`：总行数（默认200）

#### 4.3 数据绑定语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `#{dbCode.fieldName}` | 普通字段绑定 | `#{sales.amount}` |
| `#{dbCode.group(fieldName)}` | 分组字段绑定 | `#{sales.group(customer_name)}` |
| `=SUM(#{dbCode.fieldName})` | 聚合函数 | `=SUM(#{sales.amount})` |
| `=COUNT(#{dbCode.fieldName})` | 计数 | `=COUNT(#{sales.id})` |

#### 4.3.1 分组合计配置

当报表需要按某字段分组并在每组末尾显示合计行时，需要配置分组字段和聚合字段。详见 `references/report-design.md` 分组合计章节。

**分组字段（必须全部设置）：**
```json
{
    "text": "#{sales.group(customer_name)}",
    "style": 2,
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计"
}
```

**聚合字段（数值字段，必须全部设置）：**
```json
{
    "text": "#{sales.total_amount}",
    "style": 2,
    "subtotal": "-1",
    "funcname": "SUM",
    "decimalPlaces": "2"
}
```

**jsonStr 顶层需添加：**
```json
{
    "isGroup": true,
    "groupField": "数据集编码.分组字段名"
}
```

**funcname 可选值：** `"SUM"`, `"AVERAGE"`, `"COUNT"`, `"MAX"`, `"MIN"`, `"COUNTNZ"`

> **易错点：** 聚合字段的 `subtotal` 必须是 `"-1"`，不能设为 `"groupField"`。`"groupField"` 只用于分组依据字段（text 包含 `group()` 语法的字段）。否则合计行数值无法回填。

#### 4.4 样式 (styles)

样式数组，通过索引在 cells 中引用：

```json
"styles": [
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] }
    },
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] },
        "align": "center"
    },
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] },
        "align": "center",
        "valign": "middle"
    },
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] },
        "align": "center",
        "valign": "middle",
        "bgcolor": "#01b0f1"
    },
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] },
        "align": "center",
        "valign": "middle",
        "bgcolor": "#01b0f1",
        "color": "#ffffff"
    },
    {
        "border": { "bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"] },
        "align": "center",
        "valign": "middle",
        "font": { "bold": true, "size": 14 },
        "bgcolor": "#E6F2FF",
        "color": "#0066CC"
    }
]
```

**常用样式索引：**

| 索引 | 效果 | 用途 |
|------|------|------|
| 0 | 边框 | 基础单元格 |
| 1 | 边框+居中 | 文本居中 |
| 2 | 边框+居中+垂直居中 | 数据行 |
| 3 | 边框+居中+垂直居中+蓝底 | 表头（无白字） |
| 4 | 边框+居中+垂直居中+蓝底白字 | 表头（推荐） |
| 5 | 边框+居中+垂直居中+加粗14号+淡蓝底深蓝字 | 一级标题（推荐） |

**推荐配色方案（标题与表头区分）：**

| 层级 | bgcolor | color | font | 视觉效果 |
|------|---------|-------|------|---------|
| 一级标题 | `#E6F2FF`（淡蓝） | `#0066CC`（深蓝） | bold, size 14 | 清新淡雅，突出标题 |
| 二级表头 | `#01b0f1`（天蓝） | `#ffffff`（白色） | — | 醒目对比，标识列头 |
| 数据行 | 无 | 默认黑色 | — | 清晰易读 |

#### 4.5 单元格合并 (merges)

> **重要：合并单元格必须同时设置两处，缺一不可！**

**1. 单元格的 `merge` 属性** — 在起始 cell 上设置 `"merge": [rowSpan, colSpan]`，表示向下合并几行、向右合并几列：
```json
"cells": {
    "0": {"text": "标题文字", "style": 5, "merge": [0, 7], "height": 50}
}
```
> `[0, 7]` = 不向下合并，向右合并7列（共8列 A~H）。只需定义起始 cell，其他被合并的 cell 不需要定义。

**2. 顶层 `merges` 数组** — Excel 风格范围表示：
```json
"merges": ["A2:H2"]
```
> 行号为 UI 行号（= 代码行号 + 1）。如代码 row "1" 对应 merge 行号 2。

**标题行示例（从 B 列开始合并，与数据列对齐）：**
```python
# 标题 cell：放在 col 1 (B列)，和表头/数据行一样从 B 列开始
# merge 向右合并 data_col_count - 1 列（如3个数据列 B~D，merge=[0, 2]）
cells = {"1": {"text": "报表标题", "style": 5, "merge": [0, data_col_count - 1], "height": 50}}
rows[str(current_row)] = {"cells": cells, "height": 50}
# merges 数组 - 从 B 列开始
merges.append(f"B{current_row + 1}:{end_col_letter}{current_row + 1}")
```
> **注意：** 标题必须从 col 1（B列）开始，不要从 col 0（A列）。A列是左边距空列，标题应与表头、数据列对齐。

#### 4.6 打印配置 (printConfig)

| 属性 | 说明 | 可选值 |
|------|------|--------|
| paper | 纸张大小 | "A4", "A3", "B5", "letter" |
| width/height | 纸张宽高(mm) | A4: 210×297 |
| layout | 方向 | "portrait"(纵向), "landscape"(横向) |
| marginX/marginY | 边距(mm) | 默认10 |
| isBackend | 后端打印 | true/false |

#### 4.7 查询条件 (querySetting)

```json
"querySetting": {
    "izOpenQueryBar": true,
    "izDefaultQuery": true
}
```

- `izOpenQueryBar`: 是否显示查询栏
- `izDefaultQuery`: 是否默认查询

### Step 5: 调用报表保存接口

**POST** `/jmreport/save`

> **关键格式要求：**
> 1. `designerObj` 是 **JSON 字符串**（不是对象）
> 2. 所有 jsonStr 字段（`rows`、`cols`、`styles`、`merges`、`chartList` 等）都放在请求体**顶层**，每个值都是 **JSON 字符串**（不是对象）
> 3. 必须包含 `sheetId`、`sheetName`、`sheetOrder` 字段
> 4. 后端 `saveReport` 逻辑：`json.remove("designerObj")` 后，剩余的顶层 JSON 直接作为 jsonStr 存入数据库

**请求体结构（只有 designerObj 是字符串，其他都是原始对象）：**

```json
{
    "designerObj": "{\"id\":\"报表ID\",\"name\":\"报表名称\",\"type\":\"0\",\"template\":0,\"delFlag\":0,\"submitForm\":0,\"reportName\":\"报表名称\"}",
    "name": "sheet1",
    "freeze": "A1",
    "freezeLineColor": "rgb(185, 185, 185)",
    "rows": {"1": {"cells": {"1": {"text": "表头", "style": 4}}, "height": 34}, "len": 200},
    "cols": {"len": 100},
    "styles": [],
    "merges": [],
    "validations": [],
    "autofilter": {},
    "dbexps": [],
    "dicts": [],
    "loopBlockList": [],
    "zonedEditionList": [],
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "rpbar": {"show": true, "pageSize": "", "btnList": []},
    "fillFormToolbar": {"show": true, "btnList": ["save","subTable_add","verify","subTable_del","print","close","first","prev","next","paging","total","last","exportPDF","exportExcel","exportWord"]},
    "hiddenCells": [],
    "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
    "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
    "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
    "displayConfig": {},
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1, "isBackend": false, "marginX": 10, "marginY": 10, "layout": "portrait", "printCallBackUrl": ""},
    "querySetting": {"izOpenQueryBar": false, "izDefaultQuery": true},
    "queryFormSetting": {"useQueryForm": false, "dbKey": "", "idField": ""},
    "area": {"sri": 0, "sci": 0, "eri": 0, "eci": 0, "width": 100, "height": 25},
    "submitHandlers": [],
    "chartList": [],
    "background": false,
    "dataRectWidth": 700,
    "excel_config_id": "报表ID",
    "pyGroupEngine": false,
    "isViewContentHorizontalCenter": false,
    "fillFormStyle": "default",
    "sheetId": "default",
    "sheetName": "默认Sheet",
    "sheetOrder": "0"
}
```

**Python 构造示例：**

```python
save_data = {
    # 只有 designerObj 是字符串
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),
    # 其他所有字段都是原始对象/数组，不要 json.dumps
    "name": "sheet1",
    "freeze": "A1",
    "freezeLineColor": "rgb(185, 185, 185)",
    "rows": rows_data,          # dict, 不是字符串
    "cols": cols_data,           # dict
    "styles": styles_list,       # list
    "merges": merges_list,       # list
    "chartList": chart_list,     # list
    "loopBlockList": [],         # list
    "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},  # dict
    # ... 其他配置字段同理
    "sheetId": "default",
    "sheetName": "默认Sheet",
    "sheetOrder": "0",
    "background": False,         # 布尔值
    "dataRectWidth": 700,        # 数字
    "excel_config_id": report_id,
    "pyGroupEngine": False,
    "isViewContentHorizontalCenter": False,
    "fillFormStyle": "default"
}
```

> **关键：只有 `designerObj` 用 `json.dumps()` 转字符串，其他所有字段（`rows`、`cols`、`styles`、`merges`、`chartList`、`loopBlockList` 等）都保持原始 Python 对象。如果把它们也 json.dumps 转成字符串，会导致双重序列化，前端解析报错。**

**designerObj 关键字段（JSON 字符串内的对象结构）：**

| 字段 | 说明 | 必填 |
|------|------|------|
| `id` | 报表唯一ID | 是 |
| `code` | 报表编码（如时间戳格式） | 是 |
| `name` / `reportName` | 报表名称 | 是 |
| `type` | 报表分类，默认 `"0"` | 是 |
| `template` | 是否为模板（0否） | 是 |
| `cssStr` | CSS增强代码 | 否 |
| `jsStr` | JS增强代码 | 否 |
| `pyStr` | Python增强代码 | 否 |
| `tenantId` | 租户ID | 否 |
| `submitForm` | 是否填报（0否，1是） | 否 |

**注意事项：**
- **只有 `designerObj` 是字符串**（`json.dumps(obj)`），其他所有字段保持原始对象/数组
- `rows`、`cols`、`styles`、`chartList`、`loopBlockList` 等都是 **原始对象/数组**，禁止 json.dumps
- `background`、`pyGroupEngine`、`isViewContentHorizontalCenter` 是布尔值 `False`
- `dataRectWidth` 是数字（如 `700`）
- 必须传 `sheetId: "default"`、`sheetName: "默认Sheet"`、`sheetOrder: "0"`

### Step 6: 展示摘要并确认

**必须展示以下内容，等待用户确认后再执行：**

```
## 积木报表配置摘要

- 报表名称：销售统计报表
- 数据源：默认
- 目标环境：https://boot3.jeecg.com/jeecgboot

### 数据集配置
| 编码 | 名称 | SQL | 分页 |
|------|------|-----|------|
| sales | 销售数据 | SELECT id, name, amount FROM biz_sales | 是 |

### 表头设计
| 列 | 表头文本 | 数据绑定 |
|----|---------|---------|
| B | ID | #{sales.id} |
| C | 名称 | #{sales.name} |
| D | 金额 | #{sales.amount} |

确认以上配置？(y/n)
```

### Step 7: 使用 Python 调用 API

**重要限制：**
1. **Windows 环境下 curl 发送中文/长 JSON 会出错**，必须使用 Python
2. **禁止使用 `python3 -c "..."` 内联方式**
3. **必须先用 Write 工具写入 `.py` 临时文件，再用 Bash 执行，最后删除临时文件**

**完整 Python 脚本模板：**

```python
import urllib.request
import json
import time
import random
import ssl
import hashlib

API_BASE = '{用户提供的后端地址}'
TOKEN = '{用户提供的 X-Access-Token}'
SIGNATURE_SECRET = 'dd05f1c54d63749eda95f9fa6d49v442a'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 需要签名的接口列表
SIGNED_ENDPOINTS = [
    '/jmreport/queryFieldBySql',
    '/jmreport/executeSelectApi',
    '/jmreport/loadTableData',
    '/jmreport/testConnection',
    '/jmreport/download/image',
    '/jmreport/dictCodeSearch',
    '/jmreport/getDataSourceByPage',
    '/jmreport/getDataSourceById',
]

def compute_sign(params_dict):
    """计算积木报表接口签名"""
    str_params = {}
    for k, v in params_dict.items():
        if v is None:
            continue
        if isinstance(v, bool):
            str_params[k] = str(v).lower()
        elif isinstance(v, (int, float)):
            str_params[k] = str(v)
        elif isinstance(v, (dict, list)):
            str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else:
            str_params[k] = str(v)
    sorted_params = dict(sorted(str_params.items()))
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))
    sign_str = params_json + SIGNATURE_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def api_request(path, data=None, method=None):
    url = f'{API_BASE}{path}'
    headers = {
        'X-Access-Token': TOKEN,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    # 自动判断是否需要签名
    need_sign = any(path.rstrip('/').endswith(ep.rstrip('/')) for ep in SIGNED_ENDPOINTS)
    if need_sign:
        sign_params = data if data else {}
        headers['X-TIMESTAMP'] = str(int(time.time() * 1000))
        headers['X-Sign'] = compute_sign(sign_params)
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method or 'POST')
    else:
        req = urllib.request.Request(url, headers=headers, method=method or 'GET')
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))

def gen_id():
    return str(int(time.time() * 1000) * 1000000 + random.randint(100000, 999999))

# ====== Step 1: 解析SQL获取字段 ======
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": "select * from demo",
    "dbSource": "",
    "type": "0"
})
print('SQL解析结果:', json.dumps(parse_result, ensure_ascii=False, indent=2))

# ====== Step 2: 保存数据集 ======
db_data = {
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "demo",
    "dbChName": "示例数据",
    "dbType": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from demo",
    "fieldList": parse_result['result']['fieldList'],
    "paramList": []
}
db_result = api_request('/jmreport/saveDb', db_data)
print('数据集保存结果:', json.dumps(db_result, ensure_ascii=False, indent=2))

# ====== Step 3: 构造请求体并保存报表 ======
# ⚠️ 关键：只有 designerObj 用 json.dumps 转字符串，其余所有字段保持原始 Python 对象！
# 后端逻辑: json.remove("designerObj") 后, 剩余的顶层字段直接作为 jsonStr 存入数据库。
# 若对 rows/cols/styles/printConfig 等也 json.dumps，前端读取时会得到字符串而非对象，
# 导致设计器显示空白 + "配置有误，请检查数据JSON配置项！"。

designer_obj = {
    "id": report_id, "name": "报表名称", "type": "0",
    "template": 0, "delFlag": 0, "viewCount": 0, "updateCount": 0,
    "submitForm": 0, "reportName": "报表名称"
}

rows_data = {
    "1": {"cells": {"1": {"text": "ID", "style": 4}, "2": {"text": "名称", "style": 4}}, "height": 34},
    "2": {"cells": {"1": {"text": "#{demo.id}", "style": 2}, "2": {"text": "#{demo.name}", "style": 2}}},
    "len": 200
}

styles_list = [
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}},
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center"},
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle"},
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1"},
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1", "color": "#ffffff"}
]

# 正确写法：只有 designerObj 是 json.dumps 字符串，其余全部为原始对象/数组/布尔值
save_data = {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),  # ← 唯一需要 json.dumps 的字段
    "name": "sheet1",
    "freeze": "A1",
    "freezeLineColor": "rgb(185, 185, 185)",
    "rows": rows_data,           # dict，不要 json.dumps
    "cols": {"len": 100},        # dict
    "styles": styles_list,       # list
    "merges": [],                # list
    "validations": [],
    "autofilter": {},
    "dbexps": [],
    "dicts": [],
    "loopBlockList": [],
    "zonedEditionList": [],
    "fixedPrintHeadRows": [],    # list，不要 json.dumps
    "fixedPrintTailRows": [],
    "hiddenCells": [],
    "submitHandlers": [],
    "rpbar": {"show": True, "pageSize": "", "btnList": []},
    "fillFormToolbar": {"show": True, "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"]},
    "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
    "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
    "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
    "displayConfig": {},
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "isBackend": False, "marginX": 10, "marginY": 10, "layout": "portrait", "printCallBackUrl": ""},  # dict，不要 json.dumps
    "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
    "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
    "area": {"sri": 0, "sci": 0, "eri": 0, "eci": 0, "width": 100, "height": 25},
    "chartList": [],
    "background": False,         # 布尔值，不是字符串 "false"
    "dataRectWidth": 700,        # 数字，不是字符串 "700"
    "excel_config_id": report_id,
    "pyGroupEngine": False,
    "isViewContentHorizontalCenter": False,
    "fillFormStyle": "default",
    "sheetId": "default",
    "sheetName": "默认Sheet",
    "sheetOrder": "0"
}
save_result = api_request('/jmreport/save', save_data)
print('报表保存结果:', json.dumps(save_result, ensure_ascii=False, indent=2))
```

## 典型工作流总结

```
1. save (空报表)     →  先创建空报表，获取报表ID
2. queryFieldBySql   →  解析SQL，获取字段列表
3. saveDb            →  保存数据集（含字段映射、分页配置），关联报表ID
4. save (完整设计)   →  jsonStr内容放请求体顶层，保存完整报表设计
```

**关键注意事项：**
- Step 1 创建空报表时，`save` 接口首次调用会返回 `isRefresh: true`，此时报表已创建
- Step 4 的 `save` 请求体格式：`designerObj`（元数据）+ jsonStr 内容（rows/cols/styles 等）放在**同一层级**
- 禁止将 jsonStr 嵌套在 `designerObj.jsonStr` 字符串中，否则后端会清空 rows 数据
- `designerObj.type` 默认值为 `"0"`，不要传分类名称字符串（如 "demo"）

> **防重复创建规则（重要）：**
> - **报表：** 脚本中 report_id 只生成一次，后续所有步骤（包括失败重试）都使用同一 report_id。save 接口传同一 id 即为更新，不会重复创建。
> - **数据源：** 创建前先通过 `getDataSourceByPage` 按 name 查询是否已存在。已存在则取其 id 走编辑模式（addDataSource 传 id），不存在才新增（id 为空）。
> - **数据集：** saveDb 同理，传 id 为更新，不传为新增。重试前先通过 `field/tree/{reportId}` 检查数据集是否已创建。
> - **禁止**每次重试都生成新 id 或不传 id，否则会产生大量重复的报表、数据源、数据集记录。

## 已知踩坑记录

> 实际调试中遇到的问题，避免重复踩坑。

---

### ❌ 坑1：save 请求体中对 rows/cols/styles 等字段 json.dumps → 设计器空白

**现象**：`/jmreport/save` 返回 code=200，但打开设计器显示空白，提示 "配置有误，请检查数据JSON配置项！"

**原因**：将 `rows`、`cols`、`styles`、`merges`、`printConfig`、`fixedPrintHeadRows`、`fixedPrintTailRows` 等字段用 `json.dumps` 转为字符串后传入，后端把字符串原样存入 jsonStr。前端读取 jsonStr 后直接使用这些字段，拿到的是字符串而不是对象，无法渲染。

**正确做法**：**只有 `designerObj` 用 `json.dumps`**，其余所有字段（包括 `rows`、`cols`、`styles`、`merges`、`printConfig`、`fixedPrintHeadRows`、`fixedPrintTailRows`、`querySetting`、`rpbar`、`hidden` 等）全部保持原始 Python dict/list/bool/int，直接放入请求体。`background`、`pyGroupEngine`、`isViewContentHorizontalCenter` 用布尔值 `False`，`dataRectWidth` 用数字。

```python
# ✅ 正确
save_data = {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),  # 唯一字符串
    "rows": rows_data,        # dict
    "cols": cols_data,        # dict
    "styles": styles_list,    # list
    "merges": merges_list,    # list
    "printConfig": print_config,  # dict
    "fixedPrintHeadRows": [...],  # list
    "background": False,      # bool
    "dataRectWidth": 700,     # int
    ...
}

# ❌ 错误（会导致设计器空白）
save_data = {
    "rows": json.dumps(rows_data),        # ← 错
    "printConfig": json.dumps(print_config),  # ← 错
    "background": "false",                # ← 错
    "dataRectWidth": "700",               # ← 错
}
```

---

### ❌ 坑2：读取报表后二次 save 时对已有字段再次 json.dumps → 双重序列化

**现象**：通过 `GET /jmreport/get/{id}` 拿到 jsonStr，解析后修改某字段（如 `printCallBackUrl`），再 save 时对所有字段都调用 `json.dumps` → 字段变成双重序列化的字符串 → 设计器崩坏。

**原因**：从 API 读回的字段已经是正确格式（dict/list），再 `json.dumps` 会加一层多余的序列化。

**正确做法**：读取 jsonStr 后，字段直接原样传回 save，不再 json.dumps（除 designerObj）。如果要修改 `printConfig` 等对象字段，先处理（dict操作），再原样传入。

```python
# 正确的"读取→修改→保存"流程
r = api_request(f'/jmreport/get/{report_id}')
obj = json.loads(r['result']['jsonStr'])

# 修改某字段
pc = obj['printConfig']  # 已经是 dict
pc['printCallBackUrl'] = 'new_url'

# 构造 save_data 时直接用原始对象，不再 json.dumps
save_data = {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),
    "rows": obj['rows'],           # 直接用，不 json.dumps
    "cols": obj['cols'],
    "printConfig": pc,             # 直接用修改后的 dict
    ...
}
```

---

### ❌ 坑3：行列索引混淆 — UI第N行/列 ≠ rows["N"] / cells["N"]

**现象**：用户说"第1行第6列"，代码写 `rows["1"]["cells"]["6"]`，结果内容跑到 UI 第2行第7列。

**原因**：`rows` 和 `cells` 的 key 均从 **0** 开始，与 UI 显示的行列编号差1：

| UI 显示 | rows key | cells key |
|---------|----------|-----------|
| 第1行 | `"0"` | — |
| 第2行 | `"1"` | — |
| 第N行 | `str(N-1)` | — |
| A列（第1列） | — | `"0"` |
| F列（第6列） | — | `"5"` |
| G列（第7列） | — | `"6"` |
| 第N列 | — | `str(N-1)` |

**正确做法**：用户说"第R行第C列"，映射到 `rows[str(R-1)]["cells"][str(C-1)]`。

```python
# 用户要求：第1行第6列(F列)插入"JEECG"
rows["0"]["cells"]["5"] = {"text": "JEECG"}   # ✅ R=1→"0", C=6→"5"
rows["1"]["cells"]["6"] = {"text": "JEECG"}   # ❌ 实际是第2行第7列
```

---

### ℹ️ 注：printFootorFixBottom UI 显示 bug

**现象**：打印设置弹窗中"表尾固定底部"开关始终显示为关闭，即使数据库存储的是 `true`。

**原因**：前端打印设置组件的 `resetForm` 方法未读取 `printFootorFixBottom` 字段，导致每次打开弹窗时该值重置为默认 `false`。

**影响**：数据库中的 `printFootorFixBottom` 值是正确的，不影响实际打印行为。但若用户打开打印设置弹窗后点击确认，会将该值覆盖为 `false`。

**修复**：需要在前端组件的 `resetForm` 方法中补充：
```javascript
if (param.printFootorFixBottom !== undefined) {
    this.printFootorFixBottom = param.printFootorFixBottom;
}
```

---

## 智能字段配置

### 字段显示名称推导

| 字段名模式 | 推导中文名 |
|-----------|-----------|
| id | ID/主键 |
| name / title | 名称/标题 |
| code / no | 编码/编号 |
| status | 状态 |
| amount / money / price / salary | 金额/费用/价格/薪资 |
| count / qty / num / age | 数量/年龄 |
| date / time / birthday | 日期/时间/生日 |
| create_by / update_by | 创建人/更新人 |
| create_time / update_time | 创建时间/更新时间 |
| sex | 性别 |
| email | 邮箱 |
| phone / mobile / tel | 电话/手机号 |
| content / remark | 内容/备注 |
| sys_org_code | 组织编码 |
| tenant_id | 租户ID |

### 是否在报表中显示

| 规则 | 是否显示 |
|------|---------|
| 业务字段（默认） | 显示 |
| id / 主键字段 | 通常隐藏 |
| create_by / update_by | 通常隐藏 |
| sys_org_code / tenant_id | 隐藏 |

## 高级功能

### SQL 参数化与动态条件

积木报表支持在SQL中使用参数和FreeMarker动态条件：

```sql
-- 基础参数
SELECT * FROM demo WHERE name like '%${name}%'

-- FreeMarker动态条件（参数为空时自动跳过）
select * from demo where 1=1
<#if isNotEmpty(name)> and name = '${name}'</#if>
<#if isNotEmpty(age)> and age = '${age}'</#if>

-- IN查询（v1.6.2+）
select * from demo where sex in(${DaoFormat.in('${sex}')})
select * from demo where age in(${DaoFormat.inNumber('${age}')})
```

### 参数默认值与 SQL 解析顺序

> **通用规则（适用于所有数据源类型：SQL、存储过程、API、JavaBean、FreeMarker 条件等）：**
> 当用户提供了参数默认值时，必须先将默认值拼接到 SQL/API URL/JavaBean 表达式中，再调用对应的解析接口获取字段。解析完成后，保存数据集时恢复原始 `${}` 占位符。

**原因：** 解析接口（`queryFieldBySql`/`executeSelectApi`）会实际执行 SQL 或调用 API 来获取字段元数据。带 `${}` 占位符无法执行，导致解析失败或返回空字段。

**流程：**

```
1. 用户提供 SQL/API/JavaBean + 参数默认值（可选）
2. 有默认值时：将 ${参数名} 替换为默认值 → 生成解析用表达式
   无默认值时：直接去掉 ${} 参数条件（FreeMarker <#if> 整块去掉，普通 SQL 中去掉 where 条件）
3. 调用解析接口（解析用表达式）→ 获取 fieldList
4. saveDb 时：
   - dbDynSql/apiUrl = 原始表达式（保留 ${} 占位符）
   - fieldList = 解析接口返回的字段
   - paramList = 手动构建（见下方 paramValue 规则）
```

> **paramValue 传递规则（SQL/API/JavaBean 通用）：**
> - **有默认值** → paramList 条目中设置 `"paramValue": "默认值"`
> - **无默认值** → paramList 条目中 **不传 paramValue 字段**（不要传空字符串）
>
> ```python
> # 有默认值的参数
> {"paramName": "name", "paramTxt": "姓名", "paramValue": "张三", ...}
> # 无默认值的参数 — 不包含 paramValue
> {"paramName": "status", "paramTxt": "状态", ...}  # 没有 paramValue 字段
> ```

**示例1 — SQL 数据集（存储过程）：**

```python
# 原始 SQL: call jmdemo('${nameStr}')，默认值: 小王
parse_sql = "call jmdemo('小王')"  # 拼接默认值
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": parse_sql, "dbSource": "", "type": "0"
})
# saveDb 时 dbDynSql 保留: "call jmdemo('${nameStr}')"
```

**示例2 — SQL 数据集（普通查询）：**

```python
# 原始 SQL: select * from demo where name like '%${name}%'，默认值: 张三
parse_sql = "select * from demo where name like '%张三%'"  # 拼接默认值
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": parse_sql, "dbSource": "", "type": "0"
})
# saveDb 时 dbDynSql 保留: "select * from demo where name like '%${name}%'"
```

**示例3 — SQL 数据集（FreeMarker 条件，有默认值）：**

```python
# 原始 SQL: select * from demo where 1=1 <#if isNotEmpty(age)> and age = '${age}'</#if>
# 参数 age 有默认值 25 → 去掉 FreeMarker 条件，拼接默认值
parse_sql = "select * from demo where 1=1 and age = '25'"
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": parse_sql, "dbSource": "", "type": "0"
})
# saveDb 时 dbDynSql 保留原始 FreeMarker SQL
# paramList 中 paramValue 设为 "25"
```

**示例3b — SQL 数据集（FreeMarker 条件，无默认值）：**

```python
# 原始 SQL: select * from demo where 1=1 <#if isNotEmpty(age)> and age = '${age}'</#if>
# 参数 age 无默认值 → 直接去掉整个 FreeMarker 条件块，不拼接任何值
parse_sql = "select * from demo where 1=1"  # 只保留基础 SQL
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": parse_sql, "dbSource": "", "type": "0"
})
# saveDb 时 dbDynSql 保留原始 FreeMarker SQL
# paramList 中不传 paramValue
```

**示例4 — API 数据集：**

```python
# 原始 API: http://api.example.com/users?name=${nameStr}，默认值: 张三
parse_url = "http://api.example.com/users?name=张三"  # 拼接默认值
parse_result = api_request('/jmreport/executeSelectApi', {
    "apiUrl": parse_url, "apiMethod": "0", "dbSource": ""
})
# saveDb 时 dbDynSql 和 apiUrl 保留: "http://api.example.com/users?name=${nameStr}"
```

**示例5 — JavaBean 数据集：**

```python
# 原始 JavaBean: com.example.UserService?name=${nameStr}，默认值: 张三
parse_bean = "com.example.UserService?name=张三"  # 拼接默认值
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": parse_bean, "dbSource": "", "type": "2"  # type=2 为 JavaBean
})
# saveDb 时 dbDynSql 保留: "com.example.UserService?name=${nameStr}"
```

> **注意：** 如果参数无默认值，需要引导用户提供一个示例值用于解析。

### 查询配置

报表支持8种查询控件类型，完整参考见 `references/query-controls.md`。

关键配置点：
- **querySetting**：`izOpenQueryBar`(展开查询栏) / `izDefaultQuery`(自动查询)
- **控件类型约束**：模糊查询仅字符串类型；范围查询仅日期/数值类型；下拉单选/多选必须配置数据字典
- **报表参数 vs 报表字段查询**：报表参数不支持范围查询和模糊查询
- **控件默认值**：静态值 / `=dateStr('yyyy-MM-dd')` / `#{sysUserCode}` / 范围用`|`分隔
- **JS增强**：级联下拉 `updateSelectOptions()` / 监听变化 `onSearchFormChange()`
- **参数优先级**：查询条件值 > URL参数 > 默认值

### 分组报表（纵向分组）

当用户要求"分组报表"、"按XX分组"、"按XX统计"时，必须使用分组语法，**不要**用普通的汇总SQL+明细SQL拆分方式。

#### 核心配置（3个必须项）

1. **jsonStr 顶层**添加分组标记：
```json
{
    "isGroup": true,
    "groupField": "数据集编码.分组字段名"
}
```

2. **save 请求体**中也要传这两个字段（与 rows/cols 同级）：
```python
save_data = {
    ...
    "isGroup": True,
    "groupField": "users.sex_name",
    ...
}
```

3. **分组列单元格**使用 `#{db.group(field)}` 语法，并配置聚合属性：
```json
{
    "text": "#{users.group(sex_name)}",
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计"
}
```

#### 分组单元格属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `text` | `#{dbCode.group(fieldName)}` | 分组绑定，相同值自动合并单元格 |
| `aggregate` | `"group"` | 标记为分组聚合列 |
| `subtotal` | `"groupField"` | 启用小计/合计行 |
| `funcname` | `"-1"` / `"SUM"` / `"COUNT"` / `"AVG"` | 聚合函数，`"-1"`=不计算 |
| `subtotalText` | `"合计"` / `"小计"` | 小计行显示的文本 |
| `textOrders` | `"值1\|值2\|值3"` | 自定义分组排序，多个值用 `\|` 分隔，适用于任何分组（纵向/横向） |
| `rightFollowExten` | `"follow"` | 跟随分组扩展，横向分组下方第二行起的单元格需设置（最后一列除外） |

> **自定义分组排序：** 当分组字段的默认排序（按数据顺序或字母序）不符合需求时，在分组单元格上添加 `textOrders` 属性指定排序顺序。例如区域按"华北→华南→华东"排序：`"textOrders": "华北|华南|华东"`。完整示例见 `examples/custom-group-sort.md`。

#### 多级分组

从左到右为高到低级别，每级用不同的 `subtotalText` 区分：
- 一级分组（如起始站）：`subtotalText: "合计"` — 一级分组切换时显示
- 二级分组（如终止站）：`subtotalText: "小计"` — 二级分组切换时显示
- `groupField` 始终指向**一级（最高级）分组字段**

**多级分组示例（按起始站+终止站分组）：**
```json
// save 请求体
{
    "isGroup": true,
    "groupField": "jp.kaishi",  // 指向一级分组字段
    ...
}

// 数据绑定行 cells
"1": {
    "text": "#{jp.group(kaishi)}",    // 一级分组
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计"
},
"2": {
    "text": "#{jp.group(jieshu)}",    // 二级分组
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "小计"
},
"3": {"text": "#{jp.bnum}"},          // 普通字段
```

#### 分组报表布局示例

```
第1行: 标题（合并单元格）
第2行: 表头（起始站 | 终止站 | 班次号 | 发车时间 | ...）
第3行: 数据绑定行（#{db.group(kaishi)} | #{db.group(jieshu)} | #{db.bnum} | ...）
```

预览效果：
```
┌────────┬────────┬────────┬──────────┐
│ 起始站  │ 终止站  │ 班次号  │ 发车时间  │
├────────┼────────┼────────┼──────────┤
│        │        │ K7725  │ 21:13    │
│        │ 邯郸   ├────────┼──────────┤
│ 北京西  │        │        小计       │
│        ├────────┼────────┼──────────┤
│        │ 深圳   │ G101   │ 06:44    │
│        │        │        小计       │
├────────┼────────┼────────┼──────────┤
│        │        │        合计       │
└────────┴────────┴────────┴──────────┘
```

#### 注意事项
- SQL 中必须按分组字段 `ORDER BY`，确保相同值相邻（多级分组时按一级、二级顺序排序）
- 数据集 `isPage` 设为 `"0"`（不分页），否则分组合并可能不完整
- `pyGroupEngine` 保持 `false`（标准分组不需要 Python 引擎）
- 列数较多时（>6列），考虑将 `printConfig.layout` 设为 `"landscape"`（横向打印）
- 完整示例见 `examples/vertical-group-subtotal-example.md`

#### 数据探查

`queryFieldBySql` 只返回字段元数据，不返回实际数据行。当需要了解数据内容以判断分组字段，或需要建表/插数据时：
- **必须先从服务配置动态读取数据库连接参数**，详见 `references/db-connection.md`
- 通过 **pymysql 连接数据库**查看实际数据（`SELECT DISTINCT`、`GROUP BY` 等）
- **禁止硬编码数据库连接信息**，每次都从 `application-*.yml` 中读取
- 查看数据后再确定哪些字段适合作为分组依据

### CSS/JS/Python 增强

通过 `designerObj` 的 `cssStr`、`jsStr`、`pyStr` 字段传入增强代码。

### 多 Sheet

设置 `isMultiSheet` 为 1，通过 `sheets` 字段管理多个 sheet 页。

### 填报模式

设置 `submitForm` 为 1，启用数据填报功能，允许用户在报表中录入数据。

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| Token 过期（401/认证失败） | 提示用户重新获取 X-Access-Token |
| `code:1001` 签名验证失败 | 接口需要签名，需在 Header 添加 X-Sign 和 X-TIMESTAMP，详见签名机制章节 |
| `签名验证失败:X-TIMESTAMP已过期` | 客户端与服务器时间差超过5分钟，检查系统时间 |
| `签名校验失败，参数有误！` | 签名计算不匹配，检查参数排序、JSON无空格格式、密钥是否正确 |
| SQL 解析失败 | 检查 SQL 语法是否正确，表是否存在 |
| 数据集编码重复 | 换一个 dbCode |
| jsonStr 格式错误 | 检查 JSON 字符串转义是否正确 |
| 中文乱码 | 确认使用 Python urllib（不要用 curl） |

## 与其他 Skill 的区别

| Skill | 产出物 | 适用场景 |
|-------|--------|---------|
| `jeecg-jimureport` | 积木报表（可视化Excel设计器） | 复杂布局报表、合并单元格、打印、填报 |
| `jeecg-onlreport` | Online 报表（SQL 驱动列表） | 简单数据查询报表 |
| `jeecg-onlform` | Online 表单（元数据CRUD） | 数据录入管理 |
| `jeecg-desform` | 设计器表单 JSON | 数据采集、审批表单 |
| `jeecg-codegen` | Java + Vue3 代码 + SQL | 自定义业务逻辑模块 |

## 图表与数据表格布局实战经验

### chart_bottom 布局（表格在上，图表在下）

**核心问题：** 积木报表的数据绑定行在预览时会展开显示多页数据，导致图表位置被推后。

**解决方案：**
1. 图表虚拟单元格需要放在数据展开区域之后
2. 图表开始行 = 数据绑定行 + pageSize + gap
3. 示例：数据绑定行=3, pageSize=10, gap=1 → 图表从第14行开始

```python
# 布局计算公式
page_size = config.get('pageSize', 10)
gap = config.get('gap', 1)  # 默认1行间距，负值可减少间距
data_binding_row = 3  # 标题行(1) + 表头行(2) + 数据绑定行(3)
chart_start = data_binding_row + page_size + gap  # 14
```

### 虚拟单元格行数

**关键发现：** 图表的 `virtualCellRange` 只需要 **1行**（不是多行）。

错误做法（早期版本）：
```python
row_count = (chart_height // 25) + 2  # 300px高度 = 14行
```

正确做法：
```python
row_count = 1  # 只用1行作为锚点，图表大小由width/height控制
```

设计器保存后的实际结构：
- 图表虚拟单元格只有1行
- 图表位置由 `chartList[].row` 和 `chartList[].width/height` 决定

### area 和 dataRectWidth 设置

为确保预览正确显示，需要设置正确的 `area` 和 `dataRectWidth`：

```python
# 计算列宽总和
total_width = sum(col.get('width', 100) for col in cols.values() if isinstance(col, dict))

# area 定义内容边界（告诉前端报表的实际范围）
# 注意：设计器保存后会重新计算 area，建议在图表底部添加2-3行空行来确保滚动正常
area = {
    "sri": 1,           # 起始行（UI行号）
    "sci": 1,           # 起始列
    "eri": chart_start, # 结束行（图表开始的行）
    "eci": col_count,   # 结束列
    "width": total_width,
    "height": title_h + header_h + (chart_start - 3) * row_h + chart_h
}
```

**滚动问题的解决方案（已自动化）：**

脚本已自动处理滚动条问题，无需手动操作：

1. 设置 `area = False`，让系统自动计算滚动高度
2. 在图表底部自动添加分页符行（位置 = chart_start + pageSize + 3）

```python
# 在图表下方添加分页符行（使用空格避免显示"1"）
pagination_row = chart_start + pageSize + 3
all_rows[str(pagination_row)] = {"cells": {"1": {"text": "   "}}}
```

这样系统就能正确识别滚动区域，滚动条自动正常工作。

### 合并单元格行号

**重要：** 合并单元格使用 **UI 行号**（不是代码行号）。

- 代码行号从 0 开始（但 rows 中的 key 从 "1" 开始）
- UI 行号从 1 开始
- 公式：`ui_row = code_row + 1`

示例：
```python
# 标题在代码第1行，合并 C1:H1
ui_row = 1 + 1  # = 2
merges.append(f"C{ui_row}:H{ui_row}")  # "C2:H2"
```

### 报表访问地址

| 页面 | 地址 |
|------|------|
| 设计器 | `/jmreport/index/{report_id}` |
| 预览 | `/jmreport/view/{report_id}` |
| 报表列表 | `/jmreport/list` |

预览地址需要携带 token 参数：

```
https://api3.boot.jeecg.com/jmreport/view/{report_id}?token={X-Access-Token}
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 表格和图表间距过大 | 图表虚拟单元格放在了数据展开区域内 | 图表从 `data_binding_row + pageSize + gap` 开始 |
| 图表与数据重叠 | 虚拟单元格行数过多 | 虚拟单元格只用1行 |
| 设计器与预览效果不一致 | area 设置不正确 | 设置正确的 area.sri/eri |
| 滚动条不显示 | area 范围计算错误 | 确保 area.eri 等于图表实际开始的行 |
| 间距仍偏大 | gap 默认值过大 | 将 gap 改为负值（如 -5）可以减少间距 |
| 滚动幅度太小 | 内容总高度不够 | 在图表底部添加2-3行空行或分页符，增加总高度 |
