# 接口签名机制 (JimuSignature)

## 概述

积木报表部分接口使用 `@JimuSignature` 注解标记，调用时需要在请求 Header 中携带签名参数，否则返回 `code: 1001` 签名校验失败错误。

**源码位置：**
- 后端拦截器：`jimureport-spring-boot-starter/.../common/interceptor/JimuReportSignatureInterceptor.java`
- 前端签名工具：`static/jmreport/desreport_/js/biz/SignMd5Util.js`
- 前端请求拦截器：`static/jmreport/desreport_/js/core/request.js`

## 需要签名的接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/jmreport/queryFieldBySql` | POST | SQL 解析获取字段 |
| `/jmreport/executeSelectApi` | POST | API 数据集解析 |
| `/jmreport/loadTableData` | POST | 加载表数据 |
| `/jmreport/testConnection` | POST | 测试数据源连接 |
| `/jmreport/download/image` | GET | 下载图片 |
| `/jmreport/dictCodeSearch` | GET | 字典编码搜索 |
| `/jmreport/getDataSourceByPage` | GET | 分页查询数据源 |
| `/jmreport/getDataSourceById` | GET | 按ID查询数据源 |

**不需要签名的接口（常用）：**
- `/jmreport/save` — 保存报表
- `/jmreport/saveDb` — 保存数据集
- `/jmreport/get/{id}` — 获取报表
- `/jmreport/field/tree/{reportId}` — 获取数据集树
- `/jmreport/loadDbData/{dbId}` — 加载数据集详情

## 签名算法

### 请求 Headers

| Header | 值 | 说明 |
|--------|------|------|
| `X-Sign` | MD5 签名（大写） | 见下方计算方法 |
| `X-TIMESTAMP` | 当前时间戳（毫秒） | `int(time.time() * 1000)` |

### 计算步骤

```
1. 收集所有请求参数（URL query参数 + POST body参数）
2. 按 key 字母升序排序（SortedMap / TreeMap）
3. 转为 JSON 字符串：JSON.stringify(sortedParams) 或 JSONObject.toJSONString(sortedMap)
4. 拼接签名密钥：jsonStr + signatureSecret
5. 计算 MD5 并转大写：MD5(jsonStr + secret).toUpperCase()
```

### 签名密钥 (signatureSecret)

**默认值：** `dd05f1c54d63749eda95f9fa6d49v442a`

解析优先级：
1. `JmReportBaseConfig.getSignatureSecret()` — 代码配置
2. Spring 属性 `jeecg.signatureSecret` — application.yml 配置
3. 默认值 `dd05f1c54d63749eda95f9fa6d49v442a`

> **注意：** 默认密钥中第29个字符是字母 `v`，不是数字 `4`。

### 时间戳校验

服务端校验时间戳有效期为 **5 分钟（300秒）**。如果客户端与服务器时间差超过5分钟，会返回 "签名验证失败:X-TIMESTAMP已过期"。

### 参数值类型转换规则

前端在签名前会统一类型（后端用 `json.getString(key)` 读取，也是字符串）：
- **数字** → 转为字符串（如 `0` → `"0"`）
- **布尔** → 转为字符串（如 `false` → `"false"`）
- **对象/数组** → 转为 JSON 字符串
- **null/空** → 不参与签名

### 后端校验逻辑

```java
// 1. 收集参数到 SortedMap (TreeMap, 自动按key排序)
SortedMap<String, String> map = new TreeMap<>();

// 2. 从 request.getParameterMap() 取 URL/form 参数
// 3. 从 request.getQueryString() 取 GET 参数
// 4. 从 POST body JSON 取参数 (json.getString(key))

// 5. 计算签名
String paramsJsonStr = JSONObject.toJSONString(map);  // fastjson
String signValue = DigestUtils.md5DigestAsHex(
    (paramsJsonStr + CommonUtils.getSignatureSecret()).getBytes()
).toUpperCase();

// 6. 比对 header 中的 X-Sign
```

> **关键细节：** 后端用 fastjson 的 `JSONObject.toJSONString(map)` 序列化 SortedMap，输出格式为 `{"key1":"value1","key2":"value2"}`（无空格）。Python 端必须用 `json.dumps(sorted_dict, separators=(',', ':'))` 匹配（无空格）。

## Python 实现

```python
import hashlib
import json
import time

SIGNATURE_SECRET = "dd05f1c54d63749eda95f9fa6d49v442a"

def compute_sign(params_dict):
    """
    计算积木报表接口签名
    params_dict: 请求参数字典（POST body 或 GET query 参数）
    """
    # 1. 所有值转为字符串（与前端/后端保持一致）
    str_params = {}
    for k, v in params_dict.items():
        if v is None:
            continue
        if isinstance(v, bool):
            str_params[k] = str(v).lower()  # True -> "true"
        elif isinstance(v, (int, float)):
            str_params[k] = str(v)
        elif isinstance(v, (dict, list)):
            str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else:
            str_params[k] = str(v)

    # 2. 按 key 字母升序排序
    sorted_params = dict(sorted(str_params.items()))

    # 3. 转为 JSON 字符串（无空格，与 fastjson 一致）
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))

    # 4. 拼接密钥并计算 MD5
    sign_str = params_json + SIGNATURE_SECRET
    sign_value = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    return sign_value

def get_sign_headers(params_dict):
    """获取签名相关的请求头"""
    return {
        'X-Sign': compute_sign(params_dict),
        'X-TIMESTAMP': str(int(time.time() * 1000))
    }
```

### 使用示例

```python
# POST /jmreport/queryFieldBySql
body = {"sql": "select * from demo", "dbSource": "", "type": "0"}
sign_headers = get_sign_headers(body)
# sign_headers = {'X-Sign': 'AB12CD34...', 'X-TIMESTAMP': '1774019281912'}

# GET /jmreport/getDataSourceByPage?pageNo=1&pageSize=10
query_params = {"pageNo": "1", "pageSize": "10"}
sign_headers = get_sign_headers(query_params)
```

### 完整的带签名 API 请求函数

```python
def api_request(path, data=None, method=None):
    """发送 API 请求，自动判断是否需要签名"""
    url = f'{API_BASE}{path}'
    headers = {
        'X-Access-Token': TOKEN,
        'Content-Type': 'application/json; charset=UTF-8'
    }

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

    # 判断是否需要签名
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
```

## 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `签名验证失败: 签名参数不存在` | 未传 X-Sign 或 X-TIMESTAMP Header | 添加签名 Headers |
| `签名验证失败:X-TIMESTAMP已过期` | 客户端与服务器时间差超过5分钟 | 检查系统时间，使用当前时间戳 |
| `签名校验失败，参数有误！` | 签名值不匹配 | 检查参数排序、JSON序列化格式、密钥是否正确 |
| `code: 1001` | 签名相关错误的统一错误码 | 查看 message 详情 |

## 调试技巧

1. **打印签名输入**：输出 `params_json + secret` 字符串，对比前后端是否一致
2. **对比 JSON 格式**：确保使用 `separators=(',', ':')` 无空格格式
3. **检查类型转换**：数字/布尔/对象必须转为字符串
4. **验证密钥**：确认使用的密钥与服务端配置一致（默认 `dd05f1c54d63749eda95f9fa6d49v442a`）
