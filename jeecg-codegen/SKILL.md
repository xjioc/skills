---
name: jeecg-codegen
description: Use when user asks to generate JeecgBoot CRUD code, create a new module, add/modify fields on existing module, or says "代码生成", "生成代码", "创建模块", "新增功能", "建表", "加字段", "加一个字段", "增加字段", "新增字段", "修改字段", "删除字段", "generate code", "new entity", "add field"
---

# JeecgBoot 代码生成器

将自然语言需求转换为 JeecgBoot 全套 CRUD 代码（后端 Java + 前端 Vue3 + 菜单权限 SQL），并支持对已生成模块的增量字段修改。

## 主数据复用规则

> **重要：** 生成代码涉及的字典、角色、用户、部门等主数据，必须遵循"先查后建"原则。
> 使用 `jeecg-system` skill 的 `system_utils.py` 查询和管理主数据。
> 详见 `../jeecg-system/SKILL.md`。

## 交互流程

### Step 0: 判断操作类型 — 全量生成 or 增量修改？

**识别增量修改的关键词：** "加字段"、"增加字段"、"新增字段"、"加一个XX字段"、"删除字段"、"修改字段"、"改一下XX"、"给XX模块加"、"给XX表加"

如果是增量修改 → 进入 **场景C**
如果是全量生成 → 进入 **场景A** 或 **场景B**

### Step 1: 全量生成 — 判断场景

**场景A — 已有表（用户给了表名）：**
1. 通过数据库查询获取精确 DDL（见"数据库连接"章节）
2. 从 DDL 中解析：主键类型、全部字段（名称/类型/注释/是否nullable）、是否有系统字段
3. 根据字段类型和注释自动推导前端控件类型
4. 用户无需描述字段，AI 全部自动推导

**场景B — 新建表（用户用自然语言描述需求）：**
1. 从用户描述中提取：表名、实体名、功能描述、字段列表
2. 用"智能字段推导"规则推导 DB 类型和前端控件
3. 默认添加全部系统字段（create_by/create_time/update_by/update_time/sys_org_code）
4. 生成建表 DDL 写入 Flyway SQL

**场景C — 增量修改（给已有模块加/改/删字段）：**
1. **定位目标模块**：从用户提到的表名、模块名、实体名中识别目标
2. **扫描已有代码文件**：在后端和前端目录中搜索已生成的文件
3. **读取全部已有文件**：Entity.java、*.data.ts、*List.vue、*Modal.vue（如有 Form.vue 也读取）
4. **解析当前字段列表**：从 Entity.java 解析已有字段
5. **推导新字段属性**：用"智能字段推导"规则推导 DB 类型、Java 类型、前端控件
6. **展示修改摘要**，等待用户确认后再修改

**增量修改的操作类型：**
- **加字段**：在所有文件中追加新字段定义
- **删字段**：从所有文件中移除指定字段定义
- **改字段**：修改指定字段的类型、控件、注释等

**判断表类型：**
- 提到"分类/层级/树/上下级" → **树表**
- 提到"主子表/明细/一对多/订单+商品" → **一对多**
- 默认 → **单表**

### Step 2: 询问用户选项（仅全量生成需要）
一次性展示所有选项及默认值，用户说"确认"即可全部采用默认值，或只说需要改的：
1. **后端模块**：默认 `jeecg-module-system/jeecg-system-biz`
2. **前端风格**：默认 `vue3`（封装风格），可选 `vue3Native`（原生风格）
3. **前端视图目录**：默认用 entityPackage 值
4. **是否读取系统字典**：默认 `是`，读取后可自动为字段匹配已有字典编码（见"字典智能匹配"章节）

### Step 3: 展示摘要
- **全量生成**：列出表名、字段清单（名称/类型/控件/校验/字典），等待用户确认后再生成。
- **增量修改**：列出要修改的文件路径 + 每个文件的具体变更内容（新增/删除/修改哪些行），等待用户确认。

### Step 4: 执行 — 按需加载参考文件

**根据表类型读取对应的参考文件（不要全部读取！只读需要的）：**

| 表类型 | 需读取的技能文件 | 需读取的代码模板文件 |
|--------|----------------|-------------------|
| **单表** | `skill-components.md` | `codegen-ref-single.md` |
| **一对多** | `skill-components.md` + `skill-onetomany.md` | `codegen-ref-single.md` + `codegen-ref-onetomany.md` |
| **树表** | `skill-components.md` + `skill-tree.md` | `codegen-ref-tree.md` |
| **增量修改** | `skill-components.md` | `codegen-ref-incremental.md` |

> **所有文件都在同目录下**，使用 Read 工具读取，路径示例：
> `C:/Users/25067/.claude/skills/jeecg-codegen/skill-components.md`

读取完参考文件后，按模板骨架顺序生成全部文件。

- **增量修改**：使用 Edit 工具精确修改每个文件。

### Step 5: 输出清单
列出所有生成/修改的文件路径 + 后续操作说明（执行SQL、重启后端等）。

### 本地环境自动执行菜单 SQL 规则

**前置条件（必须）：执行任何 SQL 之前，必须先询问用户要执行到哪个数据库。** 不要自动假设目标数据库名称，即使配置文件中有默认值。用户本机可能有多个数据库实例。

**判断条件：** 数据库连接地址为 `127.0.0.1` 或 `localhost`（即本地开发环境）。

**自动执行方式：** 确认目标数据库后，生成 Flyway SQL 文件后，同时通过 Bash 工具直接执行菜单权限 SQL：

```bash
# 先询问用户目标数据库名，假设用户确认为 {dbname}
# 先检查菜单是否已存在，避免重复插入
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -uroot -proot {dbname} -e "SELECT id FROM sys_permission WHERE id='{timestamp}01'"
# 不存在则执行全部菜单 + 角色授权 SQL
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -uroot -proot {dbname} < {flyway_sql_file_path}
```

**注意事项：**
- **执行 SQL 前必须先询问用户目标数据库名称**，不能自动假设
- 仅在本地环境（127.0.0.1/localhost）自动执行，远程环境只生成 Flyway 文件
- 执行前先检查主菜单 ID 是否已存在，避免重复插入
- 如果 MySQL 执行失败，提示用户手动执行 Flyway SQL，不中断整体流程
- 输出结果中标注 `菜单 SQL：已自动执行 ✓`

## 数据库连接

**已有表场景必须先查数据库！** 通过以下方式获取精确 DDL：

**重要：执行任何 SQL 之前，必须先询问用户要执行到哪个数据库。** 不要自动假设数据库名称。先读取 `application-dev.yml` 获取配置中的数据库名，然后向用户确认是否使用该数据库。

```bash
# 1. 先读取项目数据库配置，获取数据库名
# 配置文件: jeecg-module-system/jeecg-system-start/src/main/resources/application-dev.yml

# 2. 向用户确认目标数据库名后，再执行查询（假设确认为 {dbname}）

# 查询表 DDL
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -uroot -proot {dbname} -e "SHOW CREATE TABLE 表名\G"

# 查询字段注释
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -uroot -proot {dbname} -e "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT, COLUMN_KEY, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='{dbname}' AND TABLE_NAME='表名' ORDER BY ORDINAL_POSITION"
```

如果无法连接数据库，回退方案：在项目 SQL 文件中搜索表定义（`grep -r "CREATE TABLE.*表名"` 在 docs/db/ 目录下）。

## Flyway 版本号规则

**生成 Flyway SQL 前必须检查已有版本号，自动递增避免冲突！**

```bash
# Flyway SQL 目录（路径以 CLAUDE.md 中的后端根路径为准）
ls {后端根路径}/jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql/ | sort -V | tail -5
```

版本命名规则：`V{YYYYMMDD}_{序号}__{描述}.sql`
- 检查当天是否已有文件（如 `V20260311_1__xxx.sql`）
- 如果有，序号递增（`V20260311_2__xxx.sql`）
- 如果没有，从 `_1` 开始

## 菜单 SQL 的 ID 生成

**必须使用真实时间戳确保唯一性！** 通过以下命令获取：

```bash
date +%s%3N  # 输出13位毫秒级时间戳，如 1741704000123
```

用这个时间戳作为基础 ID，依次拼接 01-14：
- 主菜单: `{timestamp}01`
- 添加按钮: `{timestamp}02`
- 编辑按钮: `{timestamp}03`
- ... 以此类推

## 字典智能匹配

**用户选择"读取系统字典"后，执行以下查询获取全部可用字典：**

```bash
# 查询所有字典编码及其选项值（{dbname} 需替换为用户确认的数据库名）
mysql --no-defaults --default-character-set=utf8mb4 -h127.0.0.1 -P3306 -uroot -proot {dbname} -e "
SELECT d.dict_code, d.dict_name, GROUP_CONCAT(i.item_text, '=', i.item_value ORDER BY i.sort_order SEPARATOR ', ') AS items
FROM sys_dict d
LEFT JOIN sys_dict_item i ON d.id = i.dict_id AND i.status = 1
WHERE d.del_flag = 0
GROUP BY d.dict_code, d.dict_name
ORDER BY d.dict_code
"
```

**匹配规则：** 拿到字典列表后，按以下优先级为字段匹配字典：
1. **用户明确指定** — 用户说"状态用字典 order_status"，直接使用
2. **字段名精确匹配** — 字段名（如 `status`）与 dict_code 完全一致
3. **语义关键词匹配** — 字段注释含"状态/类型/级别/分类"等关键词，搜索 dict_name 包含相同关键词的字典
4. **不匹配** — 找不到合适字典时，不使用字典注解，按普通 Input 处理

**匹配成功后的效果：**
- Entity: 自动添加 `@Dict(dicCode = "matched_dict_code")`
- data.ts columns: `dataIndex` 使用 `fieldName_dictText` 后缀
- data.ts formSchema: `component` 使用 `JDictSelectTag`，`componentProps: { dictCode: 'matched_dict_code' }`
- data.ts searchFormSchema: 同样使用 `JDictSelectTag` 组件

**展示格式：** 在 Step 3 表结构摘要中，匹配到字典的字段标注字典编码和选项值，如：
```
| 字段名 | 类型 | 控件 | 字典 |
| status | varchar(10) | JDictSelectTag | order_status (待付款=0, 已付款=1, 已完成=2) |
```

### 智能字段推导中的字典关键词

当用户描述字段时，按以下关键词自动推导使用哪种字典：

| 用户描述关键词 | 推导字典类型 | 推荐控件 |
|--------------|------------|---------|
| "状态"、"类型"、"级别"、"优先级" | 系统字典（先搜索 sys_dict 匹配） | JDictSelectTag |
| "区域"、"地区"、"分类"、"类目"、"树形选择" | 分类字典（搜索 sys_category 匹配） | JCategorySelect |
| "部门"、"组织"、"归属" | 表字典（关联 sys_depart） | JDictSelectTag(表字典) |
| "用户"、"负责人"、"经办人" | 用户选择组件（非字典） | JSelectUserByDept |

## 项目路径

> **重要：** 以下为默认路径。实际路径以 `CLAUDE.md` 和 memory 中的配置为准，优先使用它们。

| 类别 | 路径 |
|------|------|
| 后端根 | 读取 `CLAUDE.md` 中的 Backend 路径 |
| 前端根 | 读取 `CLAUDE.md` 中的 Frontend 路径 |
| 后端代码 | `{module}/src/main/java/org/jeecg/modules/{entityPackage}/` |
| 前端代码 | `src/views/{viewDir}/` |
| Flyway SQL | `jeecg-module-system/jeecg-system-start/src/main/resources/flyway/sql/mysql/` |

## 命名约定

- **表名**：snake_case（如 `biz_goods`）
- **实体名**：表名转 PascalCase（如 `BizGoods`）
- **entityPackage**：表名前缀或用户指定（如 `biz`）
- **bussiPackage** 固定：`org.jeecg.modules`
- **权限编码**：`{entityPackage}:{tableName}:add/edit/delete/deleteBatch/exportXls/importExcel`

## 智能字段推导

**用于新建表场景（从自然语言推导），或已有表但字段无注释时的补充推导：**

| 语义关键词 | dbType | Java 类型 | vue3 组件 | vue3Native 组件 |
|-----------|--------|----------|----------|----------------|
| 名称/标题/编码 | varchar(100) | String | Input | a-input |
| 金额/价格/费用 | decimal(10,2) | BigDecimal | InputNumber | a-input-number |
| 数量/数目/个数 | int | Integer | InputNumber | a-input-number |
| 状态/类型/级别 | varchar(10) | String | JDictSelectTag | JDictSelectTag |
| 是否/开关 | varchar(2) | String | Switch | a-switch |
| 日期/生日 | date | Date | DatePicker | a-date-picker |
| 时间/日期时间 | datetime | Date | DatePicker(showTime) | a-date-picker(showTime) |
| 备注/描述/说明 | text | String | InputTextArea | a-textarea |
| 内容/富文本 | text | String | JEditor | JEditor |
| 图片/头像/照片 | varchar(1000) | String | JImageUpload | JImageUpload |
| 文件/附件 | varchar(1000) | String | JUpload | JUpload |
| 用户/负责人 | varchar(32) | String | JSelectUserByDept | JSelectUserByDept |
| 部门/组织 | varchar(32) | String | JSelectDept | JSelectDept |
| 排序/序号 | int | Integer | InputNumber | a-input-number |

**已有表场景的 DB类型→控件 映射（当字段无注释时使用）：**

| DB列类型 | Java类型 | 默认前端控件 |
|---------|---------|-----------|
| varchar(n) n<=200 | String | Input |
| varchar(n) n>200 | String | InputTextArea |
| text / longtext | String | InputTextArea |
| int / tinyint | Integer | InputNumber |
| bigint | Long | InputNumber |
| decimal / double / float | BigDecimal | InputNumber |
| date | Date | DatePicker |
| datetime / timestamp | Date | DatePicker(showTime) |

## 主键策略（根据已有表结构自适应）

| 表DDL中的主键定义 | Java类型 | @TableId | 说明 |
|------------------|---------|----------|------|
| `int AUTO_INCREMENT` | Integer | `@TableId(type = IdType.AUTO)` | int自增主键 |
| `bigint AUTO_INCREMENT` | Long | `@TableId(type = IdType.AUTO)` | bigint自增主键 |
| `varchar(36)` / `varchar(32)` 无AUTO_INCREMENT | String | `@TableId(type = IdType.ASSIGN_ID)` | JeecgBoot标准字符串主键 |
| `bigint` 无AUTO_INCREMENT | Long | `@TableId(type = IdType.ASSIGN_ID)` | 雪花ID |

**注意：** 当主键为 Integer/Long 类型时，Controller 中 `delete` 和 `queryById` 的参数类型也要对应调整。

## 系统字段（按实际表结构判断）

**不是所有表都有系统字段！** 生成前必须检查表是否实际包含这些字段，**只生成表中存在的字段**：

| 字段 | 说明 | 不存在时的处理 |
|------|------|--------------|
| `create_by` | 创建人 | 不生成该属性 |
| `create_time` | 创建时间 | 不生成该属性 |
| `update_by` | 更新人 | 不生成该属性 |
| `update_time` | 更新时间 | 不生成该属性 |
| `sys_org_code` | 所属部门 | 不生成该属性 |

如果是**新建表**（用户自然语言描述需求），则默认添加全部系统字段。
如果是**已有表**（用户指定了表名且数据库中已存在），则必须根据实际 DDL 来决定。

树表额外字段：`pid`、`has_child`（同样需检查是否实际存在）。

## 子文件索引

本技能拆分为多个子文件，按需加载（不要预加载所有文件）：

### 技能规则文件（组件用法 + 特定表类型规则）
| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `skill-components.md` | 三种字典完整用法 + 全组件控件用法 + searchFormSchema规则 + 通用规则(17.2/17.3/17.5/17.6) | **所有**代码生成都需读取 |
| `skill-onetomany.md` | 一对多布局风格 + JVxeTable子表列配置 + 规则13-28 | 仅**一对多**表类型时读取 |
| `skill-tree.md` | 树表规则29-33 | 仅**树表**类型时读取 |

### 代码模板文件（后端+前端代码骨架）
| 文件 | 内容 | 何时读取 |
|------|------|---------|
| `codegen-ref-single.md` | Section A 单表模板 + Section D 字段映射 + Section E DDL模板 | **单表**和**一对多**（基础） |
| `codegen-ref-onetomany.md` | Section C 一对多差异模板 | 仅**一对多**表类型时读取 |
| `codegen-ref-tree.md` | Section B 树表模板 | 仅**树表**类型时读取 |
| `codegen-ref-incremental.md` | Section F 增量修改模板 | 仅**增量修改**时读取 |
