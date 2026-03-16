# 条件表达式、抄送、按钮与服务任务

## 1. 条件表达式系统（来自设计器源码）

### 1.1 系统内置变量（可用于网关条件）

| 变量名 | 含义 | 用法示例 |
|--------|------|---------|
| `applyUserId` | 发起人用户名 | `${applyUserId == 'admin'}` |
| `applyUserDept` | 发起人部门 | `${applyUserDept == '部门ID'}` |
| `applyUserDeptManager` | 发起部门负责人 | `${applyUserDeptManager == 'username'}` |
| `applyUserParentDeptManager` | 上级部门负责人 | 同上 |
| `lastAssignee` | 上个节点处理人 | `${lastAssignee == 'admin'}` |
| `applyUserPostLevel` | 发起人职级 | `${applyUserPostLevel == '职级ID'}` |
| `applyUserApprovalRole` | 发起人审批角色 | `${applyUserApprovalRole == '角色ID'}` |
| `applyDate` | 发起日期 | `${applyDate > '2026-01-01'}` |
| `result` | 审批结果 | `${result == 1}` 通过 / `${result == 0}` 拒绝 |

### 1.2 条件运算符

| 运算符 | 含义 | 适用类型 |
|--------|------|---------|
| `eq` / `==` | 等于 | 字符串、数字、日期 |
| `ne` / `!=` | 不等于 | 字符串、数字、日期 |
| `gt` / `>` | 大于 | 数字、日期 |
| `gte` / `>=` | 大于等于 | 数字、日期 |
| `lt` / `<` | 小于 | 数字、日期 |
| `lte` / `<=` | 小于等于 | 数字、日期 |
| `in` | 在列表中 | 字符串、数字 |
| `not_in` | 不在列表中 | 字符串、数字 |
| `contains` | 包含 | 字符串 |
| `is_empty` | 为空 | 字符串、数字、文件 |
| `is_not_empty` | 不为空 | 字符串、数字、文件 |
| `is_department_manager` | 是部门负责人 | applyUserId, lastAssignee |
| `is_not_department_manager` | 不是部门负责人 | applyUserId, lastAssignee |

---

## 2. 抄送配置（CcConfigJson）

用户任务可配置抄送人，通知相关人员但不影响审批流程：

```xml
<bpmn2:userTask id="task_xxx" name="审批">
  <bpmn2:extensionElements>
    <flowable:CcConfigJson value="${BASE64_ENCODED_JSON}" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

### 抄送类型

| 类型 | 说明 |
|------|------|
| `candidateUsers` | 指定人 |
| `candidateRoles` | 指定角色 |
| `candidateDeptPositions` | 指定岗位 |
| `submitter_user` | 提交人本人 |
| `submitter_dept_leader` | 提交人部门负责人 |
| `submitter_parent_dept_leader` | 上级部门负责人 |
| `dept_members` | 本部门成员 |
| `dept_leader` | 部门负责人 |

---

## 3. 自定义按钮（Button）

用户任务可配置自定义操作按钮：

```xml
<bpmn2:userTask id="task_xxx" name="审批">
  <bpmn2:extensionElements>
    <flowable:Button id="btn_1" name="同意" code="approve" isHide="0" next="task_next" sort="1" />
    <flowable:Button id="btn_2" name="拒绝" code="reject" isHide="0" next="end" sort="2" />
    <flowable:Button id="btn_3" name="转办" code="transfer" isHide="0" sort="3" />
  </bpmn2:extensionElements>
</bpmn2:userTask>
```

| 属性 | 说明 |
|------|------|
| `id` | 按钮唯一ID |
| `name` | 显示名称 |
| `code` | 按钮编码标识 |
| `isHide` | 是否隐藏（0=显示，1=隐藏） |
| `next` | 点击后跳转的目标节点ID |
| `sort` | 显示排序 |

---

## 4. 服务任务（ServiceTask）

### 4.1 API 服务任务

自动调用外部 HTTP 接口：

```xml
<bpmn2:serviceTask id="service_api" name="调用外部接口"
  flowable:class="org.jeecg.modules.extbpm.listener.service.ApiServiceTaskDelegate">
  <bpmn2:extensionElements>
    <flowable:ApiServiceTaskConfig value="${BASE64_ENCODED_JSON}" />
  </bpmn2:extensionElements>
</bpmn2:serviceTask>
```

ApiServiceTaskConfig JSON 结构：
```json
{
  "apiUrl": "https://api.example.com/endpoint",
  "method": "GET|POST",
  "headers": {},
  "parameters": {},
  "timeout": 30000,
  "retryCount": 0
}
```

### 4.2 AI 服务任务

调用 AI 大模型进行智能处理：

```xml
<bpmn2:serviceTask id="service_ai" name="AI智能处理"
  flowable:class="org.jeecg.modules.extbpm.listener.service.AigcServiceTaskDelegate">
  <bpmn2:extensionElements>
    <flowable:AiServiceTaskConfig value="${BASE64_ENCODED_JSON}" />
  </bpmn2:extensionElements>
</bpmn2:serviceTask>
```

AiServiceTaskConfig JSON 结构：
```json
{
  "aiFlowId": "AI对话流ID",
  "inputParams": {},
  "outputParams": {}
}
```

---

## 5. 设计器 API 端点一览

| API 路径 | 用途 |
|----------|------|
| `act/designer/api/saveProcess` | 保存/新建流程 |
| `act/designer/api/getProcessXml` | 获取流程 XML |
| `act/designer/api/getTypes` | 获取流程类型列表 |
| `act/designer/api/getPageUsers` | 获取用户列表（审批人选择） |
| `act/designer/api/getGroups` | 获取角色/组列表 |
| `act/designer/api/getRoleNameByCodes` | 根据角色编码获取名称 |
| `act/designer/api/getExpressions` | 获取可用表达式列表 |
| `act/designer/api/getListenersByType` | 获取监听器列表 |
| `sys/sysDepart/queryDepartAndPostTreeSync` | 获取部门+岗位树 |
| `sys/position/list` | 获取职级列表 |
