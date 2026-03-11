# JeecgBoot Skills

JeecgBoot 低代码平台生态的 AI Skills 集合，为 [Claude Code](https://claude.com/claude-code) 提供专业化的开发能力增强。

## 什么是 Skills？

Skills 是 Claude Code 的技能扩展机制，通过结构化的提示词让 AI 获得特定领域的专业能力。安装 Skill 后，Claude Code 可以在对话中自动识别意图并触发对应的专业工作流，无需手动指定。

## 已有 Skills

| Skill | 说明 | 状态 |
|-------|------|------|
| [jeecg-codegen](./jeecg-codegen/) | 代码生成器 — 自然语言描述需求，自动生成 JeecgBoot 全套 CRUD 代码 | ✅ 可用 |

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
└── jeecg-codegen/               # 代码生成器 Skill
    ├── SKILL.md                 # Skill 入口（触发规则 + 交互流程）
    ├── codegen-reference.md     # 完整代码模板骨架
    ├── CODEGEN-GUIDE.md         # 详细使用指南
    └── README.md                # Skill 说明
```

## 贡献

欢迎提交 PR 贡献新的 Skill。每个 Skill 应包含：

1. **SKILL.md** — Skill 入口文件，包含 frontmatter（name + description）和完整的交互流程
2. **README.md** — 安装和配置说明
3. 必要的参考文件（模板、配置等）

## License

MIT
