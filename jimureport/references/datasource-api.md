# 数据源管理 API

积木报表数据源的增删改查接口，用于管理报表关联的数据库连接。

---

## 添加/编辑数据源

- **接口：** POST `/jmreport/addDataSource`
- **说明：** 编辑时 `id` 不为空，新增时 `id` 为空
- **请求参数：**

```json
{
    "id": "",
    "reportId": "1199136323694804992",
    "code": "",
    "name": "redis",
    "dbType": "redis",
    "dbDriver": "",
    "dbUrl": "127.0.0.1:6379",
    "dbUsername": "",
    "dbPassword": ""
}
```

- **返回结果：**

```json
{
    "success": true,
    "message": "操作成功！",
    "code": 200,
    "result": true,
    "timestamp": 1775011551379
}
```

---

## 测试数据源连接

- **接口：** POST `/jmreport/testConnection`
- **说明：** 测试数据源是否可以正常连接，不需要 id 和 reportId
- **请求参数：**

```json
{
    "dbType": "MYSQL5.7",
    "dbDriver": "com.mysql.cj.jdbc.Driver",
    "dbUrl": "jdbc:mysql://192.168.1.6:3306/jeecg-boot-cr?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false",
    "dbUsername": "root",
    "dbPassword": "123456"
}
```

- **返回结果：**

```json
{
    "success": true,
    "message": "数据库连接成功",
    "code": 200,
    "result": true,
    "timestamp": 1775013503383
}
```

---

## 获取数据源

- **接口：** GET `/jmreport/getDataSourceById?id=xxx`
- **返回结果：**

```json
{
    "success": true,
    "message": "",
    "code": 200,
    "result": {
        "id": "1194904892449841152",
        "code": "",
        "name": "mysql",
        "reportId": "1773998084122373187",
        "remark": null,
        "dbType": "MYSQL5.7",
        "dbDriver": "com.mysql.cj.jdbc.Driver",
        "dbUrl": "jdbc:mysql://127.0.0.1:3306/jimureport?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false",
        "dbUsername": "root",
        "dbPassword": "123456",
        "createBy": "jeecg",
        "createTime": "2026-03-20 17:32:17",
        "updateBy": "jeecg",
        "updateTime": "2026-03-20 17:33:29",
        "connectTimes": 0,
        "tenantId": "2",
        "type": "report",
        "withoutDbType": null,
        "dbChName": null
    },
    "timestamp": 1775011724929
}
```

---

## 分页查询数据源

- **接口：** GET `/jmreport/getDataSourceByPage?token=xxx&pageNo=1&pageSize=10`
- **说明：** 分页查询数据源列表，返回含 id、name、dbType、type 等基本信息（不含连接详情）
- **返回结果：**

```json
{
    "success": true,
    "message": "",
    "code": 200,
    "result": {
        "pageNo": 1,
        "pageSize": 10,
        "total": 25,
        "pages": 3,
        "records": [
            {
                "id": "1189365702421168128",
                "name": "客户pos",
                "dbType": "POSTGRESQL",
                "type": "report"
            }
        ]
    },
    "timestamp": 1775013768401
}
```

---

## 删除数据源

- **接口：** POST `/jmreport/delDataSource`
- **请求参数：**

```json
{
    "id": "1194904892449841152"
}
```

---

## 初始化数据源列表

- **接口：** GET `/jmreport/initDataSource?token=xxx`
- **说明：** 返回当前可用的所有数据源列表（仅含 id、name、type 等基本信息，不含连接详情）

---

## 支持的数据库类型及默认配置

> **规则：** 用户未提供 dbDriver 和 dbUrl 时，根据 dbType 使用下表的默认值填充。`other` 类型无默认值，需用户自行填写。

### SQL 类型

| dbType | label | 默认 dbDriver | 默认 dbUrl |
|--------|-------|---------------|-----------|
| MYSQL5.7 | MySQL5.7+ | `com.mysql.cj.jdbc.Driver` | `jdbc:mysql://127.0.0.1:3306/jimureport?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false` |
| MYSQL5.5 | MySQL5.5 | `com.mysql.jdbc.Driver` | `jdbc:mysql://127.0.0.1:3306/jimureport?characterEncoding=UTF-8&useUnicode=true&useSSL=false&serverTimezone=GMT%2B8&tinyInt1isBit=false` |
| TIDB | TIDB | `com.mysql.cj.jdbc.Driver` | `jdbc:mysql://127.0.0.1:4000/jimureport?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false` |
| ORACLE | Oracle | `oracle.jdbc.OracleDriver` | `jdbc:oracle:thin:@127.0.0.1:1521:ORCL` |
| SQLSERVER | SQLServer | `com.microsoft.sqlserver.jdbc.SQLServerDriver` | `jdbc:sqlserver://127.0.0.1:1433;SelectMethod=cursor;DatabaseName=jimureport` |
| POSTGRESQL | PostgreSQL | `org.postgresql.Driver` | `jdbc:postgresql://127.0.0.1:5432/jimureport` |
| MARIADB | MariaDB | `org.mariadb.jdbc.Driver` | `jdbc:mariadb://127.0.0.1:3306/jimureport?characterEncoding=UTF-8&useSSL=false` |
| dm | 达梦 | `dm.jdbc.driver.DmDriver` | `jdbc:dm://127.0.0.1:5236/?jimureport&zeroDateTimeBehavior=convertToNull&useUnicode=true&characterEncoding=utf-8` |
| kingbase8 | 人大金仓 | `com.kingbase8.Driver` | `jdbc:kingbase8://127.0.0.1:54321/jimureport` |
| oscar | 神通 | `com.oscar.Driver` | `jdbc:oscar://127.0.0.1:2003/jimureport` |
| DB2 | DB2 | `com.ibm.db2.jcc.DB2Driver` | `jdbc:db2://127.0.0.1:50000/jimureport` |
| Hsqldb | Hsqldb | `org.hsqldb.jdbc.JDBCDriver` | `jdbc:hsqldb:hsql://127.0.0.1/jimureport` |
| Derby | Derby | `org.apache.derby.jdbc.ClientDriver` | `jdbc:derby://127.0.0.1:1527/jimureport` |
| H2 | H2 | `org.h2.Driver` | `jdbc:h2:tcp://127.0.0.1:8082/~/jimureport` |
| CLICKHOUSE | CLICKHOUSE | `com.clickhouse.jdbc.ClickHouseDriver` | `jdbc:clickhouse://127.0.0.1:8123/default` |
| TDENGINE | TDengine | `com.taosdata.jdbc.TSDBDriver` | `jdbc:TAOS://127.0.0.1:6030/jmreport?timezone=UTC-8&charset=utf-8&serverTimezone=Asia/Shanghai` |
| Doris | Doris | `com.mysql.cj.jdbc.Driver` | `jdbc:mysql://127.0.0.1:9030/jimureport?useUnicode=true&characterEncoding=UTF-8&serverTimezone=GMT%2B8&tinyInt1isBit=false` |
| SQLite | SQLite | `org.sqlite.JDBC` | `jdbc:sqlite://opt/jimureport.db` |

### NoSQL 类型

| dbType | label | 默认 dbDriver | 默认 dbUrl |
|--------|-------|---------------|-----------|
| redis | Redis | _(空)_ | `127.0.0.1:6379` |
| mongodb | MongoDb | _(空)_ | `127.0.0.1:27017/test` |
| es | Elasticsearch | `/` | `127.0.0.1:9200` |

### 其他

| dbType | label | 默认 dbDriver | 默认 dbUrl |
|--------|-------|---------------|-----------|
| other | 其他数据库 | _(空，用户必须自行填写)_ | _(空，用户必须自行填写)_ |

---

## 创建/更新数据源操作流程

> **核心原则：先查重 → 再测试连接 → 最后保存。失败重试时走更新（传 id），禁止重复创建。**

### 流程步骤

```
0. 查重（防止重复创建）
   GET /jmreport/getDataSourceByPage?token=xxx&pageNo=1&pageSize=100
   ├── 按 name 匹配是否已存在同名数据源
   ├── 已存在 → 取其 id，走编辑模式（步骤 4 传 id）
   └── 不存在 → 走新增模式（步骤 4 id 为空）

1. 收集参数
   ├── 用户提供：name、dbType、dbUrl（可选）、dbUsername、dbPassword
   ├── 未提供 dbDriver/dbUrl → 根据 dbType 从「默认配置表」自动填充
   └── dbType 为 other → 用户必须提供 dbDriver 和 dbUrl

2. 调用测试连接接口
   POST /jmreport/testConnection
   {
       "dbType": "...",
       "dbDriver": "...",
       "dbUrl": "...",
       "dbUsername": "...",
       "dbPassword": "..."
   }

3. 判断测试结果
   ├── success: true → 进入步骤 4，直接保存
   └── success: false → 停止，向用户反馈：
       ├── 展示返回的 message（错误原因）
       ├── 分析可能原因（地址不对、端口不通、用户名密码错误、数据库不存在等）
       └── 提示用户需要补充或修正哪些信息

4. 调用保存接口
   POST /jmreport/addDataSource
   {
       "id": "已有id或空",  ← 编辑传已有 id，新增为空
       "reportId": "...",
       "code": "",
       "name": "...",
       "dbType": "...",
       "dbDriver": "...",
       "dbUrl": "...",
       "dbUsername": "...",
       "dbPassword": "..."
   }

5. 确认保存结果
   └── success: true → 完成，告知用户数据源已保存
```

> **重要：失败重试规则**
> - 创建数据源失败后重试，必须先查询是否已创建成功（按 name 查 getDataSourceByPage），已存在则传 id 走更新
> - 创建报表失败后重试，必须用同一 report_id 调用 save（save 传同一 id 即为更新）
> - **禁止**每次重试都生成新 id 或不传 id，否则会产生大量重复记录

### 常见连接失败原因及提示

| 场景 | 可能原因 | 应提示用户提供 |
|------|---------|--------------|
| 连接超时 | IP/端口不可达 | 确认数据库服务器地址和端口 |
| 认证失败 | 用户名或密码错误 | 正确的 dbUsername 和 dbPassword |
| 数据库不存在 | dbUrl 中的库名不对 | 确认数据库名称 |
| 驱动类找不到 | 服务端未引入对应驱动包 | 确认服务端是否支持该数据库类型 |
| URL 格式错误 | dbUrl 拼写/参数有误 | 确认完整的 JDBC 连接地址 |

---

## 数据集绑定数据源流程

> **场景：** 用户指定了数据源名称（如"用mysql数据源"），需要将数据源 id 绑定到数据集的 `dbSource` 字段。

### 流程步骤

```
1. 查询数据源列表
   GET /jmreport/initDataSource?token=xxx
   └── 返回所有可用数据源（含 id、name）

2. 按名称匹配
   ├── 找到匹配项 → 取其 id
   └── 未找到 → 提示用户可用的数据源列表，让用户重新选择

3. 绑定到数据集
   在数据集保存时，将匹配到的数据源 id 赋值给 dbSource 字段
   例如：
   {
       "dbCode": "db_demo",
       "dbSource": "1161942757348524032",  ← 数据源 id
       "dbType": "sql",
       "selectSql": "select * from demo"
   }
```

### 注意事项

- `dbSource` 存的是数据源的 **id**，不是 name
- 未指定数据源时 dbSource 为空，表示使用当前服务默认数据源
- 用户只说了数据源名称时，必须先通过 initDataSource 查到对应 id 再绑定

---

## Redis 数据集使用说明

> **核心：Redis 数据集本质上使用 SQL 数据集（dbType="0"），只是 dbSource 指向 Redis 数据源，dbDynSql 填写 Redis 的 key 名。**
>
> 参考文档：https://help.jimureport.com/dataSet/redis

### 使用流程

```
1. 添加 Redis 数据源
   POST /jmreport/addDataSource
   {
       "name": "my-redis",
       "dbType": "redis",
       "dbUrl": "127.0.0.1:6379",
       "dbUsername": "",
       "dbPassword": ""
   }

2. 创建数据集时，使用 SQL 数据集类型
   - dbType: "0"（SQL 数据集，不是 "redis"）
   - dbSource: Redis 数据源的 id
   - dbDynSql: 直接填 Redis 的 key 名（如 "json_demo"）

3. 调用 queryFieldBySql 解析字段
   POST /jmreport/queryFieldBySql
   {
       "sql": "json_demo",          ← Redis key 名
       "dbSource": "redis数据源id",  ← Redis 数据源 id
       "type": "0"
   }

4. saveDb 保存数据集
   {
       "dbType": "0",
       "dbSource": "redis数据源id",
       "dbDynSql": "json_demo",     ← Redis key 名
       "fieldList": [...],
       "paramList": []
   }
```

### 注意事项

- Redis 数据集**不使用** dbType="redis"，而是 dbType="0"（SQL 数据集）
- dbType="redis" 仅用于**数据源连接**（addDataSource），不用于数据集（saveDb）
- dbDynSql 中填写的是 Redis 的 key 名称，不是 SQL 语句
- Redis 中存储的数据必须是 JSON 格式，系统通过解析 JSON 结构自动识别字段
- 解析和保存流程与普通 SQL 数据集完全一致，只是 dbSource 指向 Redis 数据源

---

## MongoDB 数据集使用说明

> **核心：MongoDB 数据集同样使用 SQL 数据集（dbType="0"），dbSource 指向 MongoDB 数据源。推荐使用第二种方式（SQL 语法 + `mongo.` 前缀）。**
>
> 参考文档：https://help.jimureport.com/dataSet/mongo

### MongoDB 数据源配置

```
# 方式一：标准配置
dbUrl: 127.0.0.1:27017/test
dbUsername: admin
dbPassword: 123456

# 方式二：连接串配置（推荐，无需单独填用户名密码）
dbUrl: mongodb://admin:123456@127.0.0.1:27017/?authSource=test
dbUsername: （空）
dbPassword: （空）
```

### 两种查询方式

#### 方式一：MongoDB 原生查询语法

在 dbDynSql 中使用 `db.getCollection` 语法：

```javascript
// 基础查询
db.getCollection('user').find({})

// 条件查询
db.getCollection('user').find({name: '张三'})

// 模糊查询 + 条件
db.getCollection('user').find({name: /张/, age:{$gt:10}})

// 分页
db.getCollection('user').find({name: /张/}).limit(1)

// 排序
db.getCollection('user').find({name: /张/}).sort({age:-1})

// 排除 _id 字段
db.getCollection('design_form_list_view').find({}, {_id: 0})

// 只返回指定字段
db.getCollection('design_form_list_view').find({}, {'desform_code':1,'name':1})

// 带参数
db.getCollection('user').find({ name:${name}})
```

#### 方式二：SQL 语法 + `mongo.` 前缀（v1.9.2+，推荐）

> **推荐使用此方式。** 表名加 `mongo.` 前缀即可用标准 SQL 查询 MongoDB，支持分页、关联、分组、排序。

```sql
-- 基础查询
select * from mongo.user

-- 条件查询
select * from mongo.user where name = '${name}'

-- 分组统计
select category, count(*) as cnt from mongo.products group by category

-- 排序
select * from mongo.user order by age desc

-- 关联查询
select a.name, b.order_no from mongo.user a left join mongo.orders b on a.id = b.user_id
```

### 使用流程

```
1. 添加 MongoDB 数据源
   POST /jmreport/addDataSource
   {
       "name": "my-mongo",
       "dbType": "mongodb",
       "dbUrl": "mongodb://admin:123456@127.0.0.1:27017/?authSource=test",
       "dbUsername": "",
       "dbPassword": ""
   }

2. 创建数据集 — 使用 SQL 数据集类型
   - dbType: "0"（SQL 数据集）
   - dbSource: MongoDB 数据源的 id
   - dbDynSql: "select * from mongo.表名"（推荐方式二）

3. 调用 queryFieldBySql 解析字段
   POST /jmreport/queryFieldBySql
   {
       "sql": "select * from mongo.user",
       "dbSource": "mongo数据源id",
       "type": "0"
   }

4. saveDb 保存数据集（同普通 SQL 数据集）
```

### 注意事项

- MongoDB 数据集与 Redis 一样，**数据集 dbType 用 "0"（SQL）**，不是 "mongodb"
- `dbType: "mongodb"` 仅用于数据源连接（addDataSource）
- 推荐使用方式二（`mongo.` 前缀 SQL），语法更熟悉、支持更丰富（JOIN、GROUP BY 等）
- 方式二需要 JimuReport **v1.9.2+** 版本支持
- 带参数时与普通 SQL 一样使用 `${}` 占位符，解析时需替换默认值
- **自动补全规则：** 如果用户只提供了 MongoDB 集合名称（如 `user`），自动加上 `mongo.` 前缀生成 SQL：`select * from mongo.user`。不要让用户手动加前缀。
- **字段名含 `-` 必须过滤（会导致 FreeMarker 报错）：** MongoDB 返回的字段名可能含 `-`（如 `auto-number_xxx`、`file-upload_xxx`、`link-record_xxx`），**绝对不能**绑定到报表单元格中。原因：`#{cai_gou_dan.auto-number_xxx}` 会被 FreeMarker 解析为 `cai_gou_dan.auto` 减去 `number_xxx`，抛出 `NonNumericalException`/`InvalidReferenceException`。解析字段后必须：
  1. 从 fieldList 中删除所有 fieldName 含 `-` 或以 `_` 开头的字段
  2. 这些字段不绑定到报表 rows 中
  3. 不影响 SQL（仍用 `select *`），只是报表不显示这些字段
- **`mongo.` SQL 语法要求：** 数据源必须单独填写 dbUsername 和 dbPassword（不能用连接串方式内嵌账号密码），否则解析失败（`Failed to parse DataSourceConfig`）。如果用户使用连接串方式（`mongodb://user:pass@host`），自动降级为原生语法 `db.getCollection('集合名').find({})`
- 同时 `mongo.` SQL 语法需要 JimuReport **v1.9.2+** 版本支持

### MongoDB 踩坑记录（实战总结）

> 以下是实际创建 MongoDB 报表时遇到的问题，按严重程度排列。

#### 坑1：dbSource 传了数据源名称而不是 ID

**现象：** 数据集保存成功，但设计器中数据源下拉框不显示关联，预览时查不到数据。

**原因：** `saveDb` 的 `dbSource` 字段传了 `"mongodb"`（名称），而不是 `"1199218436288897024"`（ID）。API 不报错但无法正确关联。

**正确做法：**
```python
# 先查询数据源ID
ds_resp = api('/jmreport/getDataSourceByPage')
records = ds_resp['result']['records']
ds_id = next(r['id'] for r in records if r['name'] == 'mongodb')

# saveDb 时传 ID
{"dbSource": ds_id}  # ✅ "1199218436288897024"
{"dbSource": "mongodb"}  # ❌ 不会报错但不关联
```

#### 坑2：缺少 `mongo.` 前缀

**现象：** `queryFieldBySql` 返回 500 NPE 错误。

**原因：** SQL 写成 `select * from cai_gou_dan`，缺少 `mongo.` schema 前缀。

**正确做法：** `select * from mongo.cai_gou_dan`

#### 坑3：字段名含连字符 `-` 导致 FreeMarker 报错

**现象：** 预览报错 `Failed at: ${cai_gou_dan.auto - number_167171031...`

**原因：** MongoDB 集合字段名如 `auto-number_1671710310317_206584` 含有 `-`，FreeMarker 将 `-` 解析为减法运算符，导致 `cai_gou_dan.auto`（null）减去 `number_xxx`（未定义变量），抛出 `NonNumericalException`。

**正确做法：** 解析字段后过滤：
```python
def is_safe_field(fname):
    if '-' in fname: return False       # 连字符会被FreeMarker当减号
    if fname.startswith('_'): return False  # 下划线开头的系统字段
    return True

safe_fields = [f for f in field_list if is_safe_field(f['fieldName'])]
# 只用 safe_fields 保存到数据集和绑定到报表
```

#### 坑4：queryFieldBySql 脚本调用失败但 UI 正常

**现象：** 通过 Python 脚本调用 `queryFieldBySql`（传 `dbSource: "mongodb"` 名称）返回 500 NPE，但在设计器 UI 中同样的 SQL 解析成功。

**原因：** UI 传的 `dbSource` 是数据源 **ID**，脚本传的是名称。签名计算基于参数值，参数值不同导致服务端走了不同的代码路径。

**正确做法：** `dbSource` 始终传数据源 ID，与 UI 行为保持一致。

---

## 数据源 CRUD 操作实战示例

> **通用规则：有多个同名数据源时，取 id 最大的（雪花ID越大越新）。**

### 修改数据源名称

```python
# 1. 按 name 查找数据源
list_r = api_request(f'/jmreport/getDataSourceByPage?token={TOKEN}&pageNo=1&pageSize=100')
matched = [r for r in list_r['result']['records'] if r.get('name') == '原名称']

# 2. 多条时取最新的（id最大）
target = max(matched, key=lambda x: x['id'])

# 3. 获取完整详情（分页查询不含连接信息）
detail = api_request(f'/jmreport/getDataSourceById?id={target["id"]}')['result']

# 4. 修改名称并保存（传 id = 编辑模式）
api_request('/jmreport/addDataSource', {
    "id": detail['id'],           # 传 id → 编辑
    "reportId": detail.get('reportId', ''),
    "code": detail.get('code', ''),
    "name": "新名称",              # 修改的字段
    "dbType": detail['dbType'],
    "dbDriver": detail['dbDriver'],
    "dbUrl": detail['dbUrl'],
    "dbUsername": detail['dbUsername'],
    "dbPassword": detail['dbPassword']
})
```

### 删除数据源

```python
# 1. 按 name 查找
list_r = api_request(f'/jmreport/getDataSourceByPage?token={TOKEN}&pageNo=1&pageSize=100')
matched = [r for r in list_r['result']['records'] if r.get('name') == '目标名称']

# 2. 多条时取最新的
target = max(matched, key=lambda x: x['id'])

# 3. 删除
api_request('/jmreport/delDataSource', {"id": target['id']})
```

### 创建数据源（含查重）

```python
# 1. 先查重
list_r = api_request(f'/jmreport/getDataSourceByPage?token={TOKEN}&pageNo=1&pageSize=100')
matched = [r for r in list_r['result']['records'] if r.get('name') == '数据源名称']

if matched:
    # 已存在 → 走编辑模式
    existing_id = max(matched, key=lambda x: x['id'])['id']
else:
    existing_id = ""

# 2. 测试连接
test_r = api_request('/jmreport/testConnection', {
    "dbType": "MYSQL5.7", "dbDriver": "com.mysql.cj.jdbc.Driver",
    "dbUrl": "jdbc:mysql://...", "dbUsername": "root", "dbPassword": "123456"
})

# 3. 保存（id 有值=更新，空=新增）
api_request('/jmreport/addDataSource', {
    "id": existing_id,
    "reportId": "", "code": "",
    "name": "数据源名称", "dbType": "MYSQL5.7",
    "dbDriver": "com.mysql.cj.jdbc.Driver",
    "dbUrl": "jdbc:mysql://...",
    "dbUsername": "root", "dbPassword": "123456"
})
```

### getDataSourceByPage 签名注意

> `getDataSourceByPage` 是需要签名的 GET 接口。签名时必须用 URL 中的查询参数（token、pageNo、pageSize）计算签名，不能传空 dict。

```python
# GET 请求签名：从 URL query 参数中提取签名参数
if '?' in path:
    sign_params = {}
    for param in path.split('?', 1)[1].split('&'):
        k, v = param.split('=', 1)
        sign_params[k] = v
    headers['X-Sign'] = compute_sign(sign_params)
```
