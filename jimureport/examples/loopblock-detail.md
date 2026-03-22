# 示例4：循环块明细表（员工信息卡片）

**类型：** 循环块报表
**特征：** `loopBlockList` 定义循环区域，每条数据渲染一个卡片，支持二维码 `display:"qrcode"`

## 关键配置

- `loopBlockList`：`[{"sci":1,"sri":2,"eci":7,"eri":5,"index":1,"db":"uiu"}]`
- 二维码：单元格 `"display":"qrcode"` + `displayConfig` 配置宽高颜色

## 报表 JSON

```json
{"loopBlockList":[{"sci":1,"sri":2,"eci":7,"eri":5,"index":1,"db":"uiu"}],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10,"layout":"portrait"},"hidden":{"rows":[],"cols":[],"conditions":{"rows":{},"cols":{}}},"queryFormSetting":{"useQueryForm":false,"dbKey":"","idField":""},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":[],"freeze":"A1","dataRectWidth":688,"isViewContentHorizontalCenter":false,"autofilter":{},"validations":[],"cols":{"0":{"width":30},"1":{"width":94},"2":{"width":96},"3":{"width":81},"4":{"width":93},"5":{"width":88},"6":{"width":90},"7":{"width":116},"8":{"width":22},"len":50},"pyGroupEngine":false,"submitHandlers":[],"excel_config_id":"1176098706643308544","hiddenCells":[],"zonedEditionList":[],"rows":{"1":{"cells":{"1":{"text":"员工信息明细表","merge":[0,5],"style":32}},"height":64},"2":{"cells":{"1":{"text":"姓名：","style":28,"loopBlock":1},"2":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.name}"},"4":{"text":"所在部门：","style":29,"loopBlock":1},"5":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.department}"},"7":{"merge":[2,0],"height":75,"style":9,"text":"#{uiu.tm}","display":"qrcode","loopBlock":1}},"height":42},"3":{"cells":{"1":{"text":"年龄：","style":28,"loopBlock":1},"2":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.age}"},"4":{"text":"学历：","style":29,"loopBlock":1},"5":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.education}"},"7":{"text":"","loopBlock":1}},"height":35},"4":{"cells":{"1":{"text":"性别：","style":28,"loopBlock":1},"2":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.sex}"},"4":{"text":"薪水：","style":29,"loopBlock":1},"5":{"style":30,"merge":[0,1],"loopBlock":1,"text":"#{uiu.salary}"},"7":{"text":"","loopBlock":1}},"height":35},"5":{"cells":{"1":{"text":"","loopBlock":1},"2":{"text":"","loopBlock":1},"3":{"text":"","loopBlock":1},"4":{"text":"","loopBlock":1},"5":{"text":"","loopBlock":1},"6":{"text":"","loopBlock":1},"7":{"text":"","loopBlock":1}},"height":17},"len":100},"rpbar":{"show":true,"pageSize":"","btnList":[]},"displayConfig":{"11":{"text":"#{uiu.tm}","width":117,"height":117,"colorDark":"#000000","colorLight":"#ffffff"}},"name":"sheet1","merges":["B2:G2","C3:D3","F3:G3","H3:H5","C4:D4","F4:G4","C5:D5","F5:G5"]}
```
