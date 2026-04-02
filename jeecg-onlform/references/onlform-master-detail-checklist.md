# 主子表创建必检清单

创建主子表时，以下 3 项配置缺一不可，否则两张表会各自独立、无关联关系。

## 必须配置项

### 1. 主表 head 设置 subTableStr
```json
{
  "tableName": "xxx_main",
  "tableType": 2,
  "subTableStr": "xxx_sub1,xxx_sub2"
}
```

### 2. 子表 head 设置 relationType + tabOrderNum
```json
{
  "tableName": "xxx_sub1",
  "tableType": 3,
  "relationType": 0,
  "tabOrderNum": 1
}
```
- `relationType`: 0=一对多, 1=一对一
- `tabOrderNum`: 子表排序号（从1开始）

### 3. 子表必须包含外键字段
```json
{
  "dbFieldName": "main_id",
  "dbFieldTxt": "主表ID",
  "fieldShowType": "text",
  "dbType": "string",
  "dbLength": 36,
  "mainTable": "xxx_main",
  "mainField": "id",
  "isShowForm": "0",
  "isShowList": "0"
}
```
- `mainTable`: 主表表名
- `mainField`: 主表关联字段（通常是 `id`）
- `isShowForm/isShowList`: 必须设为 "0"（隐藏）

## 常见错误

| 遗漏项 | 后果 |
|-------|------|
| 缺 subTableStr | 主表不知道有子表，预览时看不到子表 Tab |
| 缺 relationType | 报错"附表必须选择映射关系！" |
| 缺 tabOrderNum | 报错"附表必须填写排序序号！" |
| 缺外键字段 | 子表数据无法关联到主表记录 |
| 缺 mainTable/mainField | 外键字段不生效，数据无法关联 |
