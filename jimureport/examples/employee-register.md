# 示例10：员工信息登记（带照片）

**类型：** 单据模板（带图片占位）
**特征：** `imgList` 图片占位 + `virtual` 虚拟单元格 + `${employee.xxx}` 单值绑定 + 日期格式化

## 数据绑定

`${employee.num}`、`${employee.name}`、`${employee.sex}`、`${employee.birthday}`、`${employee.nation}`、`${employee.political}`、`${employee.native_place}`、`${employee.height}`、`${employee.weight}`、`${employee.health}`、`${employee.id_card}`、`${employee.education}`、`${employee.school}`、`${employee.major}`、`${employee.address}`、`${employee.zip_code}`、`${employee.email}`、`${employee.phone}`、`${employee.foreign_language}`、`${employee.foreign_language_level}`、`${employee.computer_level}`、`${employee.graduation_time}`、`${employee.arrival_time}`、`${employee.positional_titles}`、`${employee.education_experience}`、`${employee.work_experience}`、`${employee.create_time}`

## 图片占位配置

```json
{
    "imgList": [{
        "row": 3, "col": 6, "colspan": 1, "rowspan": 5,
        "width": "135", "height": "201",
        "src": "https://xxx.png",
        "layer_id": "8mRFFslT5d0Hfyos",
        "offsetX": 0, "offsetY": 0,
        "virtualCellRange": [[3,6]]
    }]
}
```

单元格引用图片：`"virtual":"8mRFFslT5d0Hfyos"` + `"merge":[4,0]`

## 报表 JSON

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10,"layout":"portrait"},"hidden":{"rows":[],"cols":[],"conditions":{"rows":{},"cols":{}}},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":["sex1"],"freeze":"A1","dataRectWidth":710,"autofilter":{},"validations":[],"cols":{"0":{"width":64},"1":{"width":118},"2":{"width":71},"3":{"width":115},"4":{"width":83},"5":{"width":123},"6":{"width":136},"7":{"width":1},"len":50},"excel_config_id":"1316944968992034816","hiddenCells":[],"zonedEditionList":[],"rows":{"1":{"cells":{"0":{"text":"员工信息登记表","merge":[0,6],"style":28}},"height":46},"2":{"cells":{"0":{"text":"编号:","style":29},"1":{"text":"${employee.num}","style":30,"merge":[0,3]},"5":{"text":"填写日期:","style":29},"6":{"text":"${employee.create_time}","style":34}},"isDrag":true,"height":44},"3":{"cells":{"0":{"text":"姓名:","style":29},"1":{"text":"${employee.name}","style":30},"2":{"text":"性别:","style":29},"3":{"text":"${employee.sex}","style":30},"4":{"text":"出生年月:","style":29},"5":{"text":"${employee.birthday}","style":36},"6":{"style":3,"text":" ","merge":[4,0],"virtual":"8mRFFslT5d0Hfyos"}},"isDrag":true,"height":42},"4":{"cells":{"0":{"text":"民族:","style":29},"1":{"text":"${employee.nation}","style":30},"2":{"text":"政治面貌:","style":29},"3":{"text":"${employee.political}","style":30},"4":{"text":"籍贯:","style":29},"5":{"text":"${employee.native_place}","style":30}},"isDrag":true,"height":38},"5":{"cells":{"0":{"text":"身高(cm):","style":29},"1":{"text":"${employee.height}","style":30},"2":{"text":"体重(kg):","style":29},"3":{"text":"${employee.weight}","style":30},"4":{"text":"健康状况:","style":29},"5":{"text":"${employee.health}","style":30}},"isDrag":true,"height":38},"6":{"cells":{"0":{"text":"身份证号:","style":29},"1":{"text":"${employee.id_card}","style":30,"merge":[0,2]},"4":{"text":"学历:","style":29},"5":{"text":"${employee.education}","style":30}},"isDrag":true,"height":40},"7":{"cells":{"0":{"text":"毕业学校:","style":29},"1":{"text":"${employee.school}","style":30,"merge":[0,2]},"4":{"text":"专业:","style":29},"5":{"text":"${employee.major}","style":30}},"isDrag":true,"height":44},"8":{"cells":{"0":{"text":"联系地址:","style":29},"1":{"text":"${employee.address}","style":30,"merge":[0,2]},"4":{"text":"邮编:","style":29},"5":{"text":"${employee.zip_code}","style":30,"merge":[0,1]}},"isDrag":true,"height":45},"9":{"cells":{"0":{"text":"Email:","style":29},"1":{"text":"${employee.email}","style":30,"merge":[0,2]},"4":{"text":"手机号:","style":29},"5":{"text":"${employee.phone}","style":30,"merge":[0,1]}},"isDrag":true,"height":40},"10":{"cells":{"0":{"text":"外语语种:","style":29},"1":{"text":"${employee.foreign_language}","style":30},"2":{"text":"外语水平:","style":29},"3":{"text":"${employee.foreign_language_level}","style":30},"4":{"text":"计算机水平:","style":29},"5":{"text":"${employee.computer_level}","style":30,"merge":[0,1]}},"isDrag":true,"height":41},"11":{"cells":{"0":{"text":"毕业时间:","style":29},"1":{"text":"${employee.graduation_time}","style":34},"2":{"text":"到职时间:","style":29},"3":{"text":"${employee.arrival_time}","style":34},"4":{"text":"职称:","style":29},"5":{"text":"${employee.positional_titles}","style":30,"merge":[0,1]}},"isDrag":true,"height":42},"12":{"cells":{"0":{"text":"教育经历:","style":32},"1":{"text":" ","style":35,"merge":[0,5]}},"isDrag":true,"height":39},"13":{"cells":{"0":{"text":"${employee.education_experience}","style":33,"merge":[0,6]}},"isDrag":true,"height":70},"14":{"cells":{"0":{"text":"工作经历:","style":32},"1":{"merge":[0,5],"style":30,"text":" "}},"height":43},"15":{"cells":{"0":{"text":"${employee.work_experience}","style":30,"merge":[0,6]}},"isDrag":true,"height":61},"len":100},"name":"sheet1","merges":["A2:G2","B3:E3","G4:G8","B7:D7","B8:D8","B9:D9","F9:G9","B10:D10","F10:G10","F11:G11","F12:G12","B13:G13","A14:G14","B15:G15","A16:G16"],"imgList":[{"row":3,"col":6,"colspan":1,"rowspan":5,"width":"135","height":"201","src":"https://static.jeecg.com/designreport/images/QQ截图20210115102648_1610677626114.png","layer_id":"8mRFFslT5d0Hfyos","offsetX":0,"offsetY":0,"virtualCellRange":[[3,6]]}]}
```
