# 数据集的用法

所有接口均需要提供token

## 数据源管理

数据集默认使用应用本身的数据库。如需连接外部数据库，需要先添加数据源，再在数据集中通过 `dbSource` 关联。

### 查询已有数据源

- **地址**：`GET /jmreport/getDataSourceByPage`
- **返回**：所有数据源列表，每个包含 `id` 和 `name`

```python
ds_resp = api_request('/jmreport/getDataSourceByPage')
ds_list = ds_resp.get('result', [])
# 按名称查找数据源 ID
ds_map = {ds['name']: ds['id'] for ds in ds_list}
# 示例: ds_map['ws_mysql'] -> '1010703895600087040'
```

### 添加/编辑数据源

- **地址**：`POST /jmreport/addDataSource`
- **新增不传 id，编辑传 id**
- **请求参数**：

```json
{
    "id": "",
    "reportId": "报表ID",
    "code": "",
    "name": "mysql",
    "dbType": "MYSQL5.7",
    "dbDriver": "com.mysql.cj.jdbc.Driver",
    "dbUrl": "jdbc:mysql://127.0.0.1:3306/jimureport?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false",
    "dbUsername": "root",
    "dbPassword": "123456"
}
```

| 字段 | 说明 |
|------|------|
| `id` | 数据源ID，新增不传，编辑传已有ID |
| `reportId` | 关联的报表ID |
| `name` | 数据源名称 |
| `dbType` | 数据库类型（如 `MYSQL5.7`、`ORACLE`、`POSTGRESQL` 等） |
| `dbDriver` | JDBC驱动类名 |
| `dbUrl` | JDBC连接URL |
| `dbUsername` | 数据库用户名 |
| `dbPassword` | 数据库密码 |

### 数据源与数据集的关联

数据集通过 `dbSource` 字段关联数据源，值为数据源的 `id`：

```json
{
    "dbCode": "aa",
    "dbType": "0",
    "dbDynSql": "select name from demo",
    "dbSource": "1010703895600087040",
    "dbSourceType": "mysql"
}
```

| 字段 | 说明 |
|------|------|
| `dbSource` | 数据源ID（`addDataSource` 返回或编辑时传入的 `id`）。空字符串 `""` = 使用默认数据源 |
| `dbSourceType` | 数据库类型（`mysql`、`oracle` 等），后端会自动识别，也可手动指定 |

**注意：** 如果开启了数据源安全模式（`firewall.dataSourceSafe: true`），SQL 数据集**必须**指定 `dbSource`，不允许使用默认数据源。

## SQL数据集

### SQL语句用法

- 如果id字段为字符串类型则需要加单引号：`select * from table where id='${id}'`
- 您可以编写`${id}`做为一个参数，这里id是参数的名称。例如：`select * from table where id='${id}'`
- 您可以编写`#{sysUserCode}`做为一个系统变量，这里sysUserCode是当前登录人。例如：`select * from table where create_by='#{sysUserCode}'`
- 您可以编写存储过程`CALL proc_sys_role(${pageNo}, ${pageSize})`，CALL为开启存储过程
- MongoDB和Elasticsearch支持sql语句，表名需要增加数据库标识（MongoDB：mongo，Elasticsearch：es）。例如：`select * from mongo.table`

### SQL解析接口

- **地址**：`POST /jmreport/queryFieldBySql`
- **请求参数**：
```json
{
    "sql": "select * from test_order_product where order_fk_id = ${order_fk_id}",
    "type": "0",
    "paramArray": "[{\"id\":\"1047395275108601856\",\"jimuReportHeadId\":\"1047395274039054336\",\"paramName\":\"order_fk_id\",\"paramTxt\":\"order_fk_id\",\"paramValue\":\"1\",\"orderNum\":1,\"createBy\":\"admin\",\"createTime\":\"2025-02-06 16:21:43\",\"updateBy\":null,\"updateTime\":null,\"searchFlag\":0,\"widgetType\":null,\"searchMode\":null,\"dictCode\":null,\"searchFormat\":null,\"extJson\":\"\",\"tableIndex\":1,\"_index\":0,\"_rowKey\":105}]"
}
```
- **返回结果**：
```json
{
    "success": true,
    "message": "解析成功",
    "code": 200,
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

## API数据集

### API数据集用法

- 如果id字段为字符串类型则需要加单引号：`http://127.0.0.1:8080/jeecg-boot/jimureport/test?id=${id}`
- 您可以编写`#{sysDateTime}`做为一个系统变量，这里sysDateTime是当前系统时间。例如：`http://127.0.0.1:8080/jeecg-boot/jimureport/test?riqi=#{sysDateTime}`
- 您可以简写访问路径，如：`#{domainURL}/jimureport/test/getList`

### API解析接口

- **地址**：`POST /jmreport/executeSelectApi`
- **请求参数**：
```json
{
    "api": "http://localhost:8085/jimureport/test/getList?pid=&name=",
    "method": "0",
    "paramArray": "[{\"id\":\"1066517440772788224\",\"jimuReportHeadId\":\"1066517440441438208\",\"paramName\":\"pid\",\"paramTxt\":null,\"paramValue\":\"\",\"orderNum\":1,\"createBy\":\"admin\",\"createTime\":\"2025-03-31 10:46:23\",\"updateBy\":null,\"updateTime\":null,\"searchFlag\":0,\"widgetType\":null,\"searchMode\":null,\"dictCode\":\"\",\"searchFormat\":null,\"extJson\":\"\",\"tableIndex\":1,\"_index\":0,\"_rowKey\":231}]"
}
```
- **返回结果**：
```json
{
    "success": true,
    "message": "",
    "code": 200,
    "result": [
        {
            "fieldName": "ctotal",
            "fieldText": "ctotal",
            "widgetType": "String",
            "isShow": true,
            "orderNum": 1
        }
    ]
}
```

## JSON数据集

自动将data中的字段解析成fieldName/fieldText/widgetType格式。

- **输入格式**：
```json
{
    "data": [
        {
            "ctotal": "125箱",
            "cname": "牛奶0",
            "cprice": "56",
            "riqi": "2022年10月21日",
            "id": "1",
            "dtotal": "1256箱",
            "tp": "7000",
            "ztotal": "589箱",
            "cnum": "每箱12瓶"
        }
    ]
}
```

## JavaBean数据集

- **地址**：`POST /jmreport/queryFieldByBean`
- **请求参数**：
```json
{
    "javaType": "spring-key",
    "javaValue": "testRpSpringBean",
    "isPage": false,
    "param": {}
}
```
- **返回结果**：
```json
{
    "success": true,
    "message": "解析成功",
    "code": 200,
    "result": [
        {
            "fieldName": "name",
            "fieldText": "name",
            "widgetType": "String",
            "orderNum": 1
        }
    ]
}
```

## 查询已有数据集

更新数据集前必须先查到已有数据集的 `dbId`，流程如下：

### Step 1: 获取数据集列表（含 dbId）

- **地址**：`GET /jmreport/field/tree/{reportId}`
- **返回结构**：

```json
{
    "result": [
        [
            {
                "code": "userlist",
                "dbId": "1194900477760331776",
                "title": "用户列表",
                "type": "0",
                "isList": "1",
                "izSharedSource": 0,
                "children": [
                    {"title": "username", "fieldText": "username"},
                    {"title": "realname", "fieldText": "realname"}
                ]
            }
        ]
    ]
}
```

**提取 dbCode → dbId 映射：**
```python
tree = api_request(f'/jmreport/field/tree/{report_id}')
db_map = {}  # dbCode -> dbId
for group in tree.get('result', []):
    if group and len(group) > 0:
        info = group[0]
        db_map[info['code']] = info['dbId']
```

### Step 2: 获取单个数据集详情

- **地址**：`GET /jmreport/loadDbData/{dbId}?reportId={reportId}`
- **返回结构**：`result` 包含三个顶层字段：

```json
{
    "result": {
        "dbId": "数据集ID",
        "reportDb": {
            "id": "数据集ID",
            "dbCode": "userlist",
            "dbDynSql": "SELECT ... FROM ...",
            "dbSource": "1010703895600087040",
            "dbSourceType": "mysql",
            "isPage": "1",
            "isList": "1"
        },
        "fieldList": [...],
        "paramList": [...]
    }
}
```

> **注意：`dbDynSql` 和 `dbSource` 在 `result.reportDb` 中，不在 `result` 顶层。**

```python
detail = api_request(f'/jmreport/loadDbData/{db_id}?reportId={report_id}').get('result', {})
report_db = detail.get('reportDb', {})
existing_sql = report_db.get('dbDynSql', '')
existing_db_source = report_db.get('dbSource', '')
existing_fields = detail.get('fieldList', [])
existing_params = detail.get('paramList', [])
```

### Step 3: 查询参数列表

- **地址**：`GET /jmreport/getListReportDb?reportId={reportId}`
- **返回**：每个 dbCode 对应的参数列表

```json
{"result": {"reportDbParam": {"userlist": [{"paramName": "username", ...}], "userpie": []}}}
```

## 保存或修改数据集

**新增不传 id，更新必须传 id。** 后端 `saveOrUpdate` 逻辑：有 id 则更新，无 id 则新增。

- **地址**：`POST /jmreport/saveDb`
- **请求参数**：
```json
{
    "id": "1193767090018410496",
    "izSharedSource": 0,
    "jimuReportId": "1193766682428530688",
    "dbCode": "aa",
    "dbChName": "aa",
    "dbType": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "jimuSharedSourceId": null,
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from demo",
    "fieldList": [
        {
            "id": "1193767090198765568",
            "jimuReportDbId": "1193767090018410496",
            "fieldName": "id",
            "fieldText": "id",
            "widgetType": "String",
            "widgetWidth": null,
            "orderNum": 0,
            "searchFlag": null,
            "searchMode": null,
            "searchValue": null,
            "dictCode": "",
            "createBy": "admin",
            "createTime": "2026-03-17 14:11:04",
            "updateBy": null,
            "updateTime": null,
            "searchFormat": null,
            "extJson": "",
            "fieldNamePhysics": null,
            "tableIndex": 1,
            "_index": 0,
            "_rowKey": 44
        }
    ],
    "paramList": []
}
```
- **返回结果**：
```json
{
    "success": true,
    "message": "",
    "code": 200,
    "result": {
        "id": "1193767090018410496",
        "jimuReportId": "1193766682428530688",
        "dbCode": "aa",
        "dbChName": "aa",
        "dbType": "0",
        "dbDynSql": "select * from demo",
        "fieldList": [],
        "paramList": [],
        "isPage": "1",
        "isList": "1",
        "dbSource": "",
        "dbSourceType": "mysql",
        "createBy": "admin",
        "updateBy": "admin",
        "createTime": "2026-03-19 17:12:34",
        "updateTime": "2026-03-19 17:12:34",
        "apiConvert": "",
        "izSharedSource": 0,
        "jimuSharedSourceId": null
    }
}
```

### dbType 值说明

| dbType | 类型 | 关键字段 |
|--------|------|----------|
| `"0"` | SQL数据集 | `dbDynSql` |
| `"1"` | API数据集 | `apiUrl` + `apiMethod` |
| `"2"` | JavaBean数据集 | `javaType` + `javaValue` |
| `"3"` | JSON数据集 | `jsonData` |
| `"4"` | 共享数据集 | — |
| `"5"` | 多文件数据集 | — |
| `"6"` | 单文件数据集 | — |
