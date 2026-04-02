# Elasticsearch 数据源报表示例

## 场景说明

创建一个使用 Elasticsearch 数据源的普通列表报表。ES 索引为 `jm_demo`，报表名称为「Elasticsearch数据源测试」，展示7个字段。

**ES 数据源关键规则：**
- 数据源 `dbType` 为 `"es"`
- SQL 必须加 `es.` 前缀：`select * from es.索引名`（类似 MongoDB 的 `mongo.` 前缀）
- 不加前缀会报 "Object not found"

## 完整创建流程

```
Step 1: 在 ES 中创建索引并插入测试数据（通过 ES REST API）
Step 2: POST /jmreport/addDataSource     → 添加 ES 数据源到积木报表
Step 3: POST /jmreport/save              → 创建空报表
Step 4: POST /jmreport/queryFieldBySql   → 解析 SQL 获取字段（ES 9.x 可能失败，需手动构建）
Step 5: POST /jmreport/saveDb            → 保存数据集
Step 6: POST /jmreport/save              → 保存完整报表设计
```

## Step 1: 创建 ES 索引和数据

```python
import base64

ES_HOST = '127.0.0.1:9200'
ES_USER = 'elastic'
ES_PASS = 'password'
ES_INDEX = 'jm_demo'

def es_request(path, data=None, method=None):
    url = f'http://{ES_HOST}{path}'
    auth_str = base64.b64encode(f'{ES_USER}:{ES_PASS}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_str}',
        'Content-Type': 'application/json'
    }
    # ... urllib.request 调用

# 创建索引
mapping = {
    "mappings": {
        "properties": {
            "name": {"type": "keyword"},
            "age": {"type": "keyword"},
            "email": {"type": "keyword"},
            "department": {"type": "keyword"},
            "salary": {"type": "keyword"},
            "join_date": {"type": "keyword"},
            "city": {"type": "keyword"}
        }
    }
}
es_request(f'/{ES_INDEX}', mapping, method='PUT')

# 插入数据
docs = [
    {"name": "张三", "age": "28", "email": "zhangsan@test.com", "department": "技术部", "salary": "15000", "join_date": "2022-03-15", "city": "北京"},
    {"name": "李四", "age": "32", "email": "lisi@test.com", "department": "产品部", "salary": "18000", "join_date": "2021-06-20", "city": "上海"},
    # ...
]
for i, doc in enumerate(docs):
    es_request(f'/{ES_INDEX}/_doc/{i+1}', doc, method='PUT')
es_request(f'/{ES_INDEX}/_refresh', method='POST')
```

> **建议使用 keyword 类型：** ES 9.x 与 Calcite 适配器存在类型转换兼容问题（integer/float/date 类型会报 ClassCastException），全部使用 keyword 类型最稳定。

## Step 2: 添加 ES 数据源（addDataSource）

```json
{
    "id": "",
    "reportId": "报表ID",
    "code": "",
    "name": "elasticsearch_test",
    "dbType": "es",
    "dbDriver": "",
    "dbUrl": "127.0.0.1:9200",
    "dbUsername": "elastic",
    "dbPassword": "password"
}
```

**接口：** `POST /jmreport/addDataSource`（不需要签名）

**获取数据源 ID：** `addDataSource` 返回 `result: true`（不含 ID），需通过 `getDataSourceByPage` 查询：

```python
r = api_request('/jmreport/addDataSource', ds_data)
# result 为 true，不含 ID

# 从列表中按 name 查找
ds_list = api_request('/jmreport/getDataSourceByPage')  # 需要签名
for ds in ds_list['result']['records']:
    if ds['name'] == 'elasticsearch_test':
        ds_id = ds['id']
        break
```

> **注意：** `getDataSourceByPage` 返回分页结构 `result.records`，每条记录是对象（含 id、name、dbType 等）。需要签名。

## Step 4: SQL 解析与 ES 9.x 兼容问题

```python
# ES SQL 必须加 es. 前缀
sql = "select * from es.jm_demo"

parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": sql,
    "dbSource": ds_id,  # 数据源 ID
    "type": "0"
})
```

### ES 9.x ClassCastException 问题

ES 9.x 版本（如 9.3.2）调用 `queryFieldBySql` 会报错：
```
class java.lang.String cannot be cast to class java.lang.Number
```

这是 JimuReport 的 Apache Calcite ES 适配器与 ES 9.x 的兼容性问题。

**解决方案：手动构建 fieldList，跳过 SQL 解析步骤。**

```python
# queryFieldBySql 失败时，手动构建 fieldList
fields = [
    {"fieldName": "name", "fieldText": "name", "widgetType": "String", "orderNum": 1},
    {"fieldName": "age", "fieldText": "age", "widgetType": "String", "orderNum": 2},
    {"fieldName": "email", "fieldText": "email", "widgetType": "String", "orderNum": 3},
    {"fieldName": "department", "fieldText": "department", "widgetType": "String", "orderNum": 4},
    {"fieldName": "salary", "fieldText": "salary", "widgetType": "String", "orderNum": 5},
    {"fieldName": "join_date", "fieldText": "join_date", "widgetType": "String", "orderNum": 6},
    {"fieldName": "city", "fieldText": "city", "widgetType": "String", "orderNum": 7},
]
```

> 字段信息可从 ES 的 mapping API 获取：`GET /{index}/_mapping`

## Step 5: 保存数据集（saveDb）

```json
{
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "es_demo",
    "dbChName": "ES员工数据",
    "dbType": "0",
    "dbSource": "数据源ID",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from es.jm_demo",
    "fieldList": [],
    "paramList": []
}
```

> **注意：** `dbType` 仍为 `"0"`（SQL 数据集），ES 数据源通过 `dbSource` 关联。SQL 中用 `es.` 前缀标识 ES 索引。

## Step 6: 报表设计 jsonStr

标题行 + 表头行 + 数据绑定行，7个字段。

```json
{
    "rows": {
        "1": {
            "cells": {"1": {"text": "Elasticsearch数据源测试", "style": 5, "merge": [0, 6], "height": 50}},
            "height": 50
        },
        "2": {
            "cells": {
                "1": {"text": "姓名", "style": 4},
                "2": {"text": "年龄", "style": 4},
                "3": {"text": "邮箱", "style": 4},
                "4": {"text": "部门", "style": 4},
                "5": {"text": "薪资", "style": 4},
                "6": {"text": "入职日期", "style": 4},
                "7": {"text": "城市", "style": 4}
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {"text": "#{es_demo.name}", "style": 2},
                "2": {"text": "#{es_demo.age}", "style": 2},
                "3": {"text": "#{es_demo.email}", "style": 2},
                "4": {"text": "#{es_demo.department}", "style": 2},
                "5": {"text": "#{es_demo.salary}", "style": 2},
                "6": {"text": "#{es_demo.join_date}", "style": 2},
                "7": {"text": "#{es_demo.city}", "style": 2}
            }
        },
        "len": 200
    },
    "cols": {
        "0": {"width": 25},
        "1": {"width": 100},
        "2": {"width": 80},
        "3": {"width": 180},
        "4": {"width": 100},
        "5": {"width": 100},
        "6": {"width": 120},
        "7": {"width": 100},
        "len": 100
    },
    "merges": ["B2:H2"],
    "printConfig": {"paper": "A4", "layout": "landscape"}
}
```

## 结构要点

### ES 数据源配置对照

| 项目 | 值 | 说明 |
|------|-----|------|
| `dbType`（addDataSource） | `"es"` | 数据源类型 |
| `dbUrl` | `"127.0.0.1:9200"` | ES 地址（不含 http://） |
| `dbUsername` / `dbPassword` | ES 认证信息 | 可选（无认证时留空） |
| SQL 语法 | `select * from es.索引名` | 必须加 `es.` 前缀 |
| `dbType`（saveDb） | `"0"` | 数据集类型仍为 SQL |

### 与 MongoDB 数据源对比

| 项目 | Elasticsearch | MongoDB |
|------|--------------|---------|
| 数据源 dbType | `"es"` | `"mongodb"` |
| SQL 前缀 | `es.` | `mongo.` |
| dbUrl 格式 | `host:port` | `host:port` |
| 字段过滤 | 无特殊要求 | 需过滤含 `-` 和 `_` 开头的字段 |

### 完整 Python 脚本流程

```python
# Step 1: 创建 ES 索引和数据（es_request）
# Step 2: 添加数据源
api_request('/jmreport/addDataSource', {
    "id": "", "reportId": report_id, "name": "elasticsearch_test",
    "dbType": "es", "dbUrl": "127.0.0.1:9200",
    "dbUsername": "elastic", "dbPassword": "password"
})

# 获取数据源 ID（从列表查找）
ds_list = api_request('/jmreport/getDataSourceByPage')
ds_id = next(ds['id'] for ds in ds_list['result']['records'] if ds['name'] == 'elasticsearch_test')

# Step 3: 创建空报表
api_request('/jmreport/save', {...})

# Step 4: 解析 SQL（ES 9.x 可能失败）
try:
    parse_result = api_request('/jmreport/queryFieldBySql', {
        "sql": "select * from es.jm_demo", "dbSource": ds_id, "type": "0"
    })
    fields = parse_result['result']['fieldList']
except:
    # ES 9.x 兼容问题，手动构建 fieldList
    fields = [{"fieldName": "name", "fieldText": "name", "widgetType": "String", "orderNum": 1}, ...]

# Step 5: 保存数据集
api_request('/jmreport/saveDb', {
    "dbCode": "es_demo", "dbSource": ds_id,
    "dbDynSql": "select * from es.jm_demo", "fieldList": fields, ...
})

# Step 6: 保存报表设计
api_request('/jmreport/save', {...})
```

### 已知问题

| 问题 | ES 版本 | 说明 |
|------|---------|------|
| queryFieldBySql ClassCastException | 9.x | Calcite ES 适配器不兼容，手动构建 fieldList |
| 预览无数据 | 9.x | 同上，Calcite 运行时查询也可能失败 |
| 正常工作 | 7.x / 8.x | Calcite 适配器兼容良好 |
