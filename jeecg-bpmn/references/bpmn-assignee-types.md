# 审批人配置详解

JeecgBoot BPM 支持 7 种审批人配置方式，每种对应不同的 XML 属性组合。

## 1. 固定指定人（assignee）

最简单的方式，固定指定一个用户处理：

```xml
<bpmn2:userTask id="task_xxx" name="固定人审批" flowable:assignee="admin" />
```

## 2. 发起人/流程变量（表达式）

通过表达式动态获取审批人：

```xml
<!-- 流程发起人 -->
<bpmn2:userTask id="task_xxx" name="发起人提交" flowable:assignee="${applyUserId}" />

<!-- 部门负责人（自定义变量） -->
<bpmn2:userTask id="task_xxx" name="部门领导审批" flowable:assignee="${deptLeader}" />
```

## 3. 候选人（多人选一）— candidateUsers

多人中任一人可认领处理：

```xml
<bpmn2:userTask id="task_xxx" name="多人审批" flowable:candidateUsers="admin,jeecg,zhangsan" />
```

## 4. 角色审批 — candidateGroups + groupType="role"

按角色编码分配，角色下所有用户都可处理：

```xml
<bpmn2:userTask id="task_xxx" name="角色审批"
  flowable:candidateGroups="admin,jeecg"
  flowable:groupType="role" />
```

带跳过审批人配置（taskExtendJson）：
```xml
<bpmn2:userTask id="task_xxx" name="审批角色"
  flowable:candidateGroups="vue3,jeecg,admin"
  flowable:groupType="role">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{
      &quot;sameMode&quot;:0,
      &quot;isSkipAssigneeEmpty&quot;:false,
      &quot;isSkipAssigneeOnePersion&quot;:true,
      &quot;isSkipApproval&quot;:false,
      &quot;isAssignedByPreviousNode&quot;:false,
      &quot;isEmptyAssignedByPreviousNode&quot;:true
    }" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

## 5. 部门审批 — candidateGroups + groupType="dept"

按部门 ID 分配，部门下所有用户都可处理：

```xml
<bpmn2:userTask id="task_xxx" name="部门审批"
  flowable:candidateGroups="6d35e179cd814e3299bd588ea7daed3f,c6d7cb4deeac411cb3384b1b31278596"
  flowable:groupType="dept">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

## 6. 部门岗位审批 — candidateGroups + groupType="deptPosition"

按部门岗位 ID 分配审批人：

```xml
<bpmn2:userTask id="task_xxx" name="候选岗位审批"
  flowable:candidateGroups="2032392253970890754,2032395269063098370"
  flowable:groupType="deptPosition">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

## 7. 上一节点指派 — isAssignedByPreviousNode

由上一审批节点在完成时选择下一步处理人：

```xml
<bpmn2:userTask id="task_xxx" name="分配经理">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{
      &quot;sameMode&quot;:0,
      &quot;isSkipAssigneeEmpty&quot;:false,
      &quot;isSkipAssigneeOnePersion&quot;:false,
      &quot;isSkipApproval&quot;:false,
      &quot;isAssignedByPreviousNode&quot;:true,
      &quot;isEmptyAssignedByPreviousNode&quot;:false
    }" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

## 8. 职务级别审批 — groupType="position" + 表达式

通过表达式动态获取指定职务级别的用户：

```xml
<bpmn2:userTask id="task_xxx" name="职务级别审批"
  flowable:assignee="${assigneeUserId}"
  flowable:candidateUsers="${oaFlowExpression.getApplyUserDeptPositionLevel(sys_org_code, applyUserId, '岗位ID')}"
  flowable:groupType="position"
  flowable:countersignRule="countersign_proportion">
  ...
</bpmn2:userTask>
```

## 9. 表达式审批人 — Spring Bean 动态获取

系统提供 3 个 Spring Bean 用于通过表达式动态获取审批人，在 `flowable:candidateUsers` 或 `flowable:assignee` 中使用。

### 9.1 `flowNodeExecution` — 部门层级表达式

Bean 类：`org.jeecg.modules.expression.FlowNodeExecutionExpression`

| 表达式 | 说明 | 依赖变量 |
|--------|------|---------|
| `${flowNodeExecution.getDepartLeaders(execution)}` | 发起部门的部门负责人 | `sys_org_code` |
| `${flowNodeExecution.getLevel1DepartLeaders(execution)}` | 上一级部门负责人 | `sys_org_code` |
| `${flowNodeExecution.getLevel2DepartLeaders(execution)}` | 上二级部门负责人 | `sys_org_code` |
| `${flowNodeExecution.getLevel3DepartLeaders(execution)}` | 上三级部门负责人 | `sys_org_code` |
| `${flowNodeExecution.getUserSuperPositionLevel1(execution)}` | 发起人上一级岗位人员 | `applyUserId` + `sys_org_code` |
| `${flowNodeExecution.getUserSuperPositionLevel2(execution)}` | 发起人上两级岗位人员 | `applyUserId` + `sys_org_code` |
| `${flowNodeExecution.getUserSuperPositionLevel3(execution)}` | 发起人上三级岗位人员 | `applyUserId` + `sys_org_code` |

**用法示例：**
```xml
<bpmn2:userTask id="task_dept_leader" name="部门负责人审批"
  flowable:candidateUsers="${flowNodeExecution.getDepartLeaders(execution)}">
</bpmn2:userTask>
```

### 9.2 `oaUtil` — 流程上下文表达式

Bean 类：`org.jeecg.modules.expression.OaUtilExpression`

**办理人表达式：**

| 表达式 | 说明 |
|--------|------|
| `${oaUtil.getLastTaskAssignee(execution)}` | 获取上一节点处理人用户名（排除加签节点，支持驳回场景） |
| `${oaUtil.getLastTaskAssigneePositionLevel1(execution)}` | 上一节点处理人的上一级岗位人员（支持会签节点） |

**条件分支表达式（用于 sequenceFlow 的 conditionExpression）：**

| 表达式 | 说明 | 操作符 |
|--------|------|--------|
| `${oaUtil.branchConditionByPost('eq',applyUserId,'部长')}` | 按发起人职务判断 | eq=等于, ne=不等于 |
| `${oaUtil.branchConditionByOrg('eq',sys_org_code,'A01A01')}` | 按发起人部门编码判断 | eq=等于, ne=不等于 |

**上一节点处理人条件判断写法：**
```xml
<!-- 等于 -->
<conditionExpression>${oaUtil.getLastTaskAssignee(execution) == 'zhangsan'}</conditionExpression>
<!-- 不等于 -->
<conditionExpression>${oaUtil.getLastTaskAssignee(execution) != 'zhangsan'}</conditionExpression>
<!-- in（属于多人之一） -->
<conditionExpression>${'zhangsan,lisi'.contains(oaUtil.getLastTaskAssignee(execution))}</conditionExpression>
<!-- not in -->
<conditionExpression>${!'zhangsan,lisi'.contains(oaUtil.getLastTaskAssignee(execution))}</conditionExpression>
```

### 9.3 `oaFlowExpression` — 职级审批表达式

Bean 类：`org.jeecg.modules.extbpm.process.common.expression.OaFlowExpression`

| 表达式 | 说明 |
|--------|------|
| `${oaFlowExpression.getApplyUserDeptPositionLevel(sys_org_code, applyUserId, 'targetPositionId')}` | 按职级查找审批人（见下方4种规则） |
| `${oaFlowExpression.getUserSuperPositionLevel1(applyUserId)}` | 发起人上一级岗位人员（按用户名，不需要 execution） |
| `${oaFlowExpression.getUserSuperPositionLevel2(applyUserId)}` | 发起人上两级岗位人员 |
| `${oaFlowExpression.getUserSuperPositionLevel3(applyUserId)}` | 发起人上三级岗位人员 |

**`getApplyUserDeptPositionLevel` 4种规则：**

| 发起人职级 | 目标职级 | 行为 |
|-----------|---------|------|
| 职员层（职员/部长/副部长） | 职员层 | 查发起人所在部门下对应职级人员 |
| 职员层 | 领导层（董事长/总经理/副总经理） | 查发起人所在公司领导班子中对应职级 |
| 领导层 | 职员层 | 返回空（领导不需要职员审批） |
| 领导层 | 领导层 | 查当前领导班子中对应职级 |

**用法示例（配合 groupType="position"）：**
```xml
<bpmn2:userTask id="task_position" name="职级审批"
  flowable:candidateUsers="${oaFlowExpression.getApplyUserDeptPositionLevel(sys_org_code, applyUserId, '1958471111989067778')}"
  flowable:groupType="position">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

### 9.4 条件评估工具类

`org.jeecg.modules.expression.util.EvalConditionUtils` 提供条件评估：

| 操作符 | 含义 | 支持类型 |
|--------|------|---------|
| `eq` | 等于（忽略大小写） | String / Set<String>（任一匹配） |
| `ne` | 不等于（忽略大小写） | String / Set<String>（全部不匹配） |

---

## 10. groupType 完整速查表

| groupType 值 | 含义 | candidateGroups 值 | 说明 |
|-------------|------|-------------------|------|
| `role` | 系统角色 | 角色编码（逗号分隔） | `jeecg,noticeReviewer` |
| `approvalRole` | 审批角色 | 审批角色编码（逗号分隔） | 独立于系统角色的审批专用角色 |
| `dept` | 部门 | 部门ID（逗号分隔） | `6d35e179cd814e3299bd588ea7daed3f` |
| `deptPosition` | 部门岗位 | 岗位ID（逗号分隔） | `2032392253970890754,2032395269063098370` |
| `position` | 职务级别 | 通过表达式获取 | 配合 `oaFlowExpression` 使用 |
| `formData` | 表单数据 | 从表单字段动态获取 | 用户选择控件的值作为审批人 |
| _(无)_ | 指定人/候选人 | 不使用 candidateGroups | 用 `assignee` 或 `candidateUsers` |

## 11. 审批人数据来源表

生成流程时，如需查询实际的角色编码、用户名、部门ID，可查询以下系统表：

| 数据 | 表名 | 关键字段 | 查询示例 |
|------|------|---------|---------|
| 角色编码 | `sys_role` | `role_code` | `SELECT role_code, role_name FROM sys_role` |
| 用户名 | `sys_user` | `username` | `SELECT username, realname FROM sys_user` |
| 部门ID | `sys_depart` | `id` | `SELECT id, depart_name FROM sys_depart` |

**sys_depart.org_category 机构类别：**

| 值 | 含义 | 用途 |
|----|------|------|
| `1` | 公司 | 顶级组织 |
| `2` | 部门 | `groupType="dept"` 时使用部门ID |
| `3` | 岗位 | `groupType="deptPosition"` 时使用岗位ID |
| `4` | 子公司 | 子组织 |

## 12. 草稿节点（驳回到发起人）— assignee + sameMode:2

草稿节点用于"驳回到发起人"场景：流程被驳回后，发起人可修改数据并重新提交。

**核心特征：**
- `flowable:assignee="${applyUserId}"` — 指定发起人
- `sameMode: 2` — 特殊模式，标记为草稿/首节点
- `TaskCreatedAutoSubmitListener` — 首次提交时自动跳过此节点（首节点自动提交），驳回后才需要手动操作
- `TaskSkipApprovalListener` — 标准跳过审批监听器

```xml
<bpmn2:userTask id="task_draft" name="草稿" flowable:assignee="${applyUserId}">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:2,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:false,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskCreatedAutoSubmitListener" event="create" id="9c3064baa7074eab62e3c5b3b5458691" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

> **使用场景：** 在"驳回到发起人"流程模式中，将此节点放在开始事件之后。首次发起流程时，此节点会被 `TaskCreatedAutoSubmitListener` 自动跳过；当审批被驳回到此节点时，发起人需要手动修改数据后重新提交。

## 13. 完整参考示例 — 所有审批人类型串联

以下是一个包含所有审批人配置类型的完整流程 XML（来自生产环境）：

```
开始 → 指定人(jeecg) → 候选多人(admin,jeecg) → 角色(jeecg,noticeReviewer)
     → 部门(两个部门ID) → 候选岗位(两个岗位ID) → 职级(表达式)
     → 会签固定人员(jeecg,qinfeng, 全部通过) → 结束
```

**关键 XML 片段：**

```xml
<!-- 1. 指定人 -->
<bpmn2:userTask id="Task_04woce4" name="指定人" flowable:assignee="jeecg" />

<!-- 2. 候选多人 -->
<bpmn2:userTask id="Task_1k76zxi" name="指定多人(候选多人)" flowable:candidateUsers="admin,jeecg">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>

<!-- 3. 角色 -->
<bpmn2:userTask id="Task_0gm5nm0" name="角色"
  flowable:candidateGroups="jeecg,noticeReviewer" flowable:groupType="role">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>

<!-- 4. 部门 -->
<bpmn2:userTask id="Task_0hre67h" name="部门"
  flowable:candidateGroups="6d35e179cd814e3299bd588ea7daed3f,c6d7cb4deeac411cb3384b1b31278596"
  flowable:groupType="dept">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>

<!-- 5. 候选岗位 -->
<bpmn2:userTask id="Task_0d9ubtz" name="候选岗位"
  flowable:candidateGroups="2032392253970890754,2032395269063098370"
  flowable:groupType="deptPosition">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>

<!-- 6. 职级 -->
<bpmn2:userTask id="Task_1euf9po" name="职级"
  flowable:candidateUsers="${oaFlowExpression.getApplyUserDeptPositionLevel(sys_org_code, applyUserId, '1958471111989067778')}"
  flowable:groupType="position">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:true,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:true,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
  </bpmn2:extensionElements>
</bpmn2:userTask>

<!-- 7. 会签固定人员（全部通过） -->
<bpmn2:userTask id="Task_1tj90vc" name="会签固定人员"
  flowable:assignee="${assigneeUserId}" flowable:countersignRule="countersign_all">
  <bpmn2:extensionElements>
    <flowable:taskExtendJson value="{&quot;sameMode&quot;:0,&quot;isSkipAssigneeEmpty&quot;:false,&quot;isSkipAssigneeOnePersion&quot;:false,&quot;isSkipApproval&quot;:false,&quot;isAssignedByPreviousNode&quot;:false,&quot;isEmptyAssignedByPreviousNode&quot;:false,&quot;isSkipApprovedOnCountersignReturn&quot;:false}" />
    <flowable:taskListener class="org.jeecg.modules.extbpm.listener.task.TaskSkipApprovalListener" event="create" />
    <flowable:taskCountersignExtendJson value="eyJhdWRpdG9yVXNlclR5cGUiOiJjYW5kaWRhdGVVc2VycyIsImF1ZGl0b3JVc2VySWRzIjpbImplZWNnIiwicWluZmVuZyJdLCJ0aW1lc3RhbXAiOjE3NzM0MTU4NTkwMTZ9" />
  </bpmn2:extensionElements>
  <bpmn2:multiInstanceLoopCharacteristics
    flowable:collection="${flowUtil.stringToList('jeecg,qinfeng')}"
    flowable:elementVariable="assigneeUserId">
    <bpmn2:completionCondition xsi:type="bpmn2:tFormalExpression">
      ${nrOfCompletedInstances/nrOfInstances==1}
    </bpmn2:completionCondition>
  </bpmn2:multiInstanceLoopCharacteristics>
</bpmn2:userTask>
```
