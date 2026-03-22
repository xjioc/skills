# 示例9：实习证明

**类型：** 单据模板（带背景图）
**特征：** `background` 背景图 + `${tt.xxx}` 单值绑定 + 自由布局

## 数据绑定

- `${tt.name}` — 姓名
- `${tt.pingjia}` — 评价内容（多行文本，merge跨4行5列）
- `${tt.lingdao}` — 证明人
- `${tt.shijian}` — 日期

## 关键配置

```json
{
    "background": {
        "path": "https://static.jeecg.com/designreport/images/11_1611283832037.png",
        "repeat": "no-repeat",
        "width": "",
        "height": ""
    }
}
```

## 报表 JSON

```json
{"loopBlockList":[],"area":{"sri":28,"sci":9,"eri":28,"eci":9,"width":100,"height":25},"excel_config_id":"1347373863746539520","printConfig":{"layout":"portrait","paper":"A4","isBackend":false,"width":210,"definition":1,"marginX":10,"height":297,"marginY":10},"hiddenCells":[],"zonedEditionList":[],"rows":{"7":{"cells":{"2":{"merge":[0,4],"style":2,"text":"实习证明"}},"height":41},"10":{"cells":{"2":{"style":11,"text":"${tt.name}"},"3":{"merge":[0,3],"style":19,"text":"同学在我公司与 2020年4月1日 至 2020年5月1日 实习。","height":34}},"height":34},"12":{"cells":{"2":{"merge":[3,4],"style":13,"text":"${tt.pingjia}","height":129}},"height":36},"17":{"cells":{"2":{"style":12,"text":"特此证明！"}}},"22":{"cells":{"4":{"style":11,"text":"证明人："},"5":{"style":12,"text":"${tt.lingdao}"}}},"23":{"cells":{"5":{"style":15,"text":"${tt.shijian}"}}},"len":100},"dbexps":[],"dicts":[],"freeze":"A1","dataRectWidth":707,"displayConfig":{},"background":{"path":"https://static.jeecg.com/designreport/images/11_1611283832037.png","repeat":"no-repeat","width":"","height":""},"name":"sheet1","autofilter":{},"validations":[],"cols":{"0":{"width":69},"1":{"width":41},"4":{"width":119},"5":{"width":147},"6":{"width":31},"len":50},"merges":["C8:G8","D11:G11","C13:G16"]}
```
