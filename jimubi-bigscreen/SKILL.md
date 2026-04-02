---
name: jimubi-bigscreen
description: Use when user asks to create/design a big screen (大屏), full-screen data visualization, or says "创建大屏", "生成大屏", "新建大屏", "设计大屏", "做一个大屏", "BI大屏", "数据大屏", "可视化大屏", "监控大屏", "create big screen", "design big screen", "BI visualization big screen". Also triggers when user describes big screen requirements like "做一个销售数据大屏" or mentions full-screen display like "展厅展示", "监控室大屏". Make sure to use this skill for big screens (大屏) — NOT dashboards (仪表盘/看板), which use a completely different layout and styling system.
---

# JeecgBoot 大屏 AI 自动生成器

将自然语言的大屏需求转换为 drag page 配置，并通过 API 自动创建。

> **本 skill 专门处理大屏（bigScreen）模式**：全屏展示，绝对定位（像素坐标），深色主题，适用于监控室/展厅/展示墙。
> 仪表盘（看板）请使用 `jimubi-dashboard` skill。

## 按需加载指南

本 skill 采用分层加载：核心规则始终在上下文中，专题文档按需读取。

| 场景 | 读取文件 |
|------|---------|
| 创建/绑定/修改数据集（SQL/API/文件） | `references/dataset-guide.md`（**仅自定义脚本时需要**；使用 `dataset_ops.py` / `comp_ops.py --dataset-name` / `comp_ops.py --create-sql` / `comp_ops.py --sql-params` 预置脚本时**无需读取**，脚本已封装全部逻辑，含 FreeMarker 查询参数支持） |
| SQL 数据集使用存储过程（CALL） | 直接用 `proc_ops.py bindcomp`，**无需读任何文档**（一键完成：pymysql 创建存储过程 + 创建数据集 + 绑定组件；自动从数据源 API 获取数据库连接信息） |
| 从模板复制创建大屏 | 直接用 `template_ops.py copy`，**无需读任何文档** |
| 模板复制遇到问题时 | `references/template-copy-guide.md` |
| 地图组件（JAreaMap 等） | `references/map-guide.md` |
| 签名接口 / 数据源管理 / NoSQL 数据源 | `references/signing-datasource-guide.md`（含 MongoDB/ES/Redis 创建流程、dbUrl 格式、SQL 前缀语法、已知问题） |
| 组件联动 / 钻取 | 直接用 `linkage_ops.py`，**无需读任何文档**（参数说明见下方「快捷操作：linkage_ops.py」章节）。仅遇到复杂问题时读 `references/linkage-drill-guide.md` |
| 组件外部链接跳转 | 直接用 `link_ops.py`，**无需读任何文档** |
| 组件组合（JGroup） | `references/group-guide.md` |
| 修改页面配置（背景/水印/宽高） | `references/page-config-guide.md` |
| 字典翻译（jimu_dict） | `references/dict-guide.md` |
| 组件右键操作（图层排序/复制/删除/锁定） | `references/rightclick-actions-guide.md` |
| 遇到奇怪问题时查阅 | `references/pitfalls.md` |
| 组件样式配置路径 | `references/bi-comp-option-config.md`（**仅当 SKILL.md 中未列出目标组件的配置路径时才读取**；JStatsSummary/JCapsuleChart/JGauge/JProgress/JColorBlock/JScrollBoard 等常用组件的配置路径已内联在 SKILL.md「常用组件配置路径速查」章节，无需读 600 行文档） |
| 完整组件类型清单 | `references/bi-component-types.md` |
| 新增组件默认尺寸/数据/option | `references/core-configs/component-defaults.md`（82+ 组件的 w/h/chartData/option 默认值速查） |
| 组件创建流程（addPageComp） | `references/core-configs/addPageComp-logic.md`（newItem 结构、位置计算、保存逻辑） |
| 组件菜单分类树 | `references/core-configs/menu-hierarchy.md`（完整 menuData 层级 + 统计）。**全组件批量生成时无需读取**，SKILL.md 组件速查表已包含全部 compType→中文名映射，脚本中直接硬编码 categories 列表即可 |

## 大屏特征

- **布局**：绝对定位，坐标和尺寸单位为**像素**（如 x=50, y=280, w=860, h=380）
- **主题**：默认 `dark`，深色背景，亮色/霓虹文字
- **背景图**：默认 `/img/bg/bg4.png`，支持自定义
- **装饰元素**：常用 JDragBorder（边框）、JDragDecoration（装饰条）增强视觉效果
- **典型分辨率**：1920×1080

### 图层背景色规则（强制）

> **严禁将图层背景色设为红色或任何非透明颜色（除非用户明确指定）。** 用户未指定背景色时，`config.background` 和 `config.borderColor` 必须设为 `#FFFFFF00`（透明）。

| 规则 | 说明 |
|------|------|
| **默认值** | `config.background = '#FFFFFF00'`，`config.borderColor = '#FFFFFF00'` |
| **严禁使用 `rgba(0,0,0,0)`** | Ant Design 颜色选择器将其解析为**红色**（色相 0°=红色） |
| **唯一正确的透明写法** | `#FFFFFF00`（带 alpha 通道的十六进制透明白色） |
| **何时设为非透明** | 仅当用户明确指定了具体背景颜色时 |

## 前置条件

用户必须提供 API 地址和 X-Access-Token。

## 执行效率规则（强制）

### 简单操作直接执行，禁止多余探索

**对所有大屏操作（包括创建新大屏、组件增删改查），必须跳过以下步骤直接执行：**
- 禁止触发 brainstorming 流程
- 禁止启动 Explore 子代理去探索源码
- 禁止启动子代理去读 data.ts 默认配置（skill 文档已包含完整信息）
- 禁止启动子代理去分析模板 JSON 结构（template_ops.py 已封装全部逻辑）
- 禁止用 Read 工具读取模板 JSON 文件（92KB+，严重浪费 token）
- 禁止读取 template-copy-guide.md（template_ops.py copy 已实现全部流程）
- 禁止展示设计摘要等待确认（除非用户明确要求确认）
- 禁止使用预置脚本时读取 dataset-guide.md（`dataset_ops.py` / `comp_ops.py --dataset-name` / `comp_ops.py --create-sql` / `comp_ops.py --sql-params` / `proc_ops.py bindcomp` 已封装全部数据集逻辑含存储过程+FreeMarker 参数支持，读 557 行文档浪费 ~5000 token）
- 禁止执行预置脚本前先 `--help` 查看用法（skill 文档已包含完整参数说明）
- 禁止存储过程场景手动写 pymysql 脚本再调 comp_ops.py（`proc_ops.py bindcomp` 一条命令搞定全部流程）

**正确做法：直接使用预置脚本（`template_ops.py`、`comp_ops.py`、`dataset_ops.py`）完成，1-2 轮工具调用。**

### 模板创建快速路径（强制，token 节省 90%+）

**创建整个大屏时，必须走以下快速路径，禁止自定义脚本：**

```
轮次1: cp template_ops.py + bi_utils.py（1 条 Bash 命令）
轮次2: py template_ops.py copy ... --replace '{...}' --board-data '{...}' && echo URL | clip.exe && rm（1 条 Bash 命令）
```

**替换字典构建规则：** 根据用户行业需求，直接构建 `--replace` JSON，无需分析模板内容。各模板中的占位文本是固定的：

**模板1：大数据可视化展示平台（通用/销售/综合类）**

| 占位文本 | 替换为行业术语 |
|---------|--------------|
| 大数据可视化展示平台 | 行业大屏标题 |
| 总金额 | 行业核心指标1名称 |
| 数量 | 行业核心指标2名称 |
| 数量结算率 / 金额结算率 等 | 行业百分比指标 |
| 2017年 / 2018年 | 近两年年份 |
| 结算率 | 行业趋势指标 |
| 年度数据 / 图例数据 | 行业分组标签 |
| 图例1/2/3/4 | 行业分类项 |
| 行1列1~行5列3 | 轮播表业务数据 |

**模板2：北京科技数字化云平台（科技/能源/电力/IoT/设备监控类）**

| 占位文本 | 替换为行业术语 |
|---------|--------------|
| 北京科技数字化云平台 | 行业大屏标题 |
| 网关管理/云组态/设备管理/动态数据/人员管理/监控管理/人员定位/能源管理 | 顶部8个导航菜单项 |
| 功耗总量 | 核心指标标题 |
| 电能耗 / 水能耗 | 双翻牌器标签 |
| 17563 / 11163 | 双翻牌器数值 |
| kw/h | 翻牌器单位 |
| 近七日电能耗 / 近七日水能耗 | 左侧双柱状图标题 |
| 一号~五号机房功率 | 5个仪表盘标题 |
| 设备功率信息 | 中间仪表盘区域标题 |
| 设备列表 / 信息 | 右侧面板标题 |
| 站点号：0001 / 设备状态：正常 / 环境温度：36摄氏度 / 在线设备：20 台 | 右侧4行信息文本 |
| 近七日设备在线数 | 右下折线图标题 |
| 基础折线图 | 折线图标题 |
| 1号~5号机房 / 0374~0378 / 正常 | 滚动表格数据 |
| 功率 / 编号 / 设备名 / 设备状态 | 数据字段名 |

**示例（风力发电行业，使用北京科技数字化云平台模板）：**
```bash
py template_ops.py copy $API_BASE $TOKEN \
  --template "北京科技数字化云平台_1014376428645961728.json" \
  --name "风力发电智慧监控平台" \
  --bg-image "/img/bg/bg4.png" \
  --replace '{"北京科技数字化云平台":"风力发电智慧监控平台","网关管理":"风机管理","云组态":"SCADA系统","设备管理":"机组管理","动态数据":"实时数据","人员管理":"运维管理","监控管理":"故障监控","人员定位":"风场巡检","能源管理":"发电管理","功耗总量":"发电总量","电能耗":"发电量","水能耗":"上网电量","17563":"58260","11163":"42850","kw/h":"万kWh","设备列表":"风机列表","信息":"风场信息","站点号：0001":"风场编号：WF-001","设备状态：正常":"风机状态：正常运行","环境温度：36摄氏度":"平均风速：8.5m/s","在线设备：20 台":"在线风机：126 台","近七日设备在线数":"近七日风机在线数","设备功率信息":"风机功率信息","近七日电能耗":"近七日发电量","近七日水能耗":"近七日弃风量","一号机房功率":"A区风机功率","二号机房功率":"B区风机功率","三号机房功率":"C区风机功率","四号机房功率":"D区风机功率","五号机房功率":"E区风机功率","基础折线图":"风机在线趋势","1号机房":"A区-01号风机","2号机房":"B区-03号风机","3号机房":"C区-07号风机","4号机房":"D区-12号风机","5号机房":"E区-05号风机","0374":"WF-A01","0375":"WF-B03","0376":"WF-C07","0377":"WF-D12","0378":"WF-E05","正常":"运行中","功率":"功率(MW)","编号":"风机编号","设备名":"风机名称","设备状态":"运行状态"}'
```

### 存储过程快速路径（强制，2 轮完成）

**存储过程任务必须走 `proc_ops.py bindcomp`，禁止手动 pymysql + comp_ops.py 分步执行：**

```
轮次1: Read 凭据 + Bash: cp proc_ops.py comp_ops.py bi_utils.py default_configs.json（并行）
轮次2: py proc_ops.py bindcomp ... && rm proc_ops.py comp_ops.py bi_utils.py default_configs.json && echo URL | clip.exe
```

**示例（查询 demo 表）：**
```bash
py proc_ops.py bindcomp "http://192.168.1.66:8080/jeecg-boot" "$TOKEN" \
  --page "PAGE_ID" --comp "JCommonTable" --title "Demo数据表格" \
  --x 50 --y 280 --w 900 --h 450 \
  --proc-name "sp_query_demo" \
  --proc-sql "SELECT id, name, sex, age, birthday, salary_money, email FROM demo ORDER BY create_time DESC" \
  --fields "id:String,name:String,sex:String,age:String,birthday:String,salary_money:String,email:String" \
  --dict "sex=sex"
```

**带参数的存储过程：**
```bash
py proc_ops.py bindcomp ... \
  --proc-name "sp_query_demo_by_sex" \
  --proc-params "IN p_sex varchar(10)" \
  --proc-sql "SELECT id, name, sex, age FROM demo WHERE sex = p_sex ORDER BY create_time DESC" \
  --fields "id:String,name:String,sex:String,age:String"
```

`proc_ops.py bindcomp` 自动完成：从数据源 API 获取 DB 连接信息 → pymysql 创建存储过程 → 验证 CALL → 调用 comp_ops.py 创建数据集+绑定组件。**无需读 dataset-guide.md，无需手写 pymysql 脚本。**

**使用前准备（需额外复制 comp_ops.py + default_configs.json，因为 bindcomp 内部调用 comp_ops.py）：**
```bash
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/proc_ops.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/comp_ops.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/bi_utils.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/default_configs.json" .
# 执行完后清理
rm proc_ops.py comp_ops.py bi_utils.py default_configs.json
```

### 多字段页面配置修改必须合并（强制）

修改 2 个及以上页面属性时，禁止逐个调用 page_ops.py，必须编写合并脚本（1 次 query + 修改所有字段 + 1 次 edit）。详见 `references/page-config-guide.md`。

### 所有大屏操作以耗时最少为第一优先级（强制）

1. 用户说什么就做什么，不反复权衡
2. 优先用预置脚本，能一条命令解决的不写自定义脚本
3. 多个独立操作必须并行执行
4. 复杂组件从 `default_configs.json` 加载配置
5. 最少工具调用轮次（理想 2 轮：准备 + 执行清理）
6. API 凭据已在上下文中时不重复读取

**耗时目标：**

| 操作类型 | 目标耗时 | 做法 |
|---------|---------|------|
| 单组件增/删/改/查 | ≤30s | comp_ops.py 一条命令（cp + 执行 + rm，共 2 轮） |
| 数据集 + 单组件 | ≤45s | comp_ops.py --create-sql 或 dataset_ops.py + comp_ops.py --dataset-name |
| 复合操作（数据集 + 多组件） | ≤60s | 并行 Bash 调用 |
| 模板复制创建大屏 | ≤60s | template_ops.py copy --replace |
| 存储过程 + 单组件 | ≤45s | proc_ops.py bindcomp 一条命令（cp + 执行 + rm，共 2 轮） |
| 页面配置修改（≥2项） | ≤30s | 合并脚本一次完成 |
| 全组件批量生成（95个） | ≤5s | 自定义脚本：1次query + 批量add_component(内存) + 1次save。**严格 2 轮：轮次1 Read凭据 ‖ Bash(cp) ‖ Write(脚本) 并行，轮次2 py+clip+rm 一条命令** |

### 全组件批量生成快速路径（强制）

**用户要求"生成全组件"时，必须走自定义批量脚本，禁止逐个调用 comp_ops.py add（95次API调用 vs 2次）。**

**核心原则：**
1. **必须用 `bi_utils.add_component()`**：它正确处理 config 结构（flat dict → JSON string），自动设置 `size`/`chart`/`turnConfig` 等字段
2. **先 `_page_components[page_id] = []` 清空缓存，再批量 add_component，最后一次 save_page**
3. **config 是 flat dict**（chartData/option/dataType/background 同级），由 add_component 内部 `json.dumps` 为字符串
4. **chartData 必须在传入 add_component 前序列化为 JSON 字符串**
5. **option.title 可能是 str 类型**（部分 default_configs.json 中如此），设置前需检查类型并转为 dict
6. **排除天气预报（JWeatherForecast）、装饰边框（JDragBorder）、装饰条（JDragDecoration）**：这些是纯装饰/特殊组件，不算业务组件
7. **componentName 必须使用中文名称，禁止用 compType（如 JBar）作为图层名**：参照 `menu-hierarchy.md` 中的组件中文名（如 JBar→基础柱形图、JPie→饼图、JStatsSummary_1→统计概览(卡片式)），脚本中需维护 `key→中文名` 映射表
8. **组件必须按网格布局，禁止堆叠，禁止生成分类标题组件**：所有组件扁平排列（flat list），4 列网格（COLS=4，COMP_W=440，MARGIN=20），逐行递增 y 坐标，确保无重叠。**分类（柱形图/饼图/折线图/...）仅用于代码中的注释分组，不要为每个分类生成 JText 标题组件**——分类标题不是业务组件，用户在设计器中会看到多余的文本图层
9. **生成后必须同步修改页面高度（desJson.height）**：95 个组件总高度远超默认 1080px（实际约 7800px+）。**页面宽高存储在 `desJson.height`/`desJson.width` 中，不是 `pageConfig`**。必须在 save_page 后计算组件最大 `y+h`，通过 `_request('GET', '/drag/page/queryById')` 获取完整页面实体，解析 `desJson`（可能为 None/空字符串/JSON字符串），设置 `height = max_bottom + 50`，再 `_request('POST', '/drag/page/edit')` 保存

**脚本模板（2轮完成）：**
```
轮次1: Read 凭据 + Bash: cp bi_utils.py + default_configs.json + Write 脚本
轮次2: py 脚本 && echo URL | clip.exe && rm 清理
```

**关键代码结构：**
```python
import bi_utils, json, urllib.request
bi_utils.API_BASE = API_BASE
bi_utils.TOKEN = TOKEN

defaults = json.load(open('default_configs.json', 'r', encoding='utf-8'))

# 创建页面 + 清空缓存
page_id = bi_utils.create_page('全组件大屏', style='bigScreen', theme='dark',
                                background_image='/img/bg/bg4.png')
bi_utils._page_components[page_id] = []

# 扁平网格布局（4列，无分类标题组件）
COLS, COMP_W, COMP_H, MARGIN = 4, 440, 300, 20
START_Y = 100  # 顶部标题区下方

# all_comps = [(key, compType, name), ...] 扁平列表，分类仅作注释
added = 0
for key, comp_type, name in all_comps:
    if key not in defaults:
        continue
    cfg = json.loads(json.dumps(defaults[key]))  # deep copy
    w, h = min(cfg.pop('w', COMP_W), COMP_W), min(cfg.pop('h', COMP_H), COMP_H)
    cfg.setdefault('background', '#FFFFFF00')
    cfg.setdefault('borderColor', '#FFFFFF00')
    if 'chartData' in cfg and not isinstance(cfg['chartData'], str):
        cfg['chartData'] = json.dumps(cfg['chartData'], ensure_ascii=False)
    opt = cfg.get('option', {})
    if isinstance(opt, str):
        try: opt = json.loads(opt); cfg['option'] = opt
        except: opt = {}; cfg['option'] = opt
    opt_title = opt.get('title')
    if isinstance(opt_title, str):
        opt['title'] = {'text': name, 'show': True}
    elif isinstance(opt_title, dict):
        opt_title['text'] = name
    col, row = added % COLS, added // COLS
    x = MARGIN + col * (COMP_W + MARGIN)
    y = START_Y + row * (COMP_H + MARGIN)
    bi_utils.add_component(page_id, comp_type, name, x, y, w, h, cfg)
    added += 1

bi_utils.save_page(page_id)  # 一次保存

# ⚠️ 同步修改页面高度（desJson.height，不是 pageConfig）
total_height = current_y + 50
raw = bi_utils._request('GET', '/drag/page/queryById', params={'id': page_id})
p = raw['result']
des = json.loads(p['desJson']) if p.get('desJson') and isinstance(p['desJson'], str) else (p.get('desJson') if isinstance(p.get('desJson'), dict) else {})
des['height'] = total_height
des.setdefault('width', 1920)
p['desJson'] = json.dumps(des, ensure_ascii=False)
bi_utils._request('POST', '/drag/page/edit', data=p)
```

**⚠️ 严禁在批量场景下自行构造 comp dict 并 insert 到 template**（config 必须是 JSON 字符串且包含 size/chart/turnConfig 等必要字段，手动构造容易漏字段导致"暂无数据"）

**反模式检查清单（出现任何一条就说明在浪费时间）：**
- **⚠️ 直接调用 bi_utils.add_xxx() + save_page() 添加组件**（会覆盖已有组件！必须用 comp_ops.py add）
- **⚠️ 在源码中搜索组件默认配置**（comp_ops.py add 已自动处理，Grep/Read config.ts 浪费大量 token）
- 内心在纠结"这个数据适不适合这种图表"
- 在犹豫用 comp_ops.py 还是自定义脚本（默认用预置脚本）
- 在手写超过 30 行的 config JSON（应从 default_configs.json 加载）
- 两个独立操作串行执行而非并行
- 同一会话中重复读取 API 凭据文件
- 在执行前展开长篇分析或设计讨论
- 启动子代理去探索源码或读取配置文件
- **用 Read 工具读取模板 JSON 文件**（template_ops.py 已封装，无需看原文）
- **启动子代理分析模板中有哪些组件**（占位文本是固定的，见上方表格）
- **template_ops.py copy 能完成时却手写 Python 脚本**（多写 100+ 行 = 浪费 4k+ token）
- **⚠️ 绑定已有数据集前单独调 dataset_ops.py 查询**（comp_ops.py add --dataset-name 已内置自动查询，直接用即可）
- **dataset_ops.py list --search**（不存在的参数，会报错浪费轮次）
- **读凭据和复制脚本串行执行**（应并行：Read 凭据 + Bash cp 同一轮）
- **⚠️ 使用预置脚本时读取 dataset-guide.md**（`dataset_ops.py` / `comp_ops.py --dataset-name` / `comp_ops.py --create-sql` / `comp_ops.py --sql-params` 已封装全部数据集逻辑含 FreeMarker 参数，无需读 557 行指南文档，浪费 ~5000 token）
- **执行预置脚本前先 `--help` 查看用法**（skill 文档已包含完整参数说明，额外一轮 --help 调用纯属浪费）
- **⚠️ Bash 中用 shell 变量传递 API_BASE/TOKEN 给 py 脚本**（Git Bash 下 `VAR=xxx && py script "$VAR"` 变量可能为空，必须直接内联字面值作为参数）
- **⚠️ 存储过程场景手动 pymysql + comp_ops.py 分步执行**（`proc_ops.py bindcomp` 一条命令完成全流程：获取DB连接→创建SP→创建数据集→绑定组件，分步执行浪费 4+ 轮）
- **⚠️ 存储过程场景读取 dataset-guide.md**（`proc_ops.py` 已封装全部逻辑，无需读 557 行文档）
- **⚠️ FreeMarker 动态SQL通过 bash `--create-sql` 直接传递**（`${age}` 被 shell 解释为空变量，`<#if>` 的 `>` 被解释为重定向，SQL 会被截断。必须用 `--sql-file` 写入文件）
- **⚠️ FreeMarker 判空用 `age??` 或 `age?length`**（JimuReport 只支持内置 `isNotEmpty()` 函数，标准 FreeMarker 判空语法不生效）
- **⚠️ 修改组件配置时读取 `bi-comp-option-config.md`（600行）**（SKILL.md「常用组件配置路径速查」已内联 JStatsSummary/JCapsuleChart/JGauge/JProgress/JColorBlock/JScrollBoard 的完整配置路径表，只有这些组件之外的冷门组件才需读取该文件，浪费 ~6000 token）
- **⚠️ `comp_ops.py edit` 多属性写成位置参数**（多属性必须每个一个 `--set`：`--set "k1=v1" --set "k2=v2"`，不是 `--set "k1=v1" "k2=v2"`）
- **⚠️ 用户明确指定组件名/类型时仍先 `comp_ops.py list`**（用户说"统计概览"/"胶囊图"/"柱状图"等明确组件名时，直接 `comp_ops.py edit --name "xxx"` 或 `--type "JXxx"`，跳过 list，省一轮调用。仅当用户描述模糊如"那个图表"时才需 list 确认）
- **⚠️ 批量添加组件时手动构造 comp dict 而非用 bi_utils.add_component()**（手动构造的 config 缺少 size/chart/turnConfig 等必要字段，且 config 必须是 JSON 字符串不是 dict，导致全部"暂无数据"。必须用 `bi_utils.add_component()` 处理结构转换）
- **⚠️ 批量添加 95 个组件却逐个调 comp_ops.py add**（每次调用 = 1次query + 1次save = 2次API请求，95个组件 = 190次请求。正确做法：自定义脚本 1次query + 内存批量add + 1次save = 2次请求，0.6s完成）
- **⚠️ 批量生成时用 compType 作为图层名**（如 componentName='JBar'，用户在设计器看不懂。必须用 `menu-hierarchy.md` 中的中文名：JBar→基础柱形图、JPie→饼图、JStatsSummary_1→统计概览(卡片式) 等，脚本中维护 key→中文名映射表）
- **⚠️ 全组件生成时为每个分类生成 JText 标题组件**（分类如"柱形图"、"饼状图"等仅用于代码注释分组，不应渲染为 JText 组件。用户在设计器中会看到 20 个多余的文本图层，且占用额外高度。组件应扁平排列，分类仅作注释）
- **⚠️ 全组件生成时包含装饰边框/装饰条/天气预报**（JDragBorder 13种 + JDragDecoration 12种 = 25个纯装饰组件，JWeatherForecast 需特殊API，都不是业务数据组件，应排除）
- **⚠️ 全组件批量生成时读取 menu-hierarchy.md**（SKILL.md 组件速查表已包含全部 compType→中文名映射，脚本中直接硬编码 categories 列表即可，读 253 行文档浪费 ~2500 token + 1 轮调用）
- **⚠️ 全组件批量生成超过 2 轮工具调用**（必须严格 2 轮：轮次1 = Read凭据 ‖ Bash(cp bi_utils.py + default_configs.json) ‖ Write(脚本) 三者并行；轮次2 = `py 脚本 && echo URL | clip.exe && rm 清理` 一条命令。cp 和 Write 串行、执行和清理分开都是浪费）
- **⚠️ 任何场景下 cp 依赖文件和 Write 脚本串行执行**（cp 和 Write 是独立操作，必须在同一轮并行发出，串行多花 1 轮）

## 交互流程

### Step 0: 解析用户需求

| 信息 | 默认值 |
|------|--------|
| 页面名称 | 用户指定 |
| 主题 | dark |
| 背景图 | `/img/bg/bg4.png` |
| 组件列表 | 从描述中解析 |

### Step 0.5: 模板匹配（优先使用模板布局）

**生成整个大屏时，必须先匹配模板，复用已有布局。**

**模板目录**：`references/templates/bigScreen/`（10 个经典大屏模板 JSON）

**模板名→文件名索引（直接使用，禁止 Glob 搜索）：**

| 模板名称 | 文件名 |
|---------|--------|
| 乡村振兴普惠金融服务平台 | `乡村振兴普惠金融服务平台_1024608431274250240.json` |
| 北京市污水排放总量 | `北京市污水排放总量_1022392593179791360.json` |
| 北京科技数字化云平台 | `北京科技数字化云平台_1014376428645961728.json` |
| 医院实时数据监控 | `医院实时数据监控_1011800681234354176.json` |
| 旅游数据分析中心大屏 | `旅游数据分析中心大屏_1016994272231608320.json` |
| 杭州房地产市场宏观监控 | `杭州房地产市场宏观监控_1024545852833189888.json` |
| 警务监控系统 | `警务监控系统_1024545264544305152.json` |
| 车辆分布图 | `车辆分布图_1017325669831987200.json` |
| 集团综合数据大屏 | `集团综合数据大屏_1151069555267260416.json` |
| 香山公园客流大数据 | `香山公园客流大数据_1027085484978388992.json` |

| 用户需求关键词 | 推荐模板 |
|---------------|---------|
| 销售/订单/交易/通用/综合/驾驶舱 | 集团综合数据大屏 |
| 医院/医疗/医药/机构/校园/人员管理 | 医院实时数据监控 |
| 监控/安防/警务 | 警务监控系统 |
| 旅游/公园/客流 | 旅游数据分析中心大屏、香山公园客流大数据 |
| 房地产/城市/环境 | 杭州房地产市场宏观监控、北京市污水排放总量 |
| 科技/数字化/IoT/能源/电力/风电/光伏 | 北京科技数字化云平台 |
| 金融/银行/乡村 | 乡村振兴普惠金融服务平台 |
| 车辆/交通/地图 | 车辆分布图 |

**模板选择优先级（强制，按顺序匹配）：**

1. **精确匹配** → 从上方关键词表找到直接对应的模板，使用「模板复制方式」创建大屏，保留布局和装饰，仅替换业务数据和标题文字
2. **备选三模板** → 没有精确匹配时，从以下三个模板中选最合适的：
   - `北京科技数字化云平台`（科技/工业/设备/IoT/能源类）
   - `北京市污水排放总量`（环境/城市/数据监测类）
   - `医院实时数据监控`（机构/人员/综合管理类）
3. **兜底模板** → 以上都不合适时，才选择 `集团综合数据大屏`

模板复制的详细流程（ID 映射、JTabToggle/JGroup 引用更新、边界检查等）见 `references/template-copy-guide.md`。

> **重要**：只有在用户明确要求"不使用模板"或"从零创建"时，才跳过模板匹配，直接使用 bi_utils 默认组件函数逐个添加。

### Step 1: 识别组件并选择类型

**完整组件名称→类型速查（按分类）：**

> 用户说组件名时直接查此表获取 compType，**禁止 Grep 搜索源码**。

**柱形图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 基础柱形图 | `JBar` | `comp_ops.py add --comp JBar` |
| 堆叠柱形图 | `JStackBar` | `comp_ops.py add --comp JStackBar` |
| 动态柱形图 | `JDynamicBar` | `comp_ops.py add --comp JDynamicBar` |
| 胶囊图 | `JCapsuleChart` | `comp_ops.py add --comp JCapsuleChart` |
| 基础条形图 | `JHorizontalBar` | `comp_ops.py add --comp JHorizontalBar` |
| 背景柱形图 | `JBackgroundBar` | `comp_ops.py add --comp JBackgroundBar` |
| 对比柱形图 | `JMultipleBar` | `comp_ops.py add --comp JMultipleBar` |
| 正负条形图 | `JNegativeBar` | `comp_ops.py add --comp JNegativeBar` |
| 百分比条形图 | `JPercentBar` | `comp_ops.py add --comp JPercentBar` |
| 折柱图 | `JMixLineBar` | `comp_ops.py add --comp JMixLineBar` |

**饼状图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 饼图 | `JPie` | `comp_ops.py add --comp JPie` |
| 南丁格尔玫瑰图 | `JRose` | `comp_ops.py add --comp JRose` |
| 旋转饼图 | `JRotatePie` | `comp_ops.py add --comp JRotatePie` |

**折线图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 基础折线图 | `JLine` | `comp_ops.py add --comp JLine` |
| 平滑曲线图 | `JSmoothLine` | `comp_ops.py add --comp JSmoothLine` |
| 阶梯折线图 | `JStepLine` | `comp_ops.py add --comp JStepLine` |
| 面积图 | `JArea` | `comp_ops.py add --comp JArea` |
| 对比折线图 | `JMultipleLine` | `comp_ops.py add --comp JMultipleLine` |
| 双轴图 | `DoubleLineBar` | `comp_ops.py add --comp DoubleLineBar` |

**进度图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 基础进度图 | `JCustomProgress` | `comp_ops.py add --comp JCustomProgress` |
| 进度图 | `JProgress` | `comp_ops.py add --comp JProgress` |
| 列表进度图 | `JListProgress` | `comp_ops.py add --comp JListProgress` |
| 圆形进度图 | `JRoundProgress` | `comp_ops.py add --comp JRoundProgress` |
| 水波图 | `JLiquid` | `comp_ops.py add --comp JLiquid` |

**象形图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 象形柱图 | `JPictorialBar` | `comp_ops.py add --comp JPictorialBar` |
| 象形图 | `JPictorial` | `comp_ops.py add --comp JPictorial` |
| 男女占比 | `JGender` | `comp_ops.py add --comp JGender` |

**仪表盘类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 基础仪表盘 | `JGauge` | `comp_ops.py add --comp JGauge` |
| 多色仪表盘 | `JColorGauge` | `comp_ops.py add --comp JColorGauge` |
| 渐变仪表盘 | `JAntvGauge` | `comp_ops.py add --comp JAntvGauge` |
| 半圆仪表盘 | `JSemiGauge` | `comp_ops.py add --comp JSemiGauge` |

**散点图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 普通散点图 | `JScatter` | `comp_ops.py add --comp JScatter` |
| 象限图 | `JQuadrant` | `comp_ops.py add --comp JQuadrant` |
| 气泡图 | `JBubble` | `comp_ops.py add --comp JBubble` |

**漏斗图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 普通漏斗图 | `JFunnel` | `comp_ops.py add --comp JFunnel` |
| 金字塔漏斗图 | `JPyramidFunnel` | `comp_ops.py add --comp JPyramidFunnel` |
| 3D金字塔 | `JPyramid3D` | `comp_ops.py add --comp JPyramid3D` |

**雷达图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 普通雷达图 | `JRadar` | `comp_ops.py add --comp JRadar` |
| 圆形雷达图 | `JCircleRadar` | `comp_ops.py add --comp JCircleRadar` |

**环形图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 饼状环形图 | `JRing` | `comp_ops.py add --comp JRing` |
| 多色环形图 | `JBreakRing` | `comp_ops.py add --comp JBreakRing` |
| 基础环形图 | `JRingProgress` | `comp_ops.py add --comp JRingProgress` |
| 动态环形图 | `JActiveRing` | `comp_ops.py add --comp JActiveRing` |
| 玉珏图 | `JRadialBar` | `comp_ops.py add --comp JRadialBar` |

**矩形图/3D图表：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 矩形图 | `JRectangle` | `comp_ops.py add --comp JRectangle` |
| 3D柱形图 | `JBar3d` | `comp_ops.py add --comp JBar3d` |
| 3D分组柱形图 | `JBarGroup3d` | `comp_ops.py add --comp JBarGroup3d` |

**表格/列表类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 轮播表 | `JScrollBoard` | `comp_ops.py add --comp JScrollBoard` |
| 表格 | `JScrollTable` | `comp_ops.py add --comp JScrollTable` |
| 发展历程 | `JDevHistory` | `comp_ops.py add --comp JDevHistory` |
| 数据表格 | `JCommonTable` | `comp_ops.py add --comp JCommonTable` |
| 数据列表 | `JList` | `comp_ops.py add --comp JList` |
| 排行榜 | `JScrollRankingBoard` | `comp_ops.py add --comp JScrollRankingBoard` |
| 个性排名 | `JFlashList` | `comp_ops.py add --comp JFlashList` |
| 气泡排名 | `JBubbleRank` | `comp_ops.py add --comp JBubbleRank` |
| 滚动列表 | `JScrollList` | `comp_ops.py add --comp JScrollList` |

**统计/轮播类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 日历 | `JPermanentCalendar` | `comp_ops.py add --comp JPermanentCalendar` |
| 卡片滚动 | `JCardScroll` | `comp_ops.py add --comp JCardScroll` |
| 卡片轮播 | `JCardCarousel` | `comp_ops.py add --comp JCardCarousel` |
| 统计概览(卡片) | `JStatsSummary` | `comp_ops.py add --comp JStatsSummary_1` |
| 统计概览(背景) | `JStatsSummary` | `comp_ops.py add --comp JStatsSummary_2` |
| 统计概览(高亮) | `JStatsSummary` | `comp_ops.py add --comp JStatsSummary_3` |

**装饰类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 边框1~13 | `JDragBorder` | `comp_ops.py add --comp JDragBorder` |
| 装饰1~12 | `JDragDecoration` | `comp_ops.py add --comp JDragDecoration` |
| 图片 | `JImg` | `comp_ops.py add --comp JImg` |
| 轮播图 | `JCarousel` | `comp_ops.py add --comp JCarousel` |
| 图标 | `JCustomIcon` | `comp_ops.py add --comp JCustomIcon` |

**文字类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 文本 | `JText` | `comp_ops.py add --comp JText` |
| 翻牌器 | `JCountTo` | `comp_ops.py add --comp JCountTo` |
| 颜色块 | `JColorBlock` | `comp_ops.py add --comp JColorBlock` |
| 当前时间 | `JCurrentTime` | `comp_ops.py add --comp JCurrentTime` |
| 数值 | `JNumber` | `comp_ops.py add --comp JNumber` |
| 轨道环形文字 | `JOrbitRing` | `comp_ops.py add --comp JOrbitRing` |

**字符云类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 字符云 | `JWordCloud` | `comp_ops.py add --comp JWordCloud` |
| 图层字符云 | `JImgWordCloud` | `comp_ops.py add --comp JImgWordCloud` |
| 闪动字符云 | `JFlashCloud` | `comp_ops.py add --comp JFlashCloud` |

**地图类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 散点地图 | `JBubbleMap` | `comp_ops.py add --comp JBubbleMap` |
| 飞线地图 | `JFlyLineMap` | `comp_ops.py add --comp JFlyLineMap` |
| 柱形地图 | `JBarMap` | `comp_ops.py add --comp JBarMap` |
| 时间轴飞线地图 | `JTotalFlyLineMap` | `comp_ops.py add --comp JTotalFlyLineMap` |
| 柱形排名地图 | `JTotalBarMap` | `comp_ops.py add --comp JTotalBarMap` |
| 热力地图 | `JHeatMap` | `comp_ops.py add --comp JHeatMap` |
| 区域地图 | `JAreaMap` | `comp_ops.py add --comp JAreaMap`（读 `references/map-guide.md`） |
| 高德地图 | `JGaoDeMap` | `comp_ops.py add --comp JGaoDeMap` |

**视频类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 播放器 | `JVideoPlay` | `comp_ops.py add --comp JVideoPlay` |
| RTMP播放器 | `JVideoJs` | `comp_ops.py add --comp JVideoJs` |

**其他类：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 选项卡 | `JSelectRadio` | `comp_ops.py add --comp JSelectRadio` |
| 导航切换 | `JTabToggle` | `comp_ops.py add --comp JTabToggle` |
| 表单 | `JForm` | `comp_ops.py add --comp JForm` |
| Iframe | `JIframe` | `comp_ops.py add --comp JIframe` |
| 按钮 | `JRadioButton` | `comp_ops.py add --comp JRadioButton` |
| 富文本 | `JDragEditor` | `comp_ops.py add --comp JDragEditor` |
| 通用组件 | `JCommon` | `comp_ops.py add --comp JCommon` |
| 自定义组件 | `JCustomEchart` | `comp_ops.py add --comp JCustomEchart` |
| 统计进度图 | `JTotalProgress` | `comp_ops.py add --comp JTotalProgress` |
| 透视表 | `JPivotTable` | `comp_ops.py add --comp JPivotTable` |
| 排行榜(自定义) | `JRankingList` | `comp_ops.py add --comp JRankingList` |

**天气预报（特殊，不支持 comp_ops.py）：**

| 组件名称 | compType | 添加方式 |
|---------|----------|---------|
| 天气预报(滚动版) | `JWeatherForecast` | 自定义脚本（template=11） |
| 天气预报(横线版) | `JWeatherForecast` | 自定义脚本（template=34） |
| 天气预报(带背景) | `JWeatherForecast` | 自定义脚本（template=21） |
| 天气预报(好123版) | `JWeatherForecast` | 自定义脚本（template=12） |
| 天气预报(温度计版) | `JWeatherForecast` | 自定义脚本（template=27） |
| 天气预报(列表文字版) | `JWeatherForecast` | 自定义脚本（template=94） |

### JWeatherForecast 天气预报组件（特殊组件，需自定义脚本）

> **comp_ops.py 不支持 JWeatherForecast**，必须用自定义脚本直接操作 template 数组添加。
> **dataType 必须为 1**（自动获取天气数据），不是 0。chartData 为 `"[]"`。

| 版本 | template 值 | 默认尺寸 (w×h) | fontColor | bgColor |
|------|------------|----------------|-----------|---------|
| 滚动版 | 11 | 311×47 | #fff | #ffffff00 |
| 横线版 | 34 | 300×30 | #fff | #ffffff00 |
| 带背景 | 21 | 415×131 | #000 | #ffffff00 |
| 好123版 | 12 | 318×61 | #fff | #ffffff00 |
| 温度计版 | 27 | 400×266 | #fff | #ffffff |
| 列表文字版 | 94 | 257×47 | #fff | #ffffff00 |

**添加模板（直接复制修改 template 和坐标即可）：**
```python
import sys, json
sys.path.insert(0, '.')
import bi_utils
bi_utils.API_BASE = API_BASE
bi_utils.TOKEN = TOKEN

page = bi_utils.query_page(PAGE_ID)
tmpl = page.get('template', [])

comp = {
    "i": bi_utils._gen_uuid(),
    "component": "JWeatherForecast",
    "componentName": "天气预报-滚动版",
    "x": 50, "y": 280, "w": 311, "h": 47,
    "dataType": 1,
    "chartData": "[]",
    "config": {
        "background": "#FFFFFF00",
        "borderColor": "#FFFFFF00",
        "card": {"title": ""},
        "option": {
            "city": "",
            "template": 11,  # 改这个值切换版本
            "num": 2,
            "fontSize": 16,
            "fontColor": "#fff",
            "bgColor": "#ffffff00",
            "url": ""
        }
    },
    "dataMapping": {}
}

tmpl.insert(0, comp)
bi_utils._page_components[PAGE_ID] = tmpl
bi_utils.save_page(PAGE_ID)
```

### Step 2: 展示设计摘要并确认

**可跳过确认直接执行的情况：**
- 用户说「直接生成」「不用确认」
- 模板名称与需求精确匹配
- 同一会话中已确认过类似方案

### 快捷操作：comp_ops.py（增删改查）

> **⚠️ 添加/编辑/删除组件必须使用 comp_ops.py，严禁直接调用 bi_utils.add_xxx() + save_page()。**
> 原因：bi_utils.add_component() 内部将 `_page_components[page_id]` 初始化为空列表，save_page 时会用空列表覆盖页面已有的全部组件，造成不可恢复的数据丢失。comp_ops.py 会先加载已有模板再操作，安全无损。

**使用前准备（comp_ops.py add 专用，需额外复制 default_configs.json）：**
```bash
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/comp_ops.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/bi_utils.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/default_configs.json" .
# 执行完后清理
rm comp_ops.py bi_utils.py default_configs.json
```

**核心命令：**
```bash
# 查看组件
py comp_ops.py list $API_BASE $TOKEN $PAGE_ID

# 删除组件
py comp_ops.py delete $API_BASE $TOKEN $PAGE_ID --name "组件名"

# 编辑组件属性（单属性）
py comp_ops.py edit $API_BASE $TOKEN $PAGE_ID --name "组件名" --set "option.title.text=新标题"

# 编辑组件属性（多属性：每个属性一个 --set）
py comp_ops.py edit $API_BASE $TOKEN $PAGE_ID --name "胶囊图" --set "option.showValue=true" --set "option.unit=333"

# 添加组件（静态数据）
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID --comp "JBar" --title "柱形图" --x 50 --y 500 --w 450 --h 300

# 一键：创建SQL数据集 + 字典翻译 + 添加图表
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID --comp "JPie" --title "男女比例" --x 735 --y 365 --w 450 --h 350 --create-sql "SELECT sex as name, COUNT(*) AS value FROM demo WHERE sex IS NOT NULL GROUP BY sex" --ds-name "男女比例统计" --fields "name:String,value:String" --dict "name=sex"

# 移动/缩放组件
py comp_ops.py move $API_BASE $TOKEN $PAGE_ID --name "组件名" --x 100 --y 200
```

**四种数据模式：**

| 模式 | 参数 | 说明 |
|------|------|------|
| 静态数据（默认） | 无额外参数 | 从 `default_configs.json` 加载默认配置 |
| 绑定已有数据集 | `--dataset-name "名称"` | 内置自动查询数据集、设 dataType=2，**无需单独调 dataset_ops.py 查询** |
| 一键创建SQL+绑定 | `--create-sql "SQL"` | 创建数据集+绑定+字典，支持 `--dict`、`--fields` |
| 带查询参数的SQL | `--create-sql` + `--sql-params` | `comp_ops.py add --sql-file sql.txt --sql-params "age:年龄::"` 或自定义 Python 脚本 |

**⚠️ 带 FreeMarker 动态参数的 SQL 必须用 `--sql-file`，禁止通过 bash 命令行传递。** 原因：`${age}` 会被 shell 解释为变量（值为空），`<#if>` 中的 `>` 会被解释为重定向，导致 SQL 被截断或参数丢失。

**动态SQL查询参数完整示例（强制规范）：**

```bash
# Step 1: 将含 FreeMarker 语法的 SQL 写入文件
cat > sql.txt << 'SQLEOF'
SELECT sex as name, COUNT(*) AS value FROM demo WHERE sex IS NOT NULL
<#if isNotEmpty(age)>
  AND age = '${age}'
</#if>
GROUP BY sex
SQLEOF

# Step 2: 用 --sql-file + --sql-params 创建
py comp_ops.py add $API_BASE $TOKEN $PAGE_ID \
  --comp "JPie" --title "男女比例" --x 735 --y 365 --w 450 --h 350 \
  --sql-file sql.txt --ds-name "男女比例统计" \
  --fields "name:String,value:String" --dict "name=sex" \
  --sql-params "age:年龄::"

# Step 3: 清理
rm sql.txt
```

**FreeMarker 动态条件语法规则（强制）：**

| 规则 | 正确写法 | 错误写法 |
|------|---------|---------|
| 参数判空 | `<#if isNotEmpty(age)>` | ~~`<#if age?? && age?length gt 0>`~~ |
| 参数占位 | `'${age}'` | ~~`#{age}`~~（`#{}` 是系统变量专用） |
| 条件结束 | `</#if>` | - |
| 系统变量 | `#{sys_user_code}` | ~~`${sys_user_code}`~~（`${}` 和 `#{}` 不可混用） |

**`--sql-params` 格式**：`paramName:paramTxt:defaultValue:dictCode`（后三项可省略，多个逗号分隔）

| 示例 | 说明 |
|------|------|
| `"age:年龄::"` | 年龄参数，无默认值，无字典 |
| `"sex:性别:1:sex"` | 性别参数，默认值 1，字典编码 sex |
| `"age:年龄::,sex:性别:1:sex"` | 多参数逗号分隔 |

**SQL 含 `!=` 等特殊字符时**：同样禁止通过 bash 传递，必须用 `--sql-file` 或写 Python 脚本在内部定义 SQL。

**自定义脚本添加图表的强制规则：**
1. **图表 config 必须从 `default_configs.json` 深拷贝**：`json.loads(json.dumps(defaults['JPie']))`，再覆盖动态数据字段。禁止手写 option/series 配置
2. **字典翻译用 jimu_dict**：`/jmreport/dict/*` API，不是 `/sys/dict/*`（系统字典需签名且表不同）
3. **dictOptions 从 `getAllChartData` 获取**：创建数据集后调 `getAllChartData`，将返回的 `dictOptions` 写入组件 config，禁止手动构建
4. **datasetItemList 中绑定 dictCode**：如 `{'fieldName': 'name', ..., 'dictCode': 'sex'}` 实现字段级字典翻译

### 全部预置脚本一览

| 脚本 | 功能 | 常用命令 |
|------|------|---------|
| `comp_ops.py` | 组件增删改查 | `list`, `delete`, `edit`, `add`, `move` |
| `page_ops.py` | 页面配置 | `info`, `set-bg`, `set-bgimg`, `set-theme`, `watermark`, `rename` |
| `dataset_ops.py` | 数据集管理 | `list`, `create-sql`, `create-api`, `edit`, `test`, `delete`, `bind` |
| `template_ops.py` | 模板操作 | `list`, `preview`, `search`, `copy` |
| `linkage_ops.py` | 联动/钻取 | `show`, `add-linkage`, `remove-linkage`, `add-drill` |
| `link_ops.py` | 外部链接跳转 | `show`, `set`, `remove` |
| `map_ops.py` | 地图数据 | `list`, `check`, `upload`, `add-map` |
| `style_ops.py` | 批量样式 | `show-colors`, `set-title-color`, `set-palette`, `batch-edit` |
| `backup_ops.py` | 备份恢复 | `export`, `import`, `clone`, `diff` |
| `datasource_ops.py` | 数据源管理（JDBC + NoSQL） | `list`, `detail`, `create`, `test`。**create 参数：** `--db`（非 --db-name）、`--user`（非 --username）；**test 不支持 --name**，只能用 `--id` 或直接传连接参数。**支持 NoSQL：** `--db-type mongodb/redis/es`，自动生成 `host:port/db` 格式的 dbUrl（不带协议前缀），dbDriver 自动置空。**NoSQL 数据集 SQL 语法：** MongoDB 表名加 `mongo.` 前缀（`select * from mongo.表名`），ES 加 `es.` 前缀 |
| `group_ops.py` | 组合管理 | `list`, `create`, `ungroup` |
| `dict_ops.py` | 字典管理 | `list`, `create`, `items`, `bind` |
| `proc_ops.py` | 存储过程管理 | `create`, `list`, `drop`, `bindcomp`（一键：创建存储过程+数据集+组件）。**前置条件：`py -m pip install pymysql`**，通过 pymysql 直连数据库执行 DDL |

**通用使用流程：**
```bash
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/脚本名.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/bi_utils.py" .
# 执行命令...
rm 脚本名.py bi_utils.py
```

### Step 3: 调用 API 创建大屏

**执行步骤（最少 2 轮工具调用）：**

**方式一：template_ops.py copy（模板场景，最优）：**
```
轮次1: cp template_ops.py + bi_utils.py
轮次2: 执行 copy --replace && echo URL | clip.exe && rm
```

**方式二：自定义脚本（复杂逻辑）：**
```

---

## 备选方式：从模板复制创建大屏

> **注意：模板复制方式仅作为备选。** 模板 JSON 中的 config 结构复杂且样式耦合严重，批量文本替换容易破坏配置完整性，生成效果往往不理想。仅在需要精确还原某个已有模板的视觉布局时才考虑使用。

### 模板目录

`references/templates/bigScreen/` 下有 40 个大屏模板 JSON 可供选择。

### 模板复制完整流程

```python
import sys, json
sys.path.insert(0, r'E:\workspace-cc-jeecg\jeecg-boot-framework-2026')
from bi_utils import *
import bi_utils

init_api('http://api3.boot.jeecg.com', 'your-token')

# 1. 读取模板 JSON
tpl_path = r'C:/Users/zhang/.claude/skills/jimubi-bigscreen/references/templates/bigScreen/集团综合数据大屏_1151069555267260416.json'
with open(tpl_path, 'r', encoding='utf-8') as f:
    tpl_data = json.load(f)
template_components = tpl_data.get('template', [])

# 2. 建立旧 ID → 新 ID 映射（关键！）
id_mapping = {}
for comp in template_components:
    old_i = comp['i']
    id_mapping[old_i] = bi_utils._gen_uuid()

# 3. 更新组件 ID 和清理
for comp in template_components:
    comp['i'] = id_mapping[comp['i']]
    comp.pop('pageCompId', None)
    # config 字符串转 dict
    config = comp.get('config', {})
    if isinstance(config, str):
        try: config = json.loads(config)
        except: config = {}
    comp['config'] = config

# 4. 更新 JTabToggle 的 compVals 引用（否则页签切换不工作）
for comp in template_components:
    if comp['component'] == 'JTabToggle':
        for item in comp['config'].get('option', {}).get('items', []):
            item['compVals'] = [id_mapping.get(v, v) for v in item.get('compVals', [])]

# 5. 更新 JGroup 内部 props.elements 中的 ID 引用
for comp in template_components:
    if comp['component'] == 'JGroup':
        props = comp.get('props', {})
        elements = props.get('elements', [])
        if elements:
            el_str = json.dumps(elements, ensure_ascii=False)
            for old_id, new_id in id_mapping.items():
                el_str = el_str.replace(old_id, new_id)
            props['elements'] = json.loads(el_str)

# 6. 创建页面并保存
page_id = create_page('我的大屏', style='bigScreen', theme='dark',
                       background_image='/img/bg/bg4.png')
bi_utils._page_components[page_id] = template_components
save_page(page_id)
```

**默认配置与数据加载规则：**

| 数据场景 | 是否读 data.ts |
|---------|---------------|
| 动态数据（SQL/API, dataType=2） | 不需要，chartData='[]'，option 在脚本中构建 |
| 静态数据 + 用户未指定数据 | 需要，从 data.ts 读取 compConfig |
| 静态数据 + 用户指定了数据 | 不需要 |

**数据集「先查后建」规则（强制）：** 指定名称时先查询是否已存在同名数据集，存在则复用。

**Git Bash 注意事项：**
- `python3 xxx.py 2>/dev/null || py xxx.py`（Windows 兼容）
- `/` 开头路径会被转换，脚本内部赋值不受影响
- `!=` 等特殊字符不要通过 bash 传递

## 大屏标题规则

- `option.card.title` 必须为空字符串（避免双重标题）
- 页面主标题用 `add_text()`，fontSize≥40，fontWeight='bold'，letterSpacing=5

## 常用组件配置路径速查（内联）

> 以下组件的 option 路径已内联，修改时**直接使用，无需读取 `bi-comp-option-config.md`**。

### JStatsSummary（统计概览）

| 说明 | 配置路径 | 示例值 |
|------|---------|--------|
| 卡片最小宽度 | `option.card.minWidth` | 250 |
| 卡片圆角 | `option.card.borderRadius` | 16 |
| 卡片边框宽度 | `option.card.borderWidth` | 1 |
| 卡片边框颜色 | `option.card.borderColor` | #0f66ff59 |
| 卡片阴影 | `option.card.shadow` | 0 16px 48px #0b76ff59 |
| 卡片模糊度 | `option.card.blur` | 24 |
| 卡片内边距(垂直) | `option.card.padding.vertical` | 24 |
| 卡片内边距(水平) | `option.card.padding.horizontal` | 24 |
| 卡片填充类型 | `option.card.fill.type` | none/color/gradient/image |
| 卡片填充颜色 | `option.card.fill.color` | #0b2b63 |
| 卡片填充渐变启用 | `option.card.fill.gradient.enabled` | true/false |
| 卡片填充渐变起始色 | `option.card.fill.gradient.startColor` | #05336a |
| 卡片填充渐变结束色 | `option.card.fill.gradient.endColor` | #0bb2ff |
| 卡片填充图片 | `option.card.fill.image.url` | /img/xxx.png |
| 外层间距 | `option.layout.gap` | 16 |
| 外层内边距 | `option.layout.padding.top/right/bottom/left` | 16 |
| 外层排列方式 | `option.layout.justify` | space-between |
| 外层圆角 | `option.layout.borderRadius` | 0 |
| 外层边框宽度 | `option.layout.borderWidth` | 0 |
| 外层填充类型 | `option.layout.fill.type` | none/color/gradient/image |
| 外层填充颜色 | `option.layout.fill.color` | #0b2b63 |
| 数值字号 | `option.sections.top.value.fontSize` | 34 |
| 数值字重 | `option.sections.top.value.fontWeight` | 600 |
| 数值颜色 | `option.sections.top.value.fontColor` | #d8f1ff |
| 单位字号 | `option.sections.top.value.unit.fontSize` | 18 |
| 标签字号 | `option.sections.bottom.label.fontSize` | 14 |
| 标签颜色 | `option.sections.bottom.label.fontColor` | #9ed3ff |

### JCapsuleChart（胶囊图）

| 说明 | 配置路径 | 示例值 |
|------|---------|--------|
| 显示数值 | `option.showValue` | true/false |
| X轴名称 | `option.unit` | 个 |

### JGauge（仪表盘）

| 说明 | 配置路径 |
|------|---------|
| 刻度值显隐 | `option.series[0].axisLabel.show` |
| 刻度值颜色 | `option.series[0].axisLabel.color` |
| 刻度线显隐 | `option.series[0].axisTick.show` |
| 分割线显隐 | `option.series[0].splitLine.show` |
| 分割线颜色 | `option.series[0].splitLine.lineStyle.color` |
| 指标字号 | `option.series[0].detail.fontSize` |

### JProgress（进度条-ECharts）

| 说明 | 配置路径 |
|------|---------|
| 显示标题 | `option.yAxis.axisLabel.show` |
| 标题字体颜色 | `option.yAxis.axisLabel.color` |

### JColorBlock（色块指标卡）

| 说明 | 配置路径 |
|------|---------|
| 行数 | `option.lineNum` |
| 边距 | `option.padding` |

### JScrollBoard（轮播表）

| 说明 | 配置路径 |
|------|---------|
| 悬浮暂停 | `option.hoverPause` |
| 等待时间 | `option.waitTime` |

## 图层顺序机制

**核心：`template` 数组索引决定 z-index，不是 orderNum。** 索引 0 = 最顶层。

### 新增组件必须置顶（强制）

> **新添加的组件必须插入到 `template` 数组的索引 0 位置（即最顶层），确保不会被已有组件遮挡。**
> `bi_utils.add_component()` 已使用 `insert(0, comp)` 实现自动置顶。自定义脚本操作模板时也必须用 `insert(0, comp)` 而非 `append(comp)`。

```python
# 置顶
element = tmpl.pop(target_idx)
tmpl.insert(0, element)
# 保存
bi_utils._page_components[PAGE_ID] = tmpl
save_page(PAGE_ID)
```

## 可用快捷函数（bi_utils.py）

**页面管理：** `create_page`, `query_page`, `list_pages`, `save_page`, `delete_page`, `recover_page`, `copy_page`

**添加组件：** `add_number`, `add_chart`(JBar/JLine/JPie/JRing/JRose/JFunnel/JRadar/JHorizontalBar/JSmoothLine/JStackBar/JMixLineBar), `add_table`, `add_scroll_table`, `add_ranking`, `add_text`, `add_image`, `add_gauge`, `add_liquid`, `add_countdown`, `add_border`, `add_decoration`, `add_current_time`, `add_word_cloud`, `add_color_block`, `add_progress`, `add_total_progress`, `add_component`

## Step 4: 输出结果

**必须将预览地址作为单独一行返回，并用 clip.exe 复制到剪贴板。**

```
## 大屏创建成功

- 页面ID：{id}
- 页面名称：{name}
- 组件数量：{count} 个

预览地址：
{API_BASE}/drag/share/view/{id}?token={TOKEN}&tenantId=2
```

```bash
echo -n "{完整URL}" | clip.exe
```

## bi_utils 使用规则（强制）

### 初始化方式

```python
# 正确：直接赋值模块级全局变量
bi_utils.API_BASE = 'http://...'
bi_utils.TOKEN = '...'

# 错误：没有 init() 方法
# bi_utils.init(API_BASE, TOKEN)  # ← AttributeError
```

### 页面数据与组件字段映射（query_page 返回值）

| 正确字段 | 常见误猜 | 说明 |
|---------|---------|------|
| `page['template']` | ~~`page['pageTemplate']`~~ | 组件列表，**已经是 list**，无需 `json.loads` |
| `comp['i']` | ~~`comp['id']`~~ | 组件唯一标识（UUID） |
| `comp['componentName']` | ~~`comp['label']`~~, ~~`comp['name']`~~ | 组件显示名称（中文） |
| `comp['component']` | - | 组件类型（JBar, JText 等） |
| `comp['pageCompId']` | - | 后端数据库 ID |
| `comp['isLock']` | - | 锁定状态（true/false） |

### 自定义脚本操作模板的正确模式

```python
import bi_utils
bi_utils.API_BASE = '...'
bi_utils.TOKEN = '...'
PAGE_ID = '...'

page = bi_utils.query_page(PAGE_ID)
tmpl = page.get('template', [])  # 已经是 list，不需要 json.loads

# 按组件名查找（字段是 componentName，不是 label/name）
target_idx = next(i for i, c in enumerate(tmpl) if c.get('componentName') == '目标名称')

# 修改后保存
bi_utils._page_components[PAGE_ID] = tmpl
bi_utils.save_page(PAGE_ID)
```

### Windows Python 命令

- 用 `py` 不是 `python`（Git Bash 下 `python` 找不到）

### 快捷操作：linkage_ops.py（组件联动/钻取）

> **组件联动 = 点击源组件，将参数传递给目标组件的数据集查询参数，目标组件自动刷新数据。**

**使用前准备：**
```bash
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/linkage_ops.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/bi_utils.py" .
# 执行完后清理
rm linkage_ops.py bi_utils.py
```

**核心命令：**
```bash
# 查看页面所有联动配置
py linkage_ops.py show $API_BASE $TOKEN $PAGE_ID

# 添加联动（--mapping 格式：src=tgt，多个逗号分隔）
py linkage_ops.py add-linkage $API_BASE $TOKEN $PAGE_ID --source "源组件名" --target "目标组件名" --mapping "value=age"
py linkage_ops.py add-linkage $API_BASE $TOKEN $PAGE_ID --source "柱形图" --target "饼图" --mapping "name=name,value=keyword"

# 删除联动
py linkage_ops.py remove-linkage $API_BASE $TOKEN $PAGE_ID --source "源组件名" --target "目标组件名"

# 添加钻取
py linkage_ops.py add-drill $API_BASE $TOKEN $PAGE_ID --source "源组件名" --target "目标组件名" --mapping "name=category"
```

**⚠️ 易错点（强制记忆）：**

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `--param "value:age"` | `--mapping "value=age"` | 参数名是 `--mapping` 不是 `--param` |
| `--mapping "value:age"` | `--mapping "value=age"` | 映射用 `=` 分隔，不是 `:` |
| `--mapping "a=b c=d"` | `--mapping "a=b,c=d"` | 多个映射用逗号分隔 |

**联动前提：** 目标组件必须已绑定数据集，且数据集 SQL 中有对应的查询参数（如 `${age}`）。

### 快捷操作：link_ops.py（外部链接跳转）

> **组件外部链接 = 点击图表跳转到外部 URL，并将点击参数带到链接地址上。**

**使用前准备：**
```bash
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/scripts/link_ops.py" .
cp "C:/Users/25067/.claude/skills/jimubi-bigscreen/references/bi_utils.py" .
# 执行完后清理
rm link_ops.py bi_utils.py
```

**核心命令：**
```bash
# 查看页面所有外部链接配置
py link_ops.py show $API_BASE $TOKEN $PAGE_ID

# 设置外部链接（按名称/类型/ID 三选一定位组件）
py link_ops.py set $API_BASE $TOKEN $PAGE_ID --name "饼图名" --url "https://www.baidu.com/s?wd=\${name}&value=\${value}"
py link_ops.py set $API_BASE $TOKEN $PAGE_ID --type "JPie" --url "https://example.com/detail?category=\${name}"
py link_ops.py set $API_BASE $TOKEN $PAGE_ID --id "538804ec..." --url "https://www.baidu.com/s?wd=\${name}" --target "_self"

# 删除外部链接
py link_ops.py remove $API_BASE $TOKEN $PAGE_ID --name "饼图名"
```

**URL 参数占位符（来自 ECharts 点击事件 params）：**

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `${name}` | 维度名称 | 饼图扇区名、柱子 x 轴标签 |
| `${value}` | 数值 | 饼图扇区值、柱子高度 |
| `${type}` | 系列名称 | 多系列图表的系列标识 |

**打开方式（--target）：** `_blank`（新窗口，默认）、`_self`（当前窗口）

**技术原理：** 组件 config 中 `linkType='url'` + `turnConfig={url:'...', type:'_blank'}`。点击时前端从 ECharts params 中提取 name/value/type，替换 URL 中的 `${...}` 占位符后执行跳转。参考文档：https://help.jimureport.com/biScreen/base/interactive/jumpto

## 核心踩坑速查

| 问题 | 说明 |
|------|------|
| **⚠️ 严禁直接 bi_utils.add_xxx + save_page** | `add_component` 初始化空列表，save_page 会覆盖已有组件造成数据丢失。必须用 `comp_ops.py add` |
| `POST /drag/page/edit` 乐观锁 | 必须传 `updateCount` |
| **chartData 必须是 JSON 字符串** | `json.dumps(...)` 后的字符串 |
| **dataMapping 的 filed 拼写** | `filed` 不是 `field`（少一个 d） |
| **严禁 `rgba(0,0,0,0)`** | 用 `#FFFFFF00` |
| **background 字段位置** | `config` 顶层（与 `option` 同级） |
| **图表标题去重** | `card.title=''`，只用 `option.title.text` |
| **图层顺序** | 数组索引 0=最顶层，`orderNum` 不控制 z-index |
| **⚠️ 新增组件必须置顶** | `bi_utils.add_component()` 已用 `insert(0, comp)` 自动置顶；自定义脚本也必须 `insert(0,...)` 而非 `append()`，否则新组件在最底层被遮挡 |
| **新增组件不显示** | config 不完整或被遮挡，`insert(0,...)` 到数组开头 |
| **组件 ID 字段是 `i` 不是 `id`** | `template` 数组中每个组件的唯一标识字段名为 `i` |
| **组件名称是 `componentName`** | 不是 `label` 也不是 `name`，中文名在 `componentName` |
| **模板数据在 `template` 字段** | `query_page` 返回的组件列表在 `template` 中，已是 list；`pageTemplate` 是空字符串 |
| **bi_utils 无 init() 方法** | 直接赋值 `bi_utils.API_BASE` 和 `bi_utils.TOKEN` |
| **Windows 用 `py` 不是 `python`** | Git Bash 下 `python` 命令不存在 |
| **存储过程：JimuReport API 无法执行 DDL** | `getAllChartData` 用 `executeQuery()` 只支持 SELECT/CALL，CREATE PROCEDURE 会报错。必须通过 pymysql 直连数据库创建存储过程 |
| **⚠️ FreeMarker 判空必须用 `isNotEmpty()`** | 正确：`<#if isNotEmpty(age)>`。错误：~~`<#if age?? && age?length gt 0>`~~（JimuReport 不支持标准 FreeMarker 语法，条件不生效） |
| **⚠️ 带 FreeMarker 的 SQL 禁止 bash 命令行传递** | `${age}` 被 shell 解释为空变量，`<#if>` 的 `>` 被解释为重定向。必须用 `--sql-file` 写入文件或 Python 脚本内部定义 SQL |
| **`${}` 和 `#{}` 不可混用** | `${param}` 是查询参数，`#{sys_user_code}` 是系统变量，混用导致解析失败 |
| **存储过程：数据集 SQL 写 CALL 语法** | `querySql` 填 `CALL sp_name()` 或带参 `CALL sp_name('${param}')`，参数用 FreeMarker 语法 |
| **存储过程：自定义脚本绑定组件缺字段** | 直接操作 config 会缺 `dataSetId`/`dataMapping`/`fieldOption`，导致组件显示静态数据。必须用 `comp_ops.py add --dataset-id` 或 `--create-sql "CALL ..."` |
| **⚠️ JWeatherForecast 不能用 comp_ops.py** | 天气预报组件（JWeatherForecast）不在 comp_ops.py 支持范围内，必须用自定义脚本直接操作 template 数组添加。**dataType 必须为 1**（不是 0），option.template 值决定版本样式（11=滚动版, 34=横线版, 21=带背景, 12=好123版, 27=温度计版, 94=列表文字版）。**不要误用 JScrollList 等其他组件替代** |
| **⚠️ 批量添加组件时手动构造 comp dict** | 必须用 `bi_utils.add_component()` 而非自行构造 `{'component':..., 'config':...}` 并 insert。手动构造会遗漏 `size`/`chart`/`turnConfig`/`linkageConfig` 等必要字段，且 config 必须是 JSON 字符串（不是 dict），否则全部组件显示"暂无数据" |
| **⚠️ option.title 可能是 str 类型** | `default_configs.json` 中部分组件的 `option.title` 是字符串（如 `"基础折线图"`），直接 `option['title']['text'] = x` 会报 `TypeError: 'str' object does not support item assignment`。必须先检查类型：`if isinstance(title, str): title = {'text': title}` |
| **全组件排除装饰类** | "生成全组件"时排除 JWeatherForecast（特殊API组件）、JDragBorder（13种装饰边框）、JDragDecoration（12种装饰条），这些是纯视觉装饰不是业务数据组件 |
| **⚠️ componentName 必须用中文名** | 批量生成时图层名（componentName）必须使用 `menu-hierarchy.md` 中的中文名称（如"基础柱形图"、"饼图"、"统计概览(卡片式)"），禁止直接用 compType（如 JBar、JPie）作为图层名，否则用户在设计器中无法识别组件 |
| **⚠️ 全组件生成禁止为分类生成 JText 标题** | 分类（柱形图/饼图/折线图/...）仅在代码中作注释分组，不要为每个分类生成 JText 组件作为标题。分类标题不是业务组件，会在设计器中产生 20 个多余文本图层，占用额外高度。组件应扁平排列在 all_comps 列表中 |
| **⚠️ linkage_ops.py 参数名和格式** | 联动映射参数是 `--mapping`（不是 `--param`），格式是 `src=tgt`（等号分隔，不是冒号），多个用逗号：`--mapping "name=name,value=keyword"` |
| **⚠️ 模板索引表只有 10 个实际文件** | SKILL.md 模板索引表只列实际存在的 10 个模板文件，禁止使用不存在的模板名（已修正，2026-04-01） |
| **⚠️ template_ops.py copy 集团综合数据大屏报错** | 该模板所有组件 y<150，边界缩放 `min(... if y>=150)` 返回空序列。已修复：加 fallback 取全局最小 y（2026-04-01） |
| **⚠️ JPyramid3D / JOrbitRing 默认尺寸太小** | 3D金字塔（JPyramid3D）和轨道环形文字（JOrbitRing）默认尺寸不够，生成时建议使用 **750×500**，否则显示效果不佳 |

> 完整踩坑记录见 `references/pitfalls.md`

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| Token 过期（401） | 重新获取 X-Access-Token |
| `updateCount` 不匹配 | 重新查询页面获取最新值 |
| 组件不显示 | 检查 dataType、chartData、option 完整性 |
| 中文乱码 | 使用 Python（不要用 curl） |

## 参考文档

- `references/bi-component-types.md` — 完整组件类型清单
- `references/bi-comp-option-config.md` — 组件样式配置路径
- `references/bi_utils.py` — 工具库源码
- `references/core-configs/data.ts` — 组件面板菜单树 + 初始化 config（原始源码，353KB）
- `references/core-configs/optionData.ts` — 组件属性面板配置项列表（原始源码，57KB）
- `references/core-configs/component-defaults.md` — 82+ 组件默认配置速查（尺寸/chartData/option/dataMapping）
- `references/core-configs/addPageComp-logic.md` — 组件创建流程（addPageComp 函数、newItem 结构、位置计算）
- `references/core-configs/menu-hierarchy.md` — 组件菜单分类树（完整层级 + 统计）
- `references/templates/bigScreen/` — 10 个大屏模板 JSON
- `references/scripts/` — 12 个预置操作脚本 + default_configs.json
