# API接口与数据集参考

积木报表所有 API 接口、签名机制、数据集 CRUD 操作的完整参考。

---

## 1. 接口签名机制

部分接口使用 `@JimuSignature` 注解，调用时需要签名。

### 需要签名的接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/jmreport/queryFieldBySql` | POST | SQL解析获取字段 |
| `/jmreport/executeSelectApi` | POST | API数据集解析 |
| `/jmreport/loadTableData` | POST | 加载表数据 |
| `/jmreport/testConnection` | POST | 测试数据源连接 |
| `/jmreport/download/image` | GET | 下载图片 |
| `/jmreport/dictCodeSearch` | GET | 字典编码搜索 |
| `/jmreport/getDataSourceByPage` | GET | 分页查询数据源 |
| `/jmreport/getDataSourceById` | GET | 按ID查询数据源 |

### 不需要签名的接口

`/jmreport/save`、`/jmreport/saveDb`、`/jmreport/get/{id}`、`/jmreport/field/tree/{reportId}`、`/jmreport/loadDbData/{dbId}`、`/jmreport/source/getJmReportSharedDbPageList`、`/jmreport/source/linkJmReportShareDb`、`/jmreport/source/delShareDbByDbId`

### 签名算法

```
1. 收集所有请求参数（URL query + POST body）
2. 按 key 字母升序排序
3. 转为 JSON 字符串（无空格）: json.dumps(sorted_dict, separators=(',', ':'))
4. 拼接密钥: jsonStr + "dd05f1c54d63749eda95f9fa6d49v442a"
5. MD5 并转大写
```

**默认签名密钥：** `dd05f1c54d63749eda95f9fa6d49v442a`（第29位是字母 `v`）
**时间戳有效期：5 分钟**

### 请求 Headers

| Header | 值 |
|--------|------|
| `X-Sign` | MD5签名（大写） |
| `X-TIMESTAMP` | 当前时间戳（毫秒） |

### 参数值类型转换

- 数字 → 字符串（`0` → `"0"`）
- 布尔 → 字符串（`false` → `"false"`）
- 对象/数组 → JSON字符串
- null/空 → 不参与签名

### Python 实现

```python
import hashlib, json, time

SIGNATURE_SECRET = "dd05f1c54d63749eda95f9fa6d49v442a"

def compute_sign(params_dict):
    str_params = {}
    for k, v in params_dict.items():
        if v is None: continue
        if isinstance(v, bool): str_params[k] = str(v).lower()
        elif isinstance(v, (int, float)): str_params[k] = str(v)
        elif isinstance(v, (dict, list)): str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else: str_params[k] = str(v)
    sorted_params = dict(sorted(str_params.items()))
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))
    return hashlib.md5((params_json + SIGNATURE_SECRET).encode('utf-8')).hexdigest().upper()

def get_sign_headers(params_dict):
    return {'X-Sign': compute_sign(params_dict), 'X-TIMESTAMP': str(int(time.time() * 1000))}
```

### 完整 API 请求函数

```python
def api_request(path, data=None, method=None):
    url = f'{API_BASE}{path}'
    headers = {'X-Access-Token': TOKEN, 'Content-Type': 'application/json; charset=UTF-8'}
    SIGNED_ENDPOINTS = ['/jmreport/queryFieldBySql', '/jmreport/executeSelectApi',
        '/jmreport/loadTableData', '/jmreport/testConnection', '/jmreport/download/image',
        '/jmreport/dictCodeSearch', '/jmreport/getDataSourceByPage', '/jmreport/getDataSourceById']
    need_sign = any(path.rstrip('/').endswith(ep.rstrip('/')) for ep in SIGNED_ENDPOINTS)
    if need_sign:
        headers['X-TIMESTAMP'] = str(int(time.time() * 1000))
        headers['X-Sign'] = compute_sign(data if data else {})
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method or 'POST')
    else:
        req = urllib.request.Request(url, headers=headers, method=method or 'GET')
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))
```

### 常见签名错误

| 错误信息 | 原因 |
|---------|------|
| `签名验证失败: 签名参数不存在` | 未传 X-Sign 或 X-TIMESTAMP |
| `签名验证失败:X-TIMESTAMP已过期` | 时间差超过5分钟 |
| `签名校验失败，参数有误！` | 参数排序/JSON格式/密钥不对 |

---

## 2. 数据源管理

### 查询已有数据源

`GET /jmreport/getDataSourceByPage`（需签名）

```python
ds_resp = api_request('/jmreport/getDataSourceByPage')
ds_map = {ds['name']: ds['id'] for ds in ds_resp.get('result', [])}
```

### 添加/编辑数据源

`POST /jmreport/addDataSource`（新增不传 id，编辑传 id）

```json
{
    "id": "", "reportId": "报表ID", "name": "mysql",
    "dbType": "MYSQL5.7", "dbDriver": "com.mysql.cj.jdbc.Driver",
    "dbUrl": "jdbc:mysql://127.0.0.1:3306/jimureport?...",
    "dbUsername": "root", "dbPassword": "123456"
}
```

数据集通过 `dbSource` 字段关联数据源ID。

> 如果开启数据源安全模式（`firewall.dataSourceSafe: true`），SQL数据集必须指定 `dbSource`。

---

## 3. SQL数据集

### SQL语句用法

- 参数：`select * from table where id='${id}'`
- 系统变量：`select * from table where create_by='#{sysUserCode}'`
- 存储过程：`CALL proc_sys_role(${pageNo}, ${pageSize})`

### 存储过程数据集

存储过程使用 **SQL 数据集（dbType="0"）**，SQL 语句以 `CALL` 开头。

**基本语法：**
```sql
CALL 存储过程名(参数1, 参数2, ...)
```

**参数写法：**
- 字符串参数需要单引号包围：`CALL jmdemo('${name}')`
- 数值参数无需引号：`CALL proc_page(${pageNo}, ${pageSize})`
- 多个参数用逗号分隔

**Oracle 存储过程（需输出游标）：**

Oracle 存储过程需要 `sys_refcursor` 输出游标，`?` 占位符放在括号最后：
```sql
CALL jmtest('${sex}', ?)
```

对应 Oracle 存储过程定义：
```sql
CREATE OR REPLACE procedure jmtest(
  xb in VARCHAR2,
  out_result_cursor out sys_refcursor
) is
begin
  open out_result_cursor for
    select ID, NAME, SEX from demo where SEX = xb;
end;
```

**API 调用步骤（以 `CALL jmdemo('${nameStr}')` 为例）：**

```
Step 1: save(空报表)          → 获取 report_id
Step 2: queryFieldBySql       → 解析存储过程字段（关键：必须用具体值替换参数）
Step 3: saveDb                → 保存数据集（SQL 写回原始参数化语句）
Step 4: save(完整设计)        → 保存报表 jsonStr
```

**Step 2 关键：参数必须用具体值替换后才能解析**

存储过程的 `${param}` 参数在 `queryFieldBySql` 中无法自动解析。必须将参数替换为具体值，用硬编码 SQL 调用解析接口：

```python
# ❌ 错误：带 ${} 参数直接解析 → 返回 code:1001 "结果为空"
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": "CALL jmdemo('${nameStr}')", "dbSource": "", "type": "0"
})  # → success=False, code=1001

# ✅ 正确：用具体值替换参数后解析
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": "CALL jmdemo('张三')", "dbSource": "", "type": "0"
})  # → success=True, 返回 fieldList
```

> **注意：** 空字符串 `''` 可能导致存储过程返回空结果集，同样报 1001。建议用能返回数据的测试值（如 `'张三'`、`'%'` 等）。如果不确定用什么值，可以依次尝试多个：

```python
for test_val in ['%', 'test', '张三', '']:
    result = api_request('/jmreport/queryFieldBySql', {
        "sql": f"CALL jmdemo('{test_val}')", "dbSource": "", "type": "0"
    })
    if result['success'] and result.get('result'):
        field_list = result['result']['fieldList']
        break
```

**Step 3：saveDb 时写回原始参数化 SQL**

解析用具体值，但保存数据集时 `dbDynSql` 必须写回带 `${}` 的原始语句：

```python
db_data = {
    "dbType": "0",
    "dbCode": "emp",
    "dbDynSql": "CALL jmdemo('${nameStr}')",  # ← 原始参数化 SQL
    "fieldList": field_list,                    # ← Step 2 解析得到的
    "paramList": [{
        "paramName": "nameStr",
        "paramTxt": "名称",
        "paramValue": "",
        "searchMode": 1,
        "widgetType": "String"
    }],
    "isPage": "1",
    "isList": "1",
    ...
}
```

**code:1001 排查：**

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| 所有 SQL 都返回 1001 | 签名计算错误 | 先用 `select 1 as t` 验证签名 |
| 仅存储过程返回 1001 | `${param}` 未替换，参数无值 | 用具体值硬编码 SQL 再解析 |
| 硬编码具体值仍返回 1001 | 存储过程不存在或返回空结果集 | 检查存储过程是否存在，换一个能返回数据的测试值 |

**注意事项：**
- Oracle 的 `?` 游标参数必须放在所有输入参数之后
- 存储过程的字段列表由 `queryFieldBySql` 自动解析返回
- 数值参数无需引号：`CALL proc_page(${pageNo}, ${pageSize})`

参考文档：https://help.jimureport.com/dataSet/storedProcedure

### SQL解析接口

`POST /jmreport/queryFieldBySql`（需签名）

```json
{"sql": "select * from demo", "type": "0", "dbSource": ""}
```

返回：`result.fieldList[]` 每项含 `fieldName`, `fieldText`, `widgetType`, `orderNum`

## 4. API数据集

### 4.1 解析接口

`POST /jmreport/executeSelectApi`（需签名）

```json
{"api": "http://localhost:8085/jimureport/test/getList?pid=&name=", "method": "0"}
```

API路径支持：`#{domainURL}/jimureport/test/getList`

### 4.2 saveDb 字段要求

> **重要：API 数据集（dbType="1"）必须同时设置 `apiUrl`、`apiMethod` 和 `dbDynSql` 三个字段。**
>
> - `apiUrl`：API 地址 — **设计器 UI 读取此字段**显示在「Api地址」输入框
> - `apiMethod`：请求方式 `"0"`=GET, `"1"`=POST — **设计器 UI 读取此字段**显示在「请求方式」下拉框
> - `dbDynSql`：也填 API 地址 — **后端数据拉取引擎读取此字段**执行请求
>
> 仅设 `dbDynSql` 而不设 `apiUrl`/`apiMethod`，后端能拉到数据，但设计器 UI 中「Api地址」和「请求方式」显示为空。

```python
# 正确：三个字段都设置
api_request('/jmreport/saveDb', {
    "jimuReportId": report_id,
    "dbCode": "emp", "dbChName": "员工信息",
    "dbType": "1",              # API 数据集
    "dbDynSql": api_url,        # 后端拉取数据用
    "apiUrl": api_url,          # 设计器 UI 显示用
    "apiMethod": "0",           # "0"=GET, "1"=POST
    "isList": "1", "isPage": "0",
    "dbSource": "", "jsonData": "", "apiConvert": "",
    "fieldList": field_list,
    "paramList": []
})

# 错误：只设 dbDynSql，设计器 UI 显示空白
api_request('/jmreport/saveDb', {
    "dbType": "1",
    "dbDynSql": api_url,        # ✓ 后端能拉数据
    # apiUrl: 未设置             # ✗ 设计器「Api地址」为空
    # apiMethod: 未设置          # ✗ 设计器「请求方式」为空
    ...
})
```

### 4.3 API 接口响应格式要求（重要！）

积木报表 API 数据集对后端接口的响应格式有要求，**必须返回 `{"data": [...]}` 格式**，不能直接返回 JeecgBoot 标准 `Result.ok()` 包装。

| 格式 | 示例 | 是否可用 |
|------|------|---------|
| `{"data": [...]}` | `{"data": [{"name":"张三"}]}` | ✅ 积木报表能识别 |
| 裸数组 | `[{"name":"张三"}]` | ✅ 部分版本可识别 |
| `Result.ok(list)` | `{"success":true,"result":[...],"code":200}` | ❌ 积木报表**无法**识别，报表显示空白 |
| `{"data": {"records":[...], "total": N}}` | 嵌套对象 | ❌ `data` 必须是数组，**不能是对象**，否则报表显示空白 |

**⚠️ 分页 API 数据集（isPage="1"）正确响应格式：**

`data` 字段必须始终是**平铺数组**（当前页记录），分页信息放顶层：

```json
{"data": [...当前页记录...], "total": 27, "pageNo": 1, "pageSize": 10}
```

```java
// ✅ 分页正确写法：data 是数组，total/pageNo/pageSize 顶层
@GetMapping("/list")
public Map<String, Object> list(
        @RequestParam(defaultValue = "1") Integer pageNo,
        @RequestParam(defaultValue = "10") Integer pageSize) {
    IPage<SysUser> page = service.page(new Page<>(pageNo, pageSize), qw);
    List<VO> records = page.getRecords().stream().map(...).collect(toList());
    Map<String, Object> resp = new HashMap<>();
    resp.put("data", records);       // ← 平铺数组，不是嵌套对象
    resp.put("total", page.getTotal());
    resp.put("pageNo", page.getCurrent());
    resp.put("pageSize", page.getSize());
    return resp;
}

// ❌ 错误：data 是对象而非数组，executeSelectApi 返回空，报表显示空白
resp.put("data", Map.of("records", records, "total", total));
```

**JeecgBoot Controller 正确写法：**

```java
// ✅ 正确：返回 {"data": [...]}
@GetMapping("/list")
public Map<String, Object> list(@RequestParam(required = false) String mouth) {
    List<GroupSubVO> data = service.queryList(mouth);
    return Collections.singletonMap("data", data);
}

// ❌ 错误：Result.ok() 包装后积木报表找不到数据，报表显示空白
@GetMapping("/list")
public Result<List<GroupSubVO>> list() {
    return Result.ok(service.queryList());
}
```

> **注意：** 积木报表预览时接口返回 1000+ 条数据、HTTP 200，但报表完全空白，是典型的响应格式不匹配问题。

**查询参数过滤示例（年月 yyyy-MM → 匹配数据中 "N月" 字符串）：**

```java
@GetMapping("/list")
public Map<String, Object> list(@RequestParam(required = false) String mouth) {
    List<GroupSubVO> all = generateData();
    if (mouth != null && !mouth.trim().isEmpty()) {
        String[] parts = mouth.split("-");
        if (parts.length == 2) {
            String filterYear  = parts[0];                         // "2020"
            String filterMonth = parts[1].replaceFirst("^0","") + "月"; // "06" → "6月"
            all = all.stream()
                .filter(v -> v.getYear().equals(filterYear) && v.getMouth().equals(filterMonth))
                .collect(Collectors.toList());
        }
    }
    return Collections.singletonMap("data", all);
}
```

> `class` 是 Java 保留字，VO 中用 `clazz` 字段名 + `@JsonProperty("class")` 注解序列化为 `"class"` 输出给积木报表。

### 4.4 各数据集类型的 saveDb 关键字段对比

| dbType | 类型 | 数据/地址字段 | 设计器 UI 字段 | 说明 |
|--------|------|-------------|--------------|------|
| `"0"` SQL | `dbDynSql` | 同 `dbDynSql` | 后端和 UI 读同一个字段 |
| `"1"` API | `dbDynSql` | `apiUrl` + `apiMethod` | **必须同时设三个字段**，后端读 `dbDynSql`，UI 读 `apiUrl`/`apiMethod` |
| `"2"` JavaBean | — | `javaType` + `javaValue` | 见下方 JavaBean 说明 |
| `"3"` JSON | `jsonData` | 同 `jsonData` | 必须用 `{"data":[...]}` 包裹 |
| `"5"` 多文件 | `dbDynSql` | 同 `dbDynSql` | SQL 需 `jmf.` 前缀，`dbSource` 传文件数据源ID，用标准 `queryFieldBySql` + `saveDb` |
| `"6"` 单文件 | — | — | 使用专用 `/dataset/files/single/save` 接口 |

## 5. JSON数据集

直接输入 JSON，自动解析字段：
```json
{"data": [{"cname": "牛奶", "cprice": "56", "id": "1"}]}
```

> **重要：JSON 数据必须用 `{"data": [...]}` 对象包裹，禁止直接传数组 `[...]`。** 后端使用 fastjson 解析，直接传数组会导致预览报错：`offset 1, character [, line 1, column 1`。
>
> - 正确：`{"data": [{"name": "张三", "age": "30"}]}`
> - 错误：`[{"name": "张三", "age": "30"}]`
>
> `saveDb` 接口的 `jsonData` 字段传入的是 JSON 字符串，构造时用 `json.dumps({"data": [...]})` 包裹。

## 6. JavaBean数据集

`POST /jmreport/queryFieldByBean`

```json
{"javaType": "spring-key", "javaValue": "testRpSpringBean", "isPage": false, "param": {}}
```

---

## 7. 查询已有数据集

### Step 1: 获取数据集列表

`GET /jmreport/field/tree/{reportId}`

```python
tree = api_request(f'/jmreport/field/tree/{report_id}')
db_map = {}  # dbCode -> dbId
for group in tree.get('result', []):
    if group and len(group) > 0:
        info = group[0]
        db_map[info['code']] = info['dbId']
```

### Step 2: 获取单个数据集详情

`GET /jmreport/loadDbData/{dbId}?reportId={reportId}`

```python
detail = api_request(f'/jmreport/loadDbData/{db_id}?reportId={report_id}').get('result', {})
report_db = detail.get('reportDb', {})
existing_sql = report_db.get('dbDynSql', '')
existing_fields = detail.get('fieldList', [])
existing_params = detail.get('paramList', [])
```

> **注意：`dbDynSql` 和 `dbSource` 在 `result.reportDb` 中，不在顶层。**

### Step 3: 查询参数列表

`GET /jmreport/getListReportDb?reportId={reportId}`

返回：`result.reportDbParam.{dbCode}: [{paramName, ...}]`

---

## 8. 保存/修改数据集

`POST /jmreport/saveDb`（新增不传 id，更新传 id）

> **分页规则：**
> - **第一个数据集默认设置 `isPage: "1"`**（勾选"是否分页"）
> - 一个报表**只能有一个数据集**设置 `isPage: "1"`，其余必须为 `"0"`
> - 如果报表只有一个数据集，直接设 `isPage: "1"`
> - **对象数据集（单条记录）：`isList: "0"` + `isPage: "0"`**，见下方说明

### 列表数据集 vs 对象数据集

| 特性 | 列表数据集 | 对象数据集 |
|------|-----------|-----------|
| isList | `"1"` | `"0"` |
| isPage | `"1"` 或 `"0"` | `"0"` |
| 绑定语法 | `#{dbCode.field}` | `${dbCode.field}` |
| 数据形态 | 多条记录，循环展开 | **单条记录**，直接取值 |
| 典型场景 | 明细列表、统计报表 | 套打、证件、单据（逮捕证、合同、发票） |

> **对象数据集：** 当数据集返回的是单条记录（对象）而非列表时，`isList` 和 `isPage` 都不勾选（均为 `"0"`），报表中使用 `${dbCode.field}` 单值绑定语法。适用于套打类报表（如逮捕证、合同、证书），每次只展示一条记录的详细信息。
>
> **主子表场景中：** 主表通常用对象数据集 `${}`，子表用列表数据集 `#{}`。参见 `examples/master-sub-table.md`。

**列表数据集示例：**
```json
{
    "id": "数据集ID（更新时传）",
    "izSharedSource": 0,
    "jimuReportId": "报表ID",
    "dbCode": "数据集编码",
    "dbChName": "数据集中文名",
    "dbType": "0",
    "dbSource": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from demo",
    "fieldList": [
        {"fieldName": "id", "fieldText": "id", "widgetType": "String", "orderNum": 0,
         "tableIndex": 0, "extJson": "", "dictCode": ""}
    ],
    "paramList": []
}
```

**对象数据集示例：**
```json
{
    "jimuReportId": "报表ID",
    "dbCode": "pdaibu",
    "dbChName": "逮捕信息",
    "dbType": "0",
    "dbSource": "",
    "isList": "0",
    "isPage": "0",
    "dbDynSql": "select pname, fname, fsex, cdata, shiqing, zhuzhi, gdata from pdaibu where id='${id}'",
    "fieldList": [...],
    "paramList": [
        {"paramName": "id", "paramTxt": "ID", "paramValue": "", "widgetType": "String", "orderNum": 1, "searchFlag": 1, "searchMode": 1}
    ]
}
```

### dbType 值说明

| dbType | 类型 | 关键字段 |
|--------|------|----------|
| `"0"` | SQL | `dbDynSql` |
| `"1"` | API | `apiUrl` + `apiMethod` |
| `"2"` | JavaBean | `javaType`（`"spring-key"` 或 `"java-class"`）+ `javaValue`（Bean名称或类全路径），见下方 JavaBean 说明 |
| `"3"` | JSON | `jsonData` |
| `"4"` | 共享 | — |
| `"5"` | 多文件 | SQL 需 `jmf.` 前缀，`dbSource` = 文件数据源ID，标准 `queryFieldBySql` + `saveDb` 流程 |
| `"6"` | 单文件 | 专用 `/dataset/files/single/save` 接口 |

### JavaBean 数据集字段说明

> **`javaType` 不是 Bean 名称！** 它是类型选择器，`javaValue` 才是 Bean 名称。

| 字段 | 值 | 说明 |
|------|-----|------|
| `javaType` | `"spring-key"` | Bean 通过 Spring 容器 `@Component("beanName")` 注册 |
| `javaType` | `"java-class"` | 直接通过类全路径反射创建 |
| `javaValue` | Bean 名称或类路径 | spring-key 时填 Bean 名称（如 `testRpSpringBean`），java-class 时填类全路径 |

```python
# 正确：javaType 是类型，javaValue 是 Bean 名称
{"javaType": "spring-key", "javaValue": "testRpSpringBean"}

# 错误：把 Bean 名称放到了 javaType
{"javaType": "testRpSpringBean", "javaValue": "createData"}
```

Bean 必须实现 `IDataSetFactory` 接口，框架自动调用 `createData()`（非分页）或 `createPageData()`（分页）方法，不需要在 saveDb 中指定方法名。

---

## 9. 文件数据集

通过上传 Excel/CSV 文件创建数据集。分为**单文件数据集**（dbType="6"）和**多文件数据集**（dbType="5"）两种。

| 类型 | dbType | 创建数据集方式 | 特点 |
|------|--------|--------------|------|
| 单文件 | `"6"` | `/dataset/files/single/save` 专用接口 | 后端自动生成 dbCode，不支持自定义 |
| 多文件 | `"5"` | 标准 `queryFieldBySql` + `saveDb` 流程 | SQL 需 `jmf.` 前缀，字段/参数配置与 SQL 数据集一致 |

> **上传接口 `isSingle` 固定传 `true`**，单文件和多文件都一样。区别在于后续创建数据集的方式不同。

### 9.0 上传文件（单文件/多文件共用）

`POST /jmreport/source/datasource/files/add`（**multipart/form-data**）

| 参数 | 类型 | 说明 |
|------|------|------|
| `reportId` | String | 报表ID |
| `isSingle` | Boolean | 固定传 `true` |
| `file` | MultipartFile | 用户提供本地文件路径，需构造为 multipart 上传 |

**Python 实现（用户提供本地文件路径）：**

```python
import os, mimetypes

def upload_file_dataset(report_id, file_path):
    """上传文件创建文件数据集"""
    file_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

    # 构造 multipart/form-data
    boundary = '----WebKitFormBoundary' + str(int(time.time() * 1000))
    body = b''

    # reportId 字段
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="reportId"\r\n\r\n'
    body += f'{report_id}\r\n'.encode()

    # isSingle 字段
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="isSingle"\r\n\r\n'
    body += b'true\r\n'

    # file 字段
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode()
    body += f'Content-Type: {content_type}\r\n\r\n'.encode()
    with open(file_path, 'rb') as f:
        body += f.read()
    body += b'\r\n'

    body += f'--{boundary}--\r\n'.encode()

    headers = {
        'X-Access-Token': TOKEN,
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
    url = f'{API_BASE}/jmreport/source/datasource/files/add'
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))
```

**返回结果：**

```json
{
    "success": true,
    "message": "filesDataSet/报表ID/文件名.xlsx",
    "code": 0,
    "result": {
        "id": "数据源ID",
        "name": "报表ID文件数据源",
        "reportId": "报表ID",
        "dbType": "FILES",
        "dbDriver": "filesDataSet\\报表ID",
        "dbUrl": "[{\"fileName\":\"文件名.xlsx\",\"name\":\"jmf.Sheet1_文件名_excel\"}]"
    }
}
```

**关键返回字段：**
- `result.id` — 文件数据源ID（多文件流程中作为 `dbSource` 传给 `queryFieldBySql` 和 `saveDb`）
- `result.dbUrl` — JSON 数组字符串，每项的 `name` 是表名（带 `jmf.` 前缀，用于 SQL 查询）
- **多文件场景：** 每次上传新文件后，`dbUrl` 数组会累积所有已上传文件的信息

### 9.0.1 查询已上传的文件数据源

`GET /jmreport/source/datasource/files/get?reportId={reportId}`

返回该报表关联的文件数据源信息（含所有已上传文件列表）。

### Step 2: 预览文件数据

`GET /jmreport/source/datasource/files/preview`

| 参数 | 说明 |
|------|------|
| `reportId` | 报表ID |
| `tableName` | 上传返回的 `dbUrl[].name`（需 URL 编码） |

```python
import urllib.parse

# 从上传返回中提取 tableName
db_url = json.loads(upload_result['result']['dbUrl'])
table_name = db_url[0]['name']  # e.g. "jmf.Sheet1_文件数据集_excel"

# 预览
encoded_name = urllib.parse.quote(table_name)
preview = api_request(f'/jmreport/source/datasource/files/preview?reportId={report_id}&tableName={encoded_name}')
# preview['result'] = [{"id": 1, "product_name": "苹果", "price": 100}, ...]
```

### Step 3: 创建单文件数据集（dbType="6"）

> **重要：单文件数据集必须使用 `/dataset/files/single/save` 接口，不能用通用的 `/saveDb`。**
> 使用 `saveDb` 创建的单文件数据集在设计器中无法关联文件（编辑时显示"暂无数据"），因为缺少文件数据源的正确关联。

`POST /jmreport/source/dataset/files/single/save`

```python
save_data = {
    "reportId": report_id,
    "dbSource": {
        "id": upload_result['result']['id'],   # 文件数据源ID
        "dbUrl": upload_result['result']['dbUrl'],  # 文件信息JSON
        "dbChName": "文件数据集"                # 数据集中文名
    }
}
result = api_request('/jmreport/source/dataset/files/single/save', save_data)
```

**返回说明：**
- 后端自动解析文件字段、生成 dbCode（格式 `file_` + 文件名拼音）、创建 SQL
- dbCode 由后端生成，不可自定义

### Step 3.1: 获取生成的 dbCode

创建后需通过 field/tree 获取后端生成的 dbCode：

```python
tree = api_request(f'/jmreport/field/tree/{report_id}')
for group in tree.get('result', []):
    if group:
        info = group[0] if isinstance(group, list) else group
        if info.get('type') == '6':  # 文件数据集
            db_code = info['code']
            db_id = info['dbId']
            fields = [c['fieldText'] for c in info.get('children', [])]
            print(f'dbCode={db_code}, fields={fields}')
```

### Step 3.2: 查看文件数据集详情

`GET /jmreport/source/dataset/files/single/get?id={dbId}`

返回文件数据源信息（含 dbUrl 文件列表）。

### 9.1 多文件数据集（dbType="5"）

多文件数据集使用标准的 `queryFieldBySql` + `saveDb` 流程，与 SQL 数据集的字段配置、参数配置、默认值处理**完全一致**，唯一区别是 SQL 表名需要 `jmf.` 前缀。

**完整流程：**

```
1. 上传文件（逐个）  → POST /jmreport/source/datasource/files/add（isSingle=false）
2. 获取文件数据源    → GET /jmreport/source/datasource/files/get?reportId=xxx
3. 写 SQL（jmf.前缀）→ select * from jmf.Sheet1_文件名_excel
4. 解析字段          → POST /jmreport/queryFieldBySql（dbSource = 文件数据源ID）
5. 保存数据集        → POST /jmreport/saveDb（dbType="5", dbSource = 文件数据源ID）
```

**Step 1: 逐个上传文件**

多个文件需要**一个一个上传**，每次调用 `/files/add`（`isSingle=false`），`dbUrl` 会自动累积：

```python
# 上传第1个文件
r1 = upload_file_dataset(report_id, '/path/to/sales.xlsx')
# r1.result.dbUrl = '[{"fileName":"sales.xlsx","name":"jmf.Sheet1_sales_excel"}]'

# 上传第2个文件
r2 = upload_file_dataset(report_id, '/path/to/products.csv')
# r2.result.dbUrl = '[{"fileName":"sales.xlsx","name":"jmf.Sheet1_sales_excel"},{"fileName":"products.csv","name":"jmf.products_csv"}]'
```

**Step 2: 获取文件数据源信息**

```python
files_info = api_request(f'/jmreport/source/datasource/files/get?reportId={report_id}')
datasource_id = files_info['result']['id']  # 文件数据源ID
db_url = json.loads(files_info['result']['dbUrl'])  # 所有文件的表名列表
# [{"fileName":"sales.xlsx","name":"jmf.Sheet1_sales_excel"}, ...]
```

**Step 3-4: 写 SQL 并解析字段**

> **SQL 表名必须加 `jmf.` 前缀**，表名来自上传返回的 `dbUrl[].name`。

```python
# 表名从 dbUrl 中获取
table_name = db_url[0]['name']  # "jmf.Sheet1_sales_excel"

sql = f"select * from {table_name}"
parse_result = api_request('/jmreport/queryFieldBySql', {
    "sql": sql,
    "dbSource": datasource_id,  # 文件数据源ID
    "type": "0"
})
field_list = parse_result['result']['fieldList']
```

**Step 5: 保存数据集**

```python
db_data = {
    "izSharedSource": 0,
    "jimuReportId": report_id,
    "dbCode": "sales",
    "dbChName": "销售数据",
    "dbType": "5",          #   多文件数据集
    "dbSource": datasource_id,  # 文件数据源ID
    "isList": "1",
    "isPage": "1",
    "dbDynSql": sql,        # 含 jmf. 前缀的 SQL
    "fieldList": field_list,
    "paramList": []         # 参数配置与 SQL 数据集一致
}
result = api_request('/jmreport/saveDb', db_data)
```

> **参数和默认值处理与 SQL 数据源完全一致：** FreeMarker 条件、`searchValue`/`paramValue`、`searchMode`、`dictCode`、默认值表达式等配置方式无任何区别。

### 9.1.1 Calcite 类型转换问题（String cannot be cast to Integer）

**现象：** 多文件数据集使用 FreeMarker 参数过滤时，预览报错：
```
class java.lang.String cannot be cast to class java.lang.Integer
SQL: SELECT COUNT(1) total FROM (...and user_id = ?) temp_count
```

**根因：** Calcite 引擎根据 Excel 列的实际数据推断字段类型。若列中所有值均为纯数字，Calcite 会将该列推断为 **Integer 类型**。开启分页（`isPage="1"`）后，JimuReport 将 SQL 包装为 PreparedStatement COUNT 查询，参数 `?` 被绑定为 Integer，而传入值是 String，导致类型不匹配。

**解决方案：** 在 SQL 中对字段加 `CAST(字段名 AS VARCHAR)`，强制以字符串类型比较：

```sql
-- 原始（报错）
select id, user_id, depart_name from jmf.Sheet1_部门信息_excel
where 1=1
<#if isNotEmpty(user_id)> and user_id = '${user_id}'</#if>

-- 修复（加 CAST）
select id, user_id, depart_name from jmf.Sheet1_部门信息_excel
where 1=1
<#if isNotEmpty(user_id)> and CAST(user_id AS VARCHAR) = '${user_id}'</#if>
```

**适用范围：** 所有值为纯数字但逻辑上应作为字符串的字段（如 ID、编码、手机号等）。

> **注意：** 若不需要分页，也可将 `isPage` 设为 `"0"` 规避此问题，但建议优先使用 CAST 方案以保持语义清晰。

**多文件上传 Python 实现：**

```python
def upload_file_dataset(report_id, file_path):
    """上传文件到文件数据源"""
    file_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    boundary = '----WebKitFormBoundary' + str(int(time.time() * 1000))
    body = b''

    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="reportId"\r\n\r\n'
    body += f'{report_id}\r\n'.encode()

    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="isSingle"\r\n\r\n'
    body += b'true\r\n'

    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode()
    body += f'Content-Type: {content_type}\r\n\r\n'.encode()
    with open(file_path, 'rb') as f:
        body += f.read()
    body += b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    headers = {
        'X-Access-Token': TOKEN,
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
    url = f'{API_BASE}/jmreport/source/datasource/files/add'
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))
```

### 删除多文件数据集中的单个文件

`DELETE /jmreport/source/datasource/files/del`

```json
{
    "reportId": "报表ID",
    "tableName": "jmf.Sheet1_文件名_excel"
}
```

> `tableName` 来自上传返回的 `dbUrl[].name`，删除后该文件从 `dbUrl` 数组中移除。

### 删除数据集

`GET /jmreport/delDbData/{dbId}`

- `dbId` — 数据集ID（从 `field/tree` 返回的 `dbId`，不是报表ID）

### 删除报表

`DELETE /jmreport/delete`

参数：`id` — 报表ID

```python
api_request(f'/jmreport/delete?id={report_id}', method='DELETE')
```

返回：`{"success": true, "message": "删除成功!", "code": 200, "result": true}`

---

## 10. 主子表联动配置

通过 `/jmreport/link/saveAndEdit` 接口配置主子表数据联动，子表根据主表选中行的字段值自动过滤数据。

### 新增主子表联动

`POST /jmreport/link/saveAndEdit`

```json
{
    "mainReport": "主表数据源code",
    "subReport": "子表数据源code",
    "linkName": "主子表配置",
    "parameter": "{\"main\":\"主表code\",\"sub\":\"子表code\",\"subReport\":[{\"mainField\":\"id\",\"subParam\":\"id\",\"tableIndex\":1}]}",
    "linkType": "4",
    "reportId": "报表ID"
}
```

**参数说明：**

| 字段 | 说明 |
|------|------|
| `mainReport` | 主表数据源的 dbCode |
| `subReport` | 子表数据源的 dbCode |
| `linkName` | 联动配置名称 |
| `linkType` | `"4"` = 主子表联动 |
| `reportId` | 报表ID |
| `parameter` | JSON 字符串，定义主子表字段映射关系 |

**parameter 结构（JSON 字符串）：**

```json
{
    "main": "主表code",
    "sub": "子表code",
    "subReport": [
        {
            "mainField": "id",
            "subParam": "id",
            "tableIndex": 1
        }
    ]
}
```

| 字段 | 说明 |
|------|------|
| `main` | 主表数据源 code |
| `sub` | 子表数据源 code |
| `subReport[].mainField` | 主表关联字段名 |
| `subReport[].subParam` | 子表参数名（对应子表 SQL 中的 `${param}`） |
| `subReport[].tableIndex` | 子表序号（从1开始） |

**返回值：**
```json
{
    "success": true,
    "code": 0,
    "result": "联动配置ID"
}
```

### 编辑主子表联动

同一接口 `POST /jmreport/link/saveAndEdit`，传入 `id` 字段即为更新：

```json
{
    "id": "联动配置ID",
    "reportId": "报表ID",
    "mainReport": "主表code",
    "subReport": "子表code",
    "linkName": "主子表配置",
    "linkType": "4",
    "parameter": "{\"main\":\"主表code\",\"sub\":\"子表code\",\"subReport\":[{\"mainField\":\"id\",\"subParam\":\"id\",\"tableIndex\":1}]}"
}
```

### Python 示例

```python
import json

# 构造 parameter
parameter = json.dumps({
    "main": "orderMain",
    "sub": "orderDetail",
    "subReport": [{"mainField": "id", "subParam": "order_id", "tableIndex": 1}]
}, ensure_ascii=False)

# 新增联动
link_data = {
    "mainReport": "orderMain",
    "subReport": "orderDetail",
    "linkName": "订单主子表",
    "parameter": parameter,
    "linkType": "4",
    "reportId": report_id
}
result = api_request('/jmreport/link/saveAndEdit', link_data)
link_id = result['result']  # 联动配置ID

# 编辑联动（传 id）
link_data["id"] = link_id
result = api_request('/jmreport/link/saveAndEdit', link_data)
```

### 删除主子表联动

`POST /jmreport/link/delete`

```json
{"id": "联动配置ID"}
```

返回：`{"success": true, "result": "删除成功!"}`

### linkType 值说明

| linkType | 类型 |
|----------|------|
| `"4"` | 主子表联动 |
| `"2"` | 图表联动 |

## 11. 共享数据集

共享数据集与普通数据集的 CRUD 操作完全一致，唯一区别是保存时 `izSharedSource: 1`（普通数据集为 `0`）。共享数据集不关联具体报表（`jimuReportId` 为空），可被多个报表引用。

### 查询共享数据集列表

`GET /jmreport/source/getJmReportSharedDbPageList`

**请求参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `pageSize` | 每页条数 | `10` |
| `pageNo` | 页码 | `1` |
| `name` | 按名称模糊搜索（可选） | `""` |

**返回结构：**
```json
{
    "success": true,
    "code": 0,
    "result": {
        "pageNo": 1,
        "pageSize": 10,
        "total": 6,
        "pages": 1,
        "records": [
            {
                "id": "1199211124874633216",
                "dbCode": "aaa",
                "dbChName": "aaa",
                "dbType": "0",
                "izSharedSource": 1,
                "createTime": "2026-04-01 14:43:43",
                ...
            }
        ]
    }
}
```

> **records 字段说明：** 与普通数据集结构相同（`id`、`dbCode`、`dbChName`、`dbType` 等），但 `jimuReportId` 为 `null`，`izSharedSource` 为 `1`。

### 创建共享数据集

使用 `POST /jmreport/saveDb`，与普通数据集相同，区别：
- `izSharedSource: 1`
- `jimuReportId` 传空字符串 `""` 或不传

```json
{
    "izSharedSource": 1,
    "jimuReportId": "",
    "dbCode": "shared_users",
    "dbChName": "共享用户数据",
    "dbType": "0",
    "dbSource": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from sys_user",
    "fieldList": [...],
    "paramList": []
}
```

### 修改共享数据集

与普通数据集修改一致，传 `id` 即为更新：

```json
{
    "id": "已有共享数据集ID",
    "izSharedSource": 1,
    "dbCode": "shared_users",
    "dbChName": "共享用户数据（已修改）",
    ...
}
```

### 删除共享数据集

`POST /jmreport/source/delShareDbByDbId`

```json
{"id": "共享数据集ID"}
```

**返回：**
```json
{
    "success": true,
    "message": "共享数据集删除成功！",
    "code": 0,
    "result": null
}
```

### 报表引用（关联）共享数据集

`POST /jmreport/source/linkJmReportShareDb`

将一个已有的共享数据集关联到指定报表中。关联后报表即可使用该共享数据集的字段进行数据绑定。

**请求参数：**
```json
{
    "jimuReportId": "报表ID",
    "jimuSharedSourceId": "共享数据集ID"
}
```

**返回：**
```json
{
    "success": true,
    "message": "保存共享数据集成功",
    "code": 0,
    "result": null
}
```

> **说明：** 关联后，报表的数据集列表中会出现一条 `dbType: "4"` 的数据集，通过 `jimuSharedSourceId` 指向原始共享数据集。

### dbType 与 izSharedSource 的区别

| 概念 | 说明 |
|------|------|
| `izSharedSource: 1` | 标记数据集**本身**是共享的（保存在共享数据集列表中） |
| `dbType: "4"` | 标记数据集是**引用**共享数据集的（报表中使用共享数据集时） |
