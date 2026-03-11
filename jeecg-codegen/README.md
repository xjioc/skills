# JeecgBoot 代码生成 Skill（Claude Code 专用）

将自然语言需求转换为 JeecgBoot 全套 CRUD 代码（后端 Java + 前端 Vue3 + 菜单权限 SQL）。

## 功能特性

- 单表 / 树表 / 一对多（主子表）三种模式
- 已有表反向生成（自动读取数据库 DDL）
- 新建表智能推导（自然语言 → 字段类型 + 控件）
- 增量字段修改（加字段/删字段/改字段，无需重新生成）
- 字典智能匹配（自动关联系统 `sys_dict` 字典）
- Flyway 版本号自动递增
- 菜单权限 SQL 自动生成（真实时间戳 ID）

## 安装方法

将 `SKILL.md` 和 `codegen-reference.md` 两个文件复制到 Claude Code 的 skills 目录：

```bash
# Windows
mkdir %USERPROFILE%\.claude\skills\jeecg-codegen
copy SKILL.md %USERPROFILE%\.claude\skills\jeecg-codegen\
copy codegen-reference.md %USERPROFILE%\.claude\skills\jeecg-codegen\

# macOS / Linux
mkdir -p ~/.claude/skills/jeecg-codegen
cp SKILL.md ~/.claude/skills/jeecg-codegen/
cp codegen-reference.md ~/.claude/skills/jeecg-codegen/
```

## 使用前配置

安装后需要根据实际项目修改 `SKILL.md` 中的以下配置：

| 配置项 | 位置 | 说明 |
|--------|------|------|
| 后端根路径 | "项目路径"章节 | 改为你的后端项目绝对路径 |
| 前端根路径 | "项目路径"章节 | 改为你的前端项目绝对路径 |
| 数据库连接 | "数据库连接"章节 | 改为你的 MySQL 地址/端口/用户名/密码/数据库名 |
| Flyway SQL 目录 | "Flyway 版本号规则"章节 | 如果目录不同需要调整 |

## 触发方式

在 Claude Code 中直接说以下关键词即可触发：

- `代码生成` / `生成代码` / `创建模块` / `新增功能` / `建表`
- `加字段` / `增加字段` / `新增字段` / `修改字段` / `删除字段`
- `generate code` / `new entity` / `add field`

## 使用示例

```
# 单表
生成一个商品管理模块，字段：商品名、价格、库存、状态、图片、描述

# 一对多
生成一个采购单模块，主表是采购单（单号、供应商、日期、总金额），子表是采购明细（商品名、数量、单价、小计）

# 已有表
给 biz_customer 表生成代码

# 增量修改
给采购单模块加一个"备注"字段
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 入口，定义触发规则、交互流程、字段推导、字典匹配等 |
| `codegen-reference.md` | 完整代码模板骨架，包含 Entity/Controller/Service/Mapper/Vue3 等全部模板 |

## 适用版本

- JeecgBoot 3.x（Spring Boot 3 + Jakarta + MyBatis-Plus）
- Vue3 + TypeScript + Vite + Ant Design Vue 4
