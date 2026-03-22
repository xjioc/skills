# 常见表单模式示例

## 模式 A：简单信息录入表单

**场景：** 员工信息登记（姓名、手机、邮箱、部门、备注）

```python
import urllib.request
import json
import time
import random

API_BASE = 'https://boot3.jeecg.com/jeecgboot'
TOKEN = 'your-jwt-token-here'

def api_request(path, data=None, method='POST'):
    url = f'{API_BASE}{path}'
    headers = {
        'X-Access-Token': TOKEN,
        'X-Sign': '00000000000000000000000000000000',
        'X-Tenant-Id': '1',
        'X-Timestamp': str(int(time.time() * 1000)),
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode('utf-8'))

def gen_ids(widget_type):
    """生成 key 和 model（type 中的 - 转为 _）"""
    ts = int(time.time() * 1000)
    rnd1 = random.randint(100000, 999999)
    rnd2 = random.randint(100000, 999999)
    rnd3 = random.randint(100000, 999999)
    key = f"{ts}_{rnd1}"
    safe_type = widget_type.replace('-', '_')
    model = f"{safe_type}_{ts}_{rnd2}"
    card_key = f"{ts + 1}_{rnd3}"
    card_model = f"card_{ts + 1}_{rnd3}"
    return key, model, card_key, card_model

def make_card_widget(widget_type, name, class_name, icon, options, required=False, extra_fields=None):
    """创建一个带 card 容器的控件"""
    key, model, card_key, card_model = gen_ids(widget_type)
    time.sleep(0.002)  # 确保时间戳不同

    widget = {
        "type": widget_type,
        "name": name,
        "className": class_name,
        "icon": icon,
        "hideTitle": False,
        "options": options,
        "advancedSetting": {
            "defaultValue": {
                "type": "compose",
                "value": "",
                "format": "string",
                "allowFunc": True,
                "valueSplit": "",
                "customConfig": False
            }
        },
        "remoteAPI": {"url": "", "executed": False},
        "key": key,
        "model": model,
        "modelType": "main",
        "rules": [{"required": True, "message": "${title}必须填写"}] if required else [],
        "isSubItem": False
    }

    if extra_fields:
        widget.update(extra_fields)

    card = {
        "key": card_key,
        "type": "card",
        "isAutoGrid": True,
        "isContainer": True,
        "list": [widget],
        "options": {},
        "model": card_model
    }

    return card, model

# ---- 构建表单字段 ----

widgets = []
used_types = set(["card"])
title_model = None

# 1. 姓名（input，必填，标题字段）
card, model = make_card_widget("input", "姓名", "form-input", "icon-input", {
    "width": "100%", "defaultValue": "", "required": True,
    "dataType": None, "pattern": "", "patternMessage": "",
    "placeholder": "", "clearable": False, "readonly": False,
    "disabled": False, "fillRuleCode": "", "showPassword": False,
    "unique": False, "hidden": False, "hiddenOnAdd": False,
    "fieldNote": "", "autoWidth": 100
}, required=True)
widgets.append(card)
used_types.add("input")
title_model = model

# 2. 手机（phone）
card, _ = make_card_widget("phone", "手机", "form-input-phone", "icon-mobile-phone", {
    "width": "300px", "defaultValue": "", "required": False,
    "placeholder": "", "readonly": False, "disabled": False,
    "unique": False, "hidden": False, "showVerifyCode": False,
    "hiddenOnAdd": False, "fieldNote": "", "autoWidth": 100
}, extra_fields={
    "defaultRules": [
        {"type": "phone", "message": "请输入正确的手机号码"},
        {"type": "validator", "message": "", "trigger": "blur"}
    ]
})
widgets.append(card)
used_types.add("phone")

# 3. 邮箱（email）
card, _ = make_card_widget("email", "邮箱", "form-input-email", "icon-email", {
    "width": "300px", "defaultValue": "", "required": False,
    "placeholder": "", "readonly": False, "disabled": False,
    "unique": False, "hidden": False, "showVerifyCode": False,
    "hiddenOnAdd": False, "fieldNote": "", "autoWidth": 100
}, extra_fields={
    "defaultRules": [
        {"type": "email", "message": "请输入正确的邮箱地址"},
        {"type": "validator", "message": "", "trigger": "blur"}
    ]
})
widgets.append(card)
used_types.add("email")

# 4. 部门（select-depart）
card, _ = make_card_widget("select-depart", "部门", "form-select-depart", "icon-depart", {
    "keyMaps": [], "defaultValue": "", "defaultLogin": False,
    "placeholder": "", "width": "100%", "multiple": False,
    "disabled": False, "customReturnField": "id",
    "hidden": False, "dataAuthType": "member",
    "hiddenOnAdd": False, "required": False, "fieldNote": "", "autoWidth": 100
})
widgets.append(card)
used_types.add("select-depart")

# 5. 备注（textarea）
card, _ = make_card_widget("textarea", "备注", "form-textarea", "icon-textarea", {
    "width": "100%", "defaultValue": "", "required": False,
    "disabled": False, "pattern": "", "patternMessage": "",
    "placeholder": "", "readonly": False, "unique": False,
    "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": 100
})
widgets.append(card)
used_types.add("textarea")

# ---- 构建完整 JSON ----

design_json = {
    "list": widgets,
    "config": {
        "formStyle": "normal",
        "titleField": title_model,
        "showHeaderTitle": True,
        "labelWidth": 100,
        "labelPosition": "top",
        "size": "small",
        "dialogOptions": {
            "top": 20, "width": 1000,
            "padding": {"top": 25, "right": 25, "bottom": 30, "left": 25}
        },
        "disabledAutoGrid": False,
        "designMobileView": False,
        "enableComment": True,
        "hasWidgets": sorted(list(used_types)),
        "defaultLoadLargeControls": False,
        "expand": {"js": "", "css": "", "url": {"js": "", "css": ""}},
        "transactional": True,
        "customRequestURL": [{"url": ""}],
        "disableMobileCss": True,
        "allowExternalLink": False,
        "externalLinkShowData": False,
        "headerImgUrl": "",
        "externalTitle": "",
        "enableNotice": False,
        "noticeMode": "external",
        "noticeType": "system",
        "noticeReceiver": "",
        "allowPrint": False,
        "allowJmReport": False,
        "jmReportURL": "",
        "bizRuleConfig": [],
        "bigDataMode": False
    }
}

# ---- 创建或查询表单 ----
form_name = "员工信息登记"
form_code = "yuan_gong_xin_xi_deng_ji"

# 先检查是否已存在（避免重复创建报错）
try:
    query_result = api_request(f'/desform/queryByCode?desformCode={form_code}', method='GET')
    if query_result.get('success') and query_result.get('result'):
        form_id = query_result['result']['id']
        update_count = query_result['result'].get('updateCount', 1)
        print(f'表单已存在，ID: {form_id}，将更新设计...')
    else:
        raise Exception('not found')
except:
    # 创建新表单（注意：add 返回的 result 为 null，不能直接取 ID）
    add_result = api_request('/desform/add', {
        'desformName': form_name,
        'desformCode': form_code
    })
    if not add_result.get('success'):
        print('创建失败！', add_result)
        exit(1)
    # 必须通过 queryByCode 获取表单 ID
    query_result = api_request(f'/desform/queryByCode?desformCode={form_code}', method='GET')
    form_id = query_result['result']['id']
    update_count = query_result['result'].get('updateCount', 1)
    print(f'表单ID: {form_id}')

# ---- 保存设计（updateCount 传当前值，后端自动递增） ----
edit_result = api_request('/desform/edit', {
    'id': form_id,
    'desformDesignJson': json.dumps(design_json, ensure_ascii=False),
    'updateCount': update_count,
    'autoNumberDesignConfig': {'update': {}, 'current': {}},
    'refTableDefaultValDbSync': {'changes': {}, 'removeKeys': []}
}, method='PUT')
print('保存结果:', json.dumps(edit_result, ensure_ascii=False, indent=2))

if edit_result.get('success'):
    print(f'\n表单创建成功！')
    print(f'表单ID: {form_id}')
    print(f'表单名称: {form_name}')
    print(f'表单编码: {form_code}')
else:
    print('保存失败！')
```

---

## 模式 B：带选项的审批表单

**场景：** 请假申请（请假类型单选、日期范围、天数、原因、附件）

在模式 A 基础上，字段构建部分替换为：

```python
# 请假类型（radio，必填）
card, _ = make_card_widget("radio", "请假类型", "form-radio", "icon-radio-active", {
    "inline": True, "matrixWidth": 120, "defaultValue": "",
    "showType": "default", "showLabel": False, "useColor": False,
    "colorIteratorIndex": 3,
    "options": [
        {"value": "事假", "itemColor": "#2196F3"},
        {"value": "病假", "itemColor": "#08C9C9"},
        {"value": "年假", "itemColor": "#00C345"},
        {"value": "婚假", "itemColor": "#FF9800"}
    ],
    "required": True, "width": "", "remote": False,
    "remoteOptions": [], "props": {"value": "value", "label": "label"},
    "remoteFunc": "", "disabled": False, "hidden": False,
    "hiddenOnAdd": False, "fieldNote": "", "autoWidth": 100
}, required=True)
# radio 的 advancedSetting 需要特殊设置
card["list"][0]["advancedSetting"]["defaultValue"]["valueSplit"] = ","
card["list"][0]["advancedSetting"]["defaultValue"]["customConfig"] = True
widgets.append(card)
used_types.add("radio")

# 开始日期（date，必填）
card, _ = make_card_widget("date", "开始日期", "form-date", "icon-date", {
    "defaultValue": "", "defaultValueType": 1,
    "readonly": False, "disabled": False, "editable": True,
    "clearable": True, "placeholder": "", "startPlaceholder": "",
    "endPlaceholder": "", "designType": "date", "type": "date",
    "format": "yyyy-MM-dd", "timestamp": True, "required": True,
    "width": "", "hidden": False, "hiddenOnAdd": False,
    "fieldNote": "", "autoWidth": 50  # 半行
}, required=True)
widgets.append(card)
used_types.add("date")
```

---

## 模式 C：半行布局（一行两字段）

一个 card 内放两个控件，每个 autoWidth 设为 50：

```python
ts = int(time.time() * 1000)

card = {
    "key": f"{ts + 1}_{random.randint(100000, 999999)}",
    "type": "card",
    "isAutoGrid": True,
    "isContainer": True,
    "list": [
        {
            "type": "input",
            "name": "姓名",
            "className": "form-input",
            "icon": "icon-input",
            "hideTitle": False,
            "options": {
                "width": "100%", "defaultValue": "", "required": True,
                "dataType": None, "pattern": "", "patternMessage": "",
                "placeholder": "", "clearable": False, "readonly": False,
                "disabled": False, "fillRuleCode": "", "showPassword": False,
                "unique": False, "hidden": False, "hiddenOnAdd": False,
                "fieldNote": "", "autoWidth": 50  # 半行
            },
            "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "string", "allowFunc": True, "valueSplit": "", "customConfig": False}},
            "remoteAPI": {"url": "", "executed": False},
            "key": f"{ts}_{random.randint(100000, 999999)}",
            "model": f"input_{ts}_{random.randint(100000, 999999)}",
            "modelType": "main",
            "rules": [{"required": True, "message": "${title}必须填写"}],
            "isSubItem": False
        },
        {
            "type": "phone",
            "name": "手机",
            "className": "form-input-phone",
            "icon": "icon-mobile-phone",
            "hideTitle": False,
            "options": {
                "width": "300px", "defaultValue": "", "required": False,
                "placeholder": "", "readonly": False, "disabled": False,
                "unique": False, "hidden": False, "showVerifyCode": False,
                "hiddenOnAdd": False, "fieldNote": "", "autoWidth": 50  # 半行
            },
            "defaultRules": [
                {"type": "phone", "message": "请输入正确的手机号码"},
                {"type": "validator", "message": "", "trigger": "blur"}
            ],
            "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "string", "allowFunc": True, "valueSplit": "", "customConfig": False}},
            "remoteAPI": {"url": "", "executed": False},
            "key": f"{ts}_{random.randint(100000, 999999)}",
            "model": f"phone_{ts}_{random.randint(100000, 999999)}",
            "modelType": "main",
            "rules": [],
            "isSubItem": False
        }
    ],
    "options": {},
    "model": f"card_{ts + 1}_{random.randint(100000, 999999)}"
}
```

---

## 模式 D：带子表的表单

**场景：** 采购单主表 + 采购明细子表

子表控件直接放在 list 顶层（不需要 card）：

```python
sub_table_key = f"{int(time.time() * 1000)}_{random.randint(100000, 999999)}"
sub_table_model = f"sub_table_design_{int(time.time() * 1000)}_{random.randint(100000, 999999)}"

sub_table = {
    "type": "sub-table-design",
    "name": "采购明细",
    "className": "form-sub-table",
    "icon": "icon-table",
    "hideTitle": False,
    "class": ["data-j-editable-design"],
    "isContainer": True,
    "columns": [
        {
            "span": 12,
            "list": [
                {
                    "type": "input",
                    "name": "物品名称",
                    "className": "form-input",
                    "icon": "icon-input",
                    "hideTitle": False,
                    "options": {
                        "width": "100%", "defaultValue": "", "required": True,
                        "dataType": None, "pattern": "", "patternMessage": "",
                        "placeholder": "", "clearable": False, "readonly": False,
                        "disabled": False, "fillRuleCode": "", "showPassword": False,
                        "unique": False, "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
                    },
                    "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "string", "allowFunc": True, "valueSplit": "", "customConfig": False}},
                    "remoteAPI": {"url": "", "executed": False},
                    "key": f"{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "model": f"input_{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "modelType": "main",
                    "rules": [{"required": True, "message": "${title}必须填写"}],
                    "isSubItem": True,
                    "subOptions": {"width": "200px", "parentKey": sub_table_key}
                },
                {
                    "type": "number",
                    "name": "数量",
                    "className": "form-number",
                    "icon": "icon-number",
                    "hideTitle": False,
                    "options": {
                        "width": "", "required": False, "defaultValue": 0,
                        "placeholder": "", "controls": False,
                        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
                        "step": 1, "disabled": False, "controlsPosition": "right",
                        "unitText": "", "unitPosition": "suffix", "showPercent": False,
                        "align": "left", "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
                    },
                    "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "number", "allowFunc": True, "valueSplit": "", "customConfig": False}},
                    "remoteAPI": {"url": "", "executed": False},
                    "key": f"{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "model": f"number_{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "modelType": "main",
                    "rules": [],
                    "isSubItem": True,
                    "subOptions": {"width": "200px", "parentKey": sub_table_key}
                }
            ]
        },
        {
            "span": 12,
            "list": [
                {
                    "type": "money",
                    "name": "单价",
                    "className": "form-money",
                    "icon": "icon-money",
                    "hideTitle": False,
                    "options": {
                        "width": "180px", "placeholder": "请输入金额",
                        "required": False, "unitText": "元", "unitPosition": "suffix",
                        "precision": 2, "hidden": False, "disabled": False,
                        "hiddenOnAdd": False, "fieldNote": ""
                    },
                    "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "number", "allowFunc": True, "valueSplit": "", "customConfig": False}},
                    "remoteAPI": {"url": "", "executed": False},
                    "key": f"{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "model": f"money_{int(time.time() * 1000)}_{random.randint(100000, 999999)}",
                    "modelType": "main",
                    "rules": [],
                    "isSubItem": True,
                    "subOptions": {"width": "200px", "parentKey": sub_table_key}
                }
            ]
        }
    ],
    "options": {
        "isWordStyle": False, "isWordInnerGrid": False, "gutter": 0,
        "columnNumber": 2, "operationMode": 1, "justify": "start", "align": "top",
        "defaultValue": [], "subTableName": "", "defaultRows": 0,
        "showCheckbox": True, "showNumber": True, "showRowButton": False,
        "allowAdd": True, "autoHeight": True, "defaultValType": "none",
        "hidden": False, "hiddenOnAdd": False, "required": False, "fieldNote": ""
    },
    "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "string", "allowFunc": True, "valueSplit": "", "customConfig": True}},
    "key": sub_table_key,
    "model": sub_table_model,
    "modelType": "main",
    "rules": [],
    "isSubItem": False
}

# 直接加入 list 顶层（不需要 card 容器）
widgets.append(sub_table)
used_types.add("sub-table-design")
```

**子表控件要点：**
1. 子控件 `isSubItem: True`
2. 子控件有 `subOptions: { "width": "200px", "parentKey": "子表的key" }`
3. 子控件的 options 没有 `autoWidth` 字段
4. `columns` 数组中每个元素有 `span`（栅格宽度）和 `list`（控件列表）

---

## 模式 E：多子表订单表单

**场景：** 订单表（主表 + 商品明细 + 收款记录 + 发货记录 三个子表）

在模式 A 基础上，使用 `make_widget` + `make_card` + `make_sub_table` 分离构建：

```python
def make_widget(widget_type, name, class_name, icon, options, required=False, is_sub=False, parent_key=None, extra=None):
    """创建控件（支持主表和子表控件，type 中的 - 自动转 _）"""
    ts = int(time.time() * 1000)
    rnd1 = random.randint(100000, 999999)
    rnd2 = random.randint(100000, 999999)
    key = f"{ts}_{rnd1}"
    safe_type = widget_type.replace('-', '_')
    model = f"{safe_type}_{ts}_{rnd2}"
    time.sleep(0.003)

    fmt = "number" if widget_type in ("number", "integer", "money", "slider") else "string"
    custom = widget_type in ("radio", "checkbox", "select", "link-record", "sub-table-design")

    w = {
        "type": widget_type, "name": name, "className": class_name, "icon": icon,
        "hideTitle": False, "options": options,
        "remoteAPI": {"url": "", "executed": False},
        "key": key, "model": model, "modelType": "main",
        "rules": [{"required": True, "message": "${title}必须填写"}] if required else [],
        "isSubItem": is_sub
    }

    # link-field 不需要 advancedSetting（其他控件都需要）
    if widget_type != "link-field":
        w["advancedSetting"] = {"defaultValue": {
            "type": "compose", "value": "", "format": fmt,
            "allowFunc": True, "valueSplit": "," if custom else "", "customConfig": custom
        }}

    if is_sub and parent_key:
        w["subOptions"] = {"width": "200px", "parentKey": parent_key}
    if extra:
        w.update(extra)
    return w, key, model

def make_card(*widgets_list):
    """创建 card 容器，支持放入 1~2 个控件"""
    ts = int(time.time() * 1000)
    rnd = random.randint(100000, 999999)
    time.sleep(0.003)
    return {
        "key": f"{ts}_{rnd}", "type": "card", "isAutoGrid": True,
        "isContainer": True, "list": list(widgets_list),
        "options": {}, "model": f"card_{ts}_{rnd}"
    }

def make_sub_table(name, sub_widgets):
    """创建子表，sub_widgets 为子控件列表"""
    ts = int(time.time() * 1000)
    rnd1 = random.randint(100000, 999999)
    rnd2 = random.randint(100000, 999999)
    st_key = f"{ts}_{rnd1}"
    st_model = f"sub_table_design_{ts}_{rnd2}"
    time.sleep(0.003)
    return {
        "type": "sub-table-design", "name": name,
        "className": "form-sub-table", "icon": "icon-table",
        "hideTitle": False, "class": ["data-j-editable-design"],
        "isContainer": True,
        "columns": [{"span": 24, "list": sub_widgets}],
        "options": {
            "isWordStyle": False, "isWordInnerGrid": False, "gutter": 0,
            "columnNumber": 2, "operationMode": 1, "justify": "start", "align": "top",
            "defaultValue": [], "subTableName": "", "defaultRows": 0,
            "showCheckbox": True, "showNumber": True, "showRowButton": False,
            "allowAdd": True, "autoHeight": True, "defaultValType": "none",
            "hidden": False, "hiddenOnAdd": False, "required": False, "fieldNote": ""
        },
        "advancedSetting": {"defaultValue": {"type": "compose", "value": "", "format": "string", "allowFunc": True, "valueSplit": "", "customConfig": True}},
        "key": st_key, "model": st_model, "modelType": "main",
        "rules": [], "isSubItem": False
    }, st_key

# 构建子表（先创建子表获取 key，再创建子控件绑定 parentKey）
sub_widgets = []
# 先占位获取子表 key
sub, sub_key = make_sub_table("商品明细", [])
# 创建子控件
w, _, _ = make_widget("input", "商品名称", "form-input", "icon-input",
    {...}, required=True, is_sub=True, parent_key=sub_key)
sub_widgets.append(w)
w, _, _ = make_widget("integer", "数量", "form-integer", "icon-integer",
    {...}, required=True, is_sub=True, parent_key=sub_key)
sub_widgets.append(w)
# 更新子表的 columns
sub["columns"] = [{"span": 24, "list": sub_widgets}]
all_widgets.append(sub)
```

**多子表要点：**
1. 每个子表独立调用 `make_sub_table()` 获取 `st_key`
2. 子控件创建时传 `is_sub=True, parent_key=st_key`
3. 子控件的 options **没有** `autoWidth` 字段
4. 多个子表按顺序追加到 `all_widgets`（顶层 list）
5. `config.hasWidgets` 中只需加一次 `"sub-table-design"`

---

## 执行模板（完整脚本框架）

生成脚本时遵循此框架：

```
1. 导入依赖 (urllib, json, time, random)
2. 配置 API_BASE 和 TOKEN
3. 定义工具函数 (api_request, make_widget, make_card, make_sub_table)
4. 构建各字段控件（主表 + 子表）
5. 组装 design_json (list + config)
6. 检查表单是否已存在（GET /desform/queryByCode）
7. 不存在则创建（POST /desform/add），再查询获取 ID
8. 保存设计（PUT /desform/edit），updateCount 传当前值
9. 输出结果
```

**关键注意事项：**
- `time.sleep(0.003)` 确保每个控件的时间戳不同
- `config.hasWidgets` 必须包含所有使用到的控件 type（包括 `card`）
- `config.titleField` 必须指向一个实际存在的控件 model
- 必填字段需要同时设置 `options.required = True` 和 `rules = [{"required": True, ...}]`
- 数字类控件的 advancedSetting.defaultValue.format 应为 `"number"`
- **`POST /desform/add` 返回 `result: null`**，必须用 `GET /desform/queryByCode` 获取 ID
- **`updateCount` 传当前数据库值**（不是 +1），后端自动递增
- **先检查表单是否存在**，避免重复创建报 `该code已存在` 错误

---

## 实战踩坑清单（className / icon 易错汇总）

生成表单时最容易出错的是 className 和 icon，以下为**实测验证的正确值**：

| 控件 type | className | icon | 特殊说明 |
|-----------|-----------|------|----------|
| `link-record` | `form-link-record` | **`icon-link`** | 不是 `icon-link-record`！ |
| `link-field` | `form-link-field` | **`icon-field`** | 不是 `icon-link-field`！ |
| `sub-table-design` | **`form-sub-table`** | **`icon-table`** | 不是 `form-sub-table-design` / `icon-sub-table-design`！ |
| `divider` | `form-divider` | `icon-fengexian` | |

### link-record 踩坑要点

1. **`advancedSetting.defaultValue.customConfig` 必须为 `true`**
2. **`allowView`、`allowEdit`、`allowAdd`、`allowSelect` 必须全部设为 `true`**（4 个操作选项默认全部勾选）
3. **`titleField` 必须填源表的真实标题字段 model**（如 `input_xxx`），不能留空
4. **`showFields` 建议填入源表中需要展示的字段 model 列表**
5. **跨表单关联时**，必须先创建被引用的表单，然后查询获取其字段 model，再构建引用方的 link-record

### link-field 踩坑要点

1. **link-field 没有 `advancedSetting`** — 与其他控件不同
2. **`linkRecordKey` 填的是 link-record 的 key**（如 `1773457559119_461003`），**不是 model**
3. **`fieldType` 必须填来源字段的真实控件类型**（如 `"input"`, `"select-user"`, `"money"`），不能一律写 `"input"`
4. **`fieldOptions` 需包含源字段类型相关的 options 子集**，例如：
   - select-user: `{"multiple": false, "customReturnField": "username"}`
   - select (多选): `{"multiple": true}`
   - 普通 input/money 等: `{}` 即可

### sub-table-design 踩坑要点

1. **options 必须包含 `allowAdd: true`**，否则子表没有"添加"按钮
2. **完整 options 字段（缺一不可）：**
   ```json
   {
     "isWordStyle": false, "isWordInnerGrid": false, "gutter": 0,
     "columnNumber": 2, "operationMode": 1, "justify": "start", "align": "top",
     "defaultValue": [], "subTableName": "", "defaultRows": 0,
     "showCheckbox": true, "showNumber": true, "showRowButton": false,
     "allowAdd": true, "autoHeight": true, "defaultValType": "none",
     "hidden": false, "hiddenOnAdd": false, "required": false, "fieldNote": ""
   }
   ```
3. **子表内可以放 link-record + link-field**，实现子表行级关联选择

### 跨表单关联的正确流程（多表单批量创建）

```
1. 先创建基础表单（如商品表、仓库表、供应商表）
2. 查询基础表单的 designJson，提取字段 model 和 titleField
3. 构建业务表单（如入库单）时：
   a. link-record.options.sourceCode = 基础表单的 desformCode
   b. link-record.options.titleField = 基础表单的 titleField model
   c. link-record.options.showFields = [基础表单中需要展示的字段 model 列表]
   d. link-field.options.linkRecordKey = 同表单中 link-record 控件的 KEY
   e. link-field.options.showField = 基础表单中要自动填充的字段 MODEL
   f. link-field.options.fieldType = 该字段的实际控件类型
```

### Python 中查询基础表单字段的方法

```python
def get_form_fields(form_code):
    """查询表单设计JSON，提取字段 model/key/type"""
    # 注意：queryByCode 不可靠，推荐用 queryByIdOrCode 或 desform_utils.py 中的 get_form_fields
    q = api_request(f'/desform/queryByIdOrCode?desformCode={form_code}', method='GET')
    design = json.loads(q['result']['desformDesignJson'])
    title_field = design['config']['titleField']
    fields = {}
    def extract(items):
        for item in items:
            if item.get('type') == 'card' and 'list' in item:
                extract(item['list'])
            elif 'model' in item and item.get('type') != 'card':
                fields[item['name']] = {
                    'model': item['model'],
                    'key': item['key'],
                    'type': item['type']
                }
    extract(design.get('list', []))
    return title_field, fields
```

## 模式 F：使用 desform_utils.py 的跨表单 CRM 系统（推荐）

**场景：** CRM 客户管理系统（4 个关联表单），使用共通工具库 `desform_utils.py`

> **命名规则：** 模块名作为前缀，如 `crm_customer`（不是 `customer_crm`）

```python
"""CRM系统 - 4个关联表单"""
import sys, time
sys.path.insert(0, r'{后端项目根目录}')
from desform_utils import *

init_api('https://boot3.jeecg.com/jeecgboot', 'your-token')

# ---- 1/4 客户信息（基础表单，被其他表单引用）----
fid1, uc1 = find_or_create_form('客户信息', 'crm_customer')
w0, _, m0 = INPUT('客户名称', required=True)
w1, _, _ = AUTONUMBER('客户编号', prefix='CRM')
w2, _, _ = SELECT('客户类型', ['企业客户', '个人客户'], required=True)
w3, _, _ = SELECT('所属行业', ['IT互联网', '金融', '制造业', '教育', '医疗', '房地产', '零售', '其他'])
w4, _, _ = SELECT('客户来源', ['官网', '转介绍', '电话营销', '展会', '广告', '社交媒体', '其他'])
w5, _, _ = RADIO('客户等级', ['A-重要', 'B-普通', 'C-一般'])
w6, _, _ = RADIO('客户状态', ['潜在客户', '意向客户', '成交客户', '流失客户'])
w7, _, _ = PHONE('联系电话')
w8, _, _ = EMAIL('邮箱')
w9, _, _ = AREA('所在地区')
w10, _, _ = INPUT('详细地址')
w11, _, _ = USER('负责销售', required=True)
w12, _, _ = DEPART('所属部门')
w13, _, _ = TEXTAREA('备注')
save_design(fid1, 'crm_customer', [w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13], m0, uc1)

# 查询客户表单字段，供后续表单关联引用
time.sleep(1)
cust_tf, cust_fields = get_form_fields('crm_customer')
cust_show = [cust_fields['客户编号']['model'], cust_fields['联系电话']['model']]

# ---- 2/4 联系人（关联客户）----
fid2, uc2 = find_or_create_form('联系人', 'crm_contact')
w0, _, m0 = INPUT('联系人姓名', required=True)
w1, _, _ = LINK_RECORD('所属客户', 'crm_customer', cust_tf, cust_show, required=True)
lr_key = w1['list'][0]['key']  # 获取 link-record 的 key，供 link-field 引用
w2, _, _ = LINK_FIELD('客户编号', lr_key, cust_fields['客户编号']['model'], field_type='auto-number')
w3, _, _ = INPUT('职务')
w4, _, _ = INPUT('部门')
w5, _, _ = PHONE('手机号码', required=True)
w6, _, _ = EMAIL('邮箱')
w7, _, _ = SWITCH('是否决策人')
w8, _, _ = TEXTAREA('备注')
save_design(fid2, 'crm_contact', [w0,w1,w2,w3,w4,w5,w6,w7,w8], m0, uc2)

# ---- 3/4 商机管理（关联客户 + 分隔符 + 金额 + 滑块）----
fid3, uc3 = find_or_create_form('商机管理', 'crm_opportunity')
w0, _, m0 = INPUT('商机名称', required=True)
w1, _, _ = AUTONUMBER('商机编号', prefix='BIZ')
w2, _, _ = LINK_RECORD('关联客户', 'crm_customer', cust_tf, cust_show, required=True)
lr_key = w2['list'][0]['key']
w3, _, _ = LINK_FIELD('客户编号', lr_key, cust_fields['客户编号']['model'], field_type='auto-number')
w4, _, _ = DIVIDER('商机详情')
w5, _, _ = SELECT('商机阶段', ['初步接触', '需求确认', '方案报价', '商务谈判', '赢单', '输单'], required=True)
w6, _, _ = MONEY('预计金额', required=True)
w7, _, _ = DATE('预计成交日期')
w8, _, _ = USER('负责人', required=True)
w9, _, _ = USER('协作人', multiple=True)
w10, _, _ = SLIDER('赢单概率', show_input=True)
w11, _, _ = TEXTAREA('备注')
save_design(fid3, 'crm_opportunity', [w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11], m0, uc3)

# ---- 4/4 跟进记录（关联客户 + 默认当前用户）----
fid4, uc4 = find_or_create_form('跟进记录', 'crm_follow_up')
w0, _, m0 = INPUT('跟进主题', required=True)
w1, _, _ = LINK_RECORD('关联客户', 'crm_customer', cust_tf, cust_show, required=True)
lr_key = w1['list'][0]['key']
w2, _, _ = LINK_FIELD('客户名称', lr_key, cust_fields['客户名称']['model'], field_type='input')
w3, _, _ = RADIO('跟进方式', ['电话', '拜访', '微信', '邮件', '会议', '其他'], required=True)
w4, _, _ = DATE('跟进日期', required=True)
w5, _, _ = DATE('下次跟进日期')
w6, _, _ = USER('跟进人', required=True, default_login=True)
w7, _, _ = TEXTAREA('跟进内容', required=True)
w8, _, _ = FILE('附件')
save_design(fid4, 'crm_follow_up', [w0,w1,w2,w3,w4,w5,w6,w7,w8], m0, uc4)

# ---- 输出菜单 + 角色授权 SQL ----
print(gen_menu_sql('crm_menu', 'CRM客户管理', [
    ('crm_customer_menu', '客户信息', 'crm_customer', 1),
    ('crm_contact_menu', '联系人', 'crm_contact', 2),
    ('crm_opportunity_menu', '商机管理', 'crm_opportunity', 3),
    ('crm_follow_up_menu', '跟进记录', 'crm_follow_up', 4),
]))
```

**跨表单关联要点：**
1. 先创建被引用的基础表单 → `save_design` → `time.sleep(1)` → `get_form_fields` 获取字段信息
2. `LINK_RECORD` 需要源表编码、titleField、showFields
3. `LINK_FIELD` 需要 link-record 的 **key**（通过 `w['list'][0]['key']` 获取）和源字段的 model + field_type
4. link-record 的 4 个操作选项（allowView/allowEdit/allowAdd/allowSelect）已在 desform_utils.py 中默认全部开启
