# 子流程与网关类型详解

## 1. 网关类型一览

| 用户描述 | BPMN 类型 | XML 元素 | 说明 |
|----------|----------|----------|------|
| 分支/条件判断/通过或拒绝 | 排他网关 | `exclusiveGateway` | 只走一条满足条件的路径 |
| 并行/同时 | 并行网关 | `parallelGateway` | 所有路径同时执行，全部完成后汇聚 |
| 包含/部分并行 | 包含网关 | `inclusiveGateway` | 满足条件的路径都走，全部完成后汇聚 |

> **注意：** JeecgBoot 设计器不支持事件网关（eventBasedGateway），实际只用上面三种。

---

## 2. 排他网关（exclusiveGateway）

只走一条路径，适用于"通过/拒绝"、"金额判断"等场景。

```xml
<bpmn2:exclusiveGateway id="gateway_result" name="审批结果" />

<!-- 条件连线 -->
<bpmn2:sequenceFlow id="flow_approve" name="通过" sourceRef="gateway_result" targetRef="task_next">
  <bpmn2:conditionExpression xsi:type="tFormalExpression"><![CDATA[${result == 1}]]></bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
<bpmn2:sequenceFlow id="flow_reject" name="拒绝" sourceRef="gateway_result" targetRef="end">
  <bpmn2:conditionExpression xsi:type="tFormalExpression"><![CDATA[${result == 0}]]></bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
```

**BPMNShape：** 排他网关需要 `isMarkerVisible="true"`
```xml
<bpmndi:BPMNShape id="shape_gateway" bpmnElement="gateway_result" isMarkerVisible="true">
  <dc:Bounds x="715" y="205" width="50" height="50" />
</bpmndi:BPMNShape>
```

---

## 3. 并行网关（parallelGateway）

所有路径同时执行，必须成对使用（fork + join）。连线**不需要条件表达式**。

```xml
<!-- 并行分支（fork） -->
<bpmn2:parallelGateway id="pgw_fork" name="并行开始" />

<!-- 并行任务 -->
<bpmn2:userTask id="task_a" name="部门A审批" flowable:assignee="admin" />
<bpmn2:userTask id="task_b" name="部门B审批" flowable:assignee="admin" />

<!-- 并行汇聚（join） -->
<bpmn2:parallelGateway id="pgw_join" name="并行汇聚" />

<!-- 连线（无条件） -->
<bpmn2:sequenceFlow id="flow_fork_a" sourceRef="pgw_fork" targetRef="task_a" />
<bpmn2:sequenceFlow id="flow_fork_b" sourceRef="pgw_fork" targetRef="task_b" />
<bpmn2:sequenceFlow id="flow_join_a" sourceRef="task_a" targetRef="pgw_join" />
<bpmn2:sequenceFlow id="flow_join_b" sourceRef="task_b" targetRef="pgw_join" />
```

---

## 4. 包含网关（inclusiveGateway）

满足条件的路径都会执行，也必须成对使用（分支 + 汇聚）。**连线需要条件表达式**。

### 4.1 基本用法（来自生产环境：包含网关测试）

```
开始 → 领取体检单 → 包含网关1（分支）
  ├─ 普通员工 (user_type=='1') → 常规体检 ──┐
  ├─ 全部 (user_type=='1'||'2') → 抽血化验 → 领取早餐 ──┤→ 包含网关2（汇聚）→ 结束
  └─ 领导 (user_type=='2') → 深度体检 ──┘
```

```xml
<!-- 包含网关分支 -->
<bpmn2:inclusiveGateway id="igw_fork" name="包含网关分支" />

<!-- 带条件的连线 -->
<bpmn2:sequenceFlow id="flow_1" name="普通员工" sourceRef="igw_fork" targetRef="task_normal">
  <bpmn2:conditionExpression xsi:type="tFormalExpression">${user_type=='1'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
<bpmn2:sequenceFlow id="flow_2" name="全部" sourceRef="igw_fork" targetRef="task_blood">
  <bpmn2:conditionExpression xsi:type="tFormalExpression">${user_type=='1' || user_type=='2'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
<bpmn2:sequenceFlow id="flow_3" name="领导" sourceRef="igw_fork" targetRef="task_deep">
  <bpmn2:conditionExpression xsi:type="tFormalExpression">${user_type=='2'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>

<!-- 包含网关汇聚 -->
<bpmn2:inclusiveGateway id="igw_join" name="包含网关汇聚" />

<!-- 所有分支汇聚到同一个网关 -->
<bpmn2:sequenceFlow id="flow_join_1" sourceRef="task_normal" targetRef="igw_join" />
<bpmn2:sequenceFlow id="flow_join_2" sourceRef="task_breakfast" targetRef="igw_join" />
<bpmn2:sequenceFlow id="flow_join_3" sourceRef="task_deep" targetRef="igw_join" />
```

### 4.2 包含网关 + 直通路径（来自生产环境：督办流程）

包含网关的一个分支可以直接连到汇聚网关（不经过任何任务），实现"无风险时跳过"的效果：

```
部门负责人审核 → 包含网关（分支）
  ├─ 有风险 (iz_danger=='1') → 风控审计负责 ──┐
  ├─ 有风险 (iz_danger=='1') → 部门分管领导 ──┤→ 包含网关（汇聚）→ 结束
  └─ 无风险 (iz_danger=='0') ──────────────────┘
```

```xml
<bpmn2:inclusiveGateway id="Gateway_fork" />
<bpmn2:inclusiveGateway id="Gateway_join" />

<!-- 有风险：走两条并行路径 -->
<bpmn2:sequenceFlow id="flow_risk1" name="有风险" sourceRef="Gateway_fork" targetRef="task_audit">
  <bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression">${iz_danger== '1' }</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
<bpmn2:sequenceFlow id="flow_risk2" name="有风险" sourceRef="Gateway_fork" targetRef="task_leader">
  <bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression">${iz_danger== '1' }</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>

<!-- 无风险：直接到汇聚网关 -->
<bpmn2:sequenceFlow id="flow_norisk" name="无风险" sourceRef="Gateway_fork" targetRef="Gateway_join">
  <bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression">${iz_danger=='0'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>

<!-- 汇聚 -->
<bpmn2:sequenceFlow id="flow_j1" sourceRef="task_audit" targetRef="Gateway_join" />
<bpmn2:sequenceFlow id="flow_j2" sourceRef="task_leader" targetRef="Gateway_join" />
```

### 4.3 包含网关 vs 排他网关 vs 并行网关

| 特性 | 排他网关 | 并行网关 | 包含网关 |
|------|---------|---------|---------|
| 执行路径 | 只走1条 | 全部走 | 满足条件的都走 |
| 条件表达式 | 必需 | 不需要 | 必需 |
| 汇聚行为 | 等1个 | 等全部 | 等所有已激活的 |
| 适用场景 | 二选一/多选一 | 同时并行 | 条件并行 |

---

## 5. 内嵌子流程（subProcess）

内嵌子流程在主流程 XML 内部定义，拥有自己的开始和结束事件。适用于将一组相关节点打包为一个整体。

### 5.1 基本结构

```xml
<bpmn2:subProcess id="subprocess_1" name="审批子流程">
  <bpmn2:incoming>Flow_in</bpmn2:incoming>
  <bpmn2:outgoing>Flow_out</bpmn2:outgoing>

  <!-- 子流程内部的开始事件 -->
  <bpmn2:startEvent id="sub_start" />

  <!-- 子流程内部的用户任务 -->
  <bpmn2:userTask id="sub_task1" name="经理审批" flowable:assignee="admin" />
  <bpmn2:userTask id="sub_task2" name="财务审批" flowable:candidateGroups="finance" />

  <!-- 子流程内部的结束事件 -->
  <bpmn2:endEvent id="sub_end" />

  <!-- 子流程内部的连线 -->
  <bpmn2:sequenceFlow id="sub_flow1" sourceRef="sub_start" targetRef="sub_task1" />
  <bpmn2:sequenceFlow id="sub_flow2" sourceRef="sub_task1" targetRef="sub_task2" />
  <bpmn2:sequenceFlow id="sub_flow3" sourceRef="sub_task2" targetRef="sub_end" />
</bpmn2:subProcess>
```

### 5.2 完整示例（来自生产环境：测试嵌套子流程）

```
开始 → 入职(admin) → [内嵌子流程: 开始 → 经理(qinfeng) → 财务(vue3角色) → 结束] → 人力(admin角色) → 结束
```

**布局说明：** 内嵌子流程在图形上展开显示（`isExpanded="true"`），需要为整个子流程框指定 Bounds。

```xml
<!-- 子流程 Shape（展开模式） -->
<bpmndi:BPMNShape id="shape_subprocess" bpmnElement="subprocess_1" isExpanded="true">
  <dc:Bounds x="280" y="45" width="650" height="185" />
</bpmndi:BPMNShape>
```

---

## 6. 调用子流程（callActivity）— 主子流程

调用子流程引用**另一个独立部署的流程定义**，主流程和子流程各自独立管理。

### 6.1 基本结构

```xml
<bpmn2:callActivity id="call_sub" name="调用子流程" calledElement="子流程的processKey">
  <bpmn2:extensionElements>
    <!-- 传入变量：主流程 → 子流程 -->
    <flowable:in source="applyUserId" target="applyUserId" />
    <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />

    <!-- 传出变量：子流程 → 主流程 -->
    <flowable:out source="applyUserId" target="applyUserId" />
  </bpmn2:extensionElements>
</bpmn2:callActivity>
```

### 6.2 必传变量

| 变量 | 方向 | 说明 |
|------|------|------|
| `applyUserId` | in + out | 流程发起人，子流程需要知道谁发起的 |
| `JG_LOCAL_PROCESS_ID` → `JG_SUB_MAIN_PROCESS_ID` | in | 主流程ID，子流程需要关联回主流程 |

### 6.3 完整示例（来自生产环境：出差申请主子流程）

```
开始 → 主管领导 → 部门领导 → 排他网关
  ├─ 预支借款 (travel_expenses_type=='1') → 借款申请 → callActivity(调用joa_loan子流程) → 归档 → 结束
  └─ 个人垫付 (travel_expenses_type=='2') → 归档 → 结束
```

```xml
<callActivity id="callSubProcess" name="" calledElement="joa_loan">
  <extensionElements>
    <flowable:in source="apply_no" target="id" />
    <flowable:in source="applyUserId" target="applyUserId" />
    <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />
    <flowable:out source="applyUserId" target="applyUserId" />
  </extensionElements>
</callActivity>
```

---

## 7. 会签子流程（callActivity + multiInstance）

会签子流程 = 调用子流程 + 多实例循环。每个审批人各执行一次完整的子流程。

### 7.1 结构

```xml
<bpmn2:callActivity id="call_countersign" name="会签子流程" calledElement="子流程processKey">
  <bpmn2:extensionElements>
    <flowable:in source="assigneeUserId" target="assigneeUserId" />
    <flowable:in source="applyUserId" target="applyUserId" />
    <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />
    <flowable:out source="applyUserId" target="applyUserId" />
  </bpmn2:extensionElements>

  <!-- 多实例循环：每个审批人执行一次子流程 -->
  <bpmn2:multiInstanceLoopCharacteristics
    isSequential="true"
    flowable:collection="${flowUtil.stringToList(assigneeUserIdList)}"
    flowable:elementVariable="assigneeUserId" />
</bpmn2:callActivity>
```

### 7.2 完整示例（来自生产环境：主流程会签主子流程）

```
开始 → 主流程经理审批(候选人) → callActivity(会签子流程, 顺序执行) → 主流程总监审批 → 结束
```

```xml
<callActivity id="callSubProcess" name="" calledElement="subflow">
  <extensionElements>
    <flowable:in source="assigneeUserId" target="assigneeUserId" />
    <flowable:in source="applyUserId" target="applyUserId" />
    <flowable:in source="JG_LOCAL_PROCESS_ID" target="JG_SUB_MAIN_PROCESS_ID" />
    <flowable:out source="applyUserId" target="applyUserId" />
  </extensionElements>
  <multiInstanceLoopCharacteristics
    isSequential="true"
    flowable:collection="${flowUtil.stringToList(assigneeUserIdList)}"
    flowable:elementVariable="assigneeUserId" />
</callActivity>
```

**关键区别：**
- 普通子流程：没有 `multiInstanceLoopCharacteristics`，只执行一次
- 会签子流程：有 `multiInstanceLoopCharacteristics`，按 `assigneeUserIdList` 中的人数循环执行

---

## 8. 分支条件表达式配置

### 8.1 排他网关条件

排他网关的每条出线都需要条件表达式（除了默认路径）：

```xml
<bpmn2:sequenceFlow id="flow_1" name="通过" sourceRef="gateway" targetRef="task_next">
  <bpmn2:conditionExpression xsi:type="tFormalExpression"><![CDATA[${result == 1}]]></bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
```

### 8.2 包含网关条件

包含网关的每条出线也需要条件表达式，可以多条同时满足：

```xml
<bpmn2:sequenceFlow id="flow_1" name="普通员工" sourceRef="igw" targetRef="task_a">
  <bpmn2:conditionExpression xsi:type="tFormalExpression">${user_type=='1'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
<bpmn2:sequenceFlow id="flow_2" name="全部" sourceRef="igw" targetRef="task_b">
  <bpmn2:conditionExpression xsi:type="tFormalExpression">${user_type=='1' || user_type=='2'}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
```

### 8.3 常用条件表达式写法

| 场景 | 表达式 |
|------|--------|
| 审批通过 | `${result == 1}` |
| 审批拒绝 | `${result == 0}` |
| 字段等于值 | `${field_name == 'value'}` |
| 字段不等于 | `${field_name != 'value'}` |
| 数值比较 | `${amount > 10000}` |
| 多条件 OR | `${type=='1' \|\| type=='2'}` |
| 多条件 AND | `${type=='1' && level=='high'}` |
| 布尔判断 | `${iz_danger == '1'}` |

> **注意：** `conditionExpression` 中使用 `xsi:type="tFormalExpression"`（排他网关）或 `xsi:type="bpmn2:tFormalExpression"`（新版设计器），两种都可用。
