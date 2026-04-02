"""
JeecgBoot 系统主数据工具库

提供角色、用户、部门、字典等主数据的查询和创建功能。
遵循"先查后建"原则：优先使用系统已有数据，没有才创建。

用法:
    from system_utils import *
    init_api('https://boot3.jeecg.com/jeecgboot', 'your-token')

    # 查询
    roles = query_roles()
    users = query_users(keyword='张')
    depts = query_depts()
    dict_items = query_dict('sex')
    dicts = search_dict('请假')

    # 查找或创建
    role_code = find_or_create_role('经理', 'manager')
    dict_code = find_or_create_dict('leave_type', '请假类型', [
        {'value': '1', 'text': '事假'},
        {'value': '2', 'text': '病假'},
    ])
"""

import urllib.request
import urllib.parse
import json
import sys
import time

# 修复 Windows 控制台中文乱码
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# ====== 全局配置 ======
_API_BASE = ''
_TOKEN = ''


def init_api(api_base, token):
    """初始化 API 地址和 Token"""
    global _API_BASE, _TOKEN
    _API_BASE = api_base.rstrip('/')
    _TOKEN = token


def _request(path, data=None, method='GET', content_type='application/json'):
    """通用 HTTP 请求"""
    url = f'{_API_BASE}{path}'
    headers = {
        'X-Access-Token': _TOKEN,
        'Content-Type': f'{content_type}; charset=UTF-8',
    }
    if data is not None and method in ('POST', 'PUT'):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'[system_utils] 请求失败: {url} -> {e}')
        return {'success': False, 'message': str(e)}


# ====== 角色 ======

def query_roles(keyword=None, page_size=100):
    """
    查询角色列表。
    返回: [{'roleCode': 'admin', 'roleName': '管理员', 'id': '...'}, ...]
    """
    params = f'pageNo=1&pageSize={page_size}'
    if keyword:
        params += f'&roleName={urllib.parse.quote(keyword)}'
    result = _request(f'/sys/role/list?{params}')
    if result.get('success') and result.get('result'):
        return result['result'].get('records', [])
    return []


def find_role(keyword):
    """
    按名称或编码模糊查找角色。
    返回: {'roleCode': '...', 'roleName': '...', 'id': '...'} 或 None
    """
    roles = query_roles(keyword)
    if not roles:
        # 尝试按编码精确匹配
        all_roles = query_roles()
        for r in all_roles:
            if r.get('roleCode', '').lower() == keyword.lower():
                return r
            if keyword.lower() in r.get('roleName', '').lower():
                return r
        return None
    return roles[0]


def create_role(role_name, role_code, description='', add_admin=True):
    """
    创建系统角色，返回角色信息。
    add_admin=True 时自动将 admin 用户加入角色（默认开启）。
    """
    data = {
        'roleName': role_name,
        'roleCode': role_code,
        'description': description or f'由AI自动创建: {role_name}',
    }
    result = _request('/sys/role/add', data=data, method='POST')
    if result.get('success'):
        print(f'[角色] 创建成功: {role_name} ({role_code})')
        found = find_role(role_code)
        # 自动绑定 admin
        if add_admin and found:
            add_users_to_role(found['id'], ['e9ca23d68d884d4ebb19d07889727dae'])
        return found
    else:
        print(f'[角色] 创建失败: {result.get("message", "")}')
        return None


def add_users_to_role(role_id, user_ids):
    """
    将用户绑定到系统角色。
    role_id: 角色ID
    user_ids: 用户ID列表（注意是ID，不是username）
    """
    data = {'roleId': role_id, 'userIdList': user_ids}
    result = _request('/sys/user/addSysUserRole', data=data, method='POST')
    if result.get('success'):
        print(f'[角色] 绑定用户成功: roleId={role_id}, users={user_ids}')
    else:
        print(f'[角色] 绑定用户失败: {result.get("message", "")}')
    return result.get('success', False)


def find_or_create_role(role_name, role_code=None, add_admin=True):
    """
    查找角色，不存在则创建（并自动绑定 admin）。
    返回 role_code 字符串。
    """
    # 先按名称查找
    found = find_role(role_name)
    if found:
        code = found.get('roleCode', '')
        print(f'[角色] 已存在: {found.get("roleName")} ({code})')
        return code

    # 按编码查找
    if role_code:
        found = find_role(role_code)
        if found:
            code = found.get('roleCode', '')
            print(f'[角色] 已存在: {found.get("roleName")} ({code})')
            return code

    # 创建新角色
    code = role_code or role_name.lower().replace(' ', '_')
    created = create_role(role_name, code, add_admin=add_admin)
    return code if created else None


# ====== 审批角色 ======

def query_approval_roles(keyword=''):
    """
    查询审批角色列表（search接口）。
    返回: {'roles': [...], 'persons': [...]}
    """
    params = f'keyword={urllib.parse.quote(keyword)}&onlyRoles=true'
    result = _request(f'/sys/approvalRole/search?{params}')
    if result.get('success'):
        return result.get('result', {})
    return {'roles': [], 'persons': []}


def find_approval_role(keyword):
    """
    按名称查找审批角色。
    返回: {'id': '...', 'name': '...', 'pid': '...'} 或 None
    """
    res = query_approval_roles(keyword)
    roles = res.get('roles', [])
    for r in roles:
        if keyword.lower() in r.get('name', '').lower():
            return r
    return None


def create_approval_role_group(group_name):
    """
    创建审批角色分组。
    返回: group_id 字符串 或 None
    """
    result = _request('/sys/approvalRole/group/add', data={'name': group_name, 'pid': '0'}, method='POST')
    if result.get('success'):
        print(f'[审批角色] 分组创建成功: {group_name}')
        # 查询分组ID
        r2 = _request('/sys/approvalRole/rootList?pageNo=1&pageSize=100')
        for rec in (r2.get('result') or {}).get('records', []):
            if rec.get('name') == group_name:
                return rec['id']
    else:
        print(f'[审批角色] 分组创建失败: {result.get("message", "")}')
    return None


def create_approval_role(role_name, group_id, add_admin=True):
    """
    在指定分组下创建审批角色，并可自动绑定 admin。
    返回: role_id 字符串 或 None
    """
    result = _request('/sys/approvalRole/role/add', data={'name': role_name, 'pid': group_id}, method='POST')
    if result.get('success'):
        print(f'[审批角色] 创建成功: {role_name}')
        # 查询角色ID
        r2 = _request(f'/sys/approvalRole/childList?pid={group_id}')
        role_id = None
        for c in (r2.get('result') or {}).get('records', []):
            if c.get('name') == role_name:
                role_id = c['id']
                break
        if role_id and add_admin:
            # 获取 admin 用户ID
            admin = find_user('admin')
            if admin:
                add_users_to_approval_role(role_id, [admin['id']])
        return role_id
    else:
        print(f'[审批角色] 创建失败: {result.get("message", "")}')
        return None


def add_users_to_approval_role(role_id, user_ids, biz_scope='all'):
    """
    将用户绑定到审批角色。
    user_ids: 用户ID列表
    biz_scope: 'all'=全部部门, 'org'=指定部门
    """
    data = {
        'approvalRoleId': role_id,
        'userIds': user_ids,
        'bizScope': biz_scope,
        'includeSub': 0,
    }
    result = _request('/sys/approvalRoleUser/add', data=data, method='POST')
    if result.get('success'):
        print(f'[审批角色] 绑定用户成功: roleId={role_id}, users={user_ids}')
    else:
        print(f'[审批角色] 绑定用户失败: {result.get("message", "")}')
    return result.get('success', False)


def find_or_create_approval_role(role_name, group_name='默认分组', add_admin=True):
    """
    查找审批角色，不存在则创建（自动创建分组 + 角色 + 绑定 admin）。
    返回: role_id 字符串 或 None
    """
    # 先查找
    found = find_approval_role(role_name)
    if found:
        print(f'[审批角色] 已存在: {found.get("name")} (id={found.get("id")})')
        return found['id']

    # 查找或创建分组
    r = _request('/sys/approvalRole/rootList?pageNo=1&pageSize=100')
    group_id = None
    for rec in (r.get('result') or {}).get('records', []):
        if rec.get('name') == group_name:
            group_id = rec['id']
            break
    if not group_id:
        group_id = create_approval_role_group(group_name)
    if not group_id:
        return None

    return create_approval_role(role_name, group_id, add_admin=add_admin)


# ====== 用户 ======

def query_users(keyword=None, username=None, page_size=100):
    """
    查询用户列表。
    返回: [{'username': 'admin', 'realname': '管理员', 'id': '...'}, ...]
    """
    params = f'pageNo=1&pageSize={page_size}'
    if keyword:
        params += f'&realname={urllib.parse.quote(keyword)}'
    if username:
        params += f'&username={urllib.parse.quote(username)}'
    result = _request(f'/sys/user/list?{params}')
    if result.get('success') and result.get('result'):
        return result['result'].get('records', [])
    return []


def find_user(keyword):
    """
    按用户名或真实姓名查找用户。
    返回: {'username': '...', 'realname': '...', 'id': '...'} 或 None
    """
    # 先按用户名精确查
    users = query_users(username=keyword)
    if users:
        return users[0]
    # 再按姓名模糊查
    users = query_users(keyword=keyword)
    if users:
        return users[0]
    return None


# ====== 部门 ======

def query_depts(keyword=None):
    """
    查询部门树。
    返回: 部门树结构列表
    """
    result = _request('/sys/sysDepart/queryTreeList')
    if result.get('success'):
        depts = result.get('result', [])
        if keyword:
            return _filter_dept_tree(depts, keyword)
        return depts
    return []


def _filter_dept_tree(depts, keyword):
    """递归过滤部门树"""
    matched = []
    for d in depts:
        name = d.get('departName', '')
        if keyword.lower() in name.lower():
            matched.append(d)
        children = d.get('children', [])
        if children:
            matched.extend(_filter_dept_tree(children, keyword))
    return matched


def find_dept(keyword):
    """
    按名称查找部门。
    返回: {'id': '...', 'departName': '...', 'orgCode': '...'} 或 None
    """
    depts = query_depts(keyword)
    return depts[0] if depts else None


def query_dept_positions(dept_id=None):
    """
    查询部门+岗位树（用于流程审批人配置）。
    返回: 树结构
    """
    params = ''
    if dept_id:
        params = f'?departId={dept_id}'
    result = _request(f'/sys/sysDepart/queryDepartAndPostTreeSync{params}')
    if result.get('success'):
        return result.get('result', [])
    return []


# ====== 字典 ======

def query_dict(dict_code):
    """
    查询字典项列表。
    返回: [{'value': '1', 'text': '男'}, {'value': '2', 'text': '女'}]
    """
    result = _request(f'/sys/dict/getDictItems/{urllib.parse.quote(dict_code)}')
    if result.get('success'):
        return result.get('result', [])
    return []


def search_dict(keyword, page_size=50):
    """
    按名称或编码模糊搜索字典。
    返回: [{'dictCode': 'sex', 'dictName': '性别', 'id': '...'}, ...]
    """
    params = f'pageNo=1&pageSize={page_size}'
    if keyword:
        params += f'&dictName={urllib.parse.quote(keyword)}'
    result = _request(f'/sys/dict/list?{params}')
    if result.get('success') and result.get('result'):
        records = result['result'].get('records', [])
        # 也按编码匹配
        if not records:
            params2 = f'pageNo=1&pageSize={page_size}&dictCode={urllib.parse.quote(keyword)}'
            result2 = _request(f'/sys/dict/list?{params2}')
            if result2.get('success') and result2.get('result'):
                records = result2['result'].get('records', [])
        return records
    return []


def find_dict(keyword):
    """
    按名称或编码查找字典。
    返回: {'dictCode': '...', 'dictName': '...', 'id': '...', 'items': [...]} 或 None
    """
    # 先按编码精确查
    items = query_dict(keyword)
    if items:
        dicts = search_dict(keyword)
        d = dicts[0] if dicts else {'dictCode': keyword, 'dictName': keyword}
        d['items'] = items
        return d
    # 再按名称模糊查
    dicts = search_dict(keyword)
    if dicts:
        d = dicts[0]
        d['items'] = query_dict(d['dictCode'])
        return d
    return None


def create_dict(dict_code, dict_name, items, description=''):
    """
    创建字典及字典项。
    items: [{'value': '1', 'text': '事假'}, ...]
    返回: dict_code
    """
    # 创建字典
    data = {
        'dictCode': dict_code,
        'dictName': dict_name,
        'description': description or f'由AI自动创建: {dict_name}',
    }
    result = _request('/sys/dict/add', data=data, method='POST')
    if not result.get('success'):
        print(f'[字典] 创建失败: {result.get("message", "")}')
        return None

    print(f'[字典] 创建成功: {dict_name} ({dict_code})')

    # 查询字典 ID
    dicts = search_dict(dict_code)
    dict_id = dicts[0]['id'] if dicts else None

    if dict_id and items:
        for i, item in enumerate(items):
            item_data = {
                'dictId': dict_id,
                'itemText': item.get('text', item.get('label', '')),
                'itemValue': str(item.get('value', '')),
                'sortOrder': i + 1,
                'status': 1,
            }
            item_result = _request('/sys/dictItem/add', data=item_data, method='POST')
            if item_result.get('success'):
                print(f'  字典项: {item_data["itemText"]} = {item_data["itemValue"]}')
            else:
                print(f'  字典项失败: {item_result.get("message", "")}')

    return dict_code


def find_or_create_dict(dict_code, dict_name=None, items=None):
    """
    查找字典，不存在则创建。
    返回 dict_code 字符串。
    """
    found = find_dict(dict_code)
    if found:
        print(f'[字典] 已存在: {found.get("dictName")} ({found.get("dictCode")}), {len(found.get("items", []))} 项')
        return found['dictCode']

    # 按名称再搜一次
    if dict_name:
        found = find_dict(dict_name)
        if found:
            print(f'[字典] 已存在: {found.get("dictName")} ({found.get("dictCode")}), {len(found.get("items", []))} 项')
            return found['dictCode']

    # 创建
    if items:
        return create_dict(dict_code, dict_name or dict_code, items)
    else:
        print(f'[字典] 未找到 {dict_code}，且未提供字典项，无法创建')
        return None


# ====== 便捷打印 ======

def print_roles(keyword=None):
    """打印角色列表"""
    roles = query_roles(keyword)
    print(f'\n--- 角色列表 ({len(roles)} 条) ---')
    for r in roles:
        print(f'  {r.get("roleCode", ""):20s} | {r.get("roleName", "")}')
    return roles


def print_users(keyword=None):
    """打印用户列表"""
    users = query_users(keyword)
    print(f'\n--- 用户列表 ({len(users)} 条) ---')
    for u in users:
        print(f'  {u.get("username", ""):20s} | {u.get("realname", "")}')
    return users


def print_depts(keyword=None):
    """打印部门列表"""
    depts = query_depts(keyword)
    print(f'\n--- 部门列表 ({len(depts)} 条) ---')

    def _print_tree(nodes, indent=0):
        for d in nodes:
            name = d.get('departName', '')
            did = d.get('id', '')[:12]
            cat = d.get('orgCategory', '')
            cat_label = {'1': '公司', '2': '部门', '3': '岗位', '4': '子公司'}.get(str(cat), '')
            print(f'  {"  " * indent}{name} ({cat_label}) id={did}...')
            children = d.get('children', [])
            if children:
                _print_tree(children, indent + 1)

    _print_tree(depts)
    return depts


def print_dict(dict_code):
    """打印字典项"""
    items = query_dict(dict_code)
    print(f'\n--- 字典 {dict_code} ({len(items)} 项) ---')
    for item in items:
        print(f'  {item.get("value", ""):10s} | {item.get("text", "")}')
    return items


def print_dicts(keyword=None):
    """搜索并打印字典列表"""
    dicts = search_dict(keyword) if keyword else search_dict('')
    print(f'\n--- 字典列表 ({len(dicts)} 条) ---')
    for d in dicts:
        print(f'  {d.get("dictCode", ""):30s} | {d.get("dictName", "")}')
    return dicts
