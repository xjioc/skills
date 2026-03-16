# desformDesignJson Schema 参考

## 顶层结构

```json
{
  "list": [ /* 控件列表 */ ],
  "config": { /* 全局表单配置 */ }
}
```

## 全局配置（config）完整字段

```json
{
  "formStyle": "normal",
  "titleField": "input_xxx",
  "showHeaderTitle": true,
  "labelWidth": 100,
  "labelPosition": "top",
  "size": "small",
  "dialogOptions": {
    "top": 20,
    "width": 1000,
    "padding": { "top": 25, "right": 25, "bottom": 30, "left": 25 }
  },
  "disabledAutoGrid": false,
  "designMobileView": false,
  "enableComment": true,
  "hasWidgets": ["input", "card", "textarea"],
  "defaultLoadLargeControls": false,
  "expand": { "js": "", "css": "", "url": { "js": "", "css": "" } },
  "transactional": true,
  "customRequestURL": [{ "url": "" }],
  "disableMobileCss": true,
  "allowExternalLink": false,
  "externalLinkShowData": false,
  "headerImgUrl": "",
  "externalTitle": "",
  "enableNotice": false,
  "noticeMode": "external",
  "noticeType": "system",
  "noticeReceiver": "",
  "allowPrint": false,
  "allowJmReport": false,
  "jmReportURL": "",
  "bizRuleConfig": [],
  "bigDataMode": false
}
```

**关键字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `titleField` | String | 是 | 标题字段的 model key（列表页显示用，通常指向第一个 input） |
| `hasWidgets` | String[] | 是 | 已使用的所有控件类型（包括 `card`），自动维护 |
| `labelPosition` | String | 否 | 标签位置：`"top"` / `"left"` / `"right"` |
| `size` | String | 否 | 控件尺寸：`"small"` / `"default"` / `"large"` |

## 控件列表（list）

list 是控件数组。**大部分控件被包裹在 `card` 容器中**。

### card 容器结构

```json
{
  "key": "{timestamp}_{random6}",
  "type": "card",
  "isAutoGrid": true,
  "isContainer": true,
  "list": [ /* 1~2 个子控件 */ ],
  "options": {},
  "model": "card_{timestamp}_{random6}"
}
```

### 控件通用结构

```json
{
  "type": "input",
  "name": "字段标签",
  "className": "form-input",
  "icon": "icon-input",
  "hideTitle": false,
  "options": { /* 控件特有配置 */ },
  "advancedSetting": {
    "defaultValue": {
      "type": "compose",
      "value": "",
      "format": "string",
      "allowFunc": true,
      "valueSplit": "",
      "customConfig": false
    }
  },
  "remoteAPI": { "url": "", "executed": false },
  "key": "{timestamp}_{random6}",
  "model": "{type}_{timestamp}_{random6}",
  "modelType": "main",
  "rules": [],
  "isSubItem": false
}
```

**通用字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | String | 控件类型标识 |
| `name` | String | 控件显示名称（标签） |
| `className` | String | CSS 类名 |
| `icon` | String | 图标类名 |
| `hideTitle` | Boolean | 是否隐藏标题 |
| `hideLabel` | Boolean | 是否隐藏标签（divider、text、buttons 等为 `true`） |
| `options` | Object | 控件特有配置 |
| `advancedSetting` | Object | 高级默认值设置 |
| `remoteAPI` | Object | 远程数据源 |
| `key` | String | 唯一标识 |
| `model` | String | 数据绑定 Key |
| `modelType` | String | `"main"` 或 `"sub_one2one"` |
| `rules` | Array | 校验规则（必填时加 `[{"required": true, "message": "${title}必须填写"}]`） |
| `defaultRules` | Array | 控件自带的默认校验（phone/email/rate 等自动生成，无需手动设置） |
| `isSubItem` | Boolean | 是否为子表内控件 |
| `subOptions` | Object | 子表内控件专用：`{"width": "200px", "parentKey": "子表key"}` |
| `jeecg_auth` | Object | 权限控制：`{"enabled": true, "title": "名称", "field": "model值"}` |
| `mobileOptions` | Object | 移动端覆盖配置（可选，同 options 结构，仅移动端生效） |
| `dictOptions` | Array | 字典选项（使用字典数据源时，与 options 同级） |
| `event` | Object | 事件处理（buttons 等控件）：`{"click": "console.log('hello')"}` |

## key 和 model 生成规则

源码中 key 由 `randomKey()` 生成（12-18 位随机字符串），model 由 `type + '_' + key` 派生（中划线转下划线）。但 **时间戳+随机数** 格式同样被接受，两种方式都有效：

| 方式 | key 示例 | model 示例 |
|------|---------|------------|
| 源码 randomKey | `nRk92kK92sk` | `input_nRk92kK92sk` |
| 时间戳+随机数 | `1773452631695_489584` | `input_1773452631695_489584` |

**model 生成规则（源码 widgetUtils.js）：**
```javascript
let model = widget.type + '_' + key
model = model.replace(/-/g, '_')  // 中划线 → 下划线
// link-record → link_record_xxx
```

**Python 生成方法（使用时间戳格式，实测可用）：**

```python
import time
import random

def gen_key():
    ts = int(time.time() * 1000)
    rnd = random.randint(100000, 999999)
    return f"{ts}_{rnd}"

def gen_model(widget_type):
    ts = int(time.time() * 1000)
    rnd = random.randint(100000, 999999)
    safe_type = widget_type.replace('-', '_')
    return f"{safe_type}_{ts}_{rnd}"
```

> 注意：每个控件的 key 和 model 必须全局唯一（保存时会检查重复 model）。card 容器的 key/model 与内部控件的 key/model 也必须不同。

## AutoGrid 机制（自动栅格）

设计器中启用自适应（`config.disabledAutoGrid: false`）时，拖入非容器控件会自动包裹一个 `card`（`isAutoGrid: true`）。

### 不进入 AutoGrid 的控件（不需要 card 包裹）

| 控件 type | 说明 |
|-----------|------|
| `editor` | 富文本编辑器 |
| `markdown` | Markdown 编辑器 |
| `divider` | 分隔符 |
| `map` | 地图 |
| `link-record`（`showType: "table"` 或 `isSubTable: true`） | 关联记录表格/子表模式 |
| `sub-table-design` | 设计子表 |
| `grid` | 栅格布局（本身是容器） |
| `card` | 卡片（本身是容器） |
| `tabs` | 选项卡（本身是容器） |

### 需要 card 容器的控件

所有其他控件，包括：
`input`, `textarea`, `number`, `integer`, `money`, `radio`, `checkbox`, `select`, `select-tree`, `date`, `time`, `switch`, `rate`, `color`, `slider`, `phone`, `email`, `imgupload`, `file-upload`, `buttons`, `text`, `area-linkage`, `location`, `capital-money`, `barcode`, `text-compose`, `auto-number`, `formula`, `hand-sign`, `ocr`, `link-record`（showMode="single" 且 showType 非 table）, `link-field`, `summary`, `select-user`, `select-depart`, `select-depart-post`, `org-role`

## 半行布局

一个 card 内放 2 个控件可实现半行布局，每个控件的 `options.autoWidth` 设为 `50`：

```json
{
  "type": "card",
  "isAutoGrid": true,
  "isContainer": true,
  "list": [
    { "type": "input", "name": "姓名", "options": { "autoWidth": 50, ... }, ... },
    { "type": "phone", "name": "手机", "options": { "autoWidth": 50, ... }, ... }
  ],
  ...
}
```

## advancedSetting 的 format 值

| 控件数据类型 | format 值 |
|-------------|-----------|
| 文本类（input、textarea、select、radio 等） | `"string"` |
| 数字类（number、integer、money、slider） | `"number"` |
| 多选带分隔（checkbox、多选 select） | `"string"` + `valueSplit: ","` + `customConfig: true` |

## rules 校验规则

**必填字段：**
```json
"rules": [{ "required": true, "message": "${title}必须填写" }]
```

**同时需要将 options 中的 required 设为 true。**

**自带校验的控件（有 defaultRules 字段）：**
- `phone` — 自带手机号校验
- `email` — 自带邮箱校验
- `rate` — 自带 validator

## advancedSetting 详解

```json
{
  "defaultValue": {
    "type": "compose",     // compose(静态+组合) | function(函数) | javascript(自定义JS) | linkage(关联查询) | none(无)
    "value": "",           // 默认值内容
    "format": "string",    // string | number | boolean
    "allowFunc": true,     // 是否允许在默认值中使用函数
    "valueSplit": ",",     // 多选控件的值分割符（checkbox, radio, select 多选）
    "customConfig": false  // 是否需要自定义配置界面
  }
}
```

**customConfig 为 true 的控件：** select、radio、checkbox（多选场景）、link-record、sub-table-design

## 布局容器结构

### grid — 栅格布局

```json
{
  "type": "grid",
  "isContainer": true,
  "columns": [
    {
      "span": 12,
      "options": {
        "flex": false,
        "flexAlignItems": "flex-start",
        "flexJustifyContent": "start"
      },
      "list": []
    },
    { "span": 12, "list": [] }
  ],
  "options": {
    "gutter": 8,
    "justify": "start",
    "align": "top",
    "isWordStyle": false,
    "hidden": false
  }
}
```

### tabs — 选项卡

```json
{
  "type": "tabs",
  "isContainer": true,
  "panes": [
    {
      "name": "Tab_xxx",
      "label": "Tab1",
      "rowNum": 1,
      "hidden": false,
      "hiddenOnAdd": false,
      "list": []
    }
  ],
  "options": {
    "width": "100%",
    "activeName": "Tab_xxx",
    "type": "border-card",
    "position": "top",
    "hidden": false
  }
}
```

## 完整控件类型清单

### 基础组件
`input`, `textarea`, `number`, `integer`, `money`, `radio`, `checkbox`, `time`, `date`, `rate`, `color`, `select`, `switch`, `slider`

### 高级组件
`phone`, `email`, `imgupload`, `file-upload`, `editor`, `markdown`, `buttons`, `text`, `divider`, `area-linkage`, `map`, `location`, `capital-money`, `barcode`, `text-compose`, `auto-number`, `formula`, `hand-sign`, `ocr`

### 关联组件
`link-record`, `link-field`, `sub-table-design`, `table-dict`, `select-tree`, `summary`

### 布局组件
`grid`, `card`, `tabs`

### 系统组件
`select-user`, `select-depart`, `select-depart-post`, `org-role`

### OA 组件
`oa-approval-comments`, `x_oa_timeout_date`, `x_oa_official_doc_no`, `oa-sign-holiday-select`, `oa-leave-date-select`, `oa-sign-patch-select`
