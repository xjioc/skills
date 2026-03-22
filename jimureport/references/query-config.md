# 报表查询配置完整指南

## 1. 报表参数配置

### 参数语法

| 语法 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `${paramName}` | 用户参数 | 需要在报表参数中声明，用户可查询输入 | `${id}` `${name}` |
| `#{sysVar}` | 系统变量 | 无需声明，自动解析 | `#{sysUserCode}` `#{sysDate}` |

**注意：** `$` 或 `#` 与 `{` 之间不能有空格。

### SQL 参数示例

```sql
select * from sys_user where id='${id}' and sex='${sex}' and create_by='#{sysUserCode}'
```

### API 参数示例

```
http://192.168.1.116/jmreport/test/getMessage?name='${name}'&createBy='#{sysUserCode}'
```

### 系统变量列表

| 变量 | 说明 |
|------|------|
| `#{sysUserCode}` | 当前登录用户名 |
| `#{sysDate}` | 当前系统日期 |
| `#{sysDateTime}` | 当前系统日期时间 |
| `#{domainURL}` | 系统域名地址 |

### 参数优先级（高→低）

1. **查询条件值**（用户在查询栏输入的）
2. **URL参数**（通过URL传递的）
3. **默认值**（配置的默认值）

### 参数合并规则

- 多个数据集中**同名参数**会合并为一个查询控件
- 同名**数据集字段**不会合并
- URL参数会传递给所有匹配的数据集参数

## 2. 查询控件类型

在数据集字段详情中勾选"查询"复选框，即可生成查询控件。

| 控件类型 | 查询模式值 | 说明 |
|---------|-----------|------|
| 文本输入 | 空或"输入框" | 默认类型 |
| 下拉单选 | "下拉单选" | 可搜索，默认显示10条 |
| 下拉多选 | "下拉多选" | 可搜索，默认显示10条 |
| 范围查询 | "范围查询" | 日期/数值范围；**报表参数不支持** |
| 模糊查询 | "模糊查询" | **报表参数不支持** |
| 下拉树 | 通过配置实现 | 层级树形结构 |
| 自定义下拉 | JS增强实现 | 数据需含 `value` 和 `text` 字段 |

### 下拉数据源配置

**方式一：系统字典**
- 配置字典编码（如 `sex`）

**方式二：SQL字典**
```sql
SELECT username AS value, realname AS text FROM sys_user
```
必须别名为 `value` 和 `text`。

**方式三：API**
- 相对路径：`/jmreport/test/getDictSex?createBy=#{sysUserCode}`
- 绝对路径：`http://127.0.0.1:8080/jeecg-boot/jmreport/test/getDictSex`
- 返回格式：`[{"text":"男","value":"1"},{"text":"女","value":"2"}]`

**方式四：JS增强**
```javascript
this.updateSelectOptions('dbCode', 'fieldName', options)
```

### 下拉显示条数配置

在字段的配置设置中：
```json
{"selectSearchPageSize": 20}
```
默认显示10条。

## 3. 查询控件默认值

三种方式：

| 方式 | 示例 |
|------|------|
| 静态值 | 直接输入字符串 |
| 动态表达式 | `=dateStr('yyyy-MM-dd')` |
| 系统变量 | `#{sysUserCode}` |

## 4. 时间控件

### 支持的日期格式

| 格式 | 示例 |
|------|------|
| `yyyy-MM-dd HH:mm:ss` | 2021-07-29 12:11:10 |
| `yyyy-MM-dd` | 2021-07-29 |
| `yyyy-MM` | 2021-07 |
| `yyyy` | 2021 |
| `MM` | 07 |
| `HH:mm:ss` | 12:11:10 |
| `HH:mm` | 12:11 |

**重要：** 日期控件传递的值始终为字符串类型。

### 数据库日期转换

不同数据库需要用对应的日期转换函数作为查询条件字段：

| 数据库 | 转换函数 | 示例 |
|--------|---------|------|
| MySQL | `DATE_FORMAT(field, '%Y')` | `DATE_FORMAT(birthday, '%Y') nian` |
| Oracle | `to_char(field, 'yyyy')` | `to_char(birthday, 'yyyy') nian` |
| SQL Server | `year(field)` | `year(birthday) nian` |

**SQL示例（MySQL）：**
```sql
SELECT name, birthday, DATE_FORMAT(birthday, '%Y') nian FROM demo
```
将转换后的列 `nian` 配置为查询条件，而非原始日期字段。

### 时间默认值函数

#### dateStr(date, format, offset)（v1.3.79+）

| 参数 | 说明 |
|------|------|
| date | 时间字符串（可选，默认当前时间） |
| format | 格式化模式（默认 `yyyy-MM-dd HH:mm:ss`） |
| offset | 数值偏移量 |

**示例（当前时间 2020-08-11 12:00:01）：**

| 表达式 | 结果 |
|--------|------|
| `=dateStr()` | 2020-08-11 12:00:01 |
| `=dateStr('yyyy-MM-dd')` | 2020-08-11 |
| `=dateStr('MM', 2)` | 10 |
| `=dateStr('dd', -1)` | 10 |
| `=dateStr('2020-08-15 12:00:01', 'yyyy-MM-dd', 1)` | 2020-08-16 |
| `=dateStr('yyyy-MM', -1)` | 2020-07（v1.4.0+） |

#### date2Str(date, format, offset)（v1.7.5+）

与 `dateStr()` 相同但保留前导零（如 `01` 而非 `1`）。

## 5. SQL条件表达式（FreeMarker语法）

v1.3.79+ 支持动态SQL条件，使用 FreeMarker 模板语法。

### isNotEmpty() 函数

对 `null` 和空字符串 `""` 都返回 `false`。

### 基础示例

```sql
select id, name, age from demo where create_by = '#{sysUserCode}'
<#if isNotEmpty(age)> and age = '${age}'</#if>
<#if isNotEmpty(name)> and name = '${name}'</#if>
```

### LIKE模糊查询

```sql
select * from demo where 1=1
<#if name?? && name?length gt 0>
  and name like concat('%', '${name}', '%')
</#if>
```

### 多数据集共享参数

```sql
-- 数据集1
select username, sex, phone, create_time from user where 1=1
<#if isNotEmpty(begin_date)>
  and DATE_FORMAT(create_time, '%Y-%m-%d') >= '${begin_date}'
</#if>
<#if isNotEmpty(end_date)>
  and DATE_FORMAT(create_time, '%Y-%m-%d') <= '${end_date}'
</#if>

-- 数据集2（共享 begin_date 和 end_date 参数）
select count(1) as value, DATE_FORMAT(create_time, '%Y-%m-%d') as name
from user where 1=1
<#if isNotEmpty(begin_date)>
  and DATE_FORMAT(create_time, '%Y-%m-%d') >= '${begin_date}'
</#if>
<#if isNotEmpty(end_date)>
  and DATE_FORMAT(create_time, '%Y-%m-%d') <= '${end_date}'
</#if>
GROUP BY name
```

## 6. SQL表达式函数（DaoFormat）

v1.6.2+ 支持在SQL中使用 `DaoFormat` 函数。

### DaoFormat.in() — 字符串IN查询

输入：`male,female` → 输出：`'male','female'`

```sql
select * from demo where sex in(${DaoFormat.in('${sex}')})
```

### DaoFormat.inNumber() — 数字IN查询

输入：`21,22` → 输出：`21,22`

```sql
select * from demo where age in(${DaoFormat.inNumber('${age}')})
```

### DaoFormat.concat() — 字符串拼接

```sql
select * from demo where create_time between
  '${DaoFormat.concat('${beginTime}', ' 00:00:00')}'
  and '${DaoFormat.concat('${endTime}', ' 23:59:59')}'
```

## 7. 下拉树控件

v1.3.79+ 支持层级树形下拉。

### 配置格式

```json
{"loadTree": "{{ domainURL }}/sys/user/treeTest"}
```
或绝对路径：
```json
{"loadTree": "https://api.jeecg.com/mock/26/queryTree"}
```

### 接口返回格式

```json
[
  {"id": "001", "pid": "", "value": "A01", "title": "节点1", "izLeaf": 0},
  {"id": "002", "pid": "001", "value": "A02", "title": "子节点1", "izLeaf": 1}
]
```

| 字段 | 说明 |
|------|------|
| `id` | 节点标识 |
| `pid` | 父节点ID，空=根节点 |
| `value` | 实际查询值 |
| `title` | 显示文本 |
| `izLeaf` | 1=叶子节点（无展开图标），0=父节点 |

### 穿透场景（v1.5.0+）

```json
{
  "loadTree": ".../treeTest",
  "loadTreeByValue": ".../loadTreeByValue"
}
```

**限制：** 下拉树不支持默认值配置。

## 8. 范围查询默认值

使用管道符 `|` 分隔起止值。

| 场景 | 默认值表达式 |
|------|------------|
| 数字范围 | `16\|22` |
| 固定日期 | `2021-11-01\|2021-11-30` |
| 本月1日到今天 | `=concat(string.substring(dateStr('yyyy-MM-dd'),0,8),'01')\|=dateStr('yyyy-MM-dd')` |
| 最近10天 | `=concat(dateStr('yyyy-MM-dd',-10),' 00:00:00')\|=dateStr('yyyy-MM-dd HH:mm:ss')` |
| 最近3个月 | `=concat(dateStr('yyyy',-1),'-',dateStr('MM',-3),'-',dateStr('dd'))\|=dateStr('yyyy-MM-dd')` |

## 9. JS增强与CSS增强

v1.3.79+ 支持。

### JS API方法

| 方法 | 参数 | 用途 |
|------|------|------|
| `updateSelectOptions(dbCode, fieldName, options)` | 数据集编码, 字段名, 选项数组 | 动态更新下拉选项 |
| `onSearchFormChange(dbCode, fieldName, callback)` | 数据集编码, 字段名, 回调函数 | 监听控件值变化 |
| `updateSearchFormValue(dbCode, fieldName, value)` | 数据集编码, 字段名, 值 | 设置控件初始值 |
| `getSelectOptions(dbCode, fieldName)` | 数据集编码, 字段名 | 获取当前下拉选项 |
| `notLoadDataWhenShow()` | 无 | 预览时不自动加载数据（v1.6.7+） |

### 三级联动下拉示例

```javascript
function init(){
  // 加载省份
  $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect')
    .then(res => {
      this.updateSelectOptions('pca', 'pro', res.data)
    })
  // 省→市联动
  this.onSearchFormChange('pca', 'pro', (value) => {
    $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'city', res.data) })
  })
  // 市→区联动
  this.onSearchFormChange('pca', 'city', (value) => {
    $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'area', res.data) })
  })
}
```

### 设置下拉默认选中第一项（v1.4.0+）

```javascript
function init(){
  let ops = this.getSelectOptions('de', 'sex');
  if(ops && ops.length > 0){
    this.updateSearchFormValue('de', 'sex', ops[0].value)
  }
}
```

### CSS增强示例

```css
.jm-query-form .ivu-btn-primary {
    background-color: red;
    border-color: red;
}
```

## 10. 参数配置设置

| 配置项 | 用途 | 适用控件 |
|--------|------|---------|
| `loadTree` | 树结构加载URL | 下拉树 |
| `loadTreeByValue` | 按值检索树URL | 下拉树 |
| `dictSplit` | 字典分隔符（仅英文字符） | 下拉单选/多选 |
| `selectSearchPageSize` | 每页显示条数（默认10） | 下拉单选/多选 |
| `order` | SQL排序 | 数据集字段详情（非报表参数） |
| `required` | 必填标记（v1.7.9+） | 所有类型 |

必填配置：`{"required": true}`，默认 `false`。v1.9.6+ 支持可视化配置界面。

## 11. 查询设置（querySetting）

```json
"querySetting": {
    "izOpenQueryBar": false,
    "izDefaultQuery": true
}
```

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `izDefaultQuery` | true | 是否自动执行查询（关闭后需手动点击查询按钮） |
| `izOpenQueryBar` | false | 是否默认展开查询栏 |
