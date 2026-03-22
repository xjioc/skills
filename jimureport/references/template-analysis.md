# 积木报表模板分析参考

## 模板报表查询

通过 `getReportByUser` 接口获取模板报表：
```
GET /jmreport/getReportByUser?reportId=&template=1
```

## 46个模板分类统计

| 分类 | 数量 | 示例 |
|------|------|------|
| 基础表格 | 30 | 信息采集表、简单分组报表 |
| 图表报表 | 9 | 全国各大城市化员数据、物业实时监控 |
| 循环报表 | 4 | 订单表循环打印、班级循环套打表 |
| 图片报表 | 4 | 员工信息表、证书打印 |
| 条码/二维码 | 3 | 实习证明、凭证条码报表 |

## 图表数据绑定

### extData 数据类型 (dataType)

**前端使用文本字符串，非数字：**
- `"sql"` - SQL数据集
- `"api"` - API数据集
- `"json"` - JSON数据集
- `"javabean"` - JavaBean数据集
- `"files"` - 文件数据集
- `null` - 静态图表（无数据绑定，使用ECharts配置中的硬编码数据）

### 字段映射规则

固定三个字段名映射：
```python
extData = {
    "axisX": "name",    # X轴/分类字段
    "axisY": "value",   # Y轴/数值字段
    "series": "type"    # 系列/分组字段（多系列图表用）
}
```

SQL查询需要AS别名：
```sql
SELECT category AS name, COUNT(*) AS value, '' AS type FROM table GROUP BY category
```

### xText / yText 轴标题

工作正常的模板中这两个字段常常为空字符串，轴标题主要通过ECharts配置设置：
```python
chart_config = {
    "xAxis": {
        "name": "表单类型",  # 轴标题
        "type": "category"
    },
    "yAxis": {
        "name": "数量",
        "type": "value"
    }
}
```

## displayConfig 单元格组件

用于在普通单元格中渲染条码、二维码、图片。

### 配置结构
```json
{
  "displayConfig": {
    "1": {"barcodeContent": "#{pop.id}", "format": "CODE128", "width": "50", "height": "100", "displayValue": false},
    "11": {"text": "#{uiu.tm}", "width": 227, "height": 227, "colorDark": "#000000", "colorLight": "#ffffff"},
    "111": {"barcodeContent": "固定值", "format": "QR", "width": "6", "height": 39}
  }
}
```

### 键名规则
- 键名 = `列号`（从1开始）
- 行号通过cells中的display属性关联

### 条码配置 (barcodeContent)
```json
{
  "barcodeContent": "#{字段变量}",  // 动态值
  "format": "CODE128|CODE39|QR",   // 条码格式
  "width": "2",                     // 条码宽度
  "height": 80,                    // 条码高度
  "displayValue": false             // 是否显示值
}
```

### 二维码配置 (text)
```json
{
  "text": "#{字段变量}",           // 二维码内容
  "width": 112,                    // 宽度
  "height": 112,                   // 高度
  "colorDark": "#000000",          // 前景色
  "colorLight": "#ffffff"          // 背景色
}
```

## 循环报表 (loopBlockList)

### 结构
```json
{
  "loopBlockList": [
    {
      "sci": 1,        // 起始列
      "sri": 2,        // 起始行
      "eci": 5,        // 结束列
      "eri": 5,        // 结束行
      "index": 1,      // 块索引
      "db": "jm",      // 数据集别名
      "loopTime": 3    // 循环次数(可选)
    }
  ]
}
```

### 单元格变量语法
```
#{数据集别名.字段名}
#{jm.name}
#{pop.group(id)}
```

## 常见图表类型数据要求

| 图表类型 | dataType | axisX | axisY | series | 示例数据 |
|---------|----------|-------|-------|--------|---------|
| bar.simple | sql/api | name | value | type | 单系列柱状 |
| bar.multi | sql/api | name | value | type | 多系列柱状 |
| line.simple | sql/api | name | value | type | 单线折线 |
| pie.simple | sql/api | name | value | - | 饼图 |
| gauge.simple | sql/api | name | value | - | 仪表盘 |
| radar.basic | sql/api | name | value | type | 雷达图 |
| map.scatter | sql/api | name | value | - | 地图散点 |

## 模板报表ID参考

| 报表名称 | ID | 特点 |
|---------|---|------|
| 全国各大城市化员数据 | 1339859143477039104 | 9个图表(sql+api混合) |
| 图表数据联动示例 | 1356492523694067712 | 19个图表(静态+动态) |
| 物业实时监控 | 1339478701846433792 | 9个图表+地图 |
| 凭证条码报表 | 1338370016550195200 | displayConfig条码 |
| 实习证明 | 1350035590569136128 | displayConfig二维码 |
| 图片展示平台 | 1334074491629867008 | 8个图片+4个图表 |
