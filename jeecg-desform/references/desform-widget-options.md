# 控件 Options 完整参考

每种控件的完整 options 配置。生成时按照此文档的结构填充。

## 通用 options 字段

大部分控件共有以下字段：

```json
{
  "required": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

| 字段 | 说明 |
|------|------|
| `required` | 是否必填 |
| `disabled` | 是否禁用 |
| `hidden` | 是否隐藏 |
| `hiddenOnAdd` | 新增时隐藏 |
| `fieldNote` | 字段备注 |
| `autoWidth` | 宽度百分比（100=整行，50=半行） |

---

## input — 单行文本

```json
{
  "width": "100%",
  "defaultValue": "",
  "required": false,
  "dataType": null,
  "pattern": "",
  "patternMessage": "",
  "placeholder": "",
  "clearable": false,
  "readonly": false,
  "disabled": false,
  "fillRuleCode": "",
  "showPassword": false,
  "unique": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-input` | icon: `icon-input`

## textarea — 多行文本

```json
{
  "width": "100%",
  "defaultValue": "",
  "required": false,
  "disabled": false,
  "pattern": "",
  "patternMessage": "",
  "placeholder": "",
  "readonly": false,
  "unique": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-textarea` | icon: `icon-textarea`

## number — 数字

```json
{
  "width": "",
  "required": false,
  "defaultValue": 0,
  "placeholder": "",
  "precision": null,
  "controls": false,
  "min": 0,
  "minUnlimited": true,
  "max": 100,
  "maxUnlimited": true,
  "step": 1,
  "disabled": false,
  "controlsPosition": "right",
  "unitText": "",
  "unitPosition": "suffix",
  "showPercent": false,
  "align": "left",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

| 字段 | 说明 |
|------|------|
| `precision` | 小数精度，`null`/不设置表示不限制，`0` 表示整数，`1` 保留1位小数，以此类推 |

className: `form-number` | icon: `icon-number`

## integer — 整数

```json
{
  "width": "",
  "placeholder": "请输入整数",
  "required": false,
  "min": 0,
  "minUnlimited": true,
  "max": 100,
  "maxUnlimited": true,
  "step": 1,
  "precision": 0,
  "controls": true,
  "disabled": false,
  "controlsPosition": "right",
  "unitText": "",
  "unitPosition": "suffix",
  "showPercent": false,
  "align": "left",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-integer` | icon: `icon-integer`

## money — 金额

```json
{
  "width": "180px",
  "placeholder": "请输入金额",
  "required": false,
  "unitText": "元",
  "unitPosition": "suffix",
  "precision": 2,
  "hidden": false,
  "disabled": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-money` | icon: `icon-money`

## radio — 单选框组

```json
{
  "inline": true,
  "matrixWidth": 120,
  "defaultValue": "",
  "showType": "default",
  "showLabel": false,
  "useColor": false,
  "colorIteratorIndex": 3,
  "options": [
    { "value": "选项1", "itemColor": "#2196F3" },
    { "value": "选项2", "itemColor": "#08C9C9" },
    { "value": "选项3", "itemColor": "#00C345" }
  ],
  "required": false,
  "width": "",
  "remote": false,
  "remoteOptions": [],
  "props": { "value": "value", "label": "label" },
  "remoteFunc": "",
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-radio` | icon: `icon-radio-active`

**radio 的 advancedSetting.defaultValue 需要 `valueSplit: ",", customConfig: true`**

### radio 使用系统字典

将 `remote` 设为 `"dict"`，添加 `dictCode`，同时在控件顶层添加 `dictOptions`：

```json
{
  "options": {
    "remote": "dict",
    "dictCode": "sys_user_sex",
    "showLabel": true,
    "options": [],
    "remoteOptions": [],
    "props": { "value": "value", "label": "label" }
  },
  "dictOptions": [
    { "value": "1", "label": "男" },
    { "value": "2", "label": "女" }
  ]
}
```

## checkbox — 多选框组

```json
{
  "inline": true,
  "matrixWidth": 120,
  "defaultValue": [],
  "showLabel": false,
  "showType": "default",
  "useColor": false,
  "colorIteratorIndex": 3,
  "options": [
    { "value": "选项1", "itemColor": "#2196F3" },
    { "value": "选项2", "itemColor": "#08C9C9" },
    { "value": "选项3", "itemColor": "#00C345" }
  ],
  "required": false,
  "width": "",
  "remote": false,
  "remoteOptions": [],
  "props": { "value": "value", "label": "label" },
  "remoteFunc": "",
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-checkbox` | icon: `icon-checkbox`

**checkbox 的 advancedSetting.defaultValue 需要 `valueSplit: ",", customConfig: true`**

### checkbox 使用系统字典

同 radio/select，将 `remote` 设为 `"dict"`，添加 `dictCode`：

```json
{
  "options": {
    "remote": "dict",
    "dictCode": "sys_permission_type",
    "showLabel": true,
    "options": [],
    "remoteOptions": [],
    "props": { "value": "value", "label": "label" }
  },
  "dictOptions": [
    { "value": "1", "label": "菜单" },
    { "value": "2", "label": "按钮" }
  ]
}
```

## select — 下拉选择框

```json
{
  "defaultValue": "",
  "multiple": false,
  "disabled": false,
  "clearable": true,
  "placeholder": "",
  "required": false,
  "showLabel": false,
  "showType": "default",
  "width": "",
  "useColor": false,
  "colorIteratorIndex": 3,
  "options": [
    { "value": "下拉框1", "itemColor": "#2196F3" },
    { "value": "下拉框2", "itemColor": "#08C9C9" },
    { "value": "下拉框3", "itemColor": "#00C345" }
  ],
  "remote": false,
  "filterable": false,
  "remoteOptions": [],
  "props": { "value": "value", "label": "label" },
  "remoteFunc": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-select` | icon: `icon-select`

**select 的 advancedSetting.defaultValue 需要 `valueSplit: ",", customConfig: true`**

### select 使用系统字典

将 `remote` 设为 `"dict"`，添加 `dictCode`，同时在控件顶层添加 `dictOptions`：

```json
{
  "options": {
    "remote": "dict",
    "dictCode": "priority",
    "showLabel": true,
    "options": [],
    "remoteOptions": [],
    "props": { "value": "value", "label": "label" }
  },
  "dictOptions": [
    { "value": "L", "label": "低" },
    { "value": "M", "label": "中" },
    { "value": "H", "label": "高" }
  ]
}
```

## date — 日期选择器

```json
{
  "defaultValue": "",
  "defaultValueType": 1,
  "readonly": false,
  "disabled": false,
  "editable": true,
  "clearable": true,
  "placeholder": "",
  "startPlaceholder": "",
  "endPlaceholder": "",
  "designType": "date",
  "type": "date",
  "format": "yyyy-MM-dd",
  "timestamp": true,
  "required": false,
  "width": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-date` | icon: `icon-date`

**日期范围选择：** 将 `type` 改为 `"daterange"`，`designType` 改为 `"daterange"`

## time — 时间选择器

```json
{
  "defaultValue": "",
  "inputDefVal": false,
  "readonly": false,
  "disabled": false,
  "editable": true,
  "clearable": true,
  "placeholder": "",
  "startPlaceholder": "",
  "endPlaceholder": "",
  "isRange": false,
  "arrowControl": false,
  "format": "HH:mm:ss",
  "required": false,
  "width": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-time` | icon: `icon-time`

## switch — 开关

```json
{
  "defaultValue": false,
  "disabled": false,
  "activeValue": "Y",
  "inactiveValue": "N",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-switch` | icon: `icon-switch`

## rate — 评分

```json
{
  "defaultValue": 0,
  "max": 5,
  "disabled": false,
  "allowHalf": false,
  "required": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-rate` | icon: `icon-rate`

**rate 有 defaultRules：**
```json
"defaultRules": [{ "type": "validator", "message": "", "trigger": "change" }]
```

## color — 颜色选择器

```json
{
  "defaultValue": "",
  "disabled": false,
  "showAlpha": false,
  "required": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-color` | icon: `icon-color`

## slider — 滑块

```json
{
  "defaultValue": 0,
  "disabled": false,
  "required": false,
  "min": 0,
  "max": 100,
  "step": 1,
  "showInput": false,
  "showPercent": false,
  "range": false,
  "width": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-slider` | icon: `icon-slider`

## phone — 手机

```json
{
  "width": "300px",
  "defaultValue": "",
  "required": false,
  "placeholder": "",
  "readonly": false,
  "disabled": false,
  "unique": false,
  "hidden": false,
  "showVerifyCode": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-input-phone` | icon: `icon-mobile-phone`

**phone 有 defaultRules：**
```json
"defaultRules": [
  { "type": "phone", "message": "请输入正确的手机号码" },
  { "type": "validator", "message": "", "trigger": "blur" }
]
```

## email — 邮箱

```json
{
  "width": "300px",
  "defaultValue": "",
  "required": false,
  "placeholder": "",
  "readonly": false,
  "disabled": false,
  "unique": false,
  "hidden": false,
  "showVerifyCode": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-input-email` | icon: `icon-email`

**email 有 defaultRules：**
```json
"defaultRules": [
  { "type": "email", "message": "请输入正确的邮箱地址" },
  { "type": "validator", "message": "", "trigger": "blur" }
]
```

## imgupload — 图片上传

```json
{
  "defaultValue": [],
  "size": { "width": 100, "height": 100 },
  "width": "",
  "tokenFunc": "funcGetToken",
  "token": "",
  "domain": "http://img.h5huodong.com",
  "disabled": false,
  "length": 9,
  "multiple": true,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-tupian` | icon: `icon-tupian`

## file-upload — 文件上传

```json
{
  "defaultValue": [],
  "token": "",
  "length": 0,
  "drag": false,
  "listStyleType": "card",
  "multiple": false,
  "multipleDown": true,
  "disabled": false,
  "buttonText": "点击上传文件",
  "tokenFunc": "funcGetToken",
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-file-upload` | icon: `icon-shangchuan`

## editor — 富文本编辑器

```json
{
  "defaultValue": "",
  "width": "100%",
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": ""
}
```

className: `form-editor` | icon: `icon-fuwenbenkuang`

> **不需要 card 容器，无 autoWidth 字段**

## markdown — Markdown 编辑器

```json
{
  "defaultValue": "",
  "width": "100%",
  "height": 300,
  "viewerAutoHeight": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": ""
}
```

className: `form-markdown` | icon: `icon-markdown`

> **不需要 card 容器，无 autoWidth 字段**

## buttons — 按钮

```json
{
  "text": "按钮",
  "icon": "",
  "type": "default",
  "btnSize": "default",
  "plain": false,
  "round": false,
  "circle": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-buttons` | icon: `icon-btn2` | hideLabel: `true`

**buttons 有 event 字段：**
```json
"event": { "click": "console.log('hello,world!')" }
```

## text — 文本

```json
{
  "text": "这里是一段文本",
  "width": "100%",
  "align": "left",
  "verticalAlign": "top",
  "fontSize": 16,
  "lineHeight": "",
  "fontColor": "#4c4c4c",
  "fontBold": false,
  "fontItalic": false,
  "fontUnderline": false,
  "fontLineThrough": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-text` | icon: `icon-text` | hideLabel: `true`

## divider — 分隔符

```json
{
  "heightNumber": 48,
  "type": "horizontal",
  "text": "",
  "position": "center",
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": ""
}
```

className: `form-divider` | icon: `icon-divider` | hideLabel: `true` | formItemMargin: `true`

> **不需要 card 容器，无 autoWidth 字段**

## area-linkage — 省市级联动

```json
{
  "width": "",
  "placeholder": "请选择",
  "areaLevel": 3,
  "defaultValue": "",
  "clearable": true,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-area-linkage` | icon: `icon-jilianxuanze`

`areaLevel`：2=省市，3=省市区

## map — 地图

```json
{
  "width": "100%",
  "height": "300px",
  "zoom": 15,
  "point": { "lng": 116.397467, "lat": 39.908806 },
  "mapSettings": {
    "dragging": true, "scrollWheelZoom": true, "doubleClickZoom": true,
    "keyboard": false, "inertialDragging": true, "continuousZoom": true, "pinchToZoom": true
  },
  "mapControls": {
    "navigation": true, "geolocation": true, "scale": true,
    "mapType": true, "panorama": false, "overviewMap": false
  },
  "disabled": false, "hidden": false, "hiddenOnAdd": false,
  "required": false, "fieldNote": "",
  "defaultValue": "116.397467,39.908806"
}
```

className: `form-map` | icon: `icon-map`

> **不需要 card 容器，无 autoWidth 字段**

## location — 定位

```json
{
  "width": "100%",
  "defaultValue": "",
  "defaultCurrent": false,
  "showLngLat": false,
  "showMap": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-location` | icon: `icon-location`

## capital-money — 大写金额

```json
{
  "moneyWidgetKey": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-money` | icon: `icon-money`

`moneyWidgetKey`：关联的 money 控件的 key，自动将金额转大写

## barcode — 条码

```json
{
  "maxWidth": 180,
  "codeType": "barcode",
  "sourceModel": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-barcode` | icon: `icon-tiaoma`

`codeType`：`"barcode"` 或 `"qrcode"`

## text-compose — 文本组合

```json
{
  "expression": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-text-compose` | icon: `icon-zuhe`

## auto-number — 自动编号

```json
{
  "numberRules": [
    { "type": "number", "mode": 1, "start": 1, "reset": 0, "length": 4, "continue": false }
  ],
  "generateOnAdd": true,
  "placeholder": "${title}自动生成，不需要填写",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-auto-number` | icon: `icon-hashtag`

**numberRules[] 元素结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 规则类型：`"number"` 序号 / `"create_date"` 日期 / `"text"` 固定文本 / `"field"` 字段引用 |
| `mode` | number | number 时：`1` = 自然数（1,2,3...），`2` = 指定位数（0001,0002...） |
| `start` | number | number 时：起始值（默认 1） |
| `reset` | number | number 时：重置规则 `0`=不重置 / `1`=每天 / `2`=每周 / `3`=每月 / `4`=每年 |
| `length` | number | number 时（mode=2）：指定位数（如 4 → 0001） |
| `continue` | boolean | number 时（mode=2）：超出指定位数时是否继续递增 |
| `dateFormat` | string | create_date 时：日期格式（如 `"yyyyMMdd"`） |
| `value` | string | text 时：固定文本内容；field 时：引用字段 model |

## select-user — 用户组件

```json
{
  "keyMaps": [],
  "defaultValue": "",
  "defaultLogin": false,
  "placeholder": "",
  "width": "100%",
  "multiple": false,
  "disabled": false,
  "customReturnField": "username",
  "hidden": false,
  "dataAuthType": "member",
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-select-user` | icon: `icon-user-circle`

`defaultLogin`：true 时默认填充当前登录用户（仅 add/preview 模式生效）

**keyMaps[] 元素结构**（选择用户后自动回填其他字段）：

```json
[
  { "source": "realname", "target": "user_name_field_model" },
  { "source": "orgCode", "target": "org_field_model" }
]
```

`source` 为用户属性名（realname/orgCode/phone/email 等），`target` 为本表其他字段的 model。选择用户后自动将 source 属性值回填到 target 字段。

## select-depart — 部门组件

```json
{
  "keyMaps": [],
  "defaultValue": "",
  "defaultLogin": false,
  "placeholder": "",
  "width": "100%",
  "multiple": false,
  "disabled": false,
  "customReturnField": "id",
  "hidden": false,
  "dataAuthType": "member",
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-select-depart` | icon: `icon-depart`

## select-depart-post — 岗位组件

```json
{
  "keyMaps": [],
  "defaultValue": "",
  "defaultLogin": false,
  "placeholder": "",
  "width": "100%",
  "multiple": false,
  "disabled": false,
  "customReturnField": "id",
  "hidden": false,
  "dataAuthType": "member",
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-select-depart` | icon: `icon-gangwei`

## org-role — 组织角色

```json
{
  "defaultValue": "",
  "defaultLogin": false,
  "placeholder": "选择组织角色",
  "width": "100%",
  "multiple": false,
  "disabled": false,
  "hidden": false,
  "dataAuthType": "member",
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-org-role` | icon: `icon-zuzhijuese`

## select-tree — 下拉树

```json
{
  "defaultValue": "",
  "placeholder": "",
  "width": "",
  "disabled": false,
  "multiple": false,
  "dataFrom": "category",
  "conf": {
    "category": { "code": "B02" },
    "table": {
      "name": "", "code": "", "text": "",
      "pidField": "", "rootPid": "", "leaf": "",
      "converIsLeafVal": true
    },
    "condition": "",
    "conditionOnlyRoot": true
  },
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-select-tree` | icon: `icon-tree`

## ocr — 文本识别

```json
{
  "type": "normal",
  "fieldMapping": { "content": "input_xxx" },
  "hidden": false,
  "disabled": false,
  "required": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-ocr` | icon: `icon-ocr-a`

`fieldMapping.content`：识别结果映射到的目标控件 model

## summary — 汇总控件

用于汇总子表列数据（如求和、计数等），将子表某一列的聚合结果显示在主表中。

```json
{
  "linkTable": "sub_table_design_xxx",
  "field": "money_xxx",
  "summary": "inner-sum",
  "filter": { "enabled": false, "rules": [], "matchType": "AND" },
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": "",
  "autoWidth": 50
}
```

className: `form-summary` | icon: `icon-sigma`

| 字段 | 说明 |
|------|------|
| `linkTable` | 关联的子表 model（sub-table-design 控件的 model） |
| `field` | 要汇总的子表列 model（如 `money_xxx`、`formula_xxx`），或内置值 `"inner-record-count"`（子表记录数） |
| `summary` | 汇总类型：`"inner-sum"`（求和）、`"inner-avg"`（平均）、`"inner-max"`（最大）、`"inner-min"`（最小）；当 `field` 为 `"inner-record-count"` 时留空 |
| `filter` | 过滤条件，`enabled: true` 时仅对满足条件的子表行进行汇总 |

**filter 子结构**：
```json
{
  "enabled": true,
  "matchType": "AND",
  "rules": [
    { "field": "子表字段model", "rule": "eq", "value": "过滤值" }
  ]
}
```

> **典型用法：** 主表需要显示子表某列的合计金额时，使用 `SUMMARY(name, sub_table_model, field_model, summary_type='inner-sum')`，不要用 `FORMULA`。

### summary 日期变体

在 `linkageComponents` 中还存在一个带 `isSummary: true` 标记的 date 控件变体，用于对日期类型字段的汇总。其 type 仍为 `date`，但通过 `isSummary` 标记与普通 date 区分。此变体在内部通过 `summaryTypeBefore` 常量 (`'__summary__'`) 进行识别。

## sub-table-design — 设计子表

```json
{
  "isWordStyle": false,
  "isWordInnerGrid": false,
  "gutter": 0,
  "columnNumber": 2,
  "operationMode": 1,
  "justify": "start",
  "align": "top",
  "defaultValue": [],
  "subTableName": "",
  "defaultRows": 0,
  "showCheckbox": true,
  "showNumber": true,
  "showRowButton": false,
  "allowAdd": true,
  "autoHeight": true,
  "defaultValType": "none",
  "hidden": false,
  "hiddenOnAdd": false,
  "required": false,
  "fieldNote": ""
}
```

className: `form-sub-table` | icon: `icon-table`

> **不需要 card 容器。子控件结构见 desform-examples.md**

## formula — 公式

```json
{
  "type": "number",
  "mode": "SUM",
  "expression": "",
  "decimal": 2,
  "thousand": true,
  "percent": false,
  "unitPosition": "suffix",
  "unitText": "",
  "emptyAsZero": true,
  "dateBegin": "",
  "dateEnd": "",
  "dateFormatMethod": 1,
  "datePrintUnit": "m",
  "dateAddExp": "",
  "datePrintFormat": "YYYY-MM-DD",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-formula` | icon: `icon-gongshibianji`

**表达式格式：** 使用 `$model$` 引用字段（每个字段引用以 `$` 开头和结尾）。例如：
- SUM: `"expression": "$money_xxx$$number_xxx$"`（两个字段相加）
- PRODUCT: `"expression": "$money_xxx$$integer_xxx$"`（两个字段相乘）
- CUSTOM: `"expression": "$field1$ + $field2$ - $field3$"`（自定义运算）

> **注意：** 子表内的 formula 控件引用同行其他列，格式相同。

**数字模式 (`type: "number"`)：**
| mode | 说明 |
|------|------|
| `SUM` | 求和（选择多个字段相加） |
| `AVERAGE` | 平均值 |
| `MAX` | 最大值 |
| `MIN` | 最小值 |
| `PRODUCT` | 乘积 |
| `custom` | 自定义公式，使用 `expression` 字段 |

**日期模式 (`type: "date"`)：**
| mode | 说明 |
|------|------|
| `DATEIF` | 两个日期之差 |
| `DATEADD` | 日期加减运算 |
| `NOW_DATEIF` | 当前日期与某日期之差 |

## link-record — 关联记录

```json
{
  "sourceCode": "",
  "showMode": "single",
  "showType": "card",
  "titleField": "",
  "showFields": [],
  "allowView": true,
  "allowEdit": true,
  "allowAdd": true,
  "allowSelect": true,
  "buttonText": "添加记录",
  "twoWayModel": "",
  "dataSelectAuth": "all",
  "filters": [
    {
      "matchType": "AND",
      "rules": []
    }
  ],
  "search": {
    "enabled": false,
    "field": "",
    "rule": "like",
    "afterShow": false,
    "fields": []
  },
  "createMode": {
    "add": true,
    "select": false,
    "params": {
      "selectLinkModel": ""
    }
  },
  "width": "100%",
  "defaultValue": "",
  "defaultValType": "none",
  "required": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-link-record` | icon: **`icon-link`**（注意：不是 `icon-link-record`！）

**控件顶层属性**（与 `type`/`key`/`model` 同级，不在 options 内）：

| 属性 | 说明 |
|------|------|
| `isSubTable` | 是否为子表模式（一对多），设为 `true` 时不需要 card 容器 |
| `isSelf` | 是否为自关联（关联自身表单） |

**options 字段说明：**

| 字段 | 说明 |
|------|------|
| `sourceCode` | 来源表单编码（desformCode） |
| `showMode` | `"single"`（单条）或 `"many"`（多条） |
| `showType` | `"card"`（卡片）、`"select"`（下拉）、`"table"`（表格） |
| `titleField` | **必填** — 来源表单的标题字段 model（用于下拉/卡片显示） |
| `showFields` | 要在关联视图中展示的来源表字段 model 列表 |
| `twoWayModel` | 双向关联的反向字段 model |
| `dataSelectAuth` | `"all"` 或 `"read"`（数据权限范围） |

> **showMode="many" 或 showType="table" 时不需要 card 容器**

### link-record 重要注意事项（实战踩坑）

1. **`advancedSetting.defaultValue.customConfig` 必须为 `true`**
2. **`allowView`、`allowEdit`、`allowAdd`、`allowSelect` 必须全部设为 `true`**（4 个操作选项默认全部勾选，否则关联记录功能不完整）
3. **`titleField` 必须填源表的真实标题字段 model**（如 `input_xxx`），否则关联记录无法正常显示
4. **`showFields` 建议填入源表中需要展示的字段 model 列表**，提升选择体验
5. **icon 是 `icon-link`** 而非 `icon-link-record`，写错会导致控件显示异常

## link-field — 他表字段

```json
{
  "linkRecordKey": "",
  "showField": "",
  "saveType": "view",
  "fieldType": "",
  "fieldOptions": {},
  "width": "100%",
  "defaultValue": "",
  "readonly": false,
  "disabled": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-link-field` | icon: **`icon-field`**（注意：不是 `icon-link-field`！）

| 字段 | 说明 |
|------|------|
| `linkRecordKey` | 关联记录控件的 **key**（不是 model！） |
| `showField` | 要显示的来源表字段的 **model** |
| `saveType` | `"view"`（仅显示）或 `"save"`（保存到当前表） |
| `fieldType` | 来源字段的实际控件类型（如 `"input"`, `"select-user"`, `"money"` 等） |
| `fieldOptions` | 来源字段的相关 options 子集（如 select-user 需 `{"multiple": false, "customReturnField": "username"}`） |

> **必须与一个 link-record 控件配对使用**

### link-field 重要注意事项（实战踩坑）

1. **link-field 不需要 `advancedSetting`** — 与其他控件不同，link-field 没有此字段
2. **icon 是 `icon-field`** 而非 `icon-link-field`
3. **`fieldType` 必须填来源字段的真实控件类型**，不能一律写 `"input"`
4. **`fieldOptions` 需包含来源字段类型相关的配置**，例如 select-user 需要 `{"multiple": false, "customReturnField": "username"}`
5. **`linkRecordKey` 填的是 link-record 控件的 key（如 `1773457559119_461003`）**，不是 model（如 `link_record_xxx`）

## hand-sign — 手写签名

```json
{
  "disabled": false,
  "required": false,
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-hand-sign` | icon: `icon-signature`

> `desform_utils.py` 生成时会额外传入 `"width": "100%"` 和 `"height": "200px"` 优化显示效果，但源码默认 options 不含这两个字段。

## oa-approval-comments — OA审批意见

```json
{
  "width": "100%",
  "required": false,
  "disabled": false,
  "placeholder": "",
  "hidden": false,
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-oa-approval-comments` | icon: `icon-input`

OA 流程审批意见控件，用于 BPM 审批场景。

## table-dict — 表字典

```json
{
  "width": "100%",
  "defaultValue": "",
  "placeholder": "点击选择表字典",
  "showIcon": true,
  "iconName": "icon-popup",
  "disabled": false,
  "multiple": false,
  "clearable": true,
  "style": "select",
  "dictTable": "",
  "dictCode": "",
  "dictText": "",
  "hidden": false,
  "required": false,
  "filterable": true,
  "queryScope": "cgreport",
  "hiddenOnAdd": false,
  "fieldNote": "",
  "autoWidth": 100
}
```

className: `form-dict` | icon: `icon-dict`

| 字段 | 说明 |
|------|------|
| `style` | 展示方式：`"select"`（下拉模糊搜索）或 `"popup"`（弹窗选择） |
| `dictTable` | 表名 |
| `dictCode` | 存储字段（value） |
| `dictText` | 显示字段（label） |
| `filterable` | 是否可搜索（仅 style=select 时有效） |
| `queryScope` | 查询作用域：`"cgreport"`（Online报表，默认）或 `"database"`（数据库表） |
| `showIcon` | 是否显示图标 |
| `iconName` | 图标名（默认 `"icon-popup"`） |
