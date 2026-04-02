# 子流程（callActivity / subProcess）

JeecgBoot BPM 支持三种子流程模式：
1. **外部调用子流程** `callActivity` — 调用独立部署的子流程
2. **会签子流程** `callActivity` + `countersign` — 多人并行/顺序审批
3. **内嵌子流程（扩展子流程）** `subProcess` — 子流程嵌入主流程 XML 内部

## 内嵌子流程（subProcess / 扩展子流程）

内嵌子流程将子流程的节点直接嵌入主流程 XML 中，无需单独创建和部署。

### JSON 配置

```json
{
  "processName": "扩展子流程审批",
  "nodes": [
    {"id": "start", "type": "startEvent", "name": "开始"},
    {"id": "task_fill", "type": "userTask", "name": "填写人",
     "assignee": {"type": "expression", "value": "applyUserId"}},
    {"id": "sub_process", "type": "subProcess",
     "subNodes": [
       {"id": "sub_start", "type": "startEvent", "name": "开始"},
       {"id": "sub_task1", "type": "userTask", "name": "经理审批",
        "assignee": {"type": "candidateUsers", "value": "zhangli,jeecg"}},
       {"id": "sub_task2", "type": "userTask", "name": "总监审批",
        "assignee": {"type": "assignee", "value": "admin"}},
       {"id": "sub_end", "type": "endEvent", "name": "结束"}
     ],
     "subFlows": [
       {"id": "sf1", "source": "sub_start", "target": "sub_task1"},
       {"id": "sf2", "source": "sub_task1", "target": "sub_task2"},
       {"id": "sf3", "source": "sub_task2", "target": "sub_end"}
     ]},
    {"id": "task_hr", "type": "userTask", "name": "人力审批",
     "assignee": {"type": "assignee", "value": "jeecg"}},
    {"id": "end", "type": "endEvent", "name": "结束"}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "task_fill"},
    {"id": "f2", "source": "task_fill", "target": "sub_process"},
    {"id": "f3", "source": "sub_process", "target": "task_hr"},
    {"id": "f4", "source": "task_hr", "target": "end"}
  ]
}
```

**subProcess 节点字段：**
- `subNodes` — 内部节点数组（支持 startEvent/userTask/endEvent）
- `subFlows` — 内部连线数组

### ⚠️ 关键生成规则（实测验证，必须遵守）

#### 1. BPMNShape 必须加 `isExpanded="true"`

```xml
<bpmndi:BPMNShape id="shape_sub_1" bpmnElement="sub_1" isExpanded="true">
  <dc:Bounds x="410" y="130" width="660" height="200" />
</bpmndi:BPMNShape>
```

**错误写法（缺少属性，设计器中子流程会折叠成小方块）：**
```xml
<bpmndi:BPMNShape id="shape_sub_1" bpmnElement="sub_1">  <!-- ❌ 缺少 isExpanded -->
  <dc:Bounds x="410" y="190" width="100" height="80" />   <!-- ❌ 尺寸错误 -->
</bpmndi:BPMNShape>
```

#### 2. 子流程容器尺寸：宽度 ≥ 660，高度 = 200

- 宽度公式：`max(660, len(subNodes) * 160 + 100)`
- 高度固定：200
- Y 坐标：`row_center_y - 100`（使子流程垂直居中于所在行）

#### 3. 内部节点坐标为绝对坐标（非相对坐标）

BPMNDiagram 中，内部节点（sub_start/sub_task/sub_end）使用**整个图的绝对坐标**，不是相对于子流程容器的相对坐标：

```xml
<!-- 子流程容器: x=410, y=130, w=660, h=200, center_y=230 -->
<bpmndi:BPMNShape id="shape_sub_start" bpmnElement="sub_start">
  <dc:Bounds x="519" y="212" width="36" height="36" />   <!-- 绝对坐标 -->
</bpmndi:BPMNShape>
<bpmndi:BPMNShape id="shape_sub_task1" bpmnElement="sub_task1">
  <dc:Bounds x="610" y="190" width="100" height="80" />  <!-- 绝对坐标 -->
</bpmndi:BPMNShape>
```

#### 4. 内部 subFlows 必须在 BPMNDiagram 中生成 BPMNEdge

`subFlows` 的连线除了在 `<bpmn2:subProcess>` 内部有 `sequenceFlow` 外，还必须在 BPMNDiagram 中有对应的 `BPMNEdge`：

```xml
<bpmndi:BPMNEdge id="edge_sf1" bpmnElement="sf1">
  <di:waypoint x="555" y="230" />
  <di:waypoint x="610" y="230" />
</bpmndi:BPMNEdge>
```

**常见错误：** 只生成了 `<bpmn2:sequenceFlow>` 而漏掉了 BPMNDiagram 中的 `BPMNEdge`，导致设计器中连线不可见。

#### 5. 手工分支布局中 subProcess 作为前置节点（prefix node）时

当主流程使用手工分支（task_dept 有 2 条无条件出线），而 subProcess 位于手工分支源节点**之前**（作为 prefix node）时：
- **不能**用普通任务的 100×80 尺寸
- **必须**使用展开后的实际尺寸（宽 ≥ 660，高 200）
- 后续节点的 x 坐标须在 subProcess 右边缘之后

`bpmn_creator.py` 已在 2026-04-02 修复此 bug（`calc_layout_manual_branch` 中 prefix_nodes 循环改为按实际宽度计算）。

### 内嵌子流程 vs 外部调用子流程

| 特性 | 内嵌子流程 `subProcess` | 外部调用 `callActivity` |
|------|----------------------|----------------------|
| XML 位置 | 嵌在主流程 XML 内部 | 独立流程，单独部署 |
| 部署 | 随主流程一起部署 | 需先部署子流程 |
| 复用 | 不可复用 | 可被多个主流程调用 |
| 布局 | `isExpanded="true"` 展开显示 | 普通节点大小 |
| start 节点 | 无需配 PC 表单地址 | 需要配（发布前） |

### 参考示例

- 扩展子流程: `references/example/扩展子流程.bpmn`

---

## 外部调用子流程（callActivity）

主流程通过 `callActivity` 节点调用外部子流程。子流程结束后自动回到主流程继续执行。

## JSON 配置

### 子流程配置

子流程分两种场景，使用不同的表单地址配置方式：

---

#### 场景 A：OA 类子流程（如借款、用车，复用主流程表单）

**规则：**
- 子流程**不关联独立表单**（不配置 `formLink`）
- draft 节点 PC 地址使用**主流程的 DesForm 地址**（通过 `draftNodeForm` 指定）
- 子流程 start 节点不需要单独配表单地址

```json
{
  "processName": "借款申请子流程",
  "processKey": "oa_business_trip_loan_sub",
  "isSubProcess": true,
  "draftNodeForm": {
    "formType": "desform",
    "formCode": "oa_business_trip_apply",
    "mode": "edit"
  },
  "nodes": [
    {"id": "start", "type": "startEvent", "name": "开始"},
    {"id": "task_draft", "type": "userTask", "name": "填写借款申请", "draft": true,
     "assignee": {"type": "expression", "value": "applyUserId"}},
    {"id": "task_finance", "type": "userTask", "name": "财务审批",
     "assignee": {"type": "role", "value": "admin"}},
    {"id": "end", "type": "endEvent", "name": "结束"}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "task_draft"},
    {"id": "f2", "source": "task_draft", "target": "task_finance"},
    {"id": "f3", "source": "task_finance", "target": "end"}
  ]
}
```

**`draftNodeForm` 字段说明：**

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `formType` | 否 | `desform` | `desform` 或 `online` |
| `formCode` | 是 | - | 主流程的表单编码（DesForm 时为表单 code） |
| `mode` | 否 | `edit` | `edit`=编辑 / `detail`=查看 |

> **注意：** `draftNodeForm` 只影响 draft 节点的 PC 地址，不关联表单到流程，不影响流程执行。

---

#### 场景 B：独立子流程（有自己的独立表单）

子流程拥有独立的 DesForm 表单，通过 `startNodeForm` 配置 start 节点 PC 地址：

```json
{
  "processName": "客户申请子流程",
  "processKey": "process_customer_sub",
  "isSubProcess": true,
  "startNodeForm": {
    "formType": "desform",
    "formCode": "crm_customer_info",
    "mode": "detail"
  },
  "nodes": [
    {"id": "start", "type": "startEvent", "name": "开始"},
    {"id": "sub_task1", "type": "userTask", "name": "子流程审核",
     "assignee": {"type": "expression", "value": "applyUserId"}},
    {"id": "end", "type": "endEvent", "name": "结束"}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "sub_task1"},
    {"id": "f2", "source": "sub_task1", "target": "end"}
  ]
}
```

**关键字段：**
- `isSubProcess: true` — 标记为子流程，自动添加 `SubProcessStartListener`，start 节点纳入 nodes 参数
- `startNodeForm` — start 节点的 PC 表单地址配置（**必须在发布前配置**）

### 主流程配置（含 callActivity）

```json
{
  "processName": "客户申请主流程",
  "nodes": [
    {"id": "start", "type": "startEvent", "name": "开始"},
    {"id": "task_draft", "type": "userTask", "name": "填写申请", "draft": true,
     "assignee": {"type": "expression", "value": "applyUserId"}},
    {"id": "call_sub", "type": "callActivity", "name": "调用子流程",
     "calledElement": "process_customer_sub"},
    {"id": "end", "type": "endEvent", "name": "结束"}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "task_draft"},
    {"id": "f2", "source": "task_draft", "target": "call_sub"},
    {"id": "f3", "source": "call_sub", "target": "end"}
  ]
}
```

**callActivity 节点字段：**
- `calledElement` — 子流程的 processKey（必填）
- 脚本自动传递变量 `applyUserId` 和 `JG_LOCAL_PROCESS_ID`

## 执行顺序（重要）

```
1. 创建子流程  →  保存（不发布）
2. 配 start 节点  →  配置 PC 表单地址（必须在发布前）
3. 发布子流程  →  部署到引擎
4. 创建主流程  →  保存 + 发布
```

> **严格规则：** start 节点的表单地址必须在发布流程之前配置，否则不生效。

## PC 表单地址规则

### 表单设计器（DesForm）

| 模式 | URL 格式 |
|------|---------|
| **查看**（默认） | `{{DOMAIN_URL}}/desform/detail/{formCode}/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false` |
| **编辑** | `{{DOMAIN_URL}}/desform/edit/{formCode}/${BPM_DES_DATA_ID}?token={{TOKEN}}&taskId={{TASKID}}&skip=false` |

### Online 表单

| 模式 | URL 格式 |
|------|---------|
| **查看**（默认） | `super/bpm/process/components/OnlineFormDetail` |
| **编辑** | `super/bpm/process/components/OnlineFormOpt` |

**注意：** URL 中的占位符使用规则：
- `{{DOMAIN_URL}}`、`{{TOKEN}}`、`{{TASKID}}` — 双花括号，系统模板变量
- `${BPM_DES_DATA_ID}` — 单花括号 `${}`，流程变量（不要写成 `${{}}` 双花括号）

## startNodeForm 配置

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `formType` | 否 | `desform` | `desform` 或 `online` |
| `formCode` | 是(desform) | - | DesForm 表单编码 |
| `mode` | 否 | `detail` | `detail`=查看 / `edit`=编辑 |

## 会签子流程（countersign）

会签是多人审批场景，通过 `callActivity` + `multiInstanceLoopCharacteristics` 实现。

### 会签 vs 普通调用子流程

| 特性 | 普通调用子流程 | 会签子流程 |
|------|-------------|----------|
| 监听器 | `SubProcessStartListener` | `SubProcessHqStartListener`（注意 **Hq**） |
| 多实例 | 无 | `multiInstanceLoopCharacteristics` |
| 审批人变量 | - | `assigneeUserId`（循环变量） |
| 会签人列表 | - | `assigneeUserIdList` |
| JSON 标记 | `isSubProcess: true` | `isCountersignSubProcess: true` |

### 会签子流程 JSON 配置

```json
{
  "processName": "会签子流程",
  "isCountersignSubProcess": true,
  "startNodeForm": {
    "formType": "desform",
    "formCode": "crm_customer_info",
    "mode": "detail"
  },
  "nodes": [
    {"id": "start", "type": "startEvent", "name": "开始"},
    {"id": "sub_task1", "type": "userTask", "name": "子节点1",
     "assignee": {"type": "expression", "value": "assigneeUserId"}},
    {"id": "sub_task2", "type": "userTask", "name": "子节点2",
     "assignee": {"type": "expression", "value": "assigneeUserId"}},
    {"id": "end", "type": "endEvent", "name": "结束"}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "sub_task1"},
    {"id": "f2", "source": "sub_task1", "target": "sub_task2"},
    {"id": "f3", "source": "sub_task2", "target": "end"}
  ]
}
```

### 主流程 callActivity 会签配置

```json
{"id": "call_hq", "type": "callActivity", "name": "会签子流程",
 "calledElement": "process_hq_sub_key",
 "countersign": {
   "sequential": false,
   "collection": "assigneeUserIdList",
   "elementVariable": "assigneeUserId"
 }}
```

**countersign 字段：**

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `sequential` | `false` | `false`=并行会签（所有人同时审） / `true`=顺序会签（按序逐个审） |
| `collection` | `assigneeUserIdList` | 会签人列表变量名 |
| `elementVariable` | `assigneeUserId` | 循环变量名（传入子流程的审批人） |

### 会签 XML 关键元素

```xml
<!-- callActivity 内的多实例配置 -->
<bpmn2:multiInstanceLoopCharacteristics
  isSequential="false"
  flowable:collection="${flowUtil.stringToList(assigneeUserIdList)}"
  flowable:elementVariable="assigneeUserId" />

<!-- 额外传递的变量 -->
<flowable:in source="assigneeUserId" target="assigneeUserId" />
<flowable:out source="applyUserId" target="applyUserId" />
```

### 会签子流程监听器（注意是 Hq）

```xml
<flowable:executionListener
  class="org.jeecg.modules.extbpm.listener.execution.SubProcessHqStartListener"
  event="start" id="1177167770459070465" />
```

### 参考示例

- 会签主流程: `references/example/会签主流程.bpmn`
- 会签子流程: `references/example/会签子流程.bpmn`

---

## BPMN XML 特征

### 子流程额外监听器

```xml
<flowable:executionListener
  class="org.jeecg.modules.extbpm.listener.execution.SubProcessStartListener"
  event="start" id="64d675c1a3adcb514ea5f9835093c29b" />
```

### callActivity XML

```xml
<bpmn2:callActivity id="call_sub" name="调用子流程" calledElement="process_sub_key">
  <bpmn2:extensionElements>
    <flowable:in source="applyUserId" target="applyUserId" />
    <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />
  </bpmn2:extensionElements>
</bpmn2:callActivity>
```

## 参考

- 主流程示例: `references/example/外部主流程.bpmn`
- 子流程示例: `references/example/外部子流程.bpmn`
