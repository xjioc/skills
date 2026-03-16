# JeecgBoot AI Skills — Claude Code 技能清单

> JeecgBoot 平台 Claude Code 技能集合，通过自然语言驱动，AI 自动生成代码、表单、流程、报表、图表等，覆盖低代码开发全场景。

---

## 功能清单

| 序号 | 技能名称 | 功能说明 | 触发关键词 | 产出物 |
|------|---------|---------|-----------|--------|
| 1 | **jeecg-codegen** | 代码生成器 — 自然语言描述业务需求，自动生成全套 CRUD 代码 | 代码生成、生成代码、创建模块、新增功能、建表、加字段 | Java + Vue3 + SQL |
| 2 | **jeecg-onlform** | Online 表单生成器 — 自然语言描述表结构，自动创建 Online 表单（CRUD） | 创建Online表单、创建online表、在线表单 | Online 表单配置 |
| 3 | **jeecg-onlreport** | Online 报表生成器 — 自然语言描述报表需求，自动生成 SQL 报表 | 创建报表、生成报表、SQL报表、数据报表 | Online 报表配置 |
| 4 | **jeecg-desform** | 设计器表单生成器 — 自然语言描述表单需求，自动生成表单 JSON 并创建 | AI设计表单、生成表单、创建表单 | 设计器表单 JSON |
| 5 | **jeecg-onlchart** | Online 图表生成器 — 自然语言描述图表需求，自动生成数据可视化图表 | 创建图表、生成图表、柱状图、折线图、饼图、可视化 | Online 图表配置 |
| 6 | **jeecg-bpmn** | BPM 流程生成器 — 自然语言描述审批流程，自动生成 BPMN XML 并部署 | 创建流程、生成流程、审批流程、工作流、BPM | Flowable BPMN 2.0 XML |

---

## 技能详情

### 1. jeecg-codegen — 代码生成器

**一句话**：用自然语言描述业务需求，自动生成 JeecgBoot 全套 CRUD 代码。

**核心能力**：
- 支持单表、树表、一对多（主子表）三种模式
- 智能字段推导：名称→Input、金额→InputNumber、状态→字典下拉、图片→图片上传
- 字典智能匹配：自动读取 sys_dict 表，为字段匹配已有字典编码
- 已有表反向生成：给表名即可，自动查询 DDL 生成代码
- 增量修改：加/删/改字段，精确修改每个相关文件
- 主键策略自适应、Flyway 版本号自动递增

**使用文档**：[CODEGEN-GUIDE.md](jeecg-codegen/CODEGEN-GUIDE.md)

---

### 2. jeecg-onlform — Online 表单生成器

**一句话**：用自然语言描述表结构，自动通过 API 创建 Online 表单（元数据驱动 CRUD）。

**核心能力**：
- 元数据驱动，无需写代码即可生成完整 CRUD 页面
- 单表 / 主子表（一对多/一对一）/ 树表 三种模式
- 智能字段类型推导和控件映射（30+ 控件类型）
- 字典智能匹配（系统字典 / 字典表 / 带条件字典表）
- 增量字段修改（加/删/改字段，无需重新创建）
- 自动同步数据库 + 生成菜单 SQL

---

### 3. jeecg-onlreport — Online 报表生成器

**一句话**：用自然语言描述报表需求，自动生成 SQL 并通过 API 创建 Online 数据报表。

**核心能力**：
- SQL 驱动的数据报表，支持查询、排序、导出
- 智能字段配置：显示/隐藏、查询模式（模糊/精确/范围）、排序、合计
- 字段中文名自动翻译
- 字典和取值表达式支持
- 分组表头、字段跳转等高级功能
- SQL 参数化查询（Velocity 模板语法）

---

### 4. jeecg-desform — 设计器表单生成器

**一句话**：用自然语言描述表单需求，自动生成设计器表单 JSON 并通过 API 创建。

**核心能力**：
- 支持 40+ 控件类型：文本、数字、选择、日期、上传、富文本、人员选择等
- 支持主子表（明细表）设计
- 支持布局控制：一行多字段、分栏布局
- 关联记录 + 他表字段、公式计算
- 支持表单编辑和删除

---

### 5. jeecg-onlchart — Online 图表生成器

**一句话**：用自然语言描述图表需求，自动生成 SQL 并通过 API 创建 Online 数据可视化图表。

**核心能力**：
- 支持柱状图、折线图、饼图、组合图表
- 智能推导 X/Y 轴字段：维度字段→X 轴，度量字段→Y 轴
- 根据数据特征自动推荐图表类型
- 字段中文名翻译、字典自动关联
- 组合图表（折线+柱状同时展示）
- SQL 参数化查询、动态数据源

---

### 6. jeecg-bpmn — BPM 流程生成器

**一句话**：用自然语言描述审批流程，自动生成 Flowable BPMN 2.0 XML 并通过 API 部署。

**核心能力**：
- 支持顺序审批、条件分支（排他网关）、并行审批（并行网关）
- 支持会签（多实例任务）、子流程
- 多种审批人类型：固定人、发起人、部门负责人、角色组、上一节点指派
- 条件表达式自动生成：金额判断、天数判断、状态判断
- 同一会话内可连续修改流程

---

## 使用方式

所有技能都在 Claude Code 对话中通过自然语言触发，无需手动调用。只需描述你的需求，AI 会自动识别并使用对应技能。

### 通用交互流程

```
1. 用自然语言描述需求
2. AI 询问后端地址和 Token（如需调用 API）
3. AI 展示配置摘要，等待确认
4. 确认后自动执行，返回结果
5. 可在同一会话中继续修改
```

### Token 获取方式

1. 打开 JeecgBoot 系统并登录
2. 按 F12 打开浏览器开发者工具
3. 切换到 Network 标签页
4. 点击任意请求，在 Request Headers 中找到 `X-Access-Token`
5. 复制完整的 Token 值

---

## 安装方法

将需要的 Skill 目录复制到 Claude Code 的 skills 目录：

```bash
# macOS / Linux
cp -r jeecg-codegen ~/.claude/skills/

# Windows
xcopy jeecg-codegen %USERPROFILE%\.claude\skills\jeecg-codegen\ /E /I
```

安装后需要根据实际项目修改 Skill 中的路径和数据库连接配置，具体见各 Skill 的 SKILL.md。

## 适用版本

- **JeecgBoot** 3.x（Spring Boot 3 + Jakarta + MyBatis-Plus）
- **前端** Vue3 + TypeScript + Vite + Ant Design Vue 4
- **Claude Code** 最新版本

## License

MIT
