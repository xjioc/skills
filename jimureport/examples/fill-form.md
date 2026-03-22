# 示例3：填报表单（员工信息登记表）

**类型：** 填报表单
**特征：** `fillForm` 组件配置，`submitHandlers` 提交处理器，18种填报组件

## 填报组件类型

| componentFlag | component | 说明 |
|---|---|---|
| `input-text` | Input | 文本输入 |
| `input-textarea` | Input | 多行文本 |
| `InputNumber` | InputNumber | 数字输入 |
| `DatePicker-date` | DatePicker | 日期选择 |
| `DatePicker-time` | DatePicker | 日期时间 |
| `TimePicker` | TimePicker | 时间选择 |
| `JRadio` | JRadio | 单选 |
| `JCheckbox` | JCheckbox | 多选 |
| `JSelect` | JSelect | 下拉选择 |
| `JSelectTree` | JSelectTree | 树形选择 |
| `JUploadImage` | JUploadImage | 图片上传 |
| `JUploadFile` | JUploadFile | 文件上传 |
| `JAreaLinkage` | JAreaLinkage | 省市区联动 |
| `JDepartment` | JDepartment | 部门选择 |
| `JRole` | JRole | 角色选择 |
| `JUser` | JUser | 用户选择 |
| `JSwitch` | JSwitch | 开关 |
| `JMoney` | JMoney | 金额输入 |
| `ColorPicker` | ColorPicker | 颜色选择 |

## 填报组件结构

```json
{
    "fillForm": {
        "componentFlag": "JSelect",
        "component": "JSelect",
        "field": "字段名",
        "required": false,
        "requiredTip": "不能为空~",
        "dataSource": "dict|static|api",
        "options": [{"label":"选项1","value":"1"}],
        "dictCode": "字典编码",
        "dictName": "字典名称",
        "apiUrl": "远程API地址",
        "multiple": false,
        "dbFieldBind": [{"dbTable":"表名","dbField":"字段名"}]
    }
}
```

## 提交处理器

```json
{
    "submitHandlers": [{
        "type": "api",
        "code": "api",
        "name": "api",
        "isMain": true,
        "isEdit": true,
        "apiUrl": "http://xxx/jmreport/test/submit/handle"
    }]
}
```

## 报表 JSON

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"paper":"A4","width":210,"height":297,"definition":1,"isBackend":false,"marginX":10,"marginY":10,"layout":"portrait","printCallBackUrl":""},"hidden":{"rows":[],"cols":[]},"queryFormSetting":{"useQueryForm":false,"dbKey":"","idField":""},"dbexps":[],"dicts":[],"fillFormToolbar":{"show":true,"btnList":["save","subTable_add","verify","subTable_del","print","close","first","prev","next","paging","total","last","exportPDF","exportExcel","exportWord"]},"freeze":"A1","dataRectWidth":701,"isViewContentHorizontalCenter":false,"autofilter":{},"validations":[],"cols":{"0":{"width":27},"1":{"width":79},"2":{"width":100},"3":{"width":74},"4":{"width":105},"5":{"width":85},"6":{"width":131},"len":100},"area":false,"pyGroupEngine":false,"submitHandlers":[{"type":"api","code":"api","name":"api","isMain":true,"isEdit":true,"apiUrl":"http://4350302q6b.51vip.biz/jmreport/test/submit/handle"}],"excel_config_id":"1174596178550280192","hiddenCells":[],"zonedEditionList":[],"rows":{"0":{"cells":{"1":{"merge":[1,6],"height":45,"text":"员工信息登记表","style":6}},"height":23},"2":{"cells":{"1":{"text":"编号","style":7,"fillFormLabel":"*"},"2":{"fillForm":{"componentFlag":"input-text","component":"Input","field":"no","value":"","defaultValue":"","placeholder":"","required":false,"requiredTip":"不能为空~","pattern":"","patternErrorTip":""},"style":7,"text":" "},"3":{"text":"年龄","style":7},"4":{"fillForm":{"componentFlag":"InputNumber","component":"InputNumber","field":"age","placeholder":"","required":false,"requiredTip":"不能为空~","precision":0,"isLimitMinNum":false,"minNum":0,"isLimitMaxNum":false,"maxNum":100,"dbFieldBind":[{"dbTable":"test_form_submit","dbField":"age"}]},"style":7,"text":" "},"5":{"text":"填写时间","style":7},"6":{"fillForm":{"componentFlag":"DatePicker-time","component":"DatePicker","field":"create_time","placeholder":"","required":false,"requiredTip":"不能为空~","dateFormat":"yyyy-MM-dd HH:mm:ss","defaultValue":""},"style":7,"text":" "},"7":{"merge":[3,0],"height":180,"fillForm":{"componentFlag":"JUploadImage","component":"JUploadImage","field":"photo","value":"","defaultValue":"","placeholder":"","required":false,"requiredTip":"不能为空~","multiple":false,"maxUploadNum":1,"h_align":"center"},"style":7,"text":" "}},"height":45},"3":{"cells":{"1":{"text":"姓名","style":7,"fillFormLabel":"*"},"2":{"text":" ","fillForm":{"componentFlag":"input-text","component":"Input","field":"name","placeholder":"","required":true,"requiredTip":"不能为空~","dbFieldBind":[{"dbTable":"test_form_submit","dbField":"name"},{"dbTable":"test_form_submit1","dbField":"name"}],"label":"A5","labelText":"姓名","pattern":"","patternErrorTip":""}},"3":{"text":"性别","style":7},"4":{"fillForm":{"componentFlag":"JRadio","component":"JRadio","field":"sex","dataSource":"dict","options":[{"label":"男","value":"1"},{"label":"女","value":"2"}],"dictCode":"sex1","dictName":"性别"},"style":8,"text":" "},"5":{"text":"出生日期","style":7},"6":{"fillForm":{"componentFlag":"DatePicker-date","component":"DatePicker","field":"brithday","dateFormat":"yyyy-MM-dd","dateShowType":"date"},"style":7,"text":" "}},"height":45},"4":{"cells":{"1":{"text":"民族","style":7,"fillFormLabel":"*"},"2":{"fillForm":{"componentFlag":"JSelect","component":"JSelect","field":"nation","dataSource":"dict","dictCode":"minzu","dictName":"民族"},"style":7,"text":" "},"3":{"text":"政治面貌","style":7},"4":{"fillForm":{"componentFlag":"JSelect","component":"JSelect","field":"politics","dataSource":"api","apiUrl":"https://bootapi.jeecg.com/jmreport/test/submit/dict/political"},"style":7,"text":" "},"5":{"text":"籍贯","style":7},"6":{"fillForm":{"componentFlag":"JAreaLinkage","component":"JAreaLinkage","field":"native_place","areaType":"region","dbFieldBind":[{"dbTable":"test_form_submit","dbField":"native_place"}]},"style":7,"text":" "}},"height":45},"9":{"cells":{"1":{"text":"教育经历","merge":[0,6],"height":31,"style":8}},"height":31},"10":{"cells":{"1":{"merge":[0,6],"height":83,"fillForm":{"componentFlag":"input-textarea","component":"Input","field":"education","dbFieldBind":[{"dbTable":"test_form_submit","dbField":"education"}]},"style":7,"text":" "}},"height":83},"13":{"cells":{"1":{"text":"爱好","style":7},"2":{"merge":[0,5],"height":45,"fillForm":{"componentFlag":"JCheckbox","component":"JCheckbox","field":"fruity","dataSource":"dict","dictCode":"aihao","dictName":"爱好","dbFieldBind":[{"dbTable":"test_form_submit","dbField":"fruity"}]},"style":7,"text":" "}},"height":45},"16":{"cells":{"1":{"text":"直属领导","style":7},"2":{"fillForm":{"componentFlag":"JUser","component":"JUser","field":"leader","multiple":false,"apiUrl":"https://bootapi.jeecg.com/jmreport/test/getUserList"},"merge":[0,2],"style":7,"text":" "},"5":{"style":7,"text":"是否启用"},"6":{"style":10,"text":" ","merge":[0,1],"fillForm":{"componentFlag":"JSwitch","component":"JSwitch","field":"status","switchOpen":"Y","switchClose":"N","h_align":"center"}}},"height":45},"len":201},"rpbar":{"show":true,"pageSize":"","btnList":[]},"name":"sheet1","styles":[{"align":"center"},{"align":"center","valign":"middle"},{"align":"center","valign":"middle","font":{"size":16}},{"font":{"size":16}},{"align":"center","valign":"middle","font":{"size":16,"bold":true}},{"font":{"size":16,"bold":true}},{"align":"center","valign":"middle","font":{"size":16,"bold":true},"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}},{"border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}},{"align":"center","border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}},{"align":"center","border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]},"valign":"middle"},{"align":"right","border":{"bottom":["thin","#000"],"top":["thin","#000"],"left":["thin","#000"],"right":["thin","#000"]}}],"freezeLineColor":"rgb(185, 185, 185)","merges":["B1:H2","H3:H6","C7:E7","G7:H7","C8:E8","G8:H8","C9:E9","G9:H9","B10:H10","B11:H11","B12:H12","B13:H13","C14:H14","C15:E15","G15:H15","C16:E16","G16:H16","C17:E17","G17:H17","C18:E18","G18:H18"]}
```
