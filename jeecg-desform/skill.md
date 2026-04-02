---
name: jeecg-desform
description: JeecgBoot 表单设计器（desform）全生命周期管理——通过对话的方式创建、更新、复制、删除表单设计器，管理表单数据（CRUD），生成 PC/移动端视图，以及一键创建 OA 审批应用（表单+流程+授权）。只要用户意图涉及「表单设计器」就必须使用本技能，包括但不限于：创建或生成表单（"做一个请假表单"、"AI设计表单"、"desform"）、修改已有表单或字段（"加个字段"、"改一下表单"）、复制/删除表单、录入或查询表单数据、创建表单视图（含移动端）、以及咨询设计器功能（控件类型、字典配置、校验规则、关联记录、子表、公式计算、JS/CSS增强、默认值、外链等）。当用户想要创建带审批流程的 OA 应用时也应触发（"创建OA应用"、"创建审批单"、"创建报销单"、"创建请假单"、"做一个OA表单带流程"、"一键创建表单和流程"、"面试申请"、"出差申请"等）。即使用户只是描述字段需求（如"需要姓名、手机号字段"）而未明确说"表单"，只要语境指向表单设计器也应触发。注意：本技能仅处理表单设计器（desform），不处理 Online 表单——如果用户明确提到"Online表单"或"online表"，应使用 jeecg-onlform 技能。
---

# JeecgBoot 表单设计器 AI 自动生成器

将自然语言的表单需求描述转换为 desformDesignJson，并通过 API 在 JeecgBoot 系统中自动创建表单。

> **重要：本 skill 只处理「表单设计器」（desform），不涉及 Online 表单。两者是完全独立的表单体系。**

## 前置条件

用户必须提供以下信息（或由 AI 引导确认）：

1. **API 地址**：JeecgBoot 后端地址（如 `https://boot3.jeecg.com/jeecgboot`）
2. **X-Access-Token**：JWT 登录令牌（从浏览器 F12 获取）

如果用户未提供，提示：
> 请提供 JeecgBoot 后端地址和 X-Access-Token（从浏览器 F12 → Network → 任意请求的 Request Headers 中复制）。

### API 初始化（统一入口）

所有 Python 操作前都需要先初始化 API 连接。`init_api` 只存在于 `desform_utils.py` 中，其他模块（如 `desform_data_utils.py`）不包含此函数——错误导入会导致 ImportError。

```python
import sys
sys.path.insert(0, r'<skill目录>/scripts')
from desform_utils import init_api
init_api('<api_base>', '<token>')
```

后续按需从各模块导入函数：
- `desform_utils`：`check_code_available`, `get_form_fields`, `query_form`, `create_form`, `update_form`, `add_widget`, `update_widget`, `delete_widget`, `copy_form`, `delete_form`, `sync_auth`
- `desform_data_utils`：`add_data`, `list_data`, `edit_data`, `delete_data`

## 主数据复用规则

表单字段配置字典、选人、选部门等数据源时，遵循"先查后建"原则——先查系统是否已有该字典/角色/部门，避免重复创建。

> 使用 `jeecg-system` skill 的 `system_utils.py` 查询和管理主数据，详见  `jeecg-system` 技能。

---

## 创建表单

### 1. 解析用户需求

从用户描述中提取：表单名称、表单编码（英文命名，模块名前缀）、字段列表、字段属性。

**布局选择规则：** 默认使用普通布局（`auto`/`half`/`full`），不要主动使用 Word 风格。只有当用户明确要求时才使用 `layout: "word"`——例如用户说"Word风格"、"表格边框样式"、"像Word文档那样"等。即使表单是审批单、申请表等看起来适合 Word 风格的场景，也不要自行判断使用 Word 风格，而是让用户来决定。

**编码唯一性校验（新建表单时）：**

创建新表单时，生成 `desformCode` 后立即执行编码校验，在校验通过前不要展示摘要让用户确认。原因：用户确认摘要后会期望直接执行成功，如果执行时才发现编码冲突，体验很差，且可能意外覆盖已有表单数据。

```python
from desform_utils import init_api, check_code_available
init_api('<api_base>', '<token>')
result = check_code_available('<code>')  # 只接受 1 个参数
# True → 编码可用  |  False → 已占用，自动换一个编码重试
```

### 2. 识别字段并选择控件类型

根据用户描述的关键词（也可能是图片），匹配对应的控件 type。

> 详见 `references/desform-widget-types.md` — 完整的关键词到控件类型映射表。

对于 radio/select/checkbox 控件，支持静态选项（默认）和系统字典两种数据源。

> 详见 `references/desform-dict-config.md` — 字典配置方式、常用字典编码、Python 快捷函数用法。

### 3. 展示表单摘要并确认

展示以下内容，等待用户确认后再执行：

```
## 表单摘要
- 表单名称：{name}
- 表单编码：{code}（已通过校验）
- 目标环境：{API_BASE}

### 字段列表
| 序号 | 字段名称 | 控件类型 | 必填 | 说明 |
|------|---------|---------|------|------|
| 1 | ... | ... | ... | ... |

确认以上信息正确？(y/n)
```

### 4. 防覆盖检查

用户确认后、执行创建前，通过 `get_form_id(code)` 检查编码是否已存在。这是防止误覆盖的最后一道安全网——编码校验只检查当前时刻，而从校验到执行之间可能有其他人创建了同编码表单。

如果表单已存在：
1. 告知用户：`表单 {code} 已存在 (ID={id})，是否要覆盖更新？`
2. 用户确认后才执行覆盖（调用 `update_form`）
3. 用户拒绝覆盖时，基于原编码生成 3~5 个新编码供选择

### 5. 生成 JSON 并调用 API

使用 `scripts/desform_creator.py` + JSON 配置文件创建表单。这个脚本封装了完整的 JSON 构造逻辑（控件包裹、key/model 生成、跨控件引用等），比手动拼 JSON 更可靠，也更不容易出错。

1. 根据用户需求生成 JSON 配置文件（Write 到工作目录的临时 `.json` 文件）
2. 执行脚本：`python "<skill目录>/scripts/desform_creator.py" --api-base <URL> --token <TOKEN> --config <config.json>`
3. 删除临时 JSON 配置文件

> 详见 `references/desform-json-config.md` — JSON 配置格式、字段定义、子表说明、完整示例。

**脚本自动处理的跨控件引用（无需手动配置）：**
- **capital-money（大写金额）**：自动查找前面最近的 `money` 控件并关联其 key
- **formula（公式）表达式**：支持使用字段中文名作为占位符（如 `$预算总额$`），自动解析为实际 model
- **Word 布局下的 divider（分隔符）**：自动包裹在 `span=24`、`isWordStyle=true` 的 grid 容器中

### desformDesignJson 核心规则

无论使用脚本还是手动构造，都需要理解以下规则（脚本已自动处理，但理解它们有助于排查问题和生成正确的 JSON 配置）：

- 每个普通控件必须包裹在 `card` 容器中（除了 editor、markdown、divider、map、sub-table-design、link-record（showType='table' 或 isSubTable=true）、grid、tabs）
- `config.titleField` 指向标题字段的 model
- `config.hasWidgets` 必须列出所有使用到的控件 type（包括 card）
- key 格式：`{timestamp}_{6位随机数}`，model 格式：`{type}_{timestamp}_{6位随机数}`

**className / icon 易错控件（实测验证）：**
- `link-record`: className=`form-link-record`, icon=`icon-link`
- `link-field`: className=`form-link-field`, icon=`icon-field`
- `sub-table-design`: className=`form-sub-table`, icon=`icon-table`

**link-record / link-field 关键配置：**
- link-record 的 `advancedSetting.defaultValue.customConfig` 必须为 `true`
- link-record 的 `allowView`、`allowEdit`、`allowAdd`、`allowSelect` 必须全部设为 `true`
- link-field **没有 `advancedSetting`**
- link-field 的 `linkRecordKey` 填 link-record 的 **key**（不是 model）

> **多表互相关联场景**（2+ 个表单通过 link-record 互相引用）：
> 阅读 `references/desform-cross-form-binding.md`，采用"先建表后关联"策略，避免循环依赖和 model 失效问题。

**sub-table-design 关键配置：**
- options 必须包含 `allowAdd: true`，否则子表没有"添加"按钮
- 完整 options 见 `references/desform-widget-options.md`

**降级方案：** 如果脚本执行失败，先向用户说明失败原因，经用户确认后可降级为手动构造 JSON。
> 详见 `references/desform-fallback-manual-json.md` — 手动构造 desformDesignJson 的完整指南。

### 6. 检查结果与权限

- `success: true` → 表单创建成功，脚本会自动创建字段权限
- `success: false` → 输出错误信息，参见 `references/desform-api-notes.md` 错误处理表
- 权限创建失败不会阻断主流程（仅输出警告），可用 `scripts/desform_auth_retry.py --api-base <URL> --token <TOKEN> --code <form_code>` 重试

### 7. 输出结果

```
## 表单创建成功
- 表单ID：{id}
- 表单名称：{desformName}
- 表单编码：{desformCode}
- 目标环境：{API_BASE}

请在表单设计器中查看：打开 JeecgBoot 后台 → 表单设计器 → 找到该表单
```

同时输出菜单 + 角色授权 SQL（用于将表单设计器加入系统菜单）。

> 详见 `references/desform-menu-sql.md` — gen_menu_sql 输出格式、SQL 字段说明、本地自动执行规则。

当 `api_base` 以 `http://127.0.0.1` 或 `http://localhost` 开头时，通过 MySQL CLI 自动执行菜单 SQL。

---

## 更新已有表单

所有更新相关的函数都在 `scripts/desform_utils.py` 中。

### 更新流程

1. 获取现有表单信息：`get_form_fields(code)`
2. 分析用户需求，确定操作类型（添加/修改/删除/整体重设计）
3. 展示变更摘要（新增/修改/删除的字段列表），等待用户确认
4. 执行操作
5. 自动同步权限

### 整体重设计

如果用户要全面修改已有表单：
1. 查询现有表单设计 JSON：`query_form(code)` 或 `get_form_fields(code)`
2. 根据用户需求重新组装控件列表
3. 调用 `update_form(code, new_widgets)` 保存（自动获取 `updateCount`）

### 字段级操作

如果用户只是添加/修改/删除个别字段：
- **添加字段**：`add_widget(code, widget)` — 向已有表单追加控件
- **修改字段属性**：`update_widget(code, key_or_model, changes_dict)` — 修改指定控件属性
- **删除字段**：`delete_widget(code, key_or_model)` — 删除指定控件
- 操作后自动同步权限：`sync_auth(code, design_list, form_id)`

---

## 复制表单

`copy_form(source_code, new_code)` 可快速复制已有表单的设计 JSON 创建新表单。适用于基于现有表单创建类似表单（如复制"请假申请"改造为"出差申请"）。

流程：
1. 用户提供源表单编码和新表单编码
2. 校验新编码可用性（`check_code_available(new_code)`）
3. 调用 `copy_form(source_code, new_code)` 完成复制
4. 如需修改，使用 `update_form` 或字段级操作调整

## 删除表单

`delete_form` 已封装完整的删除流程（查找 → 逻辑删除 → 物理删除），支持传 code 或 ID。

> 详见 `references/desform-api-notes.md` — 删除流程、注意事项。

## 视图与移动端视图

创建视图（PC 子视图、移动端视图）时，优先使用 `scripts/desform_view_creator.py` 通用脚本，支持复制主视图或自定义字段两种模式。

> 详见 `references/desform-view-config.md` — 创建流程、JSON 配置格式、移动端优化规则、踩坑汇总。

## 表单数据操作（CRUD）

使用 `scripts/desform_data_utils.py` 对已有表单进行数据新增、查询、编辑、删除。

> 详见 `references/desform-data-utils.md` — 完整函数列表和用法。

**数据新增流程：**
1. 先获取字段 model 映射：`get_form_fields(code)` 返回 `(titleField, {字段名: {model, key, type}, ...})`
2. 构造数据字典：key 为字段的 `model`（如 `input_1774607211242_327900`），value 为字段值
3. 调用 `add_data(code, data_dict)` 提交

```python
from desform_utils import init_api, get_form_fields
from desform_data_utils import add_data

init_api(api_base, token)
title_field, fields_map = get_form_fields('form_code')
# fields_map 结构: {"姓名": {"model": "input_xxx", "key": "xxx", "type": "input"}, ...}

add_data('form_code', {
    fields_map['姓名']['model']: '张三',
    fields_map['手机号']['model']: '13800138001',
})
```

## 错误处理

> 详见 `references/desform-api-notes.md` — 完整错误处理表。

---

## OA 审批应用一键生成（表单 + 流程 + 授权）

> 当用户说"创建审批单"、"创建报销单"、"做一个OA表单带流程"、"面试申请"、"请假申请"等，使用本章节一次性完成 **表单设计 → 流程创建 → 流程发布 → 表单关联 → 角色授权**。

### OA 交互流程

#### OA Step 0: 解析用户需求

从用户描述中提取：

| 信息 | 默认值 | 示例 |
|------|--------|------|
| 应用名称 | 用户指定 | "费用报销单" |
| 表单编码 | 英文命名，`oa_` 前缀 | `oa_expense_reimbursement` |
| 表单字段 | 从描述中解析 | 申请人、金额、附件等 |
| 流程节点 | 从描述中解析 | 提交→部门审批→财务审核→结束 |
| 审批人 | 从描述中解析 | 角色/指定人/表达式 |

#### OA Step 1: 展示应用摘要并确认

**必须展示以下内容，等待用户确认后再执行：**

```
## OA 应用摘要

- 应用名称：费用报销单
- 表单编码：oa_expense_reimbursement
- 目标环境：http://localhost:8080/jeecgboot

### 表单字段

| 序号 | 字段名称 | 控件类型 | 必填 | 说明 |
|------|---------|---------|------|------|
| 1 | 申请人 | select-user | 是 | 标题字段 |
| 2 | 报销金额 | money | 是 | |
| ... | ... | ... | ... | ... |

### 流程节点

| 序号 | 节点名称 | 类型 | 审批人 |
|------|---------|------|--------|
| 1 | 开始 | startEvent | - |
| 2 | 提交申请 | userTask (草稿) | ${applyUserId} |
| ... | ... | ... | ... |

### 连线

开始 → 提交 → 审批 → 结束

确认以上信息正确？(y/n)
```

#### OA Step 2: 一键执行创建

用户确认后，使用 `scripts/desform_oa.py` 脚本一次性完成全部操作。

**使用步骤：**
1. 根据用户需求生成 JSON 配置文件（Write 到工作目录的临时 `.json` 文件）
2. 用 Bash 执行脚本：
```bash
python "<skill目录>/scripts/desform_oa.py" \
    --api-base <后端地址> \
    --token <TOKEN> \
    --config <config.json>
```
3. 删除临时 JSON 配置文件

**脚本自动完成：**
1. 创建设计器表单（调用 desform_creator）
2. 创建 BPMN 流程（调用 bpmn_creator）
3. 发布流程
4. 关联表单到流程
5. 设置草稿节点表单可编辑 + 表单地址
6. 查询已有授权 → 追加新表单ID → 保存授权给管理员角色

### OA JSON 配置格式

```json
{
  "appName": "费用报销单",
  "form": {
    "formName": "费用报销单",
    "formCode": "oa_expense_reimbursement",
    "layout": "word",
    "titleIndex": 2,
    "fields": [
      {"name": "报销单号", "type": "auto-number", "prefix": "BXBX"},
      {"name": "---", "type": "divider", "text": "基本信息"},
      {"name": "申请人", "type": "select-user", "required": true},
      {"name": "所在部门", "type": "select-depart", "required": true},
      {"name": "申请日期", "type": "date", "required": true},
      {"name": "报销类别", "type": "select", "required": true, "options": ["差旅费", "交通费", "办公用品"]},
      {"name": "---", "type": "divider", "text": "费用明细"},
      {"name": "报销金额", "type": "money", "required": true, "unit": "元"},
      {"name": "费用说明", "type": "textarea"},
      {"name": "发票/凭证", "type": "imgupload", "required": true},
      {"name": "附件", "type": "file-upload"},
      {"name": "---", "type": "divider", "text": "审批信息"},
      {"name": "部门负责人意见", "type": "oa-approval-comments"},
      {"name": "财务审核意见", "type": "oa-approval-comments"}
    ]
  },
  "process": {
    "processName": "费用报销审批流程",
    "processKey": "oa_expense_reimbursement_process",
    "typeId": "oa",
    "nodes": [
      {"id": "start", "type": "startEvent", "name": "开始"},
      {"id": "task_draft", "type": "userTask", "name": "提交报销申请", "draft": true,
       "assignee": {"type": "expression", "value": "applyUserId"}},
      {"id": "task_dept", "type": "userTask", "name": "部门负责人审批",
       "assignee": {"type": "role", "value": "manager"}},
      {"id": "task_finance", "type": "userTask", "name": "财务审核",
       "assignee": {"type": "role", "value": "finance"}},
      {"id": "end", "type": "endEvent", "name": "结束"}
    ],
    "flows": [
      {"id": "flow_1", "source": "start", "target": "task_draft"},
      {"id": "flow_2", "source": "task_draft", "target": "task_dept"},
      {"id": "flow_approve", "source": "task_dept", "target": "task_finance", "name": "通过"},
      {"id": "flow_reject", "source": "task_dept", "target": "end", "name": "拒绝"},
      {"id": "flow_end", "source": "task_finance", "target": "end"}
    ]
  },
  "auth": {
    "roleId": "f6817f48af4fb3af11b9e8bf182f618b",
    "authMode": "role"
  }
}
```

### OA 表单字段类型

支持所有 desform 标准控件类型（见上方 Step 1），额外增加 OA 专用类型：

| type | 说明 |
|------|------|
| `oa-approval-comments` | 审批意见组件（grid 6:18布局，禁用状态，由流程节点控制启用） |

> **审批意见组件规则：** 当字段名包含"意见"、"签字"、"审批"等关键词（如"部门负责人意见"、"财务审核签字"），**必须**使用 `oa-approval-comments` 类型，**不要**使用 `hand-sign` 或 `textarea`。

### OA 审批人（assignee）类型

| type 值 | value 含义 | 示例 |
|---------|-----------|------|
| `assignee` | 固定用户名 | `"admin"` |
| `expression` | 表达式变量名 | `"applyUserId"` |
| `candidateUsers` | 多候选人 | `"admin,jeecg"` |
| `role` | 角色编码 | `"manager"` |
| `dept` | 部门ID | `"6d35e179..."` |
| `approvalRole` | 审批角色编码 | `"finance_approver"` |

### OA 流程分支规则

> **重要：** 生成流程 JSON 配置时，必须根据表单字段决定分支方式：
> - **表单有 `result` 等可用于条件判断的字段** → 使用 `exclusiveGateway` + `conditions` 条件分支
> - **表单没有 `result` 字段** → 使用**手工分支**（从 userTask 直接引出多条无条件的 sequenceFlow）
>
> **手工分支使用前提：** 仅在通过/拒绝后还需要经过不同的后续处理节点时才使用。如果审批后只有结束节点，不需要手工分支，直接连到结束即可。

### 常见 OA 应用模板

#### 费用报销单
- 字段：报销单号、申请人、部门、日期、报销类别、金额、说明、发票、附件、部门负责人意见(审批意见)、财务审核意见(审批意见)
- 流程：提交 → 部门审批 →(手工分支: 通过/拒绝)→ 财务审核 → 结束

#### 请假申请单
- 字段：申请人、部门、日期、请假类型、开始/结束日期、天数、说明、附件、部门负责人意见(审批意见)
- 流程：提交 → 部门审批 → 结束（审批后只有结束节点，不需要手工分支）

#### 采购申请单
- 字段：申请人、部门、日期、采购物品、数量、预算金额、供应商、说明、附件、部门负责人意见(审批意见)、总经理意见(审批意见)
- 流程：提交 → 部门审批 →(手工分支: 通过/拒绝)→ 总经理审批 → 结束

#### 出差申请单（含 callActivity 子流程）
- 字段：申请人、部门、出差地点、开始/结束日期、天数、事由、预算、附件、部门负责人意见(审批意见)、总监审批意见(审批意见)
- 主流程：提交 → 部门审批 →(手工分支: 同意/不同意)→ 总监审批 → 借款子流程(callActivity) → 结束
- **注意：** 需先用 `jeecg-bpmn` 的 `bpmn_creator.py` 创建子流程，再创建主流程

---

---

## 参考文档

### 脚本工具

| 脚本 | 用途 |
|------|------|
| `scripts/desform_creator.py` | 通用表单创建脚本，优先使用 |
| `scripts/desform_view_creator.py` | 通用视图创建脚本（PC/移动端） |
| `scripts/desform_utils.py` | 共通工具库（控件工厂、API 封装、布局引擎、字段权限） |
| `scripts/desform_data_utils.py` | 数据操作工具库（CRUD、批量、回收站） |
| `scripts/desform_auth_retry.py` | 字段权限重试（仅权限自动创建失败时使用） |

### 创建/更新表单时阅读

- `references/desform-json-config.md` — JSON 配置格式、字段定义、子表说明、完整示例
- `references/desform-widget-types.md` — 用户描述关键词 → 控件 type 映射表
- `references/desform-dict-config.md` — 字典数据源配置（静态选项、系统字典、Python 用法）
- `references/desform-python-utils.md` — desform_utils.py 使用指南、快捷函数、layout 参数
- `references/desform-api-notes.md` — API 踩坑记录、错误处理、命名规则
- `references/desform-menu-sql.md` — 菜单 SQL 生成、字段说明、本地自动执行

### 高级功能（按需阅读）

- `references/desform-link-record.md` — 涉及关联记录 + 他表字段时阅读
- `references/desform-cross-form-binding.md` — 多表单互相关联时阅读（跨表 link-record/isSubTable/link-field/twoWayModel）
- `references/desform-sub-table-types.md` — 涉及子表时阅读（内部子表 vs 外部子表）
- `references/desform-formula-function.md` — 涉及公式计算时阅读（内置函数库、自定义 JS 函数、日期计算）
- `references/desform-default-value.md` — 涉及默认值时阅读（compose/function/javascript/linkage 四种类型）
- `references/desform-validation-rules.md` — 涉及校验规则时阅读（rules/defaultRules/pattern/unique）
- `references/desform-option-datasource.md` — 涉及选项数据源时阅读（静态/系统字典/关联表单/远程函数）
- `references/desform-js-enhance.md` — 涉及 JS 增强时阅读（自定义 JavaScript、API 方法、事件监听）
- `references/desform-layout.md` — 涉及布局模式时阅读（auto/half/full/word 四种模式的说明和适用场景）
- `references/desform-css-enhance.md` — 涉及 CSS 增强时阅读（自定义样式、Word 风格定制）
- `references/desform-layout-controls.md` — 涉及复杂布局时阅读（AutoGrid/Card/Grid/Tabs）
- `references/desform-linkage-query.md` — 涉及查询工作表时阅读（linkage 类型默认值）
- `references/desform-online-binding.md` — 涉及关联 Online 表单时阅读（字段映射/子表/数据同步）
- `references/desform-external-link.md` — 涉及外链表单时阅读（公共填报、免登录访问、外链授权管理）
- `references/desform-view-config.md` — 涉及视图时阅读（JSON 配置、移动端优化、踩坑汇总）

### 降级/排障

- `references/desform-fallback-manual-json.md` — 脚本失败时手动构造 JSON 的完整指南
- `references/desform-design-json-schema.md` — JSON Schema 结构、控件类型清单、通用字段
- `references/desform-widget-options.md` — 每种控件的完整 options 配置

### 示例参考

- `references/desform-examples.md` — 常见表单模式示例 + Python 脚本模板
- `references/desform-real-samples.md` — 真实业务表单案例（字典、半行、分区、公式、关联）
