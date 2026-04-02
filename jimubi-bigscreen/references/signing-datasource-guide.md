# API 接口签名机制与数据源管理

## API 接口签名机制（@SignatureValidation）

部分接口（如 `queryFieldBySql`、`queryFileFieldBySql`、`getMapDataByCode` 等）带有 `@SignatureValidation` 注解，需要在请求头中携带签名，否则返回 `签名验证失败: 时间戳为空`。

**签名源码位置：** `packages/utils/encryption/signMd5Utils.js` + `packages/utils/http/request.js`

### 签名算法（Python 实现）

```python
import hashlib, json, time

SIGNATURE_SECRET = 'dd05f1c54d63749eda95f9fa6d49v442a'

def get_sign(url_path, params=None):
    json_obj = {}
    if '?' in url_path:
        qs = url_path.split('?', 1)[1]
        for kv in qs.split('&'):
            if '=' in kv:
                k, v = kv.split('=', 1)
                json_obj[k] = v
    if params:
        for k, v in params.items():
            if isinstance(v, (int, float)):
                v = str(v)
            json_obj[k] = v
    json_obj.pop('_t', None)
    sorted_obj = dict(sorted(json_obj.items()))
    sign_str = json.dumps(sorted_obj, ensure_ascii=False, separators=(',', ':')) + SIGNATURE_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def get_vsign(data, sign):
    json_obj = dict(data) if data and isinstance(data, dict) else {}
    json_obj['sign'] = sign
    sign_param_obj = {k: v for k, v in json_obj.items() if v and isinstance(v, str)}
    sorted_obj = dict(sorted(sign_param_obj.items()))
    sign_str = json.dumps(sorted_obj, ensure_ascii=False, separators=(',', ':')) + SIGNATURE_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
```

### 请求头

```python
headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Access-Token': TOKEN,
    'X-TIMESTAMP': str(int(time.time() * 1000)),
    'X-Sign': get_sign(path, params),
    'V-Sign': get_vsign(data, sign),
}
```

### 需要签名的接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/drag/onlDragDatasetHead/queryFieldBySql` | POST | 解析 SQL 字段 |
| `/drag/onlDragDatasetHead/queryFileFieldBySql` | POST | 解析文件数据集 SQL 字段 |
| `/drag/onlDragDatasetHead/queryAllById` | GET | 查询数据集详情 |
| `/drag/onlDragDatasetHead/getDictByCodes` | GET | 获取字典数据 |
| `/drag/onlDragDatasetHead/getMapDataByCode` | GET | 获取地图数据 |
| `/drag/onlDragDatasetHead/getDataForDesign` | POST | 设计页面获取数据 |
| `/drag/onlDragDatasetHead/getTotalData` | POST | 预览页面获取数据 |
| `/drag/onlDragDatasetHead/getTotalDataByCompId` | POST | 按组件ID获取数据 |
| `/drag/onlDragDatasetHead/generateChartSse` | GET | AI 生成图表 |
| `/drag/onlDragDatasetHead/updateChartOptSse` | GET | AI 修改组件配置 |
| `/drag/onlDragDatasetHead/generateSqlSse` | GET | AI 生成SQL |
| `/drag/page/addVisitsNumber` | GET | 增加访问次数 |

> **不需要签名的接口**：`/drag/onlDragDatasetHead/add`、`/drag/onlDragDatasetHead/getAllChartData`、`/drag/onlDragDatasetHead/queryFieldByApi`、`/drag/onlDragDataSource/add`、`/drag/onlDragDataSource/edit`、`/drag/onlDragDataSource/testConnection`、`/drag/page/add`、`/drag/page/edit`、`/drag/page/queryById` 等。

---

## 数据源管理

### 数据源 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/drag/onlDragDataSource/add` | POST | 新增数据源（需 Shiro 权限，不需签名） |
| `/drag/onlDragDataSource/edit` | POST | 编辑数据源 |
| `/drag/onlDragDataSource/delete?id=xxx` | DELETE | 删除数据源 |
| `/drag/onlDragDataSource/queryById?id=xxx` | GET | 查询数据源详情 |
| `/drag/onlDragDataSource/getOptions` | GET | 获取数据源下拉列表 |
| `/drag/onlDragDataSource/testConnection` | POST | 测试连接 |

### 已适配数据库类型（dbTypeOption）

| 数据库 | dbType | dbDriver | 默认端口 |
|--------|--------|----------|---------|
| MySQL 5.5 | MYSQL5.5 | com.mysql.jdbc.Driver | 3306 |
| MySQL 5.7+ | MYSQL5.7 | com.mysql.cj.jdbc.Driver | 3306 |
| Oracle | ORACLE | oracle.jdbc.OracleDriver | 1521 |
| SQLServer | SQLSERVER | com.microsoft.sqlserver.jdbc.SQLServerDriver | 1433 |
| PostgreSQL | POSTGRESQL | org.postgresql.Driver | 5432 |
| 达梦 | dm | dm.jdbc.driver.DmDriver | 5236 |
| 人大金仓 | kingbase8 | com.kingbase8.Driver | 54321 |
| MariaDB | MARIADB | org.mariadb.jdbc.Driver | 3306 |
| TIDB | TIDB | com.mysql.cj.jdbc.Driver | 4000 |
| DB2 | DB2 | com.ibm.db2.jcc.DB2Driver | 50000 |
| Doris | Doris | com.mysql.cj.jdbc.Driver | 9030 |
| SQLite | SQLite | org.sqlite.JDBC | - |
| MongoDB | mongodb | (无) | 27017 |
| Redis | redis | (无) | 6379 |
| Elasticsearch | es | / | 9200 |

### JDBC URL 模板（常用）

```
MySQL 5.7+:  jdbc:mysql://host:3306/db?characterEncoding=UTF-8&useUnicode=true&useSSL=false&tinyInt1isBit=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai
Oracle:      jdbc:oracle:thin:@host:1521:ORCL
SQLServer:   jdbc:sqlserver://host:1433;SelectMethod=cursor;DatabaseName=db
PostgreSQL:  jdbc:postgresql://host:5432/db
达梦:        jdbc:dm://host:5236/?db&zeroDateTimeBehavior=convertToNull&useUnicode=true&characterEncoding=utf-8
```

### 创建新数据源完整流程

```python
ds_result = bi_utils._request('POST', '/drag/onlDragDataSource/add', data={
    'name': '业务数据源',
    'code': 'biz_ds',
    'dbType': 'MYSQL5.7',
    'dbDriver': 'com.mysql.cj.jdbc.Driver',
    'dbUrl': 'jdbc:mysql://192.168.1.66:3306/mydb?characterEncoding=UTF-8&useUnicode=true&useSSL=false&tinyInt1isBit=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai',
    'dbUsername': 'root',
    'dbPassword': 'root',
    'type': 'drag'
})
ds_id = ds_result['result']  # 返回的是数据源 ID 字符串

test = bi_utils._request('POST', '/drag/onlDragDataSource/testConnection', data={
    'id': ds_id,
    'dbType': 'MYSQL5.7',
    'dbDriver': 'com.mysql.cj.jdbc.Driver',
    'dbUrl': '...',
    'dbUsername': 'root',
    'dbPassword': 'root'
})
```

### 解析 SQL 获取字段（需签名）

```python
parse_result = signed_request('POST', '/drag/onlDragDatasetHead/queryFieldBySql', data={
    'sql': 'select id, name, age from my_table where 1=1',
    'dbCode': ds_id,
    'paramArray': []
})
# 返回: result.fieldList = [{fieldName, fieldTxt, fieldType}, ...]
```

> **注意**：`queryFieldBySql` 有 SQL 注入检查，不能使用 `information_schema` 等系统表查询。

---

## NoSQL 数据源（MongoDB / Elasticsearch / Redis）

> **参考文档：** https://help.jimureport.com/biScreen/base/data/Nosql

### NoSQL 数据源类型

| 数据库 | dbType | dbDriver | dbUrl 格式 | 默认端口 |
|--------|--------|----------|-----------|---------|
| MongoDB | `mongodb` | `''`（空字符串） | `host:port/database` | 27017 |
| Elasticsearch | `es` | `''`（空字符串） | `host:port` | 9200 |
| Redis | `redis` | `''`（空字符串） | `host:port` | 6379 |

**关键区别：** NoSQL 数据源的 `dbUrl` **不带** `jdbc:` 或 `mongodb://` 前缀，直接写 `host:port/database`。`dbDriver` 为空字符串。

### 创建 MongoDB 数据源

```python
# 连接串：mongodb://jeecg:123456@192.168.1.188:27017/jeecg
# dbUrl 只取 host:port/database 部分
ds_result = bi_utils._request('POST', '/drag/onlDragDataSource/add', data={
    'name': 'MongoDB数据源',
    'code': 'mongodb_jeecg',
    'dbType': 'mongodb',
    'dbDriver': '',          # NoSQL 无驱动类
    'dbUrl': '192.168.1.188:27017/jeecg',  # 不带 mongodb:// 前缀
    'dbUsername': 'jeecg',
    'dbPassword': '123456',
})
ds_id = ds_result['result']  # 返回数据源 ID 字符串
```

**datasource_ops.py 命令行：**
```bash
py datasource_ops.py create $API_BASE $TOKEN \
  --name "MongoDB数据源" --code "mongodb_jeecg" \
  --db-type mongodb --host 192.168.1.188 --port 27017 --db jeecg \
  --user jeecg --password 123456
```

### NoSQL 数据集 SQL 语法

NoSQL 数据集使用标准 SQL 语句查询，**表名需加数据库标识前缀**：

| 数据库 | 前缀 | SQL 示例 |
|--------|------|---------|
| MongoDB | `mongo.` | `select * from mongo.collection_name` |
| Elasticsearch | `es.` | `select * from es.index_name` |

**支持标准 SQL 功能**：分页（LIMIT）、关联（JOIN）、分组（GROUP BY）、排序（ORDER BY）、条件过滤（WHERE）。

**创建 MongoDB SQL 数据集示例：**
```python
ds_dataset = bi_utils._request('POST', '/drag/onlDragDatasetHead/add', data={
    'name': 'MongoDB客户数据',
    'code': 'mongo_customer',
    'dataType': 'sql',
    'dbSource': ds_id,       # MongoDB 数据源 ID
    'querySql': 'select * from mongo.ke_hu_guan_li_ly5o',
    'apiMethod': 'GET',
    'parentId': '0',
    'datasetItemList': [
        {'fieldName': 'name', 'fieldTxt': '姓名', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 0},
        {'fieldName': 'phone', 'fieldTxt': '电话', 'fieldType': 'String', 'izShow': 'Y', 'orderNum': 1},
    ],
    'datasetParamList': []
})
dataset_id = ds_dataset['result']['id']
```

**comp_ops.py 一键创建（数据集 + 组件）：**
```bash
# 需先通过 datasource_ops.py list 获取 MongoDB 数据源 ID
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID \
  --comp "JCommonTable" --title "MongoDB数据表格" --x 50 --y 280 --w 900 --h 450 \
  --create-sql "select * from mongo.demo_expend" \
  --ds-name "demo_expend数据" \
  --db-source "$MONGO_DS_ID" \
  --fields "id:String,name:String,amount:String,create_time:String"
```

### NoSQL 已知问题

| 问题 | 说明 |
|------|------|
| **queryFieldBySql 字段解析失败** | MongoDB 数据源调用 `queryFieldBySql` 可能报 `NoSuchMethodError: listCollectionNames()`，这是后端 MongoDB Java Driver 版本与服务端不兼容导致。**解决方案：** 跳过字段自动解析，手动指定 `datasetItemList` 字段列表 |
| **getAllChartData 查询失败** | 同上驱动兼容性问题。需升级后端 `mongo-java-driver` 或 `mongodb-driver-sync` 依赖版本 |
| **NoSQL 数据源不支持测试连接** | 前端 `isNoSql=true` 时隐藏「测试」按钮，API 层面 testConnection 也不适用于 NoSQL |
| **dbUrl 不带协议前缀** | MongoDB 用 `host:port/db`（不是 `mongodb://host:port/db`），Redis 用 `host:port`（不是 `redis://host:port`） |
