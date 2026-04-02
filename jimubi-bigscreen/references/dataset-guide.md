# 数据集管理（动态数据源）

大屏组件支持三种数据类型（`config.dataType`）：
- `1` — 静态数据（直接写在 `chartData` 中）
- `2` — 动态数据（从数据集获取，支持 SQL / API / JSON / WebSocket）
- `4` — 表单数据（从表单关联字段查询）

## 数据集 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/drag/onlDragDatasetHead/add` | POST | 创建数据集 |
| `/drag/onlDragDatasetHead/edit` | PUT | 编辑数据集（传完整实体，无需 sign） |
| `/drag/onlDragDatasetHead/delete?id=xxx` | DELETE | 删除数据集 |
| `/drag/onlDragDatasetHead/list` | GET | 分页查询数据集列表 |
| `/drag/onlDragDatasetHead/getAllChartData` | POST | 执行数据集查询（获取图表数据） |
| `/drag/onlDragDatasetHead/queryFieldBySql` | POST | 解析 SQL 返回字段列表 |
| `/drag/onlDragDatasetHead/queryFieldByApi` | POST | 解析 API 返回字段列表 |

## 数据集实体结构（OnlDragDatasetHead）

> **强制规则：创建数据集时 `parentId` 必须设为 `'0'`**（根目录分组）。不设或留空会导致数据集在管理界面中无法正确归类显示。所有预置脚本（dataset_ops.py、comp_ops.py）已内置此默认值。

```python
{
    'name': '数据集名称',
    'code': '数据集编码',
    'dataType': 'sql',             # sql / api / json / singleFile / FILES
    'dbSource': '707437208002265088',  # 数据库源 ID（SQL 类型必填！）
    'querySql': 'SELECT ...',
    'apiMethod': 'get',
    'izAgent': '0',                # 是否代理：'0'=直连, '1'=服务端代理
    'content': '',
    'parentId': '0',               # 强制设为 '0'
    'datasetItemList': [           # 注意：不是 onlDragDatasetItemList
        {'fieldName': 'name', 'fieldTxt': '名称', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0},
        {'fieldName': 'value', 'fieldTxt': '数值', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1}
    ],
    'datasetParamList': [          # 注意：不是 onlDragDatasetParamList
        {'paramName': 'sex', 'paramTxt': '性别', 'paramValue': '1', 'dictCode': 'sex'}
    ]
}
```

## 修改数据集属性（重命名等）

**使用 dataset_ops.py edit 命令（推荐）：**

```bash
# 重命名
py dataset_ops.py edit $API_BASE $TOKEN --id "数据集ID" --name "新名称"

# 同时修改多个属性
py dataset_ops.py edit $API_BASE $TOKEN --id "数据集ID" --name "新名称" --code "new_code" --sql "SELECT ..."
```

**API 端点：** `PUT /drag/onlDragDatasetHead/edit`，传完整实体 JSON（先 list 查到完整记录，修改目标字段后 PUT 回去）。

**操作流程（理想 2 轮）：**

| 轮次 | 操作 |
|------|------|
| 1 | Read 凭据 + cp dataset_ops.py + bi_utils.py（并行） |
| 2 | `py dataset_ops.py edit ... && rm dataset_ops.py bi_utils.py` |

**注意：** bi_utils 使用 urllib（非 requests），自定义脚本必须用 `bi_utils._request()` 发请求。

## 创建 SQL 数据集

```python
import sys, json
sys.path.insert(0, r'D:\webstorm_project_2023\vue3-jeecg-drag-design-antd4')
import bi_utils
bi_utils.init_api('http://api3.boot.jeecg.com', 'your-token')

result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '用户男女比例统计',
    'code': 'user_sex_ratio',
    'dataType': 'sql',
    'dbSource': '707437208002265088',
    'querySql': "SELECT sex as name, COUNT(*) AS value FROM demo WHERE sex IS NOT NULL AND sex != '' GROUP BY sex",
    'apiMethod': 'GET',
    'parentId': '0',
    'datasetItemList': [
        {'fieldName': 'name', 'fieldTxt': 'name', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0},
        {'fieldName': 'value', 'fieldTxt': 'value', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1}
    ],
    'datasetParamList': []
})
dataset_id = result['result']['id']

test = bi_utils._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': dataset_id})
print(json.dumps(test, ensure_ascii=False))
```

## 创建 SQL 数据集（存储过程）

> **参考文档：** https://help.jimureport.com/biScreen/base/data/sqlProcedure

### 概述

JimuReport SQL 数据集支持通过 `CALL procedure_name(${param})` 语法调用 MySQL 存储过程。存储过程的结果集会作为数据集的数据返回，可绑定到任意组件（表格、图表等）。

### 前置条件

**JimuReport 的 SQL 数据集 API 使用 Spring JdbcTemplate 的 `executeQuery()`，只能执行返回结果集的 SQL（SELECT / CALL），无法执行 DDL（CREATE PROCEDURE）。** 因此必须先通过其他方式在数据库中创建存储过程：
- 方法一：直接连接数据库执行 DDL（推荐，使用 pymysql）
- 方法二：通过数据库管理工具（Navicat、DBeaver 等）手动创建
- 方法三：通过 JeecgBoot 后端自定义接口执行

### 完整流程（3 步）

**Step 1：通过 pymysql 创建存储过程**

```python
import pymysql

# 连接信息从数据源 API 获取（datasource_ops.py detail --id xxx）
# 注意：JDBC URL 中的 127.0.0.1 是服务器本地地址，需替换为实际 IP
conn = pymysql.connect(
    host='192.168.1.66', port=3306,
    user='root', password='root',
    database='jeecg-boot', charset='utf8mb4'
)
cursor = conn.cursor()

# 先删后建（幂等）
cursor.execute("DROP PROCEDURE IF EXISTS sp_query_demo")
cursor.execute("""
CREATE PROCEDURE sp_query_demo()
BEGIN
    SELECT id, name, sex, age, birthday, salary_money, email
    FROM demo
    ORDER BY create_time DESC;
END
""")
conn.commit()

# 验证
cursor.execute("CALL sp_query_demo()")
print(f"返回 {len(cursor.fetchall())} 条记录")
cursor.close()
conn.close()
```

**带参数的存储过程：**

```sql
-- 创建带参数的存储过程
CREATE PROCEDURE sp_query_demo_by_sex(IN p_sex varchar(10))
BEGIN
    SELECT id, name, sex, age, birthday
    FROM demo
    WHERE sex = p_sex
    ORDER BY create_time DESC;
END
```

**Step 2：创建 SQL 数据集（使用 CALL 语法）**

无参数：
```bash
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID \
  --comp "JCommonTable" --title "Demo数据表格" --x 50 --y 50 --w 900 --h 450 \
  --create-sql "CALL sp_query_demo()" \
  --ds-name "demo表存储过程查询" \
  --fields "id:String,name:String,sex:String,age:String,birthday:String,salary_money:String,email:String" \
  --dict "sex=sex"
```

带参数（使用 FreeMarker `${param}` 语法）：
```bash
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID \
  --comp "JCommonTable" --title "Demo按性别查询" --x 50 --y 50 --w 900 --h 450 \
  --create-sql "CALL sp_query_demo_by_sex('${sex}')" \
  --ds-name "demo按性别查询" \
  --fields "id:String,name:String,sex:String,age:String,birthday:String" \
  --sql-params "sex:性别:1:sex"
```

也可用 dataset_ops.py 单独创建数据集：
```bash
py dataset_ops.py create-sql $API_BASE $TOKEN \
  --name "demo表存储过程查询" --code "sp_query_demo_ds" \
  --sql "CALL sp_query_demo()" \
  --fields "id:String,name:String,sex:String,age:String"
```

**Step 3：绑定到组件**

使用 `--dataset-name` 或 `--dataset-id` 绑定已有数据集：
```bash
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID \
  --comp "JCommonTable" --title "Demo数据表格" --x 50 --y 50 --w 900 --h 450 \
  --dataset-name "demo表存储过程查询"
```

### 关键踩坑记录

| 问题 | 说明 |
|------|------|
| **JimuReport API 无法执行 CREATE PROCEDURE** | `getAllChartData` 内部用 `executeQuery()` 只能执行 SELECT/CALL，DDL 会报 `Statement.executeQuery() cannot issue statements that do not produce result sets` |
| **必须通过 pymysql 等直连数据库创建存储过程** | 安装：`py -m pip install pymysql`；JDBC URL 中 127.0.0.1 需替换为服务器实际 IP |
| **CALL 参数用 FreeMarker 语法** | `CALL sp_name('${param}')` ，不是 `CALL sp_name(?)` |
| **必须用 comp_ops.py 绑定组件** | 直接操作 bi_utils 会缺少 `dataSetId`/`dataMapping`/`fieldOption` 等关键字段，导致组件仍显示静态数据 |
| **datasource_ops.py 的 parseSQL 端点有误** | 脚本中使用 `/parseSQL` 但实际端点是 `/queryFieldBySql`（需签名） |
| **数据源 JDBC URL 中 127.0.0.1** | 这是服务器本地地址，从外部连接需替换为服务器 IP |

### pymysql 安装

```bash
py -m pip install pymysql
```

> Windows 下用 `py` 而非 `python`，Git Bash 下 `python` 命令可能不存在。

## 创建 API 数据集

```python
result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '产品销量排行榜',
    'code': 'product_sales',
    'dataType': 'api',
    'dbSource': None,                   # API 类型不需要数据库源
    'querySql': 'https://api.jeecg.com/mock/31/graphreport/aiproducttest',  # API 地址存在 querySql 字段
    'apiMethod': 'get',
    'izAgent': '0',
    'parentId': '0',
    'datasetItemList': [
        {'fieldName': 'name', 'fieldTxt': 'name', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0},
        {'fieldName': 'value', 'fieldTxt': 'value', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1}
    ],
    'datasetParamList': []
})
dataset_id = result['result']['id']
```

## 组件绑定数据集（dataType=2）

```python
config = {
    'dataType': 2,
    'dataSetId': dataset_id,
    'dataSetName': '数据集名称',
    'dataSetType': 'sql',               # sql / api
    'dataSetApi': 'SELECT ...',         # SQL 语句或 API 地址
    'dataSetMethod': 'get',
    'dataSetIzAgent': '1',               # SQL 类型用 '1'，API 直连用 '0'
    'dataMapping': [
        {'filed': '维度', 'mapping': 'name'},   # 注意：filed 不是 field
        {'filed': '数值', 'mapping': 'value'},
    ],
    'chartData': '[]',
    'option': { ... }
}
```

### 标准字段映射规则

| 映射标签（filed） | 标准字段（key） | 说明 |
|-------------------|----------------|------|
| `维度` / `名称` | `name` | 图表类目/维度 |
| `数值` | `value` | 图表数值 |
| `分组` | `type` | 多系列区分字段 |
| `文本` | `label` | 文本标签 |

## 组件绑定数据集完整示例（SQL 饼图）

```python
pie_comp = {
    'component': 'JPie',
    'componentName': '男女比例',
    'visible': True,
    'i': bi_utils._gen_uuid(),
    'x': 750, 'y': 700, 'w': 450, 'h': 350,
    'orderNum': 300,
    'config': {
        'dataType': 2,
        'w': 450, 'h': 350,
        'size': {'width': 450, 'height': 350},
        'dataSetId': dataset_id,
        'dataSetName': '用户男女比例统计',
        'dataSetType': 'sql',
        'dataSetApi': "SELECT sex as name, COUNT(*) AS value FROM demo ...",
        'dataSetMethod': 'GET',
        'dataSetIzAgent': '1',
        'dataMapping': [
            {'filed': '维度', 'mapping': 'name'},
            {'filed': '数值', 'mapping': 'value'}
        ],
        'chartData': '[]',
        'option': { ... }
    }
}
```

## API 数据集与 SQL 数据集的关键差异

| 项目 | API 数据集 | SQL 数据集 |
|------|-----------|-----------|
| `dataType`（数据集） | `'api'` | `'sql'` |
| `dbSource` | `None`（不需要） | 必填（数据库源 ID） |
| `querySql` | 存放 **API URL** | 存放 SQL 语句 |
| `izAgent` | `'0'`=前端直连, `'1'`=后端代理 | 不使用 |
| `apiMethod` | `'get'` / `'post'` | `'GET'`（无实际意义） |
| 组件 `dataSetIzAgent` | `'0'`（直连）或 `'1'`（代理） | `'1'`（走后端代理） |

## API 数据格式要求

API 返回的数据必须是 JSON 数组：

```json
// 标准 name/value 格式
[{"name": "新洲店", "value": 8500}, {"name": "水围店", "value": 7200}]

// 多系列格式
[{"name": "1月", "value": 100, "type": "系列A"}, {"name": "1月", "value": 200, "type": "系列B"}]
```

> 如果 API 返回 `{"success":true, "result":[...]}` 嵌套结构，系统自动提取 `result` 数组。

## API 数据集端到端完整脚本示例（API 漏斗图）

```python
import sys, json
sys.path.insert(0, r'D:\webstorm_project_2023\vue3-jeecg-drag-design-antd4')
from bi_utils import *
import bi_utils

API_BASE = 'http://192.168.1.66:8080/jeecg-boot'
TOKEN = 'your-token'
PAGE_ID = '大屏页面ID'
DATA_API_URL = 'https://api.jeecg.com/mock/51/beverageSales?type=salesRanking'

init_api(API_BASE, TOKEN)

# 1. 创建 API 数据集
ds_result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '门店销量排行-API',
    'code': 'store_sales_ranking_api',
    'dataType': 'api',
    'dbSource': None,
    'querySql': DATA_API_URL,
    'apiMethod': 'get',
    'izAgent': '0',
    'parentId': '0',
    'datasetItemList': [
        {'fieldName': 'name', 'fieldTxt': 'name', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0},
        {'fieldName': 'value', 'fieldTxt': 'value', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1}
    ],
    'datasetParamList': []
})
dataset_id = ds_result['result']['id']

# 2. 测试数据集
test = bi_utils._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': dataset_id})
print('数据预览:', json.dumps(test['result']['data'][:3], ensure_ascii=False))

# 3. 查询大屏，追加漏斗图组件
page = query_page(PAGE_ID)
template = page.get('template', [])
if isinstance(template, str):
    template = json.loads(template)

# 4. 构建 JFunnel 组件
funnel_config = {
    'borderColor': '#FFFFFF00',
    'background': '#FFFFFF00',
    'dataType': 2,
    'dataSetId': dataset_id,
    'dataSetName': '门店销量排行-API',
    'dataSetType': 'api',
    'dataSetApi': DATA_API_URL,
    'dataSetMethod': 'get',
    'dataSetIzAgent': '0',
    'dataMapping': [
        {'filed': '维度', 'mapping': 'name'},
        {'filed': '数值', 'mapping': 'value'}
    ],
    'fieldOption': [
        {'label': 'name', 'text': 'name', 'type': 'String', 'value': 'name', 'show': 'Y'},
        {'label': 'value', 'text': 'value', 'type': 'String', 'value': 'value', 'show': 'Y'},
    ],
    'paramOption': [],
    'chartData': '[]',
    'dataFilterNum': 5,
    'viewLoading': True,
    'timeOut': 0,
    'w': 580, 'h': 450,
    'size': {'width': 580, 'height': 450},
    'option': {
        'customColor': [
            {'color': '#5470C6'}, {'color': '#91CC75'}, {'color': '#FAC858'},
            {'color': '#EE6666'}, {'color': '#73C0DE'}
        ],
        'series': [{
            'type': 'funnel', 'name': '门店销量',
            'left': '10%', 'width': '80%', 'bottom': '5%', 'gap': 2,
            'sort': 'descending',
            'label': {'show': True, 'position': 'inside', 'color': '#ffffff', 'formatter': '{b}: {c}'},
            'labelLine': {'lineStyle': {'width': 1, 'type': 'solid'}, 'length': 10},
            'itemStyle': {'borderColor': 'rgba(255,255,255,0.2)', 'borderWidth': 1},
            'emphasis': {'label': {'fontSize': 18}}
        }],
        'tooltip': {'trigger': 'item', 'formatter': '{b} : {c}', 'textStyle': {'color': '#EEF1FA'}},
        'legend': {'orient': 'horizontal', 't': 90, 'r': 1, 'textStyle': {'color': '#ffffff'}},
        'title': {
            'show': True, 'text': '门店销量漏斗', 'top': 5, 'left': 'center',
            'textStyle': {'color': '#ffffff', 'fontSize': 16, 'fontWeight': 'normal'}
        },
        'card': {'title': '', 'extra': '', 'rightHref': '', 'size': 'default'}
    },
    'actionConfig': {'operateType': 'modal', 'modalName': '', 'url': ''},
    'turnConfig': {'type': '_blank', 'url': ''},
    'linkType': 'url', 'linkageConfig': [], 'url': '', 'query': []
}

template.append({
    'component': 'JFunnel', 'componentName': '门店销量漏斗', 'visible': True,
    'i': bi_utils._gen_uuid(), 'x': 1300, 'y': 500, 'w': 580, 'h': 450,
    'orderNum': len(template) + 1, 'config': funnel_config
})

bi_utils._page_components[PAGE_ID] = template
save_page(PAGE_ID)
```

## JFunnel 漏斗图组件配置参考

**数据格式**：`[{name, value}]`（与饼图相同）

| 配置路径 | 说明 | 示例值 |
|----------|------|--------|
| `config.dataFilterNum` | 只取前 N 条数据（建议 3-7） | `5` |
| `option.series[0].sort` | 排序方向 | `'descending'` |
| `option.series[0].gap` | 漏斗层间距 | `2` |
| `option.series[0].left` | 漏斗左偏移 | `'10%'` |
| `option.series[0].width` | 漏斗宽度 | `'80%'` |
| `option.series[0].label.position` | 标签位置 | `'inside'` |
| `option.customColor` | 自定义配色 `[{color:'#xxx'}]` | 见示例 |

## API 数据集常用 mock 地址

| API 地址 | 返回格式 | 适用图表 |
|----------|---------|---------|
| `https://api.jeecg.com/mock/31/graphreport/aiproducttest` | `[{name,value}]` | 柱形/饼图/漏斗 |
| `https://api.jeecg.com/mock/51/beverageSales?type=salesRanking` | `[{name,value}]` 13条门店数据 | 柱形/排行榜/漏斗 |

## 数据集「先查后建」规则（强制）

**当用户指定了数据集名称时，必须先查询是否已存在同名数据集，存在则直接复用，不存在才创建。**

```python
existing = bi_utils._request('GET', '/drag/onlDragDatasetHead/list',
    params={'pageNo': 1, 'pageSize': 10, 'name': '用户指定的数据集名称'})
records = existing.get('result', {}).get('records', [])

if records:
    dataset_id = records[0]['id']
else:
    ds_result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={...})
    dataset_id = ds_result['result']['id']
```

## SQL 数据集动态查询条件

### FreeMarker 动态条件语法

```sql
select * from sys_user where del_flag = 0
<#if isNotEmpty(realname)>
   and realname like '%${realname}%'
</#if>
<#if isNotEmpty(sex)>
   and sex = '${sex}'
</#if>
```

**语法要点：**
- `${paramName}` — 参数占位符
- `<#if isNotEmpty(paramName)>` — 当参数非空时才拼接
- `</#if>` — 条件结束标记

### 参数列表配置

```python
'datasetParamList': [
    {'paramName': 'realname', 'paramTxt': '姓名', 'paramValue': '', 'dictCode': ''},
    {'paramName': 'sex', 'paramTxt': '性别', 'paramValue': '1', 'dictCode': 'sex'}
]
```

### 组件中的参数配置（paramOption）

```python
'paramOption': [
    {'defaultVal': '', 'label': 'realname', 'text': '姓名', 'type': 'string', 'value': 'realname'},
    {'defaultVal': '', 'label': 'sex', 'text': '性别', 'type': 'string', 'value': 'sex'}
]
```

## SQL 数据集绑定图表完整端到端流程

### 完整 config 结构

```python
config = {
    'borderColor': '#FFFFFF00',
    'background': '#FFFFFF00',
    'dataType': 2,
    'dataSetId': dataset_id,
    'dataSetName': '数据集名称',
    'dataSetType': 'sql',
    'dataSetApi': DYNAMIC_SQL,
    'dataSetMethod': 'get',
    'dataSetIzAgent': '1',
    'chartData': '[]',
    'viewLoading': True,
    'timeOut': 0,
    'w': 600, 'h': 350,
    'size': {'height': 350},
    'fieldOption': [
        {'label': 'name', 'text': 'name', 'type': 'String', 'value': 'name', 'show': 'Y'},
        {'label': 'value', 'text': 'value', 'type': 'String', 'value': 'value', 'show': 'Y'}
    ],
    'paramOption': [
        {'defaultVal': '', 'label': 'name', 'text': '名称', 'type': 'string', 'value': 'name'}
    ],
    'dataMapping': [
        {'mapping': 'name', 'filed': '维度'},
        {'mapping': 'value', 'filed': '数值'}
    ],
    'option': {
        'title': {'text': '图表标题', 'show': True, 'textStyle': {'color': '#ffffff'}},
        'tooltip': {...},
        'xAxis': {'axisLabel': {'color': '#ffffff'}},
        'yAxis': {'axisLabel': {'color': '#ffffff'}, 'splitLine': {'lineStyle': {'color': 'rgba(255,255,255,0.1)'}}},
        'grid': {'top': 50, 'left': 10, 'bottom': 20, 'right': 30, 'containLabel': True, 'show': False},
        'series': [{'type': 'line/bar/pie', 'data': [], ...}],
        'card': {'title': '', 'extra': '', 'rightHref': '', 'size': 'default'}
    },
    'actionConfig': {'operateType': 'modal', 'modalName': '', 'url': ''},
    'turnConfig': {'type': '_blank', 'url': ''},
    'linkType': 'url',
    'linkageConfig': [],
    'seriesType': [],
    'markLineConfig': {'show': False, 'markLine': []},
    'drillData': [],
    'dictOptions': {},
    'query': [],
    'url': ''
}
```

## 文件数据集（单文件 singleFile / 多文件 FILES）

### 文件数据集 vs SQL/API 数据集的关键差异

| 项目 | 单文件 (singleFile) | 多文件 (FILES) | SQL 数据集 | API 数据集 |
|------|-------------------|---------------|-----------|-----------|
| `dataType`（数据集） | `'singleFile'` | `'FILES'` | `'sql'` | `'api'` |
| `dbSource` | **reportId**（页面 ID） | **reportId**（页面 ID） | 数据库源 ID | `None` |
| `querySql` | `select * from {tableName}` | 可跨表 SQL 查询 | SQL 语句 | API URL |
| 文件上传 | 1 个文件（`isSingle=true`） | 多个文件 | 不需要 | 不需要 |
| `content` | `JSON.stringify(fileList)` | 不需要 | 不需要 | 不需要 |
| 字段解析 API | 自动从文件解析 | `queryFileFieldBySql` | `queryFieldBySql` | `queryFieldByApi` |
| 支持格式 | `.csv .xls .xlsx .json` | `.csv .xls .xlsx .json` | — | — |

### 文件上传 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/jmreport/source/datasource/files/add` | POST (multipart) | 上传文件 |
| `/jmreport/source/datasource/files/get` | GET | 获取文件列表 `?reportId=xxx` |
| `/jmreport/source/datasource/files/preview` | GET | 预览文件数据 |
| `/jmreport/source/datasource/files/del` | DELETE | 删除数据源 |
| `/jmreport/source/datasource/files/del/file` | DELETE | 删除单个文件 |

### 上传 API 返回值结构

```json
{
  "success": true,
  "message": "filesDataSet/PAGE_ID/default.xls",
  "result": {
    "id": "数据源记录ID",
    "reportId": "PAGE_ID",
    "dbType": "FILES",
    "dbDriver": "filesDataSet\\PAGE_ID",
    "dbUrl": "[{\"fileName\":\"default.xls\",\"name\":\"jmf.Sheet1_default_excel\"}]"
  }
}
```

**关键字段：**
- `result.dbUrl`：JSON 字符串，包含 `fileName`（原始文件名）和 `name`（解析后的表名）
- **表名命名规则**：`jmf.{SheetName}_{文件名去后缀}_excel`（Excel）、`jmf.{文件名去后缀}_csv`（CSV）、`jmf.{文件名去后缀}_json`（JSON）

### 预览 API（获取字段列表）

```python
preview = bi_utils._request('GET', '/jmreport/source/datasource/files/preview',
    params={'reportId': PAGE_ID, 'tableName': table_name, 'pageNo': 1, 'pageSize': 5})
```

**返回值注意：** `result` 直接是**列表**（`list`），不是分页对象（无 `records` 键），与 SQL 数据集的 list API 不同。

```python
# 从预览数据自动提取字段列表
records = preview['result']  # 直接是 list，不需要 ['records']
fields = []
if records:
    for idx, key in enumerate(records[0].keys()):
        fields.append({
            'fieldName': key, 'fieldTxt': key,
            'fieldType': 'String', 'izShow': 'Y', 'orderNum': idx
        })
```

### 创建单文件数据集（singleFile）端到端

```python
import sys, json, os, time
sys.path.insert(0, '.')
import bi_utils
import urllib.request

API_BASE = 'http://192.168.1.66:8080/jeecg-boot'
TOKEN = 'your-token'
PAGE_ID = '大屏页面ID'
FILE_PATH = r'E:\data\default.xls'

bi_utils.API_BASE = API_BASE
bi_utils.TOKEN = TOKEN

# ======= Step 1: 上传文件（isSingle=True） =======
def upload_file(file_path, report_id, is_single=False):
    url = f'{API_BASE}/jmreport/source/datasource/files/add'
    boundary = f'----WebKitFormBoundary{int(time.time()*1000)}'
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_data = f.read()
    body_parts = []
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="reportId"\r\n\r\n{report_id}\r\n'.encode())
    if is_single:
        body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="isSingle"\r\n\r\ntrue\r\n'.encode())
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file_name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
    body_parts.append(file_data)
    body_parts.append(f'\r\n--{boundary}--\r\n'.encode())
    body = b''.join(body_parts)
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'X-Access-Token': TOKEN,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

result = upload_file(FILE_PATH, PAGE_ID, is_single=True)
db_url = result['result']['dbUrl']
file_list = json.loads(db_url)
table_name = file_list[0]['name']

# ======= Step 2: 预览文件获取字段 =======
preview = bi_utils._request('GET', '/jmreport/source/datasource/files/preview',
    params={'reportId': PAGE_ID, 'tableName': table_name, 'pageNo': 1, 'pageSize': 5})
records = preview['result']  # 直接是 list
fields = []
if records:
    for idx, key in enumerate(records[0].keys()):
        fields.append({
            'fieldName': key, 'fieldTxt': key,
            'fieldType': 'String', 'izShow': 'Y', 'orderNum': idx
        })

# ======= Step 3: 创建数据集 =======
ds = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '销售数据(单文件)',
    'code': 'sales_single',
    'dataType': 'singleFile',
    'dbSource': PAGE_ID,                              # 关键：dbSource = 页面ID
    'querySql': f'select * from {table_name}',
    'apiMethod': 'GET',
    'content': json.dumps(file_list, ensure_ascii=False),  # 关键：必须传 content
    'parentId': '0',
    'datasetItemList': fields,
    'datasetParamList': []
})
dataset_id = ds['result']['id']

# ======= Step 4: 验证数据集 =======
test = bi_utils._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': dataset_id})
print(f"返回 {len(test['result']['data'])} 条记录")

# ======= 组件绑定（可选） =======
# config = {
#     'dataType': 2,
#     'dataSetId': dataset_id,
#     'dataSetType': 'singleFile',
#     'dataSetApi': f'select * from {table_name}',
#     'dataSetMethod': 'get',
#     'dataSetIzAgent': '',
#     'dataMapping': [
#         {'filed': '维度', 'mapping': 'name'},
#         {'filed': '数值', 'mapping': 'value'}
#     ],
#     'chartData': '[]',
# }
```

### 单文件数据集踩坑记录

| 问题 | 说明 |
|------|------|
| **content 字段必传** | `content` = `json.dumps(file_list)`，不传则数据集无法关联到文件 |
| **dbSource = 页面 ID** | 不是数据库源 ID，是大屏页面 ID（reportId） |
| **预览返回 list 不是分页对象** | `preview['result']` 直接是数组，没有 `records` 键 |
| **字段自动检测** | 用预览 API 取第一条记录的 keys 即可获取全部字段，无需手动指定 |
| **表名由系统生成** | 格式 `jmf.{SheetName}_{filename}_excel`，从上传返回的 `dbUrl` 中提取 |
| **upload 必须用 multipart** | urllib 手动构建 multipart body，不能用 `_request()` |
| **isSingle 参数** | 单文件必须传 `isSingle=true`，否则按多文件(FILES)处理 |
| **组件绑定 dataSetIzAgent** | 单文件类型 `dataSetIzAgent` 设为空字符串 `''`，不是 `'0'` 或 `'1'` |

### 创建多文件数据集（FILES）端到端

```python
# 1. 上传多个文件
upload_file(r'E:\data\temperature.csv', PAGE_ID)
upload_file(r'E:\data\population.csv', PAGE_ID)

# 2. 获取完整文件列表
files_resp = bi_utils._request('GET', '/jmreport/source/datasource/files/get',
                                params={'reportId': PAGE_ID})
file_list = json.loads(files_resp['result']['dbUrl'])

# 3. 创建数据集（可跨文件表查询）
ds = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '城市温度(多文件)',
    'code': 'city_temp_multi',
    'dataType': 'FILES',            # 关键：FILES（大写）
    'dbSource': PAGE_ID,
    'querySql': f'select city as name, temperature as value from {temp_table} order by temperature desc',
    'apiMethod': 'GET',
    'parentId': '0',
    'datasetItemList': [...],
    'datasetParamList': []
})
```

## SQL 数据集 + 带参数查询 + 字典翻译 + 绑定图表（完整端到端流程）

> **适用场景：** comp_ops.py `--create-sql` 不支持 `--sql-params`，带 FreeMarker 动态参数的 SQL 数据集必须用自定义脚本。

### 完整示例：demo 表男女比例饼图（带 age 查询参数）

```python
import sys, json
sys.path.insert(0, '.')
import bi_utils
bi_utils.API_BASE = 'http://192.168.1.66:8080/jeecg-boot'
bi_utils.TOKEN = 'your-token'
PAGE_ID = '大屏页面ID'

DYNAMIC_SQL = """SELECT sex as name, COUNT(*) AS value FROM demo WHERE sex IS NOT NULL
<#if isNotEmpty(age)>
   and age = '${age}'
</#if>
GROUP BY sex"""

# ======= 1. 确保 jimu_dict 中有字典（大屏字典，非 sys_dict） =======
check = bi_utils._request('GET', '/jmreport/dict/list', params={'dictCode': 'sex', 'pageNo': 1, 'pageSize': 10})
records = check.get('result', {}).get('records', [])
sex_dict = next((r for r in records if r.get('dictCode') == 'sex'), None)

if not sex_dict:
    bi_utils._request('POST', '/jmreport/dict/add', data={
        'dictName': '性别', 'dictCode': 'sex', 'description': '性别字典'
    })
    re_query = bi_utils._request('GET', '/jmreport/dict/list', params={'dictCode': 'sex', 'pageNo': 1, 'pageSize': 10})
    sex_dict = next(r for r in re_query['result']['records'] if r.get('dictCode') == 'sex')
    dict_id = sex_dict['id']
    for item in [{'itemText': '男', 'itemValue': '1', 'sortOrder': 1}, {'itemText': '女', 'itemValue': '2', 'sortOrder': 2}]:
        bi_utils._request('POST', '/jmreport/dictItem/add', data={
            'dictId': dict_id, 'itemText': item['itemText'],
            'itemValue': item['itemValue'], 'sortOrder': item['sortOrder'], 'status': 1
        })

# ======= 2. 查数据源 ID =======
ds_options = bi_utils._request('GET', '/drag/onlDragDataSource/getOptions')
db_source = ds_options['result'][0]['id']

# ======= 3. 创建数据集（含 itemList + paramList + dictCode） =======
ds_result = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': '男女比例统计',
    'code': 'demo_sex_ratio',
    'dataType': 'sql',
    'dbSource': db_source,
    'querySql': DYNAMIC_SQL,
    'apiMethod': 'GET',
    'parentId': '0',
    'datasetItemList': [
        {'fieldName': 'name', 'fieldTxt': 'name', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0, 'dictCode': 'sex'},
        {'fieldName': 'value', 'fieldTxt': 'value', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1}
    ],
    'datasetParamList': [
        {'paramName': 'age', 'paramTxt': '年龄', 'paramValue': '', 'dictCode': ''}
    ]
})
dataset_id = ds_result['result']['id']

# ======= 4. 测试数据集 → 获取 dictOptions =======
test = bi_utils._request('POST', '/drag/onlDragDatasetHead/getAllChartData', data={'id': dataset_id})
dict_options = test.get('result', {}).get('dictOptions', {})
# dict_options 示例: {"name": [{"value":"1","text":"男","color":"#2196F3",...}, ...]}

# ======= 5. 从 default_configs.json 加载默认图表配置 =======
with open('default_configs.json', 'r', encoding='utf-8') as f:
    defaults = json.load(f)
config = json.loads(json.dumps(defaults['JPie']))  # 深拷贝！

# ======= 6. 覆盖动态数据相关字段 =======
config.update({
    'dataType': 2,
    'dataSetId': dataset_id,
    'dataSetName': '男女比例统计',
    'dataSetType': 'sql',
    'dataSetApi': DYNAMIC_SQL,
    'dataSetMethod': 'get',
    'dataSetIzAgent': '1',
    'chartData': '[]',
    'w': 450, 'h': 350,
    'size': {'width': 450, 'height': 350},
    'background': '#FFFFFF00',
    'borderColor': '#FFFFFF00',
    'viewLoading': True,
    'dictOptions': dict_options,  # 从 getAllChartData 获取，不要手动构建！
    'dataMapping': [
        {'filed': '维度', 'mapping': 'name'},
        {'filed': '数值', 'mapping': 'value'}
    ],
    'fieldOption': [
        {'label': 'name', 'text': 'name', 'type': 'String', 'value': 'name', 'show': 'Y'},
        {'label': 'value', 'text': 'value', 'type': 'String', 'value': 'value', 'show': 'Y'}
    ],
    'paramOption': [
        {'defaultVal': '', 'label': 'age', 'text': '年龄', 'type': 'string', 'value': 'age'}
    ],
})
config['option']['title']['text'] = '男女比例'
config['option']['title']['show'] = True
config['option']['title'].setdefault('textStyle', {})['color'] = '#ffffff'
config['option']['card'] = {'title': '', 'extra': '', 'rightHref': '', 'size': 'default'}

# ======= 7. 追加到大屏 =======
page = bi_utils.query_page(PAGE_ID)
tmpl = page.get('template', [])
tmpl.insert(0, {
    'component': 'JPie', 'componentName': '男女比例', 'visible': True,
    'i': bi_utils._gen_uuid(), 'x': 735, 'y': 365, 'w': 450, 'h': 350,
    'orderNum': len(tmpl) + 1, 'config': config
})
bi_utils._page_components[PAGE_ID] = tmpl
bi_utils.save_page(PAGE_ID)
```

### 关键注意事项

| 步骤 | 易错点 | 正确做法 |
|------|--------|---------|
| 字典 | 用了 `/sys/dict/` | 必须用 `/jmreport/dict/`（jimu_dict 表） |
| 数据集字段 | 缺少 `dictCode` | `datasetItemList[].dictCode = 'sex'` 绑定字典翻译 |
| 数据集参数 | 缺少 `datasetParamList` | FreeMarker `${age}` 需要对应的 paramList 项 |
| dictOptions | 手动构建 | 必须从 `getAllChartData` 返回值获取（含 value/text/color/label/title） |
| 图表 config | 手写 option | 必须从 `default_configs.json` 深拷贝默认配置，再覆盖动态字段 |
| list 接口验证 | 查 itemList/paramList | list 接口始终返回空数组，用 `getAllChartData` 验证 dictOptions |

## 数据库源 ID 参考

| 环境 | dbSource / dbCode | 说明 |
|------|-------------------|------|
| api3.boot.jeecg.com 主库 | `707437208002265088` | 默认 MySQL 数据库 |

> 不同环境的 dbSource ID 不同，部署到新环境时需要通过 `/drag/onlDragDataSource/getOptions` 查询可用的数据源列表。
