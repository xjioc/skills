# BPMN XML 骨架与基本节点模板

## 1. XML 骨架模板

所有生成的 BPMN XML 必须使用以下骨架：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions
  xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  xmlns:flowable="http://flowable.org/bpmn"
  id="sample-diagram"
  targetNamespace="http://bpmn.io/schema/bpmn"
  xsi:schemaLocation="http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd">

  <bpmn2:process id="${PROCESS_KEY}" name="${PROCESS_NAME}">
    <!-- 必需的监听器 -->
    <bpmn2:extensionElements>
      <flowable:executionListener class="org.jeecg.modules.extbpm.listener.execution.ProcessEndListener" event="end" />
      <flowable:eventListener class="org.jeecg.modules.listener.tasktip.TaskCreateGlobalListener" />
    </bpmn2:extensionElements>

    <!-- 节点定义区 -->
    ${NODES}

    <!-- 连线定义区 -->
    ${SEQUENCE_FLOWS}
  </bpmn2:process>

  <!-- 图形布局区 -->
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="${PROCESS_KEY}">
      ${SHAPES_AND_EDGES}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>
```

## 2. 节点 XML 模板

### 2.1 开始节点（必需）

```xml
<bpmn2:startEvent id="start" name="开始" flowable:initiator="applyUserId" />
```

### 2.2 结束节点（必需）

**普通结束节点：**
```xml
<bpmn2:endEvent id="end" name="结束" />
```

**带监听器的结束节点（如需在结束时触发业务逻辑）：**
```xml
<bpmn2:endEvent id="End_reject">
  <bpmn2:extensionElements>
    <flowable:executionListener expression="${myListener.onReject(execution)}" event="start" />
  </bpmn2:extensionElements>
</bpmn2:endEvent>
```

> 一个流程可以有多个结束节点（如"同意结束"和"拒绝结束"各一个），每个可挂不同监听器。

### 2.3 用户任务（userTask）

```xml
<!-- 指定人 -->
<bpmn2:userTask id="task_xxx" name="节点名称" flowable:assignee="username" />

<!-- 候选人（多人） -->
<bpmn2:userTask id="task_xxx" name="节点名称" flowable:candidateUsers="user1,user2" />

<!-- 候选角色组 -->
<bpmn2:userTask id="task_xxx" name="节点名称" flowable:candidateGroups="roleCode" />

<!-- 表达式（动态） -->
<bpmn2:userTask id="task_xxx" name="节点名称" flowable:assignee="${variableName}" />

<!-- 发起人 -->
<bpmn2:userTask id="task_xxx" name="节点名称" flowable:assignee="${applyUserId}" />
```

### 2.4 排他网关（exclusiveGateway）

```xml
<bpmn2:exclusiveGateway id="gateway_xxx" name="网关名称" />
```

带条件的连线：
```xml
<bpmn2:sequenceFlow id="flow_xxx" name="通过" sourceRef="gateway_xxx" targetRef="task_yyy">
  <bpmn2:conditionExpression xsi:type="tFormalExpression"><![CDATA[${result == 1}]]></bpmn2:conditionExpression>
</bpmn2:sequenceFlow>

<bpmn2:sequenceFlow id="flow_xxx" name="拒绝" sourceRef="gateway_xxx" targetRef="end">
  <bpmn2:conditionExpression xsi:type="tFormalExpression"><![CDATA[${result == 0}]]></bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
```

### 2.5 并行网关（parallelGateway）

并行网关需要成对使用（分支 + 汇聚）：

```xml
<!-- 并行分支 -->
<bpmn2:parallelGateway id="gateway_fork" name="并行开始" />

<!-- 并行汇聚 -->
<bpmn2:parallelGateway id="gateway_join" name="并行汇聚" />
```

### 2.6 普通连线（sequenceFlow）

```xml
<bpmn2:sequenceFlow id="flow_xxx" name="" sourceRef="nodeA" targetRef="nodeB" />
```
