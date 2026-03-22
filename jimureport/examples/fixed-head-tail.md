# 示例8：固定表头表尾

**类型：** 分组报表 + 固定打印表头表尾
**特征：** `fixedPrintHeadRows`/`fixedPrintTailRows` + 横向分组 `groupRight` + 纵向分组 `group` + 动态聚合 `dynamic`

## 关键配置

```json
{
    "fixedPrintHeadRows": [{"sci":1,"eci":3,"sri":1,"eri":2}],
    "fixedPrintTailRows": [{"sri":6,"sci":1,"eri":6,"eci":5}],
    "isGroup": true,
    "groupField": "xs.diqu"
}
```

## 数据绑定语法

- 横向分组（年）：`#{xs.groupRight(year)}`，`direction:"right"`，`aggregate:"group"`，`sort:"desc"`
- 横向分组（月）：`#{xs.groupRight(mouth)}`，`aggregate:"group"`，`direction:"right"`
- 纵向分组（地区）：`#{xs.group(diqu)}`，`aggregate:"group"`，`subtotal:"groupField"`
- 纵向分组（分类）：`#{xs.group(class)}`，`aggregate:"group"`
- 动态聚合（销量）：`#{xs.dynamic(sales)}`，`aggregate:"dynamic"`，`funcname:"SUM"`
- 合计行：`=sum(D4)`
- 斜线表头：`lineStart:"lefttop"`，`text:"地区|销量|时间"`
- 固定表头标记：`fixedHead:1`
- 固定表尾标记：`fixedTail:1`

## 报表 JSON

```json
{"loopBlockList":[],"printConfig":{"layout":"portrait","paper":"A4","isBackend":false,"width":210,"definition":1,"marginX":10,"height":297,"marginY":10},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":[],"freeze":"A1","dataRectWidth":713,"autofilter":{},"validations":[],"cols":{"0":{"width":36},"1":{"width":95},"2":{"width":95},"4":{"width":141},"5":{"width":246},"6":{"width":155},"len":50},"area":{"sri":6,"sci":1,"eri":6,"eci":5,"width":677,"height":25},"excel_config_id":"739738655920574464","zonedEditionList":[],"rows":{"0":{"cells":{"1":{"merge":[0,2],"style":6,"text":"固定表头表尾打印实例"},"5":{"style":30,"text":"说明：本示例在横向分组、纵向分组基础上，添加固定表头表尾。在打印时可显示表头及表尾"}},"height":83},"1":{"cells":{"1":{"lineStart":"lefttop","merge":[1,1],"style":2,"text":"地区|销量|时间","fixedHead":1,"height":74},"2":{"text":"","fixedHead":1},"3":{"style":8,"text":"#{xs.groupRight(year)}年","sort":"desc","fixedHead":1,"aggregate":"group","direction":"right"}},"height":40},"2":{"cells":{"1":{"text":"","fixedHead":1},"2":{"text":"","fixedHead":1},"3":{"style":8,"text":"#{xs.groupRight(mouth)}","sort":"default","fixedHead":1,"aggregate":"group","direction":"right"}},"height":34},"3":{"cells":{"1":{"subtotal":"groupField","style":28,"text":"#{xs.group(diqu)}","aggregate":"group"},"2":{"style":28,"text":"#{xs.group(class)}","aggregate":"group"},"3":{"decimalPlaces":"0","funcname":"SUM","style":29,"text":"#{xs.dynamic(sales)}","aggregate":"dynamic"}},"height":38},"4":{"cells":{"1":{"merge":[0,1],"style":24,"text":"总计"},"3":{"style":25,"text":"=sum(D4)"}},"height":37},"6":{"cells":{"1":{"style":32,"text":"审核：","fixedTail":1},"2":{"style":32,"text":"张三","fixedTail":1},"3":{"style":32,"fixedTail":1},"4":{"style":32,"text":"复审：","fixedTail":1},"5":{"style":32,"text":"李四","fixedTail":1}}},"len":100},"rpbar":{"show":true,"pageSize":"","btnList":[]},"groupField":"xs.diqu","fixedPrintHeadRows":[{"sci":1,"eci":3,"sri":1,"eri":2}],"fixedPrintTailRows":[{"sri":6,"sci":1,"eri":6,"eci":5}],"displayConfig":{},"background":false,"name":"sheet1","isGroup":true,"merges":["B1:D1","B2:C3","B5:C5"]}
```
