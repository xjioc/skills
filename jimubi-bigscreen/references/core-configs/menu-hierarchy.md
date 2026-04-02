# 大屏组件菜单层级结构

> 提取自 `packages/dragEngine/components/bigScreenComponents/data.ts` 的 `menuData` 导出。
> 此文件记录组件面板的完整分类树，用于理解组件归属和定位。

---

## 一级分类

```
menuData [
  {id:'200',              name:'图表',      icon:'JBar'}
  {id:'15341365037580',   name:'装饰'}
  {id:'300000100',        name:'文字'}
  {id:'400000300',        name:'表格'}
  {id:'200000',           name:'地图'}
  {id:'11551',            name:'视频'}
  {id:'100',              name:'表单/组件'}
]
```

---

## 完整层级树

### 图表 (id:200)

```
图表
├── 柱形图 (id:200200)
│   ├── JBar          基础柱形图
│   ├── JStackBar     堆叠柱形图
│   ├── JDynamicBar   动态柱形图
│   ├── JCapsuleChart 胶囊柱形图
│   ├── JHorizontalBar 水平柱形图
│   ├── JBackgroundBar 背景柱形图
│   ├── JMultipleBar  对比柱形图
│   ├── JNegativeBar  负数柱形图
│   ├── JPercentBar   百分比柱形图
│   └── JMixLineBar   混合折线柱形
│
├── 饼图 (id:200201)
│   ├── JPie          饼图
│   ├── JRose         南丁格尔玫瑰图
│   └── JRotatePie    旋转饼图
│
├── 折线图 (id:200202)
│   ├── JLine         基础折线图
│   ├── JSmoothLine   平滑曲线图
│   ├── JStepLine     阶梯折线图
│   ├── JArea         面积图
│   ├── JMultipleLine 多条折线图
│   └── DoubleLineBar 折线柱形混合
│
├── 进度图
│   ├── JCustomProgress 基础进度图
│   ├── JProgress       进度图
│   ├── JListProgress   列表进度图
│   ├── JRoundProgress  圆形进度图
│   └── JLiquid         液体进度图(水球)
│
├── 仪表盘
│   ├── JGauge        基础仪表盘
│   ├── JColorGauge   多色仪表盘
│   ├── JAntvGauge    渐变仪表盘
│   └── JSemiGauge    半圆仪表盘
│
├── 散点图
│   ├── JScatter      普通散点图
│   ├── JQuadrant     象限图
│   └── JBubble       气泡图
│
├── 漏斗图
│   ├── JFunnel       普通漏斗图
│   ├── JPyramidFunnel 金字塔漏斗
│   └── JPyramid3D    3D金字塔
│
├── 雷达图
│   ├── JRadar        普通雷达图
│   └── JCircleRadar  圆形雷达图
│
├── 环形图
│   ├── JRing         饼状环形图
│   ├── JBreakRing    多色环形图
│   ├── JRingProgress 环形进度图
│   ├── JActiveRing   动态环形图
│   └── JRadialBar    径向柱形图
│
├── 其他图表
│   ├── JPictorialBar 象形柱形图
│   ├── JPictorial    象形图
│   ├── JGender       性别占比
│   └── JRectangle    矩形树图
│
└── 3D图表
    ├── JBar3d        3D柱形图
    └── JBarGroup3d   3D分组柱形
```

### 装饰 (id:15341365037580)

```
装饰
├── 边框
│   ├── JDragBorder type='1'   边框1
│   ├── JDragBorder type='2'   边框2
│   ├── JDragBorder type='3'   边框3
│   ├── JDragBorder type='4'   边框4
│   ├── JDragBorder type='5'   边框5
│   ├── JDragBorder type='6'   边框6
│   ├── JDragBorder type='7'   边框7
│   ├── JDragBorder type='8'   边框8
│   ├── JDragBorder type='9'   边框9
│   ├── JDragBorder type='10'  边框10
│   ├── JDragBorder type='11'  边框11
│   ├── JDragBorder type='12'  边框12
│   └── JDragBorder type='13'  边框13
│
├── 装饰
│   ├── JDragDecoration type='1'~'12'  装饰1~12
│
└── 图片
    ├── JImg          图片
    └── JCarousel     轮播图
```

### 文字 (id:300000100)

```
文字
├── 文本
│   ├── JText         文本
│   ├── JCountTo      翻牌器
│   ├── JColorBlock   色块
│   ├── JCurrentTime  当前时间
│   └── JNumber       数字
│
├── 词云
│   ├── JWordCloud    词云
│   ├── JImgWordCloud 图片词云
│   └── JFlashCloud   闪动词云
│
└── 其他
    ├── JOrbitRing      轨道环
    └── JWeatherForecast 天气预报
```

### 表格 (id:400000300)

```
表格
├── 表格
│   ├── JScrollBoard      翻滚表格
│   ├── JScrollTable      表格
│   ├── JCommonTable      通用表格
│   └── JDevHistory       开发进度
│
├── 列表
│   ├── JList             列表
│   ├── JScrollRankingBoard 排行榜
│   ├── JFlashList        闪动列表
│   └── JBubbleRank       气泡排行
│
└── 高级
    ├── JScrollList       滚动列表(基础)
    ├── JScrollList       滚动列表(带序号)
    └── JScrollList       滚动列表(高亮)
```

### 地图 (id:200000)

```
地图
├── 地图
│   ├── JBubbleMap      气泡地图
│   ├── JFlyLineMap     飞线地图
│   ├── JBarMap         柱形地图
│   ├── JTotalFlyLineMap 总飞线地图
│   ├── JTotalBarMap    总柱形地图
│   ├── JHeatMap        热力地图
│   └── JAreaMap        区域地图
│
└── 高德地图
    └── JGaoDeMap       高德地图
```

### 视频 (id:11551)

```
视频
├── JVideoPlay   视频播放
└── JVideoJs     视频播放器
```

### 表单/组件 (id:100)

```
表单/组件
├── JSelectRadio   单选框
├── JTabToggle     导航切换
├── JForm          表单
├── JIframe        框架
├── JRadioButton   单选按钮
├── JDragEditor    富文本编辑
├── JCommon        通用组件
├── JCustomEchart  自定义组件
│
├── 轮播
│   ├── JCardScroll     卡片滚动(横向)
│   ├── JCardScroll     卡片滚动(竖向+序号)
│   ├── JCardScroll     卡片滚动(高亮)
│   └── JCardCarousel   卡片轮播
│
├── 统计
│   ├── JStatsSummary   统计概览(卡片式)
│   ├── JStatsSummary   统计概览(背景式)
│   └── JStatsSummary   统计概览(高亮式)
│
└── 日历
    └── JPermanentCalendar 日历
```

---

## 组件总数统计

| 分类 | 组件数 | 说明 |
|------|--------|------|
| 柱形图 | 10 | 含混合图 |
| 饼图 | 3 | |
| 折线图 | 6 | 含混合图 |
| 进度图 | 5 | |
| 仪表盘 | 4 | |
| 散点图 | 3 | |
| 漏斗图 | 3 | |
| 雷达图 | 2 | |
| 环形图 | 5 | |
| 其他图表 | 4 | |
| 3D图表 | 2 | |
| 边框 | 13 | JDragBorder |
| 装饰 | 12 | JDragDecoration |
| 图片/轮播 | 2 | |
| 文字 | 5 | |
| 词云 | 3 | |
| 表格 | 4 | |
| 列表 | 7 | 含 ScrollList 变体 |
| 地图 | 8 | |
| 视频 | 2 | |
| 表单/交互 | 8 | |
| 轮播/卡片 | 4 | CardScroll 变体 |
| 统计/日历 | 4 | StatsSummary 变体 |
| **总计** | **~82 compType** | 含同 compType 不同变体共 ~110+ |
