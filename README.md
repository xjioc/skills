# JeecgBoot Skills

JeecgBoot 低代码平台生态的 AI Skills 集合，为 [Claude Code](https://claude.com/claude-code) 提供专业化的开发能力增强。

## 什么是 Skills？

Skills 是 Claude Code 的技能扩展机制，通过结构化的提示词让 AI 获得特定领域的专业能力。安装 Skill 后，Claude Code 可以在对话中自动识别意图并触发对应的专业工作流，无需手动指定。

## 已有 Skills

| Skill | 说明 | 状态 |
|-------|------|------|
| [jeecg-codegen](./jeecg-codegen/) | 代码生成器 — 自然语言描述需求，自动生成 JeecgBoot 全套 CRUD 代码 | ✅ 可用 |
| [jeecg-onlform](#jeecg-onlform-online-表单生成器) | Online 表单生成器 — 自然语言描述需求，通过 API 自动创建/编辑 Online 表单 | ✅ 可用 |
| [jeecg-onlreport](#jeecg-onlreport-online-报表生成器) | Online 报表生成器 — 自然语言描述需求，通过 API 自动创建/编辑 Online 报表 | ✅ 可用 |
| [jeecg-desform](#jeecg-desform-设计器表单生成器) | 设计器表单生成器 — 自然语言描述需求，通过 API 自动创建/编辑设计器表单 | ✅ 可用 |
| [jeecg-bpmn](#jeecg-bpmn-bpm-流程生成器) | BPM 流程生成器 — 自然语言描述审批流程，自动生成 BPMN XML 并创建流程 | ✅ 可用 |

### jeecg-codegen 代码生成器

将自然语言需求转换为 JeecgBoot 全套 CRUD 代码（后端 Java + 前端 Vue3 + 建表 SQL + 菜单权限 SQL）。

**核心能力：**
- 单表 / 树表 / 一对多（主子表）三种模式
- 已有表反向生成（自动读取数据库 DDL）
- 新建表智能推导（自然语言 → 字段类型 + 前端控件）
- 增量字段修改（加字段 / 删字段 / 改字段，无需重新生成）
- 字典智能匹配（自动关联系统 `sys_dict` 字典）
- 主键策略自适应、Flyway 版本号自动递增

**快速体验：**
```
帮我生成一个商品管理模块，包含商品名称、价格、库存、状态、图片、描述
```

详细使用说明请查看 [jeecg-codegen/CODEGEN-GUIDE.md](./jeecg-codegen/CODEGEN-GUIDE.md)。

### jeecg-onlform Online 表单生成器

将自然语言的表单需求描述转换为 Online 表单配置，并通过 API 在 JeecgBoot 系统中自动创建/编辑表单。

> **注意：** 本 Skill 处理「Online 表单」（元数据驱动，运行时 CRUD），不涉及「设计器表单」（desform）。

**核心能力：**
- 单表 / 主子表（一对多/一对一）/ 树表 三种模式
- 自然语言 → 字段控件类型智能推导（text / date / list / image / file / sel_user / popup 等 30+ 控件）
- 字典智能匹配（系统字典 / 字典表 / 带条件字典表）
- 增量字段修改（加字段 / 删字段 / 改字段，无需重新创建）
- 自动同步数据库 + 生成菜单 SQL
- 主子表自动关联（外键、主题模板 tab/erp/innerTable）
- 树表自动配置（pid / has_child / 树形字段）

**前置条件：**
- JeecgBoot 后端 API 地址
- X-Access-Token（从浏览器 F12 → Network → Request Headers 中获取）

**快速体验：**
```
创建一个请假申请表单，包含姓名(必填)、请假类型(下拉)、开始日期、结束日期、请假天数、请假原因、附件、审批人(用户选择)
```

**支持的控件类型（部分）：**

| 用户描述 | 控件类型 | 说明 |
|---------|---------|------|
| 文本/名称/编码 | `text` | 单行文本 |
| 备注/描述 | `textarea` | 多行文本 |
| 日期/生日 | `date` | 日期选择 |
| 日期时间 | `datetime` | 日期时间选择 |
| 是否/开关 | `switch` | 开关 |
| 状态/类型(单选) | `radio` | 字典单选 |
| 下拉/选择 | `list` | 字典下拉 |
| 多选/标签 | `checkbox` | 字典多选 |
| 图片/头像 | `image` | 图片上传 |
| 文件/附件 | `file` | 文件上传 |
| 富文本/HTML | `umeditor` | 富文本编辑器 |
| 用户/审批人 | `sel_user` | 用户选择 |
| 部门/组织 | `sel_depart` | 部门选择 |
| 省市区/地址 | `pca` | 省市区联动 |
| 分类/树选择 | `cat_tree` | 分类字典树 |

**交互流程：**
1. 用户描述表单需求
2. AI 智能推导字段配置（控件类型、字典、查询方式等）
3. 展示配置摘要（系统字段 + 业务字段），等待确认
4. 调用 API 创建表单 → 自动同步数据库 → 输出菜单 SQL

### jeecg-onlreport Online 报表生成器

将自然语言的报表需求描述转换为 Online 报表配置，并通过 API 在 JeecgBoot 系统中自动创建/编辑报表。

> **注意：** 本 Skill 处理「Online 报表」（SQL 驱动的数据报表），不涉及「Online 表单」或「设计器表单」。

**核心能力：**
- SQL 驱动的只读数据报表
- 自然语言描述 → SQL 语句智能推导
- 字段显示名称自动中文翻译
- 查询条件智能配置（模糊 / 精确 / 范围）
- 字典值翻译（系统字典 / SQL 字典 / 取值表达式）
- 合计行自动识别（金额/数量字段）
- 分组表头（多级表头）
- SQL 参数化查询（Velocity 模板语法）
- 动态数据源支持
- 增量修改（编辑已有报表）

**前置条件：**
- JeecgBoot 后端 API 地址
- X-Access-Token（从浏览器 F12 → Network → Request Headers 中获取）

**快速体验：**
```
创建一个销售统计报表，查询销售表的商品名称、销售金额、销售日期、状态，金额需要合计，名称支持模糊查询，日期支持范围查询
```

**字段智能配置：**

| 配置项 | 自动推导规则 |
|--------|-------------|
| 显示名称 | 根据字段名语义翻译中文（name→名称, amount→金额） |
| 是否显示 | id/系统字段自动隐藏，业务字段显示 |
| 查询方式 | 文本→模糊, 状态→精确, 日期→范围 |
| 是否排序 | 日期/金额/数量字段可排序 |
| 是否合计 | 金额/数量字段自动合计 |
| 字典翻译 | 自动匹配系统字典或生成取值表达式 |

**交互流程：**
1. 用户描述报表需求（或直接提供 SQL）
2. 调用 parseSql API 解析字段列表
3. AI 智能配置每个字段（显示名、查询、排序、字典、合计等）
4. 展示配置摘要，等待确认
5. 调用 API 创建报表 → 输出菜单 SQL

**高级功能：**
- **SQL 参数化**：支持 Velocity 模板 `${#if($param != '')} AND field = '$param' ${#end}`
- **动态数据源**：通过 `dbSource` 指定非默认数据源
- **分组表头**：多个字段共用 `groupTitle` 实现多级表头
- **字段跳转**：通过 `fieldHref` 配置点击跳转链接

### jeecg-desform 设计器表单生成器

将自然语言的表单需求描述转换为设计器表单（desform）配置 JSON，并通过 API 在 JeecgBoot 系统中自动创建/编辑表单。

> **注意：** 本 Skill 处理「设计器表单」（desform，可视化拖拽设计），不涉及「Online 表单」（cgform）。两者是完全独立的表单体系。

**核心能力：**
- 自然语言 → 表单设计 JSON 智能生成
- 40+ 控件类型支持（文本 / 数字 / 日期 / 下拉 / 图片上传 / 富文本 / 用户选择 / 部门选择 / 手写签名 / 子表等）
- 字典数据源配置（静态选项 / 系统字典）
- 子表设计（sub-table-design）
- 关联记录 + 他表字段（link-record / link-field）
- 公式计算（求和 / 均值 / 自定义公式）
- 编辑已有表单（查询 + 修改 + 保存）
- 自动生成菜单 SQL

**前置条件：**
- JeecgBoot 后端 API 地址
- X-Access-Token（从浏览器 F12 → Network → Request Headers 中获取）

**快速体验：**
```
AI设计一个员工请假申请表单，包含姓名(必填)、请假类型(下拉：事假/病假/年假)、开始日期、结束日期、请假天数(整数)、请假原因(多行文本)、附件(文件上传)
```

**支持的控件类型（部分）：**

| 用户描述 | 控件类型 | 说明 |
|---------|---------|------|
| 文本/姓名 | `input` | 单行文本 |
| 备注/原因 | `textarea` | 多行文本 |
| 数量/金额 | `number` / `money` | 数字 / 金额 |
| 整数/天数 | `integer` | 整数输入 |
| 日期/生日 | `date` | 日期选择 |
| 时间/几点 | `time` | 时间选择 |
| 单选/性别 | `radio` | 单选框组 |
| 多选/标签 | `checkbox` | 多选框组 |
| 下拉/选择 | `select` | 下拉选择 |
| 开关/启用 | `switch` | 开关 |
| 评分/星级 | `rate` | 评分 |
| 图片/照片 | `imgupload` | 图片上传 |
| 附件/文件 | `file-upload` | 文件上传 |
| 富文本/HTML | `editor` | 富文本编辑器 |
| 省市/地区 | `area-linkage` | 省市级联动 |
| 选人/审批人 | `select-user` | 用户选择 |
| 部门/选部门 | `select-depart` | 部门选择 |
| 手写签名 | `hand-sign` | 手写签名 |
| 子表/明细 | `sub-table-design` | 设计子表 |
| 关联记录 | `link-record` | 关联其他表单记录 |
| 公式/计算 | `formula` | 公式计算 |
| 自动编号 | `auto-number` | 流水号 |

**交互流程：**
1. 用户描述表单需求
2. AI 识别字段并选择控件类型，配置字典数据源
3. 展示表单摘要（字段列表 + 控件类型 + 必填等），等待确认
4. 生成 desformDesignJson → 调用 API 创建/更新表单 → 输出菜单 SQL

### jeecg-bpmn BPM 流程生成器

将自然语言的流程描述转换为 Flowable BPMN 2.0 XML，并通过 API 在 JeecgBoot 系统中自动创建流程。

> **注意：** 本 Skill 处理 BPM 工作流（审批流程、业务流程），基于 Flowable 引擎。

**核心能力：**
- 自然语言 → Flowable BPMN 2.0 XML 智能生成
- 多种节点类型支持（用户任务 / 排他网关 / 并行网关 / 包含网关 / 子流程 / 调用子流程）
- 灵活的审批人配置（固定指定人 / 角色组 / 部门 / 岗位 / 表达式 / 表单字段选人 / 上一节点指派）
- 会签支持（并行会签 / 顺序会签 / 多实例配置）
- 条件分支（通过/拒绝、金额判断等条件表达式）
- 自动生成流程布局图（BPMNDiagram）
- 编辑已有流程
- 数据库配置表管理（节点配置 / 表单绑定 / 字段权限）

**前置条件：**
- JeecgBoot 后端 API 地址
- X-Access-Token（从浏览器 F12 → Network → Request Headers 中获取）

**快速体验：**
```
创建一个请假审批流程：员工提交申请 → 部门经理审批 → 通过则HR审批 → 结束，拒绝则直接结束
```

**支持的节点类型：**

| 用户描述 | BPMN 节点类型 | 说明 |
|---------|--------------|------|
| 开始 | `startEvent` | 流程起点 |
| 结束 | `endEvent` | 流程终点 |
| 审批/审核/处理 | `userTask` | 用户任务节点 |
| 条件判断/分支 | `exclusiveGateway` | 排他网关（二选一） |
| 同时/并行 | `parallelGateway` | 并行网关（同时执行） |
| 条件并行 | `inclusiveGateway` | 包含网关（部分并行） |
| 子流程/嵌套 | `subProcess` | 内嵌子流程 |
| 会签 | `multiInstance` | 多人同时/顺序审批 |

**审批人配置方式：**

| 配置方式 | 示例 | 说明 |
|---------|------|------|
| 发起人 | `${applyUserId}` | 流程发起人自动填充 |
| 固定用户 | `admin` | 指定用户名 |
| 角色组 | `candidateGroups="manager"` | 系统角色候选审批 |
| 部门审批 | `groupType="dept"` | 按部门审批 |
| 岗位审批 | `groupType="deptPosition"` | 按部门岗位审批 |
| 表达式 | `${deptLeader}` | 动态表达式 |
| 上一节点指派 | `isAssignedByPreviousNode` | 由上一审批人选择 |
| 表单字段选人 | `groupType="formData"` | 从表单动态获取 |

**交互流程：**
1. 用户描述流程需求（节点、审批人、条件分支等）
2. AI 解析并构建流程结构
3. 展示流程摘要（节点列表 + 连线与条件），等待确认
4. 生成 BPMN XML → 调用 API 创建流程

## 安装方法

将需要的 Skill 目录复制到 Claude Code 的 skills 目录：

```bash
# macOS / Linux
cp -r jeecg-codegen ~/.claude/skills/

# Windows
xcopy jeecg-codegen %USERPROFILE%\.claude\skills\jeecg-codegen\ /E /I
```

安装后需要根据实际项目修改 Skill 中的路径和数据库连接配置，具体见各 Skill 的 README。

## 适用版本

- **JeecgBoot** 3.x（Spring Boot 3 + Jakarta + MyBatis-Plus）
- **前端** Vue3 + TypeScript + Vite + Ant Design Vue 4
- **Claude Code** 最新版本

## Skills 对比

| Skill | 产出物 | 适用场景 |
|-------|--------|---------|
| jeecg-codegen | Java + Vue3 代码 + SQL | 需要自定义业务逻辑的模块 |
| jeecg-onlform | Online 表单配置（元数据驱动，CRUD） | 数据录入管理表单，无需写代码 |
| jeecg-onlreport | Online 报表配置（SQL 驱动，只读展示） | 数据查询报表、统计分析、数据导出 |
| jeecg-desform | 设计器表单 JSON（可视化拖拽设计） | 数据采集、审批表单、复杂布局表单 |
| jeecg-bpmn | Flowable BPMN 2.0 XML | 审批流程、业务工作流 |

## 规划中的 Skills

欢迎贡献更多 JeecgBoot 生态的 Skills，例如：

- 权限配置助手 — 自然语言描述角色权限需求，自动生成配置
- 数据库迁移助手 — 智能生成 Flyway 迁移脚本
- 接口联调助手 — 根据后端接口自动生成前端调用代码
- 性能诊断助手 — 分析慢查询、优化建议

## 项目结构

```
skills/
├── README.md                    # 本文件
├── jeecg-codegen/               # 代码生成器 Skill
│   ├── SKILL.md                 # Skill 入口（触发规则 + 交互流程）
│   ├── codegen-reference.md     # 完整代码模板骨架
│   ├── CODEGEN-GUIDE.md         # 详细使用指南
│   └── README.md                # Skill 说明
├── jeecg-onlform/               # Online 表单生成器 Skill
│   └── SKILL.md                 # Skill 入口（交互流程 + API 调用）
├── jeecg-onlreport/             # Online 报表生成器 Skill
│   └── SKILL.md                 # Skill 入口（交互流程 + API 调用）
├── jeecg-desform/               # 设计器表单生成器 Skill
│   ├── SKILL.md                 # Skill 入口（交互流程 + API 调用）
│   └── references/              # 参考文档（JSON Schema、控件配置、示例）
└── jeecg-bpmn/                  # BPM 流程生成器 Skill
    ├── SKILL.md                 # Skill 入口（交互流程 + API 调用）
    └── references/              # 参考文档（XML骨架、审批人、网关、会签等）
```

## 贡献

欢迎提交 PR 贡献新的 Skill。每个 Skill 应包含：

1. **SKILL.md** — Skill 入口文件，包含 frontmatter（name + description）和完整的交互流程
2. **README.md** — 安装和配置说明
3. 必要的参考文件（模板、配置等）

## License

MIT
