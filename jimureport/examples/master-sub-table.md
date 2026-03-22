# 示例1：主子表（订货商+订单详情）

**类型：** 主子表报表
**特征：** `${gg.xxx}` 主表单值绑定 + `#{xb.xxx}` 子表列表绑定，linkType=4

## 数据绑定

- 主表（单值）：`${gg.dGoodsCode}`、`${gg.dAddress}`、`${gg.dName}`
- 子表（列表）：`#{xb.id}`、`#{xb.cname}`、`#{xb.cprice}`

## 主子关系配置

### 配置 API

`POST /jmreport/link/saveAndEdit`

### 请求参数

```json
{
    "id": "",
    "reportId": "报表ID（创建报表后获得）",
    "parameter": "{\"main\":\"gg\",\"sub\":\"xb\",\"subReport\":[{\"mainField\":\"id\",\"subParam\":\"did\",\"tableIndex\":1}]}",
    "linkName": "主子报表",
    "mainReport": "gg",
    "subReport": "xb",
    "linkType": "4"
}
```

### 参数说明

| 字段 | 说明 |
|------|------|
| `reportId` | 报表 ID（创建报表后获得的 ID） |
| `linkName` | 关联名称（自定义） |
| `mainReport` | 主表数据集的 `db_code`（这里是 `gg`） |
| `subReport` | 子表数据集的 `db_code`（这里是 `xb`） |
| `linkType` | 关联类型，`4` = 主子表关联 |
| `parameter` | JSON 字符串，定义主子表关联关系 |

### parameter 内部结构

```json
{
    "main": "gg",           // 主表数据集 db_code
    "sub": "xb",            // 子表数据集 db_code
    "subReport": [{
        "mainField": "id",      // 主表关联字段（主键）
        "subParam": "did",      // 子表接收参数名（子表 SQL 中用 ${did} 接收）
        "tableIndex": 1         // 子表序号（从1开始）
    }]
}
```

### 返回示例

```json
{
    "success": true,
    "message": "",
    "code": 0,
    "result": "1194556192647892992",
    "timestamp": 1773916000334
}
```

### 主子表数据绑定规则

- 主表用 **`${主表db_code.字段名}`** 单值绑定（如 `${gg.dGoodsCode}`）
- 子表用 **`#{子表db_code.字段名}`** 列表绑定（如 `#{xb.id}`、`#{xb.cname}`）
- 子表 SQL 需要包含参数占位符，如 `SELECT * FROM order_detail WHERE order_id = '${did}'`
- 预览时 URL 传参 `?did=1` 指定主表记录

## 报表 JSON

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10},"hidden":{"rows":[],"cols":[]},"queryFormSetting":{"useQueryForm":false,"dbKey":"","idField":""},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":[],"freeze":"A1","dataRectWidth":682,"autofilter":{},"validations":[],"cols":{"0":{"width":39},"1":{"width":73},"2":{"width":89},"3":{"width":101},"4":{"width":80},"len":50},"area":{"sri":5,"sci":10,"eri":5,"eci":10,"width":100,"height":51},"pyGroupEngine":false,"submitHandlers":[],"excel_config_id":"537516331017523200","hiddenCells":[],"zonedEditionList":[],"rows":{"0":{"cells":{"1":{"merge":[0,6],"height":0,"text":"订货商信息","style":8}},"height":57},"1":{"cells":{"1":{"text":"订单编号：","style":10},"2":{"merge":[0,2],"height":0,"style":42,"text":"${gg.dGoodsCode}"}},"height":34},"2":{"cells":{"1":{"text":"订单地址：","style":10},"2":{"merge":[0,1],"height":0,"style":42,"text":"${gg.dAddress}"},"4":{"text":"订单日期：","style":10},"5":{"merge":[0,1],"height":0,"style":42,"text":"${gg.dArrivalDate}"}},"height":34},"3":{"cells":{"1":{"text":"订单姓名：","style":10},"2":{"merge":[0,1],"height":0,"style":42,"text":"${gg.dName}"},"4":{"text":"到货日期：","style":10},"5":{"merge":[0,1],"height":0,"style":42,"text":"${gg.dGoodsDate}"}},"height":31},"5":{"cells":{"1":{"text":"订单详情","merge":[0,6],"style":31,"decimalPlaces":"4"}},"height":51},"6":{"cells":{"1":{"text":"商品编码","style":15},"2":{"text":"商品名称","style":15},"3":{"text":"销售时间","style":15},"4":{"text":"销售数据量","style":15},"5":{"text":"定价","style":15},"6":{"text":"优惠价","style":15},"7":{"text":"付款金额","style":15}},"height":42},"7":{"cells":{"1":{"style":18,"text":"#{xb.id}"},"2":{"style":18,"text":"#{xb.cname}"},"3":{"style":18,"text":"#{xb.riqi}"},"4":{"style":18,"text":"#{xb.dtotal}"},"5":{"style":19,"text":"#{xb.cprice}","decimalPlaces":"4"},"6":{"style":19,"text":"#{xb.cprice}","decimalPlaces":"1"},"7":{"style":18,"text":"#{xb.tp}"}}},"10":{"cells":{"1":{"style":39,"text":"备注："}}},"11":{"cells":{"1":{"style":41,"text":"1、查看信息，在浏览器输入"?did=1"或"?did=2"","merge":[0,6],"height":0}},"height":37},"len":102,"-1":{"cells":{"-1":{"text":"#{xb.username}"}}}},"rpbar":{"show":true,"pageSize":"","btnList":[]},"name":"sheet1","styles":[{"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}},{"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]},"align":"center"},{"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]},"align":"center","bgcolor":"#5b9cd6"},{"font":{"size":18}},{"font":{"size":18,"bold":true}},{"align":"center"},{"font":{"size":18,"bold":true},"align":"center"},{"align":"center","bgcolor":"#5b9cd6"},{"font":{"size":18,"bold":true,"name":"宋体"},"align":"center"},{"align":"center","bgcolor":"#5b9cd6","font":{"name":"宋体"}},{"font":{"name":"宋体"}},{"align":"center","bgcolor":"#5b9cd6","font":{"name":"宋体"},"color":"#ffffff"},{"align":"center","bgcolor":"#5b9cd6","font":{"name":"宋体"},"color":"#ffffff","border":{"bottom":["thin","#5b9cd6"],"top":["thin","#5b9cd6"],"left":["thin","#5b9cd6"],"right":["thin","#5b9cd6"]}},{"font":{"name":"宋体"},"border":{"bottom":["thin","#5b9cd6"],"top":["thin","#5b9cd6"],"left":["thin","#5b9cd6"],"right":["thin","#5b9cd6"]}},{"border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]}},{"align":"center","bgcolor":"#5b9cd6","font":{"name":"宋体"},"color":"#ffffff","border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]}},{"font":{"name":"宋体"},"border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]}},{},{"font":{"name":"宋体"},"border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]},"align":"center"},{"font":{"name":"宋体"},"border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]},"align":"center","format":"number"},{"font":{"name":"宋体"},"border":{"bottom":["thin","#bfbfbf"],"top":["thin","#bfbfbf"],"left":["thin","#bfbfbf"],"right":["thin","#bfbfbf"]},"align":"center","format":"normal"},{"font":{"size":18,"bold":false}},{"font":{"size":18,"bold":false,"name":"宋体"}},{"font":{"size":18,"bold":false,"name":"宋体"},"align":"center"},{"font":{"size":18,"bold":true,"name":"宋体"}},{"border":{"bottom":["thin","#000"]}},{"border":{"bottom":["thin","#a5a5a5"]}},{"border":{"bottom":["thin","#262626"]}},{"border":{"bottom":["thin","#595959"]}},{"font":{"size":18,"bold":true,"name":"宋体"},"align":"center","valign":"bottom"},{"font":{"size":18,"bold":true,"name":"宋体"},"align":"left","valign":"bottom"},{"font":{"size":18,"bold":true,"name":"宋体"},"align":"center","valign":"middle"},{"border":{"top":["thin","#595959"],"left":["thin","#595959"]}},{"border":{"top":["thin","#595959"]}},{"border":{"top":["thin","#595959"],"right":["thin","#595959"]}},{"border":{"left":["thin","#595959"]}},{"border":{"right":["thin","#595959"]}},{"border":{"bottom":["thin","#595959"],"left":["thin","#595959"]}},{"border":{"bottom":["thin","#595959"],"right":["thin","#595959"]}},{"border":{"top":["thin","#595959"],"left":["thin","#595959"]},"font":{"name":"宋体"}},{"border":{"left":["thin","#595959"],"right":["thin","#595959"]}},{"border":{"left":["thin","#595959"],"right":["thin","#595959"]},"font":{"name":"宋体"}},{"border":{"bottom":["thin","#595959"]},"font":{"name":"宋体"}}],"freezeLineColor":"rgb(185, 185, 185)","merges":["B1:H1","C2:E2","C3:D3","F3:G3","C4:D4","F4:G4","B6:H6","B12:H12"]}
```
