# 示例11：横向分组

**类型：** 横向分组统计表
**特征：** `customGroup()` + `direction:"right"` 数据横向展开

## 关键语法

所有数据行使用 `#{hex.customGroup(字段名)}` + `direction:"right"` 实现横向展开：

```json
{"text":"#{hex.customGroup(department)}","style":11,"direction":"right"}
```

## 数据字段

| 行 | 标签 | 绑定 |
|---|---|---|
| 2 | 部门 | `#{hex.customGroup(department)}` |
| 3 | 学历 | `#{hex.customGroup(education)}` |
| 4 | 性别 | `#{hex.customGroup(sex)}` |
| 5 | 年龄 | `#{hex.customGroup(age)}` （无 direction，纵向） |
| 6 | 姓名 | `#{hex.customGroup(name)}` |
| 7 | 薪水 | `#{hex.customGroup(salary)}` |

## 报表 JSON

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10},"hidden":{"rows":[],"cols":[],"conditions":{"rows":{},"cols":{}}},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":[],"freeze":"A1","dataRectWidth":204,"isViewContentHorizontalCenter":false,"autofilter":{},"validations":[],"cols":{"0":{"width":44},"1":{"width":79},"2":{"width":81},"len":50},"area":{"sri":7,"sci":5,"eri":7,"eci":5,"width":100,"height":36},"excel_config_id":"1194552262320803840","hiddenCells":[],"zonedEditionList":[],"rows":{"1":{"cells":{"0":{"text":"员工信息横向统计表","style":9,"merge":[0,11]}},"height":97},"2":{"cells":{"1":{"text":"部门","style":7},"2":{"text":"#{hex.customGroup(department)}","style":11,"direction":"right"}},"isDrag":true,"height":40},"3":{"cells":{"1":{"text":"学历","style":7},"2":{"text":"#{hex.customGroup(education)}","style":11,"direction":"right"}},"isDrag":true,"height":39},"4":{"cells":{"1":{"text":"性别","style":7},"2":{"text":"#{hex.customGroup(sex)}","style":11,"direction":"right"}},"isDrag":true,"height":41},"5":{"cells":{"1":{"text":"年龄","style":7},"2":{"text":"#{hex.customGroup(age)}","style":11}},"isDrag":true,"height":39},"6":{"cells":{"1":{"text":"姓名","style":7},"2":{"text":"#{hex.customGroup(name)}","style":11,"direction":"right"}},"isDrag":true,"height":40},"7":{"cells":{"1":{"text":"薪水","style":7},"2":{"text":"#{hex.customGroup(salary)}","style":11,"direction":"right"}},"isDrag":true,"height":36},"len":100},"name":"sheet1","fillFormStyle":"default","merges":["A2:L2"]}
```
