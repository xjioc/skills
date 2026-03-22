# 示例5：分栏

**类型：** 分栏报表
**特征：** `loopBlockList` 中加 `"loopTime":2` 实现横向循环2次（分2栏）

## 关键配置

```json
{"loopBlockList":[{"sci":1,"sri":2,"eci":5,"eri":5,"index":1,"db":"jm","loopTime":2}]}
```

## 报表 JSON

```json
{"loopBlockList":[{"sci":1,"sri":2,"eci":5,"eri":5,"index":1,"db":"jm","loopTime":2}],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10,"layout":"portrait"},"hidden":{"rows":[],"cols":[]},"dbexps":[],"dicts":[],"freeze":"A1","dataRectWidth":817,"autofilter":{},"validations":[],"cols":{"0":{"width":72},"3":{"width":101},"4":{"width":90},"5":{"width":54},"len":50},"pyGroupEngine":false,"submitHandlers":[],"excel_config_id":"590831722099462144","hiddenCells":[],"zonedEditionList":[],"rows":{"1":{"cells":{"5":{"style":15,"text":"分栏示例","merge":[0,1],"height":59},"8":{"style":9,"text":"说明：需要对多行区域进行循环且分栏展示时，则进行循环块设置并指定横向循环次数","merge":[0,2],"height":59}},"height":59},"2":{"cells":{"1":{"text":"","loopBlock":1},"2":{"text":"职员信息","style":2,"merge":[0,1],"height":34,"loopBlock":1},"4":{"text":"","loopBlock":1},"5":{"text":"","loopBlock":1}},"height":51},"3":{"cells":{"1":{"text":"姓名","style":4,"loopBlock":1},"2":{"text":"性别","style":4,"loopBlock":1},"3":{"text":"职务","style":4,"loopBlock":1},"4":{"text":"联系方式","style":4,"loopBlock":1},"5":{"text":"","loopBlock":1}},"height":31},"4":{"cells":{"1":{"text":"#{jm.name}","style":0,"loopBlock":1},"2":{"style":0,"loopBlock":1,"text":"#{jm.sex}"},"3":{"style":0,"loopBlock":1,"text":"#{jm.update_by}"},"4":{"style":0,"loopBlock":1,"text":"#{jm.jphone}"},"5":{"text":"","loopBlock":1}}},"5":{"cells":{"1":{"text":"","loopBlock":1},"5":{"text":"","loopBlock":1}},"height":34},"len":103},"rpbar":{"show":true,"pageSize":"","btnList":[]},"name":"sheet1","merges":["F2:G2","I2:K2","C3:D3"]}
```
