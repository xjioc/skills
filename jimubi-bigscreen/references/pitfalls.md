# API 踩坑记录（大屏常见问题速查）

## 组件类型匹配踩坑

| 用户描述 | 错误匹配 | 正确组件 | 说明 |
|---------|---------|---------|------|
| 表格 | JScrollList | JScrollTable | 「表格」应映射到 JScrollTable（滚动表格），JScrollList 是「滚动列表」 |
| 轮播表 | JScrollTable | JScrollBoard | 「轮播表」是 JScrollBoard，不是 JScrollTable（滚动表格） |
| 发展历程 | JLine | JDevHistory | 「发展历程」有专用组件 JDevHistory，不要用折线图替代 |

## 组件名称匹配踩坑（按名称查找已有组件时）

| 规则 | 说明 |
|------|------|
| **⚠️ 禁止仅按组件类型匹配** | 页面上可能有多个同类型组件（如 2 个 JLine），仅按 `component=='JLine'` 会选错 |
| **必须按业务关键词匹配 componentName** | 用户说「智慧社区折线图」→ 匹配 `componentName` 包含「智慧社区」的组件，而非随意选一个 JLine |
| **匹配优先级** | 精确匹配 > 包含用户业务关键词 > 包含组件类型关键词 |
| **示例** | 用户说「智慧社区折线图」，页面有「基础折线图」和「智慧社区_时间分部」两个 JLine → 正确选「智慧社区_时间分部」 |

## 核心踩坑

| 问题 | 说明 |
|------|------|
| `POST /drag/page/edit` 乐观锁 | 必须传 `updateCount`（当前数据库值） |
| **chartData 必须是 JSON 字符串** | `config.chartData` 的值必须是 `json.dumps(...)` 后的字符串 |
| **dataMapping 的 filed 拼写** | 系统中 `filed` 不是 `field`（少一个 d） |
| **严禁使用 `rgba(0,0,0,0)` 作为背景色** | Ant Design 颜色选择器将其解析为红色。必须用 `#FFFFFF00` |
| **background 字段位置** | `config` 的顶层字段（与 `option` 同级），不是在 `option` 内部 |
| **图表标题去重** | `option.card.title` 必须为空字符串，标题仅通过 `option.title.text` 显示 |
| **图层顺序由数组索引决定** | `template` 数组索引 0=最顶层，`orderNum` 不控制 z-index |

## 数据集相关

| 问题 | 说明 |
|------|------|
| **"数据源不存在"** | SQL 数据集未设置 `dbSource` |
| **字段列表不生效** | 用了 `onlDragDatasetItemList`，正确是 `datasetItemList` |
| **编辑数据集 510 权限错误** | 确保用户 Token 拥有 `drag:dataset:save` 权限 |
| **API 地址存在 querySql 字段** | API 数据集没有独立 url 字段，`querySql` 存 API URL |
| **API 数据集不需要 dbSource** | `dbSource` 设为 `None` |
| **创建数据集 parentId 必须为 '0'** | 不设或留空导致管理界面无法正确归类 |
| **数据集创建返回值是 dict** | `result` 是完整实体对象，需取 `result.id` |
| **数据源创建返回值是 string** | `result` 直接是数据源 ID 字符串 |
| **queryAllById 返回 result=null** | 权限或数据隔离问题，不要依赖此接口 |
| **编辑数据集字段名与查询不同** | `queryAllById` 返回 `onlDragDatasetItemList`，`edit` 需要 `datasetItemList` |
| **comp_ops.py --dataset-name 绑定后无数据** | list 接口不返回字段列表，已修复：自动从 getAllChartData 推断 |
| **字典翻译用 jimu_dict 不是 sys_dict** | 大屏字典 API 为 `/jmreport/dict/*`，不是 `/sys/dict/*`。`/sys/dict/getDictItems/` 需要签名且是系统字典表，大屏不使用 |
| **SQL 最大返回 1000 条** | 后端限制 |
| **⚠️ list 接口不返回 datasetItemList/datasetParamList** | `GET /drag/onlDragDatasetHead/list` 返回的记录中 `datasetItemList` 和 `datasetParamList` 始终为空数组，但数据实际已保存。验证方式：调用 `getAllChartData` 检查 `dictOptions` 是否生效 |
| **⚠️ 带 FreeMarker 的 SQL 禁止通过 bash 命令行传递** | `${age}` 被 shell 解释为空变量，`<#if>` 中的 `>` 被解释为重定向。**必须用 `--sql-file sql.txt`** 将 SQL 写入文件再传给 comp_ops.py / dataset_ops.py，或写自定义 Python 脚本在代码内部定义 SQL 字符串 |
| **⚠️ FreeMarker 判空必须用 `isNotEmpty()`** | JimuReport 内置函数 `isNotEmpty(param)` 判断 null 和空字符串均返回 false。正确：`<#if isNotEmpty(age)>`。**错误：`<#if age?? && age?length gt 0>`**（标准 FreeMarker 语法但 JimuReport 不支持，会导致条件不生效） |
| **⚠️ `${}` 和 `#{}` 不可混用** | `${param}` 是查询参数占位符，`#{sys_user_code}` 是系统变量。混用会导致解析失败 |
| **⚠️ 数据集字典绑定在 datasetItemList 中** | 字典翻译通过 `datasetItemList[].dictCode` 绑定（如 `'dictCode': 'sex'`），不是在组件 config 中手动构建 `dictOptions`。绑定后 `getAllChartData` 会自动返回 `dictOptions` |
| **⚠️ 组件 dictOptions 必须从 getAllChartData 获取** | 创建组件时，先调 `getAllChartData` 获取数据集的 `dictOptions`，再写入组件 `config.dictOptions`。手动构建 dictOptions 容易遗漏格式（需包含 value/text/color/label/title 等字段） |

## 组件相关

| 问题 | 说明 |
|------|------|
| **⚠️ 严禁直接用 bi_utils.add_xxx + save_page** | `add_component` 内部初始化空列表 `_page_components[page_id] = []`，不会加载已有组件。`save_page` 会用这个空列表+新组件覆盖整个页面，**导致已有组件全部丢失**。必须用 `comp_ops.py add` 或手动先执行 `bi_utils._page_components[PAGE_ID] = page.get('template', [])` |
| **添加组件必须用 comp_ops.py add** | comp_ops.py 在 cmd_add 中会先 `load_template` 再赋值 `_page_components`，安全保留已有组件。直接调 bi_utils 函数是危险操作 |
| **新增组件不显示** | config 不完整或被背景图遮挡，将新组件 `insert(0, ...)` 到数组开头 |
| **comp_ops.py add 渲染失败** | 缺少 `default_configs.json`，使用 add 时必须同时复制 |
| **⚠️ 高级组件添加后无渲染（已修复）** | 胶囊图、列表进度图、圆形进度图、半圆仪表盘、日历、卡片轮播、统计概览、滚动列表等非 ECharts 组件，其 default_configs.json 中的 chartData/option 原先是 `__ref:` 占位符，`_clean_ref_values()` 将其替换为 None 导致数据丢失。**已修复**：所有 `__ref:` 已内联为实际 JSON 数据 |
| **⚠️ 自定义脚本添加图表必须从 default_configs.json 加载默认 config** | 手写 option/series/legend 等配置容易遗漏字段导致渲染异常。正确做法：`json.loads(json.dumps(defaults['JPie']))` 深拷贝默认配置，再覆盖动态数据字段（dataType/dataSetId/dataMapping 等） |
| **JGroup 子组件存储位置** | 在 `comp.props.elements` 中 |
| **JGroup 子组件缺少 groupStyle** | 必须按百分比计算 |
| **联动必须设 linkType** | 必须同时设置 `linkType: 'comp'` 和 `linkageConfig` |
| **联动 linkageId 必须精确** | 值是目标组件的 `i` 字段（UUID） |
| **source 字段来自 ECharts params** | `name`/`value`/`type` 对应 ECharts 点击事件 params |
| **多系列 chartData 格式** | 需要 `type` 字段：`[{"name":"1月","value":10,"type":"系列A"}]` |

## 模板相关

| 问题 | 说明 |
|------|------|
| **页签切换不工作** | JTabToggle 的 `compVals` 引用了旧 ID，必须建 ID 映射 |
| **模板组件超出 1920x1080** | 预览不支持滚动，复制后必须做边界检查 |
| **替换数据量与原模板不一致** | 保持数据条数一致，避免溢出 |

## 脚本参数相关

| 问题 | 说明 |
|------|------|
| **datasource_ops.py create 参数名** | `--db`（不是 `--db-name`），`--user`（不是 `--username`） |
| **datasource_ops.py test 不支持 --name** | 只能用 `--id` 或直接传连接参数（`--db-type --host --port --db --user --password`） |
| **datasource_ops.py 创建+测试不能链式执行** | test 不支持按名称查找，创建后需用连接参数重复传递来测试 |

## bi_utils 内部结构相关

| 问题 | 说明 |
|------|------|
| **bi_utils 没有 init() 方法** | 直接赋值模块级全局变量：`bi_utils.API_BASE = '...'`、`bi_utils.TOKEN = '...'` |
| **组件列表在 `page['template']` 中** | `query_page()` 返回的组件列表字段是 `template`（已经是 list），**不是** `pageTemplate`（那个是空字符串） |
| **组件 ID 字段是 `i` 不是 `id`** | 每个组件的唯一标识存储在 `comp['i']` 中，不是 `comp['id']`（`id` 字段不存在） |
| **组件名称字段是 `componentName`** | 中文显示名存储在 `comp['componentName']`，不是 `label` 也不是 `name`（这两个字段不存在） |
| **template 字段已经是 list** | 无需 `json.loads()`，直接 `page.get('template', [])` 即可使用 |
| **page 主要 keys** | `id, name, path, desJson, template, coverUrl, backgroundColor, backgroundImage, theme, style, designType, type, izTemplate, ...` |

## 环境相关

| 问题 | 说明 |
|------|------|
| **Windows Git Bash 找不到 python** | 用 `py xxx.py`（不是 `python`） |
| **Git Bash 路径自动转换** | `/img/bg/bg5.png` 被转为 `C:/Program Files/Git/...`。预置脚本已修复，自定义脚本在 Python 内部赋值 |
| **Git Bash `!` 转义** | SQL 中 `!=` 变成 `\!=`。必须用 Python 脚本传递 SQL |
| **⚠️ Git Bash shell 变量传递给 py 脚本为空** | `API_BASE="http://..." && py script.py "$API_BASE"` 变量可能为空（尤其含特殊字符的长 JWT token）。**必须直接内联字面值**：`py script.py "http://..." "eyJ..."` |
| **⚠️ comp_ops.py list 中文乱码** | Git Bash 终端默认编码非 UTF-8，`comp_ops.py list` 输出的中文组件名全部乱码。**解决方案：不要单独调 list 查看名称，直接在自定义 Python 脚本中用 `query_page()` + `json.dumps(ensure_ascii=False)` 输出，或用 `py -X utf8` 执行** |
| **签名验证失败：时间戳为空** | 需要 `X-TIMESTAMP` + `X-Sign` + `V-Sign`，见 `signing-datasource-guide.md` |
| **HTTPS 连接问题** | api3.boot.jeecg.com 使用 HTTP 协议 |
| **后端项目目录不存在** | bi_utils.py 复制到当前工作目录 |

## 页面配置相关

| 问题 | 说明 |
|------|------|
| **页面级配置用 _request** | `query_page()` 只返回组件信息，修改背景色/水印等需用 `_request('GET', '/drag/page/queryById')` |
| **desJson 是 JSON 字符串** | 修改前 `json.loads()`，修改后 `json.dumps()` |
| **水印在 desJson.waterMark 中** | 不是页面顶层字段 |
| **数据集绑定必须设 dataSetName** | 缺少导致设计器中数据集下拉框显示为空 |

## 地图相关

| 问题 | 说明 |
|------|------|
| **地图空白** | 后端没有对应 adcode 的地图数据 |
| **addMapData 的 name 格式** | 存储 adcode（`"650000"`），不是中文名 |
| **china 地图不走后端** | 前端内置，不需要上传 |
| **area.value 是数组** | `["650000"]`，取最后一个元素 |
