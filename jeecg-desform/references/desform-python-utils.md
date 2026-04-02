# desform_utils.py 共通工具库使用指南

位于 `scripts/desform_utils.py`，提供控件工厂、API 封装、布局引擎、字段权限等功能。

## 基本用法

```python
import sys
sys.path.insert(0, r'<skill目录>/scripts')
from desform_utils import *

init_api('https://boot3.jeecg.com/jeecgboot', 'your-token')

# 简单表单（含字典用法）
create_form('员工信息', 'employee_info', [
    INPUT('姓名', required=True),
    RADIO('性别', [{'value': '1', 'label': '男'}, {'value': '2', 'label': '女'}], dict_code='sex'),
    PHONE('电话'),
    EMAIL('邮箱'),
    DEPART('部门'),
    SELECT('职称', options=['教授', '副教授', '讲师', '助教']),
    TEXTAREA('备注'),
])

# 带关联的表单
form_id, title = create_form('客户信息', 'customer_info', [
    INPUT('客户名称', required=True),
    PHONE('电话'),
])
# 查询字段用于关联
tf, fields = get_form_fields('customer_info')
create_form('联系人', 'contact_info', [
    INPUT('姓名', required=True),
    LINK_RECORD('所属客户', 'customer_info', tf, [fields['客户名称']['model']]),
])
```

## 执行步骤

```
1. Write 工具 → 写入业务脚本 create_xxx.py（scripts/ 目录，import desform_utils）
2. Bash 工具 → cd <skill目录>/scripts && python create_xxx.py
3. Bash 工具 → rm create_xxx.py（清理临时脚本）
```

## 可用的快捷函数（大写命名）

- 基础: `INPUT`, `TEXTAREA`, `NUMBER`, `INTEGER`, `MONEY`, `DATE`, `TIME`, `SWITCH`, `SLIDER`, `RATE`, `COLOR`
- 选择: `RADIO`, `SELECT`, `CHECKBOX`（支持 dict_code 字典）
- 系统: `USER`, `DEPART`, `DEPART_POST`, `ORG_ROLE`, `PHONE`, `EMAIL`, `AREA`
- 选择(高级): `TABLE_DICT`, `SELECT_TREE`
- 文件: `FILE`, `IMGUPLOAD`, `HANDSIGN`
- 高级: `AUTONUMBER`, `FORMULA`, `SUMMARY`, `LINK_RECORD`, `LINK_FIELD`
- 展示: `BARCODE`, `CAPITAL_MONEY`, `TEXT_COMPOSE`, `LOCATION`, `MAP`, `OCR`
- 静态(不存储数据): `TEXT`, `BUTTONS`
- 不需要 card: `DIVIDER`, `EDITOR`, `MARKDOWN`, `TABS`
- 子表内基础: `SUB_INPUT`, `SUB_TEXTAREA`, `SUB_INTEGER`, `SUB_NUMBER`, `SUB_MONEY`, `SUB_DATE`, `SUB_TIME`
- 子表内选择: `SUB_SELECT`, `SUB_RADIO`, `SUB_CHECKBOX`, `SUB_TABLE_DICT`, `SUB_SELECT_TREE`
- 子表内系统: `SUB_USER`, `SUB_DEPART`, `SUB_DEPART_POST`, `SUB_PHONE`, `SUB_EMAIL`, `SUB_AREA`
- 子表内开关: `SUB_SWITCH`, `SUB_SLIDER`, `SUB_RATE`, `SUB_COLOR`
- 子表内文件: `SUB_IMGUPLOAD`, `SUB_FILE`
- 子表内系统（补充）: `SUB_ORG_ROLE`
- 子表内关联: `SUB_LINK_RECORD`, `SUB_LINK_FIELD`, `SUB_FORMULA`, `SUB_PRODUCT`（formula PRODUCT 模式的语法糖）
- 布局容器: `GRID`, `CARD`, `TABS`（不需要外层 card 包裹的独立容器）
- 内部容器: `make_card`（AutoGrid card 包裹）, `make_sub_table`
- API: `init_api`, `create_form`, `update_form`, `delete_form`, `query_form`, `get_form_id`, `get_form_fields`, `find_or_create_form`, `save_design`, `check_code_available`
- 权限: `add_auth_batch`（新建时批量创建）, `sync_auth`（更新时增删同步）, `save_auth_from_design`（重试用）
- 字典: `query_dict(code)` 查询字典项, `search_dict(keyword)` 按名称/编码模糊搜索字典
- SQL: `gen_menu_sql`

## `create_form` 的 `layout` 参数

- `'auto'`（默认）：字段数 >= 6 时自动使用半行两列布局
- `'half'`：强制半行布局
- `'full'`：强制整行布局（不做半行处理）
- `'word'`：Word 风格布局（仅在用户明确要求时使用）

> 各布局模式的详细说明、适用场景和实现原理详见 `desform-layout.md`。

## `gen_menu_sql` 用法

```python
# 菜单SQL（ID 自动生成 UUID，只需传菜单名和子项）
print(gen_menu_sql('CRM系统', [
    ('客户信息', 'customer_info', 1),
    ('联系人', 'contact_info', 2),
]))
```

**`gen_menu_sql` 的 `icon` 参数：**
- 默认值 `'ant-design:appstore-outlined'`，一级菜单自动带图标
- 可自定义：`gen_menu_sql('费用管理', [...], icon='ant-design:dollar-outlined')`

## 更多用法

```python
# 查询表单
form = query_form('customer_info')
print(form['id'], form['updateCount'])

# 修改已有表单设计（自动获取 updateCount）
update_form('customer_info', [
    INPUT('客户名称', required=True),
    PHONE('电话'),
    EMAIL('邮箱'),
    TEXTAREA('备注'),
])

# 删除表单（支持 3 种方式）
delete_form('customer_info')                    # 传 code，自动查找 ID
delete_form('customer_info', '123456789')       # 传 code + 已知 ID，跳过搜索（最快）
delete_form('123456789012345678')               # 只传 ID
```

## 通过 `**kw` 传递高级参数

所有大写工厂函数接受 `**kw`，其中 `mobile_options` 会传递到 `make_widget()` 的 `mobile_options` 参数。

### mobile_options — 移动端覆盖配置

`mobileOptions` 是 widget 顶层属性（非 options 内部），移动端渲染时自动 merge 到 options。

```python
# radio/checkbox 移动端横向排列
RADIO('性别', ['男', '女'], mobile_options={"inline": True, "matrixWidth": 120})
CHECKBOX('兴趣', ['阅读', '运动'], mobile_options={"inline": True, "matrixWidth": 120})

# date/time 移动端禁止手动输入
DATE('日期', mobile_options={"editable": False})
TIME('时间', mobile_options={"editable": False})

# table-dict 移动端禁用搜索过滤
TABLE_DICT('字典', dict_table='...', mobile_options={"filterable": False})
```

### options 内的通用属性

`hiddenOnAdd` 和 `fieldNote` 已包含在各工厂函数的 opts 中，可在调用前或调用后修改：

```python
# 方式1：创建后修改 widget dict
w, k, m = INPUT('备注字段')
w[0]['options']['hiddenOnAdd'] = True   # 新增时隐藏
w[0]['options']['fieldNote'] = '仅编辑时显示'  # 字段备注
```

### GRID / CARD 容器函数

`GRID()` 和 `CARD()` 是布局容器的大写工厂函数，与 `TABS()` 类似，不需要外层 card 包裹：

```python
# CARD 容器 — 将多个控件放入一个卡片
input_w, _, _ = INPUT('姓名', wrap=False)
phone_w, _, _ = PHONE('手机', wrap=False)
card_w, card_k, card_m = CARD(input_w, phone_w, row_num=2)

# GRID 栅格 — 精确控制列宽
left_w, _, _ = INPUT('左列', wrap=False)
right_w, _, _ = INPUT('右列', wrap=False)
grid_w, grid_k, grid_m = GRID([
    (12, [left_w]),
    (12, [right_w]),
])

# 注意：CARD/GRID 内的子控件需要 wrap=False 避免双重 card 包裹
```

> 与 `make_card()` 的区别：`make_card()` 创建的是 AutoGrid 内部的 card（`isAutoGrid: true`），
> 而 `CARD()` 创建的是显式的非 AutoGrid 卡片容器，结构更完整（含 className、icon 等）。

## 重要限制（实战踩坑）

1. **Windows 环境下 curl 发送中文/长JSON会出错**，必须使用 Python 的 urllib/requests 确保 UTF-8 编码
2. **禁止使用 `python3 -c "..."` 内联方式**，因为 JSON 中的特殊字符会被 bash 解析出错
3. **必须先用 Write 工具写入 `.py` 临时文件，再用 Bash 执行，最后删除临时文件**
4. **Windows 控制台中文输出乱码**：`desform_utils.py` 模块加载时已自动执行 `sys.stdout.reconfigure(encoding='utf-8')`，因此 `from desform_utils import *` 之后的脚本和 `desform_creator.py` 脚本均不会乱码。`python -c "..."` 内联脚本如未 import desform_utils，需手动加 `import sys; sys.stdout.reconfigure(encoding='utf-8')`
