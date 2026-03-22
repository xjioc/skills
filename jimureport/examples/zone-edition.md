# 示例6：分版（多表格并排）

**类型：** 分版报表
**特征：** `zonedEditionList` 定义多个独立数据区域，单元格标记 `"zonedEdition":N`

## 关键配置

```json
{
    "zonedEditionList": [
        {"sci":4,"sri":3,"eci":6,"eri":4,"db":"flapi","index":1},
        {"sci":8,"sri":4,"eci":9,"eri":5,"db":"flapi","index":2}
    ]
}
```

## 报表 JSON

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10,"layout":"portrait"},"hidden":{"rows":[],"cols":[],"conditions":{"rows":{},"cols":{}}},"queryFormSetting":{"useQueryForm":false,"dbKey":"","idField":""},"dbexps":[],"dicts":[],"freeze":"A1","dataRectWidth":930,"isViewContentHorizontalCenter":false,"autofilter":{},"validations":[],"cols":{"3":{"width":69},"7":{"width":61},"len":50},"pyGroupEngine":false,"submitHandlers":[],"excel_config_id":"1193411148792549376","hiddenCells":[],"zonedEditionList":[{"sci":4,"sri":3,"eci":6,"eri":4,"db":"flapi","index":1},{"sci":8,"sri":4,"eci":9,"eri":5,"db":"flapi","index":2}],"rows":{"1":{"cells":{"3":{"style":18,"text":"分版示例","merge":[0,1],"height":65},"5":{"merge":[0,2],"height":65,"text":"说明：当报表左侧已有表格，右侧仍需要展示表格时，需使用分版功能","style":20}},"height":65},"2":{"cells":{"1":{"text":"表1","style":7},"5":{"text":"表2","style":7}},"height":41},"3":{"cells":{"0":{"text":"姓名","style":2},"1":{"text":"性别","style":2},"2":{"text":"年龄","style":2},"4":{"text":"省份","style":2,"zonedEdition":1},"5":{"style":2,"zonedEdition":1,"text":"月份"},"6":{"style":2,"zonedEdition":1,"text":"金额"},"8":{"text":"表3","style":8}},"height":35},"4":{"cells":{"0":{"text":"#{jm.name}","style":0},"1":{"text":"#{jm.sex}","style":0},"2":{"text":"#{jm.age}","style":0},"4":{"text":"#{flapi.dept}","style":0,"zonedEdition":1},"5":{"style":0,"zonedEdition":1,"text":"#{flapi.month}月"},"6":{"style":0,"zonedEdition":1,"text":"#{flapi.amount}"},"8":{"text":"年份","style":2,"zonedEdition":2},"9":{"text":"金额","style":2,"zonedEdition":2}},"height":30},"5":{"cells":{"8":{"text":"#{flapi.year}年","style":0,"zonedEdition":2},"9":{"text":"#{flapi.settleamount}","style":0,"zonedEdition":2}}},"len":103},"rpbar":{"show":true,"pageSize":"","btnList":[]},"name":"sheet1","merges":["D1:E1","D2:E2","F2:H2"]}
```
