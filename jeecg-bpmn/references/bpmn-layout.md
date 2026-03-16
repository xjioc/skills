# 节点 ID 命名与图形布局规则

## 1. 节点 ID 命名规范

| 节点类型 | ID 前缀 | 示例 |
|----------|---------|------|
| 开始事件 | `start` | `start` |
| 结束事件 | `end` | `end` |
| 用户任务 | `task_` | `task_apply`, `task_manager`, `task_hr` |
| 排他网关 | `gateway_` | `gateway_result`, `gateway_amount` |
| 并行网关 | `pgw_` | `pgw_fork`, `pgw_join` |
| 连线 | `flow_` | `flow_1`, `flow_approve`, `flow_reject` |

## 2. 图形布局计算规则

### 2.1 尺寸常量

| 元素 | 宽度(width) | 高度(height) |
|------|------------|-------------|
| startEvent | 36 | 36 |
| endEvent | 36 | 36 |
| userTask | 100 | 60 |
| exclusiveGateway | 50 | 50 |
| parallelGateway | 50 | 50 |

### 2.2 布局策略 — 垂直主轴

所有节点沿 **垂直方向（Y轴）** 从上到下排列，中心线 X 固定。

**基准参数：**
- 主轴中心 X = `218`（所有节点以此为中心对齐）
- 起始 Y = `30`
- 节点间垂直间距 = `40`（节点底部到下一节点顶部的距离）

**计算公式：**

```python
CENTER_X = 218
START_Y = 30
VERTICAL_GAP = 40

# 节点尺寸
SIZES = {
    "startEvent":       {"w": 36, "h": 36},
    "endEvent":         {"w": 36, "h": 36},
    "userTask":         {"w": 100, "h": 60},
    "exclusiveGateway": {"w": 50, "h": 50},
    "parallelGateway":  {"w": 50, "h": 50},
}

def layout_nodes(nodes):
    """计算每个节点的 Bounds (x, y, width, height)"""
    y = START_Y
    positions = []
    for node in nodes:
        size = SIZES[node["type"]]
        x = CENTER_X - size["w"] / 2
        positions.append({
            "id": node["id"],
            "x": x, "y": y,
            "w": size["w"], "h": size["h"],
            "center_x": CENTER_X,
            "center_y": y + size["h"] / 2,
            "bottom_y": y + size["h"]
        })
        y += size["h"] + VERTICAL_GAP
    return positions
```

### 2.3 Shape XML 生成

```xml
<!-- startEvent / endEvent -->
<bpmndi:BPMNShape id="shape_{id}" bpmnElement="{id}">
  <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" />
  <bpmndi:BPMNLabel>
    <dc:Bounds x="{x+7}" y="{y+h+7}" width="22" height="14" />
  </bpmndi:BPMNLabel>
</bpmndi:BPMNShape>

<!-- userTask -->
<bpmndi:BPMNShape id="shape_{id}" bpmnElement="{id}">
  <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" />
</bpmndi:BPMNShape>

<!-- gateway (isMarkerVisible="true" 用于排他网关) -->
<bpmndi:BPMNShape id="shape_{id}" bpmnElement="{id}" isMarkerVisible="true">
  <dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" />
  <bpmndi:BPMNLabel>
    <dc:Bounds x="{x+w+10}" y="{center_y-7}" width="44" height="14" />
  </bpmndi:BPMNLabel>
</bpmndi:BPMNShape>
```

### 2.4 Edge XML 生成

**直线连接（垂直方向、上下相邻节点）：**
```xml
<bpmndi:BPMNEdge id="edge_{flow_id}" bpmnElement="{flow_id}">
  <di:waypoint x="{source.center_x}" y="{source.bottom_y}" />
  <di:waypoint x="{target.center_x}" y="{target.y}" />
</bpmndi:BPMNEdge>
```

**分支连线（排他网关的非主路径，从右侧绕行）：**

当网关有拒绝/回退路径需要连接到非相邻节点时，使用右侧绕行：
```xml
<bpmndi:BPMNEdge id="edge_{flow_id}" bpmnElement="{flow_id}">
  <di:waypoint x="{gateway.center_x + 25}" y="{gateway.center_y}" />
  <di:waypoint x="{gateway.center_x + 132}" y="{gateway.center_y}" />
  <di:waypoint x="{gateway.center_x + 132}" y="{target.center_y}" />
  <di:waypoint x="{target.center_x + target.w/2}" y="{target.center_y}" />
</bpmndi:BPMNEdge>
```

**并行分支连线（从左侧出发）：**
```xml
<bpmndi:BPMNEdge id="edge_{flow_id}" bpmnElement="{flow_id}">
  <di:waypoint x="{gateway.center_x - 25}" y="{gateway.center_y}" />
  <di:waypoint x="{target.center_x - target.w/2 - 50}" y="{gateway.center_y}" />
  <di:waypoint x="{target.center_x - target.w/2 - 50}" y="{target.center_y}" />
  <di:waypoint x="{target.center_x - target.w/2}" y="{target.center_y}" />
</bpmndi:BPMNEdge>
```
