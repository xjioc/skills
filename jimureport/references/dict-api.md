# 积木报表 字典 API 参考

## 通用说明

- **Header**: `X-Access-Token: <token>`
- **请求时需绕过本地代理**（否则 302 重定向到登录页）

---

## 字典（Dict）接口

### 查询字典列表

```
GET /dict/list?pageNo=1&dictCode=<code>&dictName=<name>
```

- `dictCode`：精确匹配（按编码查）
- `dictName`：模糊匹配（按名称查，需 URL encode）

**响应示例：**
```json
{
  "result": {
    "pageNo": 1, "pageSize": 10, "total": 1, "pages": 1,
    "records": [
      {
        "id": "1199580287929507840",
        "dictName": "审核",
        "dictCode": "audit_status",
        "description": "审核项目的类型",
        "type": 0, "delFlag": 0
      }
    ]
  }
}
```

---

### 添加字典

```
POST /dict/add
Content-Type: application/json
```

```json
{
  "dictName": "审核",
  "dictCode": "audit_status",
  "description": "审核项目的类型"
}
```

> 字典编码唯一，重复添加返回 `success:false`，需先查询确认是否存在。

---

### 编辑字典

```
POST /dict/edit
Content-Type: application/json
```

```json
{
  "id": "1199580287929507840",
  "dictName": "审核",
  "dictCode": "audit_status",
  "description": "审核项目的类型"
}
```

---

### 删除字典

```
DELETE /dict/delete?id=<dictId>
```

> 删除字典后，其下字典项也会一并清除。

---

## 字典项（DictItem）接口

### 查询字典项列表

```
GET /dictItem/list?dictId=<dictId>
```

**响应示例：**
```json
{
  "result": {
    "records": [
      {
        "id": "1199581000466259968",
        "dictId": "1199580287929507840",
        "itemText": "已通过",
        "itemValue": "1",
        "sortOrder": 1,
        "status": 1
      }
    ]
  }
}
```

---

### 添加字典项

```
POST /dictItem/add
Content-Type: application/json
```

```json
{
  "dictId": "1199580287929507840",
  "itemText": "已通过",
  "itemValue": "1",
  "sortOrder": 1,
  "status": 1
}
```

| 字段 | 说明 |
|------|------|
| `dictId` | 所属字典的 id |
| `itemText` | 显示文本 |
| `itemValue` | 存储值 |
| `sortOrder` | 排序（数字越小越靠前） |
| `status` | 1=启用，0=不启用 |

---

### 编辑字典项

```
POST /dictItem/edit
Content-Type: application/json
```

```json
{
  "id": "1199581795861487616",
  "dictId": "1199580287929507840",
  "itemText": "不通过",
  "itemValue": "2",
  "sortOrder": 2,
  "status": 0
}
```

> 编辑时需带上 `id`，其余字段全量传递。

---

### 删除字典项

```
DELETE /dictItem/delete?id=<itemId>
```

---

## 操作流程示例

1. **查询字典是否存在** → `/dict/list?dictCode=xxx`
2. **不存在则添加** → `/dict/add`
3. **查询字典 id** → 从上一步响应或查询结果中取
4. **批量添加字典项** → `/dictItem/add`（每项单独请求）
5. **需要修改时** → `/dictItem/edit`（先查 itemId）
6. **删除字典项** → `/dictItem/delete?id=xxx`
7. **删除字典** → `/dict/delete?id=xxx`
