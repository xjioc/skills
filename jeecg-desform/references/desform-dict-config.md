# 字典数据源配置

对于 radio/select/checkbox 控件，数据源有两种方式。

## 方式一：静态选项（默认）

```json
"options": {
  "remote": false,
  "options": [
    { "value": "选项1", "itemColor": "#2196F3" },
    { "value": "选项2", "itemColor": "#08C9C9" }
  ]
}
```

## 方式二：系统字典

当用户描述中提到「字典」、「数据字典」或使用了 JeecgBoot 常见字典编码（如 sex、priority、valid_status 等），使用字典配置：

```json
"options": {
  "remote": "dict",
  "dictCode": "sex",
  "showLabel": true,
  "options": [],
  "remoteOptions": [],
  "props": { "value": "value", "label": "label" }
}
```

同时在**控件顶层**（与 options 同级）添加 `dictOptions`：
```json
"dictOptions": [
  { "value": "1", "label": "男" },
  { "value": "2", "label": "女" }
]
```

## 常用 JeecgBoot 系统字典编码

| 字典编码 | 说明 | 典型值 |
|---------|------|--------|
| `sex` | 性别 | 1=男, 2=女 |
| `priority` | 优先级 | L=低, M=中, H=高 |
| `valid_status` | 有效状态 | 0=无效, 1=有效 |
| `msg_category` | 消息类型 | 1=通知, 2=系统 |
| `send_status` | 发送状态 | 0=未发送, 1=已发送 |
| `yn` | 是否 | Y=是, N=否 |

> **提示：** 当用户指定的字典编码不确定是否存在时，可通过 API `GET /sys/dict/getDictItems/{dictCode}` 查询确认。如果用户只说了"用字典"但未指定编码，需要询问具体的字典编码。

## desform_utils.py 快捷函数使用字典的正确写法

> **踩坑警告：** `RADIO`/`SELECT`/`CHECKBOX` 的 `options` 是**必填位置参数**，使用字典时也不能省略。
> 当指定 `dict_code` 时，`options` 参数必须传**字典项列表**（`[{value, label}]` 格式），不要传字符串列表。
> **不存在** `dict_options` 关键字参数，不要传它（会报 `unexpected keyword argument` 错误）。

```python
# 正确 ✅ — options 传字典项列表 + dict_code
RADIO('性别', [{'value': '1', 'label': '男'}, {'value': '2', 'label': '女'}], dict_code='sex')
SELECT('状态', [{'value': '0', 'label': '无效'}, {'value': '1', 'label': '有效'}], dict_code='valid_status')

# 错误 ❌ — 缺少 options 位置参数
RADIO('性别', dict_code='sex')

# 错误 ❌ — 不存在 dict_options 参数
RADIO('性别', ['男', '女'], dict_code='sex', dict_options=[...])

# 不用字典时，options 传字符串列表即可
SELECT('职称', options=['教授', '副教授', '讲师', '助教'])
```

## 底层 `make_widget` 函数中字典的实现原理（仅供参考）

```python
# desform_utils.py 内部处理逻辑：
if dict_code:
    opts["remote"] = "dict"
    opts["dictCode"] = dict_code
    opts["showLabel"] = True
    opts["options"] = []
    extra["dictOptions"] = options if isinstance(options[0], dict) else []
```
