"""
JeecgBoot 表单设计器（desform）通用工具库
==========================================
提供 API 调用、控件工厂、表单组装、菜单SQL生成等共通功能。

使用示例:
    from desform_utils import *
    init_api('https://boot3.jeecg.com/jeecgboot', 'your-token')
    form_id, uc = find_or_create_form('Customer Info', 'customer_info')
    widgets = [
        INPUT('客户名称', required=True),
        PHONE('电话'),
        SELECT('类型', options=['企业', '个人']),
    ]
    save_design(form_id, 'customer_info', widgets, title_index=0, update_count=uc)
"""

import urllib.request
import json
import time
import random
import ssl
import uuid
import sys

# Windows 控制台中文乱码修复：强制 UTF-8 输出
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# 全局配置
# ============================================================
_API_BASE = ''
_TOKEN = ''
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# 固定角色ID（用于授权SQL）
ROLE_ID = 'f6817f48af4fb3af11b9e8bf182f618b'

# 表单缓存: {code: {'id': str, 'uc': int}}
_FORM_CACHE = {}


def clear_cache():
    """清空 Python 内存缓存"""
    global _FORM_CACHE
    _FORM_CACHE = {}


def init_api(api_base, token):
    """初始化 API 地址和 Token"""
    global _API_BASE, _TOKEN
    _API_BASE = api_base.rstrip('/')
    _TOKEN = token


# ============================================================
# API 请求
# ============================================================
def api_request(path, data=None, method='POST'):
    """发送 API 请求，返回 JSON 响应"""
    url = f'{_API_BASE}{path}'
    headers = {
        'X-Access-Token': _TOKEN,
        'X-Sign': '00000000000000000000000000000000',
        'X-Tenant-Id': '1',
        'X-Timestamp': str(int(time.time() * 1000)),
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req, context=_SSL_CTX)
    return json.loads(resp.read().decode('utf-8'))


# ============================================================
# 字典查询
# ============================================================
def query_dict(dict_code):
    """查询字典项列表，返回 [{value, text, label, ...}, ...]

    用法: query_dict('sex') → [{'value': '1', 'text': '男'}, {'value': '2', 'text': '女'}]
    """
    r = api_request(f'/sys/dict/getDictItems/{dict_code}', method='GET')
    if r.get('success') and r.get('result'):
        return r['result']
    return []


def search_dict(keyword):
    """通过关键词模糊搜索字典编码，返回匹配的字典列表 [{id, dictCode, dictName, ...}, ...]

    用法: search_dict('性别') → [{'dictCode': 'sex', 'dictName': '性别', ...}]
          search_dict('sex')  → [{'dictCode': 'sex', 'dictName': '性别', ...}]
    """
    r = api_request(f'/sys/dict/list?pageNo=1&pageSize=200&dictName={keyword}', method='GET')
    results = []
    if r.get('success') and r.get('result'):
        records = r['result'].get('records', [])
        results.extend(records)
    # 也按 dictCode 搜索
    r2 = api_request(f'/sys/dict/list?pageNo=1&pageSize=200&dictCode={keyword}', method='GET')
    if r2.get('success') and r2.get('result'):
        seen_ids = {rec['id'] for rec in results}
        for rec in r2['result'].get('records', []):
            if rec['id'] not in seen_ids:
                results.append(rec)
    return results


# ============================================================
# 编码唯一性检查
# ============================================================
def check_code_available(code):
    """检查表单编码是否可用（数据库级唯一性校验）

    调用 GET /sys/duplicate/check 接口检查 design_form 表中 desform_code 是否已存在。

    Args:
        code: 表单编码

    Returns:
        True 表示可用，False 表示已存在
    """
    r = api_request(
        f'/sys/duplicate/check?tableName=design_form&fieldName=desform_code&fieldVal={code}',
        method='GET'
    )
    return r.get('success', False)


# ============================================================
# 表单缓存 & 查找
# ============================================================
def _cache_put(code, form_id, uc=0):
    """写入缓存"""
    _FORM_CACHE[code] = {'id': form_id, 'uc': uc}


def _cache_get(code):
    """读取缓存，返回 (id, uc) 或 (None, None)"""
    c = _FORM_CACHE.get(code)
    if c:
        return c['id'], c['uc']
    return None, None


def _cache_remove(code):
    """清除缓存"""
    _FORM_CACHE.pop(code, None)


def _find_by_list(code):
    """通过 list API 全量搜索 + 精确匹配 desformCode 查找表单（按创建时间倒序，取最新的）"""
    page = 1
    while page <= 10:
        r = api_request(f'/desform/list?pageNo={page}&pageSize=100&column=createTime&order=desc', method='GET')
        if not r.get('success') or not r.get('result'):
            break
        records = r['result'].get('records', [])
        if not records:
            break
        for rec in records:
            if rec.get('desformCode') == code:
                fid, uc = rec['id'], rec.get('updateCount', 0)
                _cache_put(code, fid, uc)
                return fid, uc
        total = r['result'].get('total', 0)
        if page * 100 >= total:
            break
        page += 1
    return None, None


def _verify_form_exists(form_id):
    """验证表单 ID 是否真实存在（通过 list API 验证，不走缓存）"""
    try:
        # list API 不走 Redis 缓存，结果可靠
        page = 1
        while page <= 5:
            r = api_request(f'/desform/list?pageNo={page}&pageSize=100&column=createTime&order=desc', method='GET')
            if not r.get('success') or not r.get('result'):
                return False
            for rec in r['result'].get('records', []):
                if rec.get('id') == form_id:
                    return True
            total = r['result'].get('total', 0)
            if page * 100 >= total:
                break
            page += 1
        return False
    except Exception:
        return False


def get_form_id(code):
    """通过表单编码获取表单 ID（带缓存），返回 (form_id, update_count) 或 (None, None)

    查找顺序: 缓存 → queryByCode(带验证) → list 全量搜索
    """
    # 1. 缓存（已验证过的）
    fid, uc = _cache_get(code)
    if fid:
        return fid, uc

    # 2. queryByCode（需要验证，该接口有服务端缓存可能返回已删除的幽灵记录）
    try:
        r = api_request(f'/desform/queryByCode?desformCode={code}', method='GET')
        if r.get('success') and r.get('result') and r['result'].get('id'):
            fid = r['result']['id']
            uc = r['result'].get('updateCount', 0)
            # 验证 ID 是否真实存在
            if _verify_form_exists(fid):
                _cache_put(code, fid, uc)
                return fid, uc
            # 幽灵记录，跳过
    except Exception:
        pass

    # 3. list 全量搜索（list 结果比较可靠）
    return _find_by_list(code)


def find_or_create_form(name, code):
    """查找或创建表单，返回 (form_id, update_count, code)

    策略：先 add → 成功则查找 ID；add 失败(code已存在)则查找已有表单。
    结果自动缓存。
    """
    # 1. 尝试创建
    try:
        add_r = api_request('/desform/add', {'desformName': name, 'desformCode': code})
        if add_r.get('success'):
            # add 成功，优先从返回值获取 ID
            if add_r.get('result') and add_r['result'].get('id'):
                fid = add_r['result']['id']
                _cache_put(code, fid, 0)
                return fid, 0, code
            # 旧版后端不返回 ID，通过 list 搜索
            for wait in [2, 2, 3]:
                time.sleep(wait)
                fid, uc = _find_by_list(code)
                if fid:
                    _cache_put(code, fid, uc)
                    return fid, uc, code
    except Exception:
        pass

    # 3. add 失败(code已存在)，查找已有表单直接使用
    fid, uc = get_form_id(code)
    if fid:
        return fid, uc, code

    raise RuntimeError(f'无法查找或创建表单: {code}')


def get_form_fields(form_code):
    """查询已有表单的字段信息，返回 (titleField_model, {name: {model, key, type}})"""
    # 优先使用缓存获取 ID
    fid, _ = get_form_id(form_code)
    q = None
    if fid:
        q = api_request(f'/desform/queryById?id={fid}', method='GET')
    if not q or not q.get('success') or not q.get('result') or not q['result'].get('desformDesignJson'):
        # fallback: queryByCode
        q = api_request(f'/desform/queryByCode?desformCode={form_code}', method='GET')
        if not q.get('success') or not q.get('result') or not q['result'].get('desformDesignJson'):
            raise RuntimeError(f'表单 {form_code} 未找到或无设计数据')
    design = json.loads(q['result']['desformDesignJson'])
    title_field = design['config']['titleField']
    fields = {}
    def extract(items):
        for item in items:
            if item.get('type') == 'card' and 'list' in item:
                extract(item['list'])
            elif item.get('type') == 'sub-table-design' and 'columns' in item:
                for col in item['columns']:
                    extract(col.get('list', []))
            elif 'model' in item and item.get('type') not in ('card',):
                fields[item['name']] = {
                    'model': item['model'],
                    'key': item['key'],
                    'type': item['type']
                }
    extract(design.get('list', []))
    return title_field, fields


# ============================================================
# ID 生成
# ============================================================
def _gen_key():
    ts = int(time.time() * 1000)
    rnd = random.randint(100000, 999999)
    return f"{ts}_{rnd}"


def _gen_model(widget_type):
    ts = int(time.time() * 1000)
    rnd = random.randint(100000, 999999)
    safe = widget_type.replace('-', '_')
    return f"{safe}_{ts}_{rnd}"


def _sleep():
    time.sleep(0.003)


# ============================================================
# 控件核心工厂
# ============================================================
def _adv(fmt='string', custom=False, split=''):
    return {
        "defaultValue": {
            "type": "compose", "value": "", "format": fmt,
            "allowFunc": True, "valueSplit": split, "customConfig": custom
        }
    }


def make_widget(widget_type, name, class_name, icon, options,
                required=False, is_sub=False, parent_key=None, extra=None,
                mobile_options=None):
    """创建控件（通用工厂），返回 (widget_dict, key, model)

    Args:
        mobile_options: 移动端覆盖配置（widget 顶层属性），移动端渲染时 merge 到 options。
            例如 radio/checkbox: {"inline": True, "matrixWidth": 120}
            例如 date/time: {"editable": False}
    """
    key = _gen_key()
    model = _gen_model(widget_type)
    _sleep()

    fmt = "number" if widget_type in ("number", "integer", "money", "slider") else "string"
    custom = widget_type in ("radio", "checkbox", "select", "link-record", "sub-table-design")
    # select-user/depart/depart-post 需要 valueSplit=',' 但 customConfig=False
    needs_split = custom or widget_type in ("select-user", "select-depart", "select-depart-post")
    split = "," if needs_split else ""

    w = {
        "type": widget_type, "name": name,
        "className": class_name, "icon": icon,
        "hideTitle": False, "options": options,
        "remoteAPI": {"url": "", "executed": False},
        "key": key, "model": model, "modelType": "main",
        "rules": [{"required": True, "message": "${title}必须填写"}] if required else [],
        "isSubItem": is_sub
    }

    if mobile_options:
        w["mobileOptions"] = mobile_options

    if widget_type != "link-field":
        w["advancedSetting"] = _adv(fmt, custom, split)

    if is_sub and parent_key:
        w["subOptions"] = {"width": "200px", "parentKey": parent_key}

    if extra:
        w.update(extra)

    return w, key, model


# ============================================================
# Card 容器
# ============================================================
def make_card(*widgets):
    """创建 card 容器，包裹 1~4 个控件"""
    key = _gen_key()
    _sleep()
    return {
        "key": key, "type": "card", "isAutoGrid": True,
        "isContainer": True, "list": list(widgets),
        "options": {}, "model": f"card_{key}"
    }


def CARD(*widgets, width='100%', row_num=1):
    """卡片容器控件（不需要外层 card 包裹）

    Card 是 AutoGrid 布局之外的独立容器，可容纳多个子控件。
    普通控件自动包裹在 AutoGrid card 中，但 CARD() 创建的是
    显式的非 AutoGrid 卡片容器。

    Args:
        widgets: 子控件的 (widget_dict, key, model) tuple 或裸 widget dict
        width: 卡片宽度，默认 '100%'
        row_num: 每行控件数，默认 1

    Returns:
        (widget_dict, key, model)

    用法:
        input_w, _, _ = INPUT('姓名', wrap=False)
        phone_w, _, _ = PHONE('手机', wrap=False)
        card_w, card_k, card_m = CARD(input_w, phone_w, row_num=2)
    """
    key = _gen_key()
    _sleep()
    child_list = []
    for item in widgets:
        if isinstance(item, tuple):
            child_list.append(item[0])
        else:
            child_list.append(item)
    w = {
        "type": "card", "name": "卡片",
        "className": "form-card", "icon": "icon-card",
        "hideTitle": False, "hideLabel": True,
        "isContainer": True,
        "list": child_list,
        "options": {
            "width": width, "rowNum": row_num, "hidden": False,
        },
        "key": key, "model": f"card_{key}",
    }
    return w, key, w["model"]


def GRID(columns, gutter=8, justify='start', align='top',
         is_word_style=False):
    """栅格布局控件（不需要 card 包裹）

    Grid 是 12 列栅格系统，用于精确控制列宽和多列布局。

    Args:
        columns: 列定义列表，每项为 dict: {"span": 12, "list": [widget...]}
            或简写为 (span, [widget_list]) tuple
        gutter: 列间距（px），默认 8
        justify: 水平对齐 'start'|'center'|'end'|'space-between'|'space-around'
        align: 垂直对齐 'top'|'middle'|'bottom'
        is_word_style: 是否为 Word 风格栅格

    Returns:
        (widget_dict, key, model)

    用法:
        input_w, _, _ = INPUT('姓名', wrap=False)
        phone_w, _, _ = PHONE('手机', wrap=False)
        grid_w, grid_k, grid_m = GRID([
            {"span": 12, "list": [input_w]},
            {"span": 12, "list": [phone_w]},
        ])
        # 或简写：
        grid_w, grid_k, grid_m = GRID([
            (12, [input_w]),
            (12, [phone_w]),
        ])
    """
    key = _gen_key()
    _sleep()
    cols = []
    for col in columns:
        if isinstance(col, tuple):
            span, col_list = col
            cols.append({
                "span": span,
                "options": {
                    "flex": False,
                    "flexAlignItems": "flex-start",
                    "flexJustifyContent": "start",
                },
                "list": [w[0] if isinstance(w, tuple) else w for w in col_list],
            })
        elif isinstance(col, dict):
            # 确保 list 中的 tuple 被解包
            col_list = col.get("list", [])
            col["list"] = [w[0] if isinstance(w, tuple) else w for w in col_list]
            if "options" not in col:
                col["options"] = {
                    "flex": False,
                    "flexAlignItems": "flex-start",
                    "flexJustifyContent": "start",
                }
            cols.append(col)
    class_name = "form-grid form-grid-word-theme" if is_word_style else "form-grid"
    w = {
        "type": "grid", "name": "栅格布局",
        "className": class_name, "icon": "icon-grid",
        "hideTitle": False, "hideLabel": True,
        "isContainer": True,
        "columns": cols,
        "options": {
            "isWordStyle": is_word_style,
            "gutter": gutter, "justify": justify, "align": align,
            "hidden": False,
        },
        "key": key, "model": f"grid_{key}",
        "rules": [], "modelType": "main",
    }
    return w, key, w["model"]


# ============================================================
# 子表
# ============================================================
def make_sub_table(name, sub_widgets, column_number=2, operation_mode=1,
                   is_word_style=False, is_word_inner_grid=False, default_rows=0):
    """创建子表容器，sub_widgets 为子控件列表，返回 (sub_table_dict, sub_key)

    Args:
        column_number: 布局列数 1/2/3/4，columns 数组长度必须与此一致
        operation_mode: 操作方式 1=行内编辑，2=弹出编辑
        is_word_style: 是否启用 Word 文档风格（黑色边框表格样式）
        is_word_inner_grid: 是否启用内嵌栅格（配合 is_word_style 解决内部边框问题）
        default_rows: 默认预填行数

    注意：columns 数组的长度必须等于 columnNumber，每列的 span = 24 / columnNumber。
    如果不匹配，设计器会显示异常（如空白列或控件挤压）。
    """
    key = _gen_key()
    model = _gen_model("sub-table-design")
    _sleep()
    col_span = 24 // column_number
    columns = []
    for i in range(column_number):
        columns.append({"span": col_span, "list": []})
    # 将 sub_widgets 均匀分配到各列（轮流分配）
    for idx, w in enumerate(sub_widgets):
        columns[idx % column_number]["list"].append(w)
    return {
        "type": "sub-table-design", "name": name,
        "className": "form-sub-table", "icon": "icon-table",
        "hideTitle": False, "class": ["data-j-editable-design"],
        "isContainer": True,
        "columns": columns,
        "options": {
            "isWordStyle": is_word_style, "isWordInnerGrid": is_word_inner_grid,
            "gutter": 0,
            "columnNumber": column_number, "operationMode": operation_mode,
            "justify": "start", "align": "top",
            "defaultValue": [], "subTableName": "", "defaultRows": default_rows,
            "showCheckbox": True, "showNumber": True, "showRowButton": False,
            "allowAdd": True, "autoHeight": True, "defaultValType": "none",
            "hidden": False, "hiddenOnAdd": False, "required": False, "fieldNote": ""
        },
        "advancedSetting": _adv("string", True, ""),
        "key": key, "model": model, "modelType": "main",
        "rules": [], "isSubItem": False
    }, key


# ============================================================
# 快捷控件工厂函数（大写命名）
# 默认返回 (autoGridCard, widget_key, widget_model)
# wrap=False 时返回 (widget_dict, widget_key, widget_model)
# is_sub=True 时返回子表控件 (widget_dict, widget_key, widget_model)
# ============================================================

def _card_wrap(w, key, model):
    """包裹控件到 card 并返回 (card, key, model)"""
    return make_card(w), key, model


def _finalize(w, k, m, wrap, is_sub, col_width, sub_extra=None):
    """统一处理控件的包裹逻辑。

    - is_sub=True → 设置子表列宽，返回裸控件
    - wrap=True → 包裹 AutoGrid card
    - wrap=False → 返回裸控件（用于 Grid 列内）
    """
    if is_sub:
        w["subOptions"]["width"] = col_width
        if sub_extra:
            w["subOptions"].update(sub_extra)
        return w, k, m
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def INPUT(name, required=False, width=100, placeholder='', unique=False,
          *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "width": "100%", "defaultValue": "", "required": required,
        "dataType": None, "pattern": "", "patternMessage": "",
        "placeholder": placeholder, "clearable": False, "readonly": False,
        "disabled": False, "fillRuleCode": "", "showPassword": False,
        "unique": unique, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("input", name, "form-input", "icon-input", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def TEXTAREA(name, required=False, width=100, placeholder='',
             *, wrap=True, is_sub=False, parent_key=None, col_width='250px', **kw):
    opts = {
        "width": "100%", "defaultValue": "", "required": required,
        "disabled": False, "pattern": "", "patternMessage": "",
        "placeholder": placeholder, "readonly": False, "unique": False,
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("textarea", name, "form-textarea", "icon-textarea", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def NUMBER(name, required=False, width=100, unit='', precision=0,
           *, wrap=True, is_sub=False, parent_key=None, col_width='120px', **kw):
    opts = {
        "width": "", "required": required, "defaultValue": 0,
        "placeholder": "", "precision": precision, "controls": False,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "disabled": False, "controlsPosition": "right",
        "unitText": unit, "unitPosition": "suffix", "showPercent": False,
        "align": "left", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("number", name, "form-number", "icon-number", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def INTEGER(name, required=False, width=100, unit='',
            *, wrap=True, is_sub=False, parent_key=None, col_width='120px', **kw):
    opts = {
        "width": "", "placeholder": "请输入整数", "required": required,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "precision": 0, "controls": not bool(unit), "disabled": False,
        "controlsPosition": "right", "unitText": unit, "unitPosition": "suffix",
        "showPercent": False, "align": "left", "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("integer", name, "form-integer", "icon-integer", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def MONEY(name, required=False, width=100, unit='元',
          *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    opts = {
        "width": "180px", "placeholder": "请输入金额", "required": required,
        "unitText": unit, "unitPosition": "suffix", "precision": 2,
        "hidden": False, "disabled": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("money", name, "form-money", "icon-money", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def DATE(name, required=False, width=100, fmt='yyyy-MM-dd',
         *, wrap=True, is_sub=False, parent_key=None, col_width='180px', **kw):
    opts = {
        "defaultValue": "", "defaultValueType": 1,
        "readonly": False, "disabled": False, "editable": True,
        "clearable": True, "placeholder": "", "startPlaceholder": "",
        "endPlaceholder": "", "designType": "date", "type": "date",
        "format": fmt, "timestamp": True, "required": required,
        "width": "", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("date", name, "form-date", "icon-date", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def TIME(name, required=False, width=100,
         *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    opts = {
        "defaultValue": "", "inputDefVal": False,
        "readonly": False, "disabled": False, "editable": True,
        "clearable": True, "placeholder": "", "startPlaceholder": "",
        "endPlaceholder": "", "isRange": False, "arrowControl": False,
        "format": "HH:mm:ss", "required": required, "width": "",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("time", name, "form-time", "icon-time", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def SWITCH(name, active='Y', inactive='N', width=100,
           *, wrap=True, is_sub=False, parent_key=None, col_width='100px', **kw):
    opts = {
        "defaultValue": False, "disabled": False,
        "activeValue": active, "inactiveValue": inactive,
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("switch", name, "form-switch", "icon-switch", opts,
                          is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def _make_options_list(options, colors=None):
    """将简单字符串列表或 dict 列表转为 options 数组。

    支持两种输入格式：
    - 字符串列表: ['选项1', '选项2'] → [{"value": "选项1", "itemColor": "#xxx"}, ...]
    - dict 列表: [{'value': '1', 'label': '男'}] → [{"value": "1", "itemColor": "#xxx"}, ...]

    注意：value 必须是简单字符串，不能是嵌套对象，否则渲染时显示 [object Object]。
    """
    default_colors = ["#2196F3", "#08C9C9", "#00C345", "#FF9800", "#9C27B0", "#795548", "#607D8B", "#E91E63"]
    result = []
    for i, opt in enumerate(options):
        c = (colors[i] if colors and i < len(colors)
             else default_colors[i % len(default_colors)])
        # dict 格式时提取 value 字段，避免嵌套对象导致 [object Object]
        if isinstance(opt, dict):
            val = opt.get('value', opt.get('label', str(opt)))
        else:
            val = opt
        result.append({"value": val, "itemColor": c})
    return result


def RADIO(name, options, required=False, width=100, dict_code=None,
          *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """单选框组。options: 字符串列表 或 dict_code 指定系统字典"""
    opts = {
        "inline": True, "matrixWidth": 120, "defaultValue": "",
        "showType": "default", "showLabel": False, "useColor": False,
        "colorIteratorIndex": 3,
        "options": _make_options_list(options) if options else [],
        "required": required, "width": "", "remote": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "disabled": False, "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("radio", name, "form-radio", "icon-radio-active", opts,
                          required=required, extra=extra, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def CHECKBOX(name, options, required=False, width=100, dict_code=None,
             *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "inline": True, "matrixWidth": 120, "defaultValue": [],
        "showLabel": False, "showType": "default", "useColor": False,
        "colorIteratorIndex": 3,
        "options": _make_options_list(options) if options else [],
        "required": required, "width": "", "remote": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "disabled": False, "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("checkbox", name, "form-checkbox", "icon-checkbox", opts,
                          required=required, extra=extra, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def SELECT(name, options, required=False, width=100, multiple=False, dict_code=None,
           *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    opts = {
        "defaultValue": "" if not multiple else [],
        "multiple": multiple, "disabled": False, "clearable": True,
        "placeholder": "", "required": required, "showLabel": False,
        "showType": "default", "width": "", "useColor": False,
        "colorIteratorIndex": 3,
        "options": _make_options_list(options) if options else [],
        "remote": False, "filterable": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("select", name, "form-select", "icon-select", opts,
                          required=required, extra=extra, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def PHONE(name, required=False, width=100, placeholder='',
          *, wrap=True, is_sub=False, parent_key=None, col_width='180px', **kw):
    opts = {
        "width": "", "defaultValue": "", "required": required,
        "placeholder": placeholder, "readonly": False, "disabled": False,
        "unique": False, "hidden": False, "showVerifyCode": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("phone", name, "form-input-phone", "icon-mobile-phone", opts,
                          required=required, extra={
        "defaultRules": [
            {"type": "phone", "message": "请输入正确的手机号码"},
            {"type": "validator", "message": "", "trigger": "blur"}
        ]
    }, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def EMAIL(name, required=False, width=100, placeholder='',
          *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "width": "", "defaultValue": "", "required": required,
        "placeholder": placeholder, "readonly": False, "disabled": False,
        "unique": False, "hidden": False, "showVerifyCode": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("email", name, "form-input-email", "icon-email", opts,
                          required=required, extra={
        "defaultRules": [
            {"type": "email", "message": "请输入正确的邮箱地址"},
            {"type": "validator", "message": "", "trigger": "blur"}
        ]
    }, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def USER(name, required=False, width=100, multiple=False, default_login=False, placeholder='',
         *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "keyMaps": [], "defaultValue": "", "defaultLogin": default_login,
        "placeholder": placeholder, "width": "100%", "multiple": multiple,
        "disabled": False, "customReturnField": "username",
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("select-user", name, "form-select-user", "icon-user-circle", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def DEPART(name, required=False, width=100, multiple=False, placeholder='',
           *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "keyMaps": [], "defaultValue": "", "defaultLogin": False,
        "placeholder": placeholder, "width": "100%", "multiple": multiple,
        "disabled": False, "customReturnField": "id",
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("select-depart", name, "form-select-depart", "icon-depart", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def AREA(name, required=False, width=100, level=3, placeholder='请选择',
         *, wrap=True, is_sub=False, parent_key=None, col_width='250px', **kw):
    opts = {
        "width": "", "placeholder": placeholder, "areaLevel": level,
        "defaultValue": "", "clearable": True, "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("area-linkage", name, "form-area-linkage", "icon-jilianxuanze", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def ORG_ROLE(name, required=False, width=100, multiple=False, placeholder='选择组织角色',
             *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """组织角色选择控件"""
    opts = {
        "defaultValue": "", "defaultLogin": False,
        "placeholder": placeholder, "width": "100%", "multiple": multiple,
        "disabled": False,
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("org-role", name, "form-org-role", "icon-zuzhijuese", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def DEPART_POST(name, required=False, width=100, placeholder='',
                *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """岗位组件"""
    opts = {
        "keyMaps": [], "defaultValue": "", "defaultLogin": False,
        "placeholder": placeholder, "width": "100%", "multiple": False,
        "disabled": False, "customReturnField": "id",
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("select-depart-post", name, "form-select-depart", "icon-gangwei", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def TABLE_DICT(name, dict_table='', dict_code_col='', dict_text_col='',
               required=False, width=100, multiple=False, style='select',
               *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """表字典控件

    Args:
        name: 控件名称
        dict_table: 字典表名（Online报表编码或数据库表名）
        dict_code_col: 值字段列名
        dict_text_col: 显示字段列名
        style: 展示风格 'select'(下拉) 或 'popup'(弹窗)
    """
    opts = {
        "width": "100%", "defaultValue": "", "placeholder": "点击选择表字典",
        "showIcon": True, "iconName": "icon-popup",
        "disabled": False, "multiple": multiple, "clearable": True,
        "style": style, "dictTable": dict_table,
        "dictCode": dict_code_col, "dictText": dict_text_col,
        "hidden": False, "required": required, "filterable": True,
        "queryScope": "cgreport",
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("table-dict", name, "form-dict", "icon-dict", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def SELECT_TREE(name, category_code='', required=False, width=100, multiple=False, placeholder='',
                *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """下拉树控件

    Args:
        name: 控件名称
        category_code: 分类字典编码（dataFrom='category' 时使用）
    """
    opts = {
        "defaultValue": "", "placeholder": placeholder, "width": "",
        "disabled": False, "multiple": multiple,
        "dataFrom": "category",
        "conf": {
            "category": {"code": category_code},
            "table": {
                "name": "", "code": "", "text": "",
                "pidField": "", "rootPid": "", "leaf": "",
                "converIsLeafVal": True,
            },
            "condition": "",
            "conditionOnlyRoot": True,
        },
        "hidden": False, "required": required,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("select-tree", name, "form-select-tree", "icon-tree", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def IMGUPLOAD(name, required=False, width=100, length=9,
              *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    opts = {
        "defaultValue": [], "size": {"width": 100, "height": 100},
        "width": "", "tokenFunc": "funcGetToken", "token": "",
        "domain": "http://img.h5huodong.com", "disabled": False,
        "length": length, "multiple": True, "hidden": False,
        "hiddenOnAdd": False, "required": required,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("imgupload", name, "form-tupian", "icon-tupian", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    sub_extra = {"size": {"width": 50, "height": 50}} if is_sub else None
    return _finalize(w, k, m, wrap, is_sub, col_width, sub_extra=sub_extra)


def FILE(name, required=False, width=100,
         *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "defaultValue": [], "token": "", "length": 0,
        "drag": False, "listStyleType": "card", "multiple": False,
        "multipleDown": True, "disabled": False, "buttonText": "点击上传文件",
        "tokenFunc": "funcGetToken", "hidden": False, "hiddenOnAdd": False,
        "required": required, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("file-upload", name, "form-file-upload", "icon-shangchuan", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def SLIDER(name, required=False, width=100, min_val=0, max_val=100, show_input=False,
           *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    opts = {
        "defaultValue": 0, "disabled": False, "required": required,
        "min": min_val, "max": max_val, "step": 1,
        "showInput": show_input, "showPercent": False, "range": False,
        "width": "", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("slider", name, "form-slider", "icon-slider", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def RATE(name, required=False, width=100, max_val=5, allow_half=False,
         *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    opts = {
        "defaultValue": None, "max": max_val, "disabled": False,
        "allowHalf": allow_half, "required": required,
        "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("rate", name, "form-rate", "icon-rate", opts,
                          required=required, extra={
        "defaultRules": [{"type": "validator", "message": "", "trigger": "change"}]
    }, is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def COLOR(name, width=100,
          *, wrap=True, is_sub=False, parent_key=None, col_width='120px', **kw):
    opts = {
        "defaultValue": "", "disabled": False, "showAlpha": False,
        "required": False, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("color", name, "form-color", "icon-color", opts,
                          is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def AUTONUMBER(name, prefix='', width=100, *, wrap=True, **kw):
    """自动编号控件"""
    rules = [{"type": "number", "mode": 1, "start": 1, "reset": 0, "length": 4, "continue": False}]
    if prefix:
        rules.insert(0, {"type": "text", "text": prefix})
        rules.insert(1, {"type": "create_date", "format": "yyyyMMdd"})
    w, k, m = make_widget("auto-number", name, "form-auto-number", "icon-hashtag", {
        "numberRules": rules,
        "generateOnAdd": True,
        "placeholder": "${title}自动生成，不需要填写",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def HANDSIGN(name, required=False, width=100, *, wrap=True, **kw):
    w, k, m = make_widget("hand-sign", name, "form-hand-sign", "icon-signature", {
        "width": "100%", "height": "200px", "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def OA_APPROVAL_COMMENTS(name='审批意见', required=False, width=100, *, wrap=True, **kw):
    """OA 审批意见控件"""
    w, k, m = make_widget("oa-approval-comments", name, "form-oa-approval-comments", "icon-input", {
        "width": "100%", "required": required, "disabled": False,
        "placeholder": "", "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


# ============================================================
# 静态展示 / 高级控件（不存储数据或特殊用途）
# ============================================================

def TEXT(text='这里是一段文本', font_size=16, font_color='#4c4c4c',
         align='left', bold=False, *, wrap=True, **kw):
    """静态文本展示控件（不存储数据）"""
    w, k, m = make_widget("text", "文本", "form-text", "icon-text", {
        "text": text, "width": "100%", "align": align,
        "verticalAlign": "top", "fontSize": font_size, "lineHeight": "",
        "fontColor": font_color, "fontBold": bold,
        "fontItalic": False, "fontUnderline": False, "fontLineThrough": False,
        "hidden": False,
    }, **kw)
    w["hideLabel"] = True
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def BUTTONS(text='按钮', btn_type='default', icon='', click_code="console.log('hello,world!')",
            *, wrap=True, **kw):
    """按钮控件（不存储数据）

    Args:
        text: 按钮文字
        btn_type: 按钮类型 'default'|'primary'|'success'|'warning'|'danger'|'info'
        icon: 图标名称
        click_code: 点击事件 JS 代码
    """
    w, k, m = make_widget("buttons", "按钮", "form-buttons", "icon-btn2", {
        "text": text, "icon": icon, "type": btn_type,
        "btnSize": "default", "plain": False, "round": False,
        "circle": False, "disabled": False, "hidden": False,
    }, **kw)
    w["hideLabel"] = True
    w["event"] = {"click": click_code}
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def BARCODE(name, source_model='', code_type='barcode', max_width=180,
            *, wrap=True, **kw):
    """条码/二维码控件

    Args:
        source_model: 引用字段的 model（条码内容来源）
        code_type: 'barcode'(一维码) 或 'qrcode'(二维码)
    """
    w, k, m = make_widget("barcode", name, "form-barcode", "icon-tiaoma", {
        "maxWidth": max_width, "codeType": code_type,
        "sourceModel": source_model, "hidden": False,
    }, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def CAPITAL_MONEY(name, money_widget_key='', *, wrap=True, **kw):
    """大写金额控件 — 关联一个金额/数字字段，自动转换为中文大写

    Args:
        money_widget_key: 关联的金额控件 key
    """
    w, k, m = make_widget("capital-money", name, "form-money", "icon-money", {
        "moneyWidgetKey": money_widget_key, "hidden": False,
    }, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def TEXT_COMPOSE(name, expression='', *, wrap=True, **kw):
    """文本组合控件 — 将多个字段值拼接展示

    Args:
        expression: 组合表达式，使用 $model$ 引用字段，如 '$input_xxx$-$input_yyy$'
    """
    w, k, m = make_widget("text-compose", name, "form-text-compose", "icon-zuhe", {
        "expression": expression, "hidden": False,
    }, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def LOCATION(name, required=False, width=100, default_current=False, show_map=False,
             *, wrap=True, **kw):
    """定位控件"""
    w, k, m = make_widget("location", name, "form-location", "icon-location", {
        "width": "100%", "defaultValue": "",
        "defaultCurrent": default_current,
        "showLngLat": False, "showMap": show_map,
        "disabled": False, "hidden": False,
        "hiddenOnAdd": False, "required": required, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def MAP(name, required=False, width='100%', height='300px', zoom=15, lng=116.397467, lat=39.908806, **kw):
    """地图控件（百度地图）"""
    w, k, m = make_widget("map", name, "form-map", "icon-map", {
        "width": width, "height": height, "zoom": zoom,
        "required": required,
        "point": {"lng": lng, "lat": lat},
        "mapSettings": {
            "dragging": True, "scrollWheelZoom": True,
            "doubleClickZoom": True, "keyboard": False,
            "inertialDragging": True, "continuousZoom": True,
            "pinchToZoom": True,
        },
        "mapControls": {
            "navigation": True, "geolocation": True,
            "scale": True, "mapType": True,
            "panorama": False, "overviewMap": False,
        },
        "disabled": False, "hidden": False,
    }, **kw)
    return w, k, m


def OCR(name, ocr_type='normal', field_mapping=None, required=False, width=100,
        *, wrap=True, **kw):
    """文本识别控件（OCR）

    Args:
        ocr_type: 识别类型 'normal'(通用)|'id_card'(身份证)|'vat_invoice'(增值税发票)|'train_ticket'(火车票)
        field_mapping: 识别结果到表单字段的映射 dict
    """
    w, k, m = make_widget("ocr", name, "form-ocr", "icon-ocr-a", {
        "type": ocr_type,
        "fieldMapping": field_mapping or {},
        "hidden": False, "disabled": False, "required": required,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


# ============================================================
# 不需要 card 包裹的控件（直接返回控件本身）
# ============================================================

def DIVIDER(text='', **kw):
    """分隔符（不需要 card 包裹），返回 (widget_dict, key, model)"""
    w, k, m = make_widget("divider", text or "分隔符", "form-divider", "icon-divider", {
        "heightNumber": 48, "type": "horizontal", "text": text,
        "position": "center", "hidden": False, "hiddenOnAdd": False,
        "required": False, "fieldNote": ""
    }, **kw)
    w["hideLabel"] = True
    w["formItemMargin"] = True
    return w, k, m


def EDITOR(name, required=False, **kw):
    """富文本编辑器（不需要 card 包裹）"""
    w, k, m = make_widget("editor", name, "form-editor", "icon-fuwenbenkuang", {
        "defaultValue": "", "width": "100%", "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required, "fieldNote": ""
    }, required=required, **kw)
    return w, k, m


def MARKDOWN(name, required=False, **kw):
    """Markdown 编辑器（不需要 card 包裹）"""
    w, k, m = make_widget("markdown", name, "form-markdown", "icon-markdown", {
        "defaultValue": "", "width": "100%", "height": 300,
        "viewerAutoHeight": False, "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required, "fieldNote": ""
    }, required=required, **kw)
    return w, k, m


def TABS(tab_labels=None, tab_type='border-card', position='top'):
    """标签页容器控件（不需要 card 包裹）

    Args:
        tab_labels: 标签页名称列表，默认 ['Tab1', 'Tab2']
        tab_type: 标签样式 'border-card'|'card'|''
        position: 标签位置 'top'|'bottom'|'left'|'right'

    Returns:
        (widget_dict, key, model) — 向 panes[i]['list'] 中添加子控件

    用法:
        tabs_w, tabs_k, tabs_m = TABS(['基本信息', '详细信息'])
        # 向第一个标签页添加控件
        tabs_w['panes'][0]['list'].append(input_widget)
        # 向第二个标签页添加控件
        tabs_w['panes'][1]['list'].append(select_widget)
    """
    if tab_labels is None:
        tab_labels = ['Tab1', 'Tab2']
    key = _gen_key()
    _sleep()
    panes = []
    for label in tab_labels:
        panes.append({
            "name": label, "label": label, "rowNum": 1,
            "hidden": False, "hiddenOnAdd": False, "list": []
        })
    w = {
        "type": "tabs", "name": "Tabs",
        "className": "form-tabs", "icon": "icon-tab",
        "hideTitle": False, "hideLabel": True,
        "isContainer": True,
        "key": key, "model": f"tabs_{key}",
        "panes": panes,
        "options": {
            "width": "100%", "activeName": "",
            "type": tab_type, "position": position,
            "hidden": False,
        },
    }
    return w, key, w["model"]


# ============================================================
# 关联控件
# ============================================================

def LINK_RECORD(name, source_code, title_field, show_fields=None,
                required=False, width=100, show_mode='single', show_type='card',
                *, wrap=True, is_sub=False, parent_key=None, col_width='200px', **kw):
    """关联记录控件，返回 (card_or_widget, key, model)

    Args:
        source_code: 源表单 desformCode
        title_field: 源表单标题字段 model
        show_fields: 源表单展示字段 model 列表
        show_mode: 'single' 或 'many'
        show_type: 'card', 'select', 'table'
    """
    opts = {
        "sourceCode": source_code, "showMode": show_mode, "showType": show_type,
        "titleField": title_field, "showFields": show_fields or [],
        "allowView": True, "allowEdit": True, "allowAdd": True, "allowSelect": True,
        "buttonText": "添加记录", "twoWayModel": "", "dataSelectAuth": "all",
        "filters": [{"matchType": "AND", "rules": []}],
        "search": {"enabled": False, "field": "", "rule": "like", "afterShow": False, "fields": []},
        "createMode": {"add": True, "select": False, "params": {"selectLinkModel": ""}},
        "width": "100%", "defaultValue": "", "defaultValType": "none",
        "required": required, "disabled": False, "hidden": False,
        "isSubTable": False, "isSelf": False,
        "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("link-record", name, "form-link-record", "icon-link", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    if is_sub:
        w["subOptions"]["width"] = col_width
        return w, k, m
    # AutoGrid.check: showType='table' bypasses AutoGrid
    if show_type == 'table':
        return w, k, m
    if wrap:
        return _card_wrap(w, k, m)
    return w, k, m


def LINK_FIELD(name, link_record_key, show_field, field_type='input',
               field_options=None, width=100,
               *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    """他表字段控件（与 link-record 配对使用）"""
    opts = {
        "linkRecordKey": link_record_key, "showField": show_field,
        "saveType": "view", "fieldType": field_type,
        "fieldOptions": field_options or {},
        "width": "100%", "defaultValue": "", "readonly": False,
        "disabled": False, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    w, k, m = make_widget("link-field", name, "form-link-field", "icon-field", opts,
                          is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


def FORMULA(name, mode='CUSTOM', expression='', fields=None,
            width=100, unit='', decimal=2,
            date_begin='', date_end='', date_format_method=1,
            date_print_unit='m', date_add_exp='', date_print_format='YYYY-MM-DD',
            *, wrap=True, is_sub=False, parent_key=None, col_width='150px', **kw):
    """公式控件

    Args:
        mode: 数值模式（必须大写）: 'SUM', 'AVERAGE', 'MAX', 'MIN', 'PRODUCT', 'CUSTOM'
              日期模式: 'DATEIF', 'DATEADD', 'NOW_DATEIF'
        expression: 自定义表达式（mode='CUSTOM' 时使用），字段引用语法: $model$
        fields: SUM/AVERAGE 等预定义模式时的字段 model 列表
        date_begin: 日期模式 — 开始日期字段引用，如 '$date_model$'
        date_end: 日期模式 — 结束日期字段引用，如 '$date_model$'
        date_format_method: 日期模式 — 格式化方式（1=开始00:00结束00:00，2=开始00:00结束24:00）
        date_print_unit: 日期模式 — 输出单位（'Y'年/'M'月/'d'天/'h'小时/'m'分钟）
        date_add_exp: DATEADD 模式 — 加减表达式，如 '+8h+30m', '-2d'
        date_print_format: DATEADD 模式 — 输出格式，如 'YYYY-MM-DD HH:mm:ss'
    """
    mode = mode.upper()
    _DATE_MODES = {'DATEIF', 'DATEADD', 'NOW_DATEIF'}
    opt_type = 'date' if mode in _DATE_MODES else 'number'
    opts = {
        "type": opt_type, "mode": mode, "expression": expression,
        "decimal": decimal, "thousand": True, "percent": False,
        "unitPosition": "suffix", "unitText": unit, "emptyAsZero": True,
        "dateBegin": date_begin, "dateEnd": date_end,
        "dateFormatMethod": date_format_method,
        "datePrintUnit": date_print_unit, "dateAddExp": date_add_exp,
        "datePrintFormat": date_print_format,
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "",
    }
    if not is_sub:
        opts["autoWidth"] = width
    if fields and mode != 'CUSTOM':
        opts["fields"] = fields
    w, k, m = make_widget("formula", name, "form-formula", "icon-formula", opts,
                          is_sub=is_sub, parent_key=parent_key, **kw)
    return _finalize(w, k, m, wrap, is_sub, col_width)


# ============================================================
# 子表控件别名（向后兼容，推荐直接使用主函数 + is_sub=True）
# ============================================================

def SUB_INPUT(name, parent_key, required=False, col_width='200px'):
    return INPUT(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_INTEGER(name, parent_key, required=False, col_width='120px', unit=''):
    return INTEGER(name, required=required, unit=unit, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_NUMBER(name, parent_key, required=False, col_width='120px', unit=''):
    return NUMBER(name, required=required, unit=unit, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_MONEY(name, parent_key, required=False, col_width='150px', unit='元'):
    return MONEY(name, required=required, unit=unit, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_SELECT(name, parent_key, options, required=False, col_width='150px'):
    return SELECT(name, options, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_DATE(name, parent_key, required=False, col_width='180px'):
    return DATE(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_TIME(name, parent_key, required=False, col_width='150px'):
    return TIME(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_SWITCH(name, parent_key, active='Y', inactive='N', col_width='100px'):
    return SWITCH(name, active=active, inactive=inactive, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_RADIO(name, parent_key, options, required=False, col_width='200px', dict_code=None):
    return RADIO(name, options, required=required, dict_code=dict_code, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_CHECKBOX(name, parent_key, options, required=False, col_width='200px', dict_code=None):
    return CHECKBOX(name, options, required=required, dict_code=dict_code, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_TEXTAREA(name, parent_key, required=False, col_width='250px'):
    return TEXTAREA(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_SLIDER(name, parent_key, col_width='200px', min_val=0, max_val=100):
    return SLIDER(name, min_val=min_val, max_val=max_val, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_RATE(name, parent_key, col_width='150px', max_val=5):
    return RATE(name, max_val=max_val, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_COLOR(name, parent_key, col_width='120px'):
    return COLOR(name, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_USER(name, parent_key, required=False, col_width='200px', multiple=False):
    return USER(name, required=required, multiple=multiple, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_DEPART(name, parent_key, required=False, col_width='200px', multiple=False):
    return DEPART(name, required=required, multiple=multiple, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_DEPART_POST(name, parent_key, required=False, col_width='200px'):
    return DEPART_POST(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_ORG_ROLE(name, parent_key, required=False, col_width='200px', multiple=False):
    return ORG_ROLE(name, required=required, multiple=multiple, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_PHONE(name, parent_key, required=False, col_width='180px'):
    return PHONE(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_EMAIL(name, parent_key, required=False, col_width='200px'):
    return EMAIL(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_AREA(name, parent_key, required=False, col_width='250px'):
    return AREA(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_IMGUPLOAD(name, parent_key, required=False, col_width='150px'):
    """子表图片上传。缩略图自动缩小为 50x50（主表默认 100x100）。"""
    return IMGUPLOAD(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_FILE(name, parent_key, required=False, col_width='200px'):
    return FILE(name, required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_TABLE_DICT(name, parent_key, dict_table='', dict_code_col='', dict_text_col='',
                   required=False, col_width='200px'):
    return TABLE_DICT(name, dict_table=dict_table, dict_code_col=dict_code_col,
                      dict_text_col=dict_text_col, required=required,
                      wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_SELECT_TREE(name, parent_key, category_code='', required=False, col_width='200px'):
    return SELECT_TREE(name, category_code=category_code, required=required,
                       wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_LINK_RECORD(name, parent_key, source_code, title_field, show_fields=None,
                    required=False, col_width='200px'):
    return LINK_RECORD(name, source_code, title_field, show_fields=show_fields,
                       required=required, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_LINK_FIELD(name, parent_key, link_record_key, show_field,
                   field_type='input', field_options=None, col_width='150px'):
    return LINK_FIELD(name, link_record_key, show_field, field_type=field_type,
                      field_options=field_options, wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)

def SUB_FORMULA(name, parent_key, mode='CUSTOM', expression='', col_width='150px', unit='',
                fields=None, date_begin='', date_end='', date_format_method=1,
                date_print_unit='m', date_add_exp='', date_print_format='YYYY-MM-DD'):
    """子表公式控件（向后兼容别名）。详见 FORMULA() 文档。"""
    return FORMULA(name, mode=mode, expression=expression, unit=unit,
                   fields=fields, date_begin=date_begin, date_end=date_end,
                   date_format_method=date_format_method, date_print_unit=date_print_unit,
                   date_add_exp=date_add_exp, date_print_format=date_print_format,
                   wrap=False, is_sub=True, parent_key=parent_key, col_width=col_width)


def SUB_PRODUCT(name, parent_key, field_models, col_width='150px', unit=''):
    """子表乘积公式（快捷方式）—— formula 控件 PRODUCT 模式的语法糖。

    等价于 SUB_FORMULA(name, parent_key, mode='PRODUCT', expression='$a$*$b$')，
    自动根据 field_models 列表拼接 PRODUCT 表达式。

    Args:
        name: 控件标签名
        parent_key: 所属子表的 key
        field_models: 参与乘积的字段 model 列表，如 ['money_xxx', 'integer_xxx']
        col_width: 子表列宽（默认 '150px'）
        unit: 单位文本

    用法:
        sub_qty = SUB_INTEGER('数量', sub_key)
        sub_price = SUB_MONEY('单价', sub_key)
        sub_amount = SUB_PRODUCT('金额', sub_key, [sub_price[2], sub_qty[2]])
    """
    expression = ''.join(f'${m}$' for m in field_models)
    return SUB_FORMULA(name, parent_key, mode='PRODUCT', expression=expression,
                       col_width=col_width, unit=unit)


def SUMMARY(name, sub_table_model, field_model, summary_type='inner-sum', width=100):
    """汇总控件 — 对子表某列进行汇总计算。

    用于替代 FORMULA(mode='SUM') 来汇总子表列数据（FORMULA 的 SUM 模式只能汇总主表字段）。

    Args:
        name: 控件名称，如 '合计金额'
        sub_table_model: 子表的 model，如 'sub_table_design_xxx'
        field_model: 要汇总的子表列 model，如 'formula_xxx'（预估金额列）
        summary_type: 汇总方式，'inner-sum'(求和), 'inner-avg'(平均), 'inner-max', 'inner-min', 'inner-count'

    用法:
        sub_table, sub_key = make_sub_table('明细', [])
        sub_amount = SUB_PRODUCT('金额', sub_key, [price_model, qty_model])
        # ... 组装子表 ...
        total = SUMMARY('合计金额', sub_table['model'], sub_amount[2])
    """
    key = _gen_key()
    model = _gen_model("summary")
    _sleep()
    w = {
        "type": "summary", "name": name,
        "className": "form-summary", "icon": "icon-sigma",
        "hideTitle": False,
        "options": {
            "linkTable": sub_table_model,
            "field": field_model,
            "summary": summary_type,
            "filter": {"enabled": False, "rules": [], "matchType": "AND"},
            "hidden": False, "hiddenOnAdd": False, "required": False, "fieldNote": ""
        },
        "key": key, "model": model, "modelType": "main",
        "rules": [], "isSubItem": False
    }
    return w, key, model


# ============================================================
# 设计 JSON 组装 & 保存
# ============================================================

def _collect_types(items):
    """递归收集所有控件类型"""
    types = set()
    for item in items:
        t = item.get('type')
        if t:
            types.add(t)
        if t == 'card' and 'list' in item:
            types.update(_collect_types(item['list']))
        if t == 'grid' and 'columns' in item:
            for col in item['columns']:
                types.update(_collect_types(col.get('list', [])))
        if t == 'sub-table-design' and 'columns' in item:
            for col in item['columns']:
                types.update(_collect_types(col.get('list', [])))
    return types


def make_word_grid(*rows, cols_per_row=2):
    """创建 Word 风格的栅格行（匹配 JeecgBoot 真实 Word 风格实现）

    真实 Word 风格通过 CSS class `form-grid form-grid-word-theme` +
    表单设计器内置 Word 风格 CSS 实现表格边框效果。

    布局规则（参照加班申请等真实表单）：
    - 两列行：标签 span=6 + 控件 span=6 + 标签 span=4 + 控件 span=8
    - 单列整行：标签 span=6 + 控件 span=18
    - 标签列使用 `text` 控件（居中、16px），flex 垂直居中
    - 控件列的控件 hideTitle=True

    Args:
        rows: 每个 row 是一组 (widget_dict, key, model) tuple 或裸 widget dict
        cols_per_row: 每行放几个控件（1 或 2）

    Returns:
        grid dict
    """
    key = _gen_key()
    _sleep()

    columns = []

    for idx, item in enumerate(rows):
        if isinstance(item, tuple):
            w = item[0]
        else:
            w = item

        # 从 card 中提取内部控件
        inner = w
        if w.get('type') == 'card' and w.get('list') and len(w['list']) == 1:
            inner = w['list'][0]

        widget_name = inner.get('name', '')
        inner['hideTitle'] = True
        inner['hideLabel'] = True

        # 计算 span
        if cols_per_row == 2:
            if idx == 0:
                label_span, field_span = 6, 6
            else:
                label_span, field_span = 4, 8
        else:
            label_span, field_span = 6, 18

        # 标题列（text 控件，居中 16px）
        label_key = _gen_key()
        _sleep()
        label_widget = {
            "type": "text", "name": "文本",
            "className": "form-text", "icon": "icon-text",
            "hideLabel": True, "hideTitle": False,
            "options": {
                "text": widget_name, "width": "100%", "align": "center",
                "fontSize": 16, "fontColor": "#000000",
                "fontBold": False, "fontItalic": False,
                "fontUnderline": False, "fontLineThrough": False,
                "hidden": False, "required": False, "hiddenOnAdd": False,
                "verticalAlign": "top", "fieldNote": ""
            },
            "remoteAPI": {"url": "", "executed": False},
            "key": label_key, "model": f"text_{label_key}",
            "modelType": "main", "rules": [], "isSubItem": False
        }

        # 标签列 options：flex 垂直居中（textarea/hand-sign 等宽控件也居中）
        label_col_opts = {"flex": True, "flexAlignItems": "center", "flexJustifyContent": "start"}

        columns.append({
            "span": label_span,
            "list": [label_widget],
            "options": label_col_opts
        })

        # 控件列
        columns.append({
            "span": field_span,
            "list": [inner],
            "options": {"flex": True, "flexAlignItems": "center", "flexJustifyContent": "start"}
        })

    grid = {
        "type": "grid", "name": "栅格布局",
        "className": "form-grid form-grid-word-theme",
        "icon": "icon-grid",
        "hideLabel": True, "isContainer": True,
        "columns": columns,
        "options": {
            "gutter": 0, "justify": "start", "align": "top",
            "hidden": False, "required": False, "hiddenOnAdd": False,
            "isWordStyle": False, "isWordInnerGrid": False, "fieldNote": ""
        },
        "key": key, "model": f"grid_{key}",
        "rules": [], "hideTitle": False, "modelType": "main"
    }
    return grid


def _make_word_title(title_text):
    """创建 Word 风格表单顶部标题（text 控件，24px 加粗居中）"""
    key = _gen_key()
    _sleep()
    return {
        "type": "text", "name": "文本",
        "className": "form-text", "icon": "icon-text",
        "hideLabel": True, "hideTitle": False,
        "options": {
            "text": title_text, "width": "100%", "align": "center",
            "fontSize": 24, "fontColor": "#000000",
            "fontBold": True, "fontItalic": False,
            "fontUnderline": False, "fontLineThrough": False,
            "hidden": False, "required": False, "hiddenOnAdd": False,
            "verticalAlign": "top", "fieldNote": ""
        },
        "remoteAPI": {"url": "", "executed": False},
        "key": key, "model": f"text_{key}",
        "modelType": "main", "rules": [], "isSubItem": False
    }


def _make_word_divider_grid(item):
    """将分隔符包裹在 Word 风格的 grid 中（单列 span=24, isWordStyle=true）

    Word 布局下分隔符不使用标签+控件的两列格式，而是用一个占满整行的 grid 容器，
    内部放置 divider 控件，grid 设置 isWordStyle=true 以保持边框一致性。
    """
    if isinstance(item, tuple):
        w = item[0]
    else:
        w = item
    key = _gen_key()
    _sleep()
    grid = {
        "type": "grid", "name": "栅格布局",
        "className": "form-grid form-grid-word-theme",
        "icon": "icon-grid",
        "hideLabel": True, "isContainer": True,
        "columns": [{
            "span": 24,
            "list": [w],
            "options": {
                "flex": False,
                "flexAlignItems": "flex-start",
                "flexJustifyContent": "start",
            }
        }],
        "options": {
            "gutter": 0, "justify": "start", "align": "top",
            "hidden": False, "required": False, "hiddenOnAdd": False,
            "isWordStyle": True, "isWordInnerGrid": False, "fieldNote": ""
        },
        "key": key, "model": f"grid_{key}",
        "rules": [], "hideTitle": False, "modelType": "main"
    }
    return grid


def _apply_word_layout(widgets, form_name=''):
    """将 widgets 列表转换为 Word 风格布局（匹配 JeecgBoot 真实实现）

    真实 Word 风格特征：
    - 顶部有独立的 text 标题控件（24px 加粗居中）
    - 每行是 grid 容器，className = 'form-grid form-grid-word-theme'
    - 适合半行的控件两两配对（标签6+值6 | 标签4+值8）
    - textarea/file-upload/hand-sign 等宽控件独占一行（标签6+值18）
    - formStyle 设为 'word'，表单设计器内置 Word 风格 CSS 自动生效

    Args:
        widgets: 控件列表
        form_name: 表单名称（用于生成顶部标题，空则不生成）

    Returns:
        (new_top_items, all_models)
    """
    top_items = []
    all_models = []

    # 添加顶部标题
    if form_name:
        title_widget = _make_word_title(form_name)
        top_items.append(title_widget)

    half_buffer = None

    for item in widgets:
        wtype = _get_widget_type(item)

        if isinstance(item, tuple):
            key, model = item[1], item[2]
        else:
            key, model = item.get('key', ''), item.get('model', '')

        if _is_half_suitable(wtype):
            if half_buffer is None:
                half_buffer = (item, key, model)
            else:
                # 两个控件配对成一行
                grid = make_word_grid(half_buffer[0], item, cols_per_row=2)
                top_items.append(grid)
                all_models.append((half_buffer[1], half_buffer[2]))
                all_models.append((key, model))
                half_buffer = None
        else:
            # 先刷出缓冲区
            if half_buffer is not None:
                grid = make_word_grid(half_buffer[0], cols_per_row=1)
                top_items.append(grid)
                all_models.append((half_buffer[1], half_buffer[2]))
                half_buffer = None

            # 分隔符特殊处理：包裹在单列 span=24 的 grid 中，带 isWordStyle
            if wtype == 'divider':
                divider_grid = _make_word_divider_grid(item)
                top_items.append(divider_grid)
                all_models.append((key, model))
            else:
                # 宽控件独占一行
                grid = make_word_grid(item, cols_per_row=1)
                top_items.append(grid)
                all_models.append((key, model))

    if half_buffer is not None:
        grid = make_word_grid(half_buffer[0], cols_per_row=1)
        top_items.append(grid)
        all_models.append((half_buffer[1], half_buffer[2]))

    return top_items, all_models


def build_design_json(widgets, title_model, form_style='normal', expand=None):
    """组装完整的 desformDesignJson

    Args:
        widgets: 顶层控件列表（card 包裹的和不需要 card 的混合）
        title_model: 标题字段的 model
        form_style: 表单风格 'normal' 或 'word'
            - 'normal': 默认风格
            - 'word': Word 风格（表单设计器内置 CSS 自动生效）
        expand: JS/CSS 增强配置 dict，格式: {"js": "...", "css": "...", "url": {"js": "...", "css": "..."}}
    """
    is_word = (form_style == 'word')
    has_widgets = sorted(list(_collect_types(widgets)))

    # Word 风格：关闭自动栅格和顶部标题（内置 CSS 自动生效，无需加载外部 CSS）
    if is_word:
        base_expand = {"js": "", "css": "", "url": {"js": "", "css": ""}}
        show_header = False
        disabled_auto_grid = True
        dialog_top = 60
        dialog_width = 1100
        allow_print = True
    else:
        base_expand = {"js": "", "css": "", "url": {"js": "", "css": ""}}
        show_header = True
        disabled_auto_grid = False
        dialog_top = 20
        dialog_width = 1000
        allow_print = False

    # 合并用户传入的 expand 配置
    if expand:
        if expand.get('js'):
            base_expand['js'] = expand['js']
        if expand.get('css'):
            base_expand['css'] = expand['css']
        if expand.get('url'):
            if expand['url'].get('js'):
                base_expand['url']['js'] = expand['url']['js']
            if expand['url'].get('css'):
                base_expand['url']['css'] = expand['url']['css']
    expand = base_expand

    return {
        "list": widgets,
        "config": {
            "formStyle": "word" if is_word else "normal",
            "titleField": title_model,
            "showHeaderTitle": show_header,
            "labelWidth": 100,
            "labelPosition": "top",
            "size": "small",
            "dialogOptions": {
                "top": dialog_top, "width": dialog_width,
                "padding": {"top": 25, "right": 25, "bottom": 30, "left": 25}
            },
            "disabledAutoGrid": disabled_auto_grid,
            "designMobileView": False,
            "enableComment": True,
            "hasWidgets": has_widgets,
            "defaultLoadLargeControls": False,
            "expand": expand,
            "transactional": True,
            "customRequestURL": [{"url": ""}],
            "disableMobileCss": True,
            "allowExternalLink": False,
            "externalLinkShowData": is_word,
            "headerImgUrl": "",
            "externalTitle": "",
            "enableNotice": False,
            "noticeMode": "external",
            "noticeType": "system",
            "noticeReceiver": "",
            "allowPrint": allow_print,
            "allowJmReport": False,
            "jmReportURL": "",
            "bizRuleConfig": [],
            "bigDataMode": False
        }
    }


def save_design(form_id, form_code, widgets, title_model, update_count=1, form_style='normal',
                expand=None):
    """保存表单设计到 API

    Args:
        form_id: 表单 ID
        form_code: 表单编码（用于日志）
        widgets: 顶层控件列表
        title_model: 标题字段 model
        update_count: 当前 updateCount（从 find_or_create_form 获取）
        form_style: 表单风格 'normal' 或 'word'
        expand: JS/CSS 增强配置 dict（可选），见 build_design_json

    Returns:
        API 响应 dict
    """
    design_json = build_design_json(widgets, title_model, form_style, expand=expand)
    payload = {
        'id': form_id,
        'desformDesignJson': json.dumps(design_json, ensure_ascii=False),
        'updateCount': update_count,
        'autoNumberDesignConfig': {'update': {}, 'current': {}},
        'refTableDefaultValDbSync': {'changes': {}, 'removeKeys': []}
    }
    result = api_request('/desform/edit', payload, method='PUT')

    if result.get('success'):
        print(f'  {form_code} 保存成功')
        return result

    msg = result.get('message', '')

    # 自动重试: 未找到对应实体 → ID 可能是旧的幽灵记录，清缓存后重新搜索
    if '未找到对应实体' in msg:
        print(f'  {form_code} ID={form_id} 无效，重新搜索...')
        _cache_remove(form_code)
        new_id, new_uc = _find_by_list(form_code)
        if new_id and new_id != form_id:
            payload['id'] = new_id
            payload['updateCount'] = new_uc
            result = api_request('/desform/edit', payload, method='PUT')
            if result.get('success'):
                print(f'  {form_code} 保存成功 (重试, ID={new_id})')
                return result

    # 自动重试: 版本过时 → updateCount 不匹配，逐个尝试 uc+1, uc+2, ...
    if '版本已过时' in msg or '版本过时' in msg:
        print(f'  {form_code} 版本过时(uc={update_count})，尝试递增...')
        _cache_remove(form_code)
        for try_uc in range(update_count + 1, update_count + 10):
            payload['updateCount'] = try_uc
            result = api_request('/desform/edit', payload, method='PUT')
            if result.get('success'):
                print(f'  {form_code} 保存成功 (uc={try_uc})')
                return result
            retry_msg = result.get('message', '')
            if '版本已过时' not in retry_msg and '版本过时' not in retry_msg:
                break

    raise RuntimeError(f'{form_code} 保存失败: {msg}')


# ============================================================
# 字段权限（auth）
# ============================================================

# 不创建权限的控件类型（容器 + 纯布局/展示元素）
_AUTH_SKIP_TYPES = {'card', 'grid', 'tabs', 'divider', 'text'}


def _recursive_all_widgets(data_list, handler, parent=None):
    """Python 版 recursiveAllWidget（参考 vue-form-making-jeecg/src/util/utils.js:208）

    遍历 design JSON 的 list，对每个控件调用 handler(item, parent)。
    容器控件会先递归其子控件，再对自身调用 handler。
    """
    for item in data_list:
        if item.get('isContainer'):
            if item.get('columns'):
                # grid / sub-table-design 等有 columns 的容器
                for col in item['columns']:
                    _recursive_all_widgets(col.get('list', []), handler, parent=item)
            elif item.get('type') == 'card':
                _recursive_all_widgets(item.get('list', []), handler, parent=item)
            elif item.get('type') == 'tabs':
                for pane in item.get('panes', []):
                    _recursive_all_widgets(pane.get('list', []), handler, parent=item)
        handler(item, parent)


def _build_auth_list(form_code, design_list, form_id=None):
    """从 design JSON 的 list 中提取所有需要权限控制的字段

    Args:
        form_code: 表单编码
        design_list: design JSON 的 list 数组（layout 变换后的最终结构）
        form_id: 表单ID（后端 desform_id 字段必填）

    Returns:
        auth 权限数组，可直接传给 addAuthBatch 接口
    """
    auth_items = []

    def handler(item, parent):
        wtype = item.get('type', '')
        if wtype in _AUTH_SKIP_TYPES or not wtype:
            return
        auth = {
            "desformCode": form_code,
            "desformId": form_id or "",
            "authComKey": item['key'],
            "authTitle": item.get('name', ''),
            "authField": item['model'],
            "subTable": bool(item.get('isSubItem', False)),
            "status": 0
        }
        if item.get('isSubItem') and parent:
            auth["subKey"] = parent['key']
            auth["subTitle"] = parent.get('name', '')
        auth_items.append(auth)

    _recursive_all_widgets(design_list, handler)
    return auth_items


def _collect_auth_keys(design_list):
    """从 design list 中收集所有需要权限的控件 key 集合"""
    keys = set()

    def handler(item, parent):
        wtype = item.get('type', '')
        if wtype not in _AUTH_SKIP_TYPES and wtype:
            keys.add(item['key'])

    _recursive_all_widgets(design_list, handler)
    return keys


def _query_existing_auth_keys(form_code):
    """查询表单已有的权限 key 集合

    Returns:
        set of authComKey
    """
    try:
        r = api_request(f'/desform/auth/query/{form_code}?permissionType=field&onlyEnabled=false', method='GET')
        if r.get('success') and r.get('result'):
            return {item['authComKey'] for item in r['result']}
    except Exception:
        pass
    return set()


def add_auth_batch(form_code, design_list, form_id=None):
    """批量新增字段权限（用于新建表单）

    Args:
        form_code: 表单编码
        design_list: design JSON 的 list 数组
        form_id: 表单ID（后端 desform_id 字段必填）

    Returns:
        API 响应 dict，无字段时返回 None
    """
    auth_list = _build_auth_list(form_code, design_list, form_id=form_id)
    if not auth_list:
        return None
    result = api_request('/desform/auth/addAuthBatch', auth_list, method='POST')
    if result.get('success'):
        print(f'  {form_code} 字段权限已创建 ({len(auth_list)} 个字段)')
    else:
        raise RuntimeError(f'权限创建失败: {result.get("message", "")}')
    return result


def _delete_auth_keys(form_code, keys_to_delete):
    """批量删除权限（按 authComKey）

    Args:
        form_code: 表单编码
        keys_to_delete: 要删除的 authComKey 集合
    """
    if not keys_to_delete:
        return
    keys_str = ','.join(keys_to_delete)
    r = api_request(
        f'/desform/auth/deleteBatchByAuthComKey?desformCode={form_code}&authComKeys={keys_str}',
        method='DELETE'
    )
    if r.get('success'):
        print(f'  {form_code} 已删除 {len(keys_to_delete)} 个旧字段权限')
    else:
        print(f'  [警告] {form_code} 删除旧字段权限失败: {r.get("message", "")}')


def sync_auth(form_code, design_list, form_id=None):
    """同步字段权限（用于更新表单）：新增新字段权限 + 删除已移除字段权限

    Args:
        form_code: 表单编码
        design_list: 新的 design JSON 的 list 数组
        form_id: 表单ID（后端 desform_id 字段必填）
    """
    new_keys = _collect_auth_keys(design_list)
    old_keys = _query_existing_auth_keys(form_code)

    # 需要新增的 key
    added_keys = new_keys - old_keys
    # 需要删除的 key
    removed_keys = old_keys - new_keys

    # 删除已移除的字段权限
    if removed_keys:
        _delete_auth_keys(form_code, removed_keys)

    # 新增新字段权限
    if added_keys:
        auth_list = _build_auth_list(form_code, design_list, form_id=form_id)
        new_auth_list = [a for a in auth_list if a['authComKey'] in added_keys]
        if new_auth_list:
            result = api_request('/desform/auth/addAuthBatch', new_auth_list, method='POST')
            if result.get('success'):
                print(f'  {form_code} 新增 {len(new_auth_list)} 个字段权限')
            else:
                raise RuntimeError(f'新增权限失败: {result.get("message", "")}')

    if not added_keys and not removed_keys:
        print(f'  {form_code} 字段权限无变化')


def save_auth_from_design(form_code):
    """查询已有表单设计并创建字段权限（用于重试）

    Args:
        form_code: 表单编码

    Returns:
        API 响应 dict
    """
    form = query_form(form_code)
    if not form or not form.get('desformDesignJson'):
        raise RuntimeError(f'表单 {form_code} 未找到或无设计数据')
    form_id = form.get('id', '')
    design = json.loads(form['desformDesignJson'])
    return add_auth_batch(form_code, design.get('list', []), form_id=form_id)


# ============================================================
# 菜单 SQL 生成（含授权 SQL）
# ============================================================

def _gen_id():
    """生成 32 位无横线 UUID 作为菜单/授权记录 ID"""
    return uuid.uuid4().hex


def gen_menu_sql(parent_name, children, role_id=None, icon='ant-design:appstore-outlined'):
    """生成菜单 + 授权 SQL

    Args:
        parent_name: 父菜单名称
        children: [(name, desform_code, sort), ...] 或 [(menu_id, name, desform_code, sort), ...] (兼容旧格式)
        role_id: 角色 ID（默认使用全局 ROLE_ID）
        icon: 父菜单图标（默认 'ant-design:appstore-outlined'）

    Returns:
        完整 SQL 字符串
    """
    rid = role_id or ROLE_ID
    lines = []
    parent_id = _gen_id()

    # 父菜单
    lines.append(f"""INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('{parent_id}', NULL, '{parent_name}', '/{parent_id}', 'layouts/RouteView', NULL, NULL, 0, NULL, '1', 1.00, 0, '{icon}', 1, 0, 0, 0, 0, NULL, '1', 0, 0, 'admin', now(), NULL, NULL, 0);""")

    # 父菜单授权
    lines.append(f"""INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip)
VALUES ('{_gen_id()}', '{rid}', '{parent_id}', NULL, now(), '127.0.0.1');""")

    # 子菜单
    for item in children:
        # 兼容旧格式 (menu_id, name, code, sort) 和新格式 (name, code, sort)
        if len(item) == 4:
            _, name, code, sort = item
        else:
            name, code, sort = item
        menu_id = _gen_id()
        lines.append(f"""
INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('{menu_id}', '{parent_id}', '{name}', '/online/desform/list/{code}', 'super/online/desform/auto/AutoDesformDataList', 'AutoDesformDataList', NULL, 0, NULL, '1', {sort}.00, 0, NULL, 0, 1, 0, 0, 0, NULL, '1', 0, 0, 'admin', now(), NULL, NULL, 0);""")

        lines.append(f"""INSERT INTO sys_role_permission (id, role_id, permission_id, data_rule_ids, operate_date, operate_ip)
VALUES ('{_gen_id()}', '{rid}', '{menu_id}', NULL, now(), '127.0.0.1');""")

    return '\n'.join(lines)


# ============================================================
# 便捷函数：批量创建表单
# ============================================================

def query_form(code):
    """查询表单基本信息，返回 dict 或 None（带缓存）

    返回字段包括: id, desformCode, desformName, updateCount, desformDesignJson 等
    """
    fid, _ = get_form_id(code)
    if fid:
        try:
            r = api_request(f'/desform/queryById?id={fid}', method='GET')
            if r.get('success') and r.get('result'):
                # 更新缓存中的 updateCount
                _cache_put(code, fid, r['result'].get('updateCount', 0))
                return r['result']
        except Exception:
            pass
    return None


def delete_form(code_or_id, form_id=None):
    """删除表单：逻辑删除 → 真实删除

    支持 3 种调用方式：
      delete_form('elder_person')              # 传 code，自动查找 ID
      delete_form('elder_person', '123456')     # 传 code + 已知 ID，跳过搜索
      delete_form(id='123456')                  # 只传 ID

    会自动处理同 code 多条记录的情况（全部删除）。
    删除后自动清除缓存。返回已删除的 ID 列表。
    """
    deleted_ids = []
    code = None

    # 判断传入的是 code 还是 ID
    if form_id:
        # 明确传了 form_id，code_or_id 就是 code
        code = code_or_id
        all_ids = [str(form_id)]
    elif code_or_id and str(code_or_id).isdigit() and len(str(code_or_id)) > 15:
        # 纯数字且长度>15，判定为 ID
        all_ids = [str(code_or_id)]
    else:
        # 传的是 code，需要查找 ID
        code = code_or_id
        all_ids = []

        # 优先从缓存获取
        cached_id, _ = _cache_get(code)
        if cached_id:
            all_ids.append(cached_id)

        # 再通过 queryByIdOrCode 快速查找
        try:
            r = api_request(f'/desform/queryByIdOrCode?desformCode={code}', method='GET')
            if r.get('success') and r.get('result') and r['result'].get('id'):
                qid = r['result']['id']
                if qid not in all_ids:
                    all_ids.append(qid)
        except Exception:
            pass

        # 如果快速查找没结果，再走 list 全量搜索兜底
        if not all_ids:
            page = 1
            while page <= 10:
                r = api_request(f'/desform/list?pageNo={page}&pageSize=100&column=createTime&order=desc', method='GET')
                if not r.get('success') or not r.get('result'):
                    break
                records = r['result'].get('records', [])
                if not records:
                    break
                for rec in records:
                    if rec.get('desformCode') == code:
                        all_ids.append(rec['id'])
                total = r['result'].get('total', 0)
                if page * 100 >= total:
                    break
                page += 1

    if not all_ids:
        print(f'  {code_or_id}: 未找到表单，无需删除')
        return deleted_ids

    for fid in all_ids:
        try:
            # Step 1: 逻辑删除
            r2 = api_request(f'/desform/deleteBatch?ids={fid}', method='DELETE')
            ok2 = r2.get('success', False)
            # Step 2: 真实删除
            r3 = api_request(f'/desform/recycleBin/deleteByIds?ids={fid}', method='DELETE')
            ok3 = r3.get('success', False)
            if ok2 and ok3:
                deleted_ids.append(fid)
                print(f'  {code_or_id}: 已删除 {fid}')
            else:
                print(f'  {code_or_id}: 删除 {fid} 部分失败 (deleteBatch={ok2}, recycleBin={ok3})')
        except Exception as e:
            print(f'  {code_or_id}: 删除 {fid} 异常: {e}')

    # 清除缓存
    if code:
        _cache_remove(code)
    return deleted_ids


def update_form(code, widgets, title_index=0):
    """修改已有表单设计：查询 → 重新保存设计 → 返回 (form_id, title_model)

    Args:
        code: 表单编码
        widgets: 新的控件列表（同 create_form 格式）
        title_index: 标题字段在 widgets 中的索引
    """
    # 查询表单（带缓存）
    form_id, uc = get_form_id(code)
    if not form_id:
        raise RuntimeError(f'表单 {code} 不存在，无法更新')

    # 解包 widgets
    top_items = []
    all_models = []
    for item in widgets:
        if isinstance(item, tuple):
            top_items.append(item[0])
            all_models.append((item[1], item[2]))
        else:
            top_items.append(item)
            all_models.append((item.get('key', ''), item.get('model', '')))

    title_model = all_models[title_index][1] if title_index < len(all_models) else all_models[0][1]

    # 保存设计
    save_design(form_id, code, top_items, title_model, uc)
    # 更新缓存（updateCount 会被后端自动递增）
    _cache_put(code, form_id, uc + 1)
    print(f'  {code}: 已更新 (ID={form_id})')

    # 同步字段权限（新增 + 删除）
    try:
        sync_auth(code, top_items, form_id=form_id)
    except Exception as e:
        print(f'  [警告] {code} 字段权限同步失败: {e}')

    return form_id, title_model


def _is_half_suitable(widget_type):
    """判断控件是否适合半行布局（textarea/editor/markdown/file-upload/imgupload/sub-table-design 等宽控件不适合）"""
    wide_types = {'textarea', 'editor', 'markdown', 'file-upload', 'imgupload',
                  'sub-table-design', 'divider', 'map', 'hand-sign', 'grid', 'tabs'}
    return widget_type not in wide_types


def _get_widget_type(item):
    """从 widget tuple 或 dict 中获取控件类型"""
    if isinstance(item, tuple):
        w = item[0]
    else:
        w = item
    # card 容器：检查内部控件
    if w.get('type') == 'card' and w.get('list'):
        return w['list'][0].get('type', '')
    return w.get('type', '')


def _get_inner_widget(item):
    """从 card-wrapped tuple 中提取内部控件 dict"""
    if isinstance(item, tuple):
        w = item[0]
    else:
        w = item
    if w.get('type') == 'card' and w.get('list') and len(w['list']) == 1:
        return w['list'][0]
    return None


def _set_autowidth(widget, width):
    """设置控件的 autoWidth"""
    if 'options' in widget and isinstance(widget['options'], dict):
        widget['options']['autoWidth'] = width


def _apply_half_layout(widgets):
    """将 widgets 列表中适合的控件两两配对为半行布局

    规则：
    - textarea/editor/markdown/file-upload/imgupload/sub-table-design/divider 等保持整行
    - 其余控件两两配对到同一个 card 中，autoWidth 设为 50
    - 奇数个适合半行的控件时，最后一个保持整行

    Args:
        widgets: [(card_dict, key, model), ...] 或 dict 混合列表

    Returns:
        (new_top_items, all_models) — 重组后的顶层控件列表和 model 列表
    """
    top_items = []
    all_models = []
    half_buffer = None  # 缓存一个待配对的半行控件

    for item in widgets:
        wtype = _get_widget_type(item)
        inner = _get_inner_widget(item)

        if inner and _is_half_suitable(wtype):
            # 适合半行布局
            _set_autowidth(inner, 50)
            if isinstance(item, tuple):
                key, model = item[1], item[2]
            else:
                key, model = item.get('key', ''), item.get('model', '')

            if half_buffer is None:
                # 缓存等配对
                half_buffer = (inner, key, model)
            else:
                # 配对成功，合并到一个 card
                paired_card = make_card(half_buffer[0], inner)
                top_items.append(paired_card)
                all_models.append((half_buffer[1], half_buffer[2]))
                all_models.append((key, model))
                half_buffer = None
        else:
            # 不适合半行的控件，先刷出缓冲区
            if half_buffer is not None:
                _set_autowidth(half_buffer[0], 100)  # 恢复整行
                solo_card = make_card(half_buffer[0])
                top_items.append(solo_card)
                all_models.append((half_buffer[1], half_buffer[2]))
                half_buffer = None

            # 原样添加
            if isinstance(item, tuple):
                top_items.append(item[0])
                all_models.append((item[1], item[2]))
            else:
                top_items.append(item)
                all_models.append((item.get('key', ''), item.get('model', '')))

    # 刷出最后的缓冲区
    if half_buffer is not None:
        _set_autowidth(half_buffer[0], 100)
        solo_card = make_card(half_buffer[0])
        top_items.append(solo_card)
        all_models.append((half_buffer[1], half_buffer[2]))

    return top_items, all_models


def create_form(name, code, widgets, title_index=0, layout='auto', expand=None):
    """一站式创建表单：查找/创建 → 保存设计 → 返回 (form_id, title_model)

    Args:
        name: 表单名称
        code: 表单编码
        widgets: 顶层控件列表（card 包裹的 tuple 和裸控件 tuple 混合）
        title_index: 标题字段在 widgets 中的索引
        layout: 布局模式
            - 'auto': 字段数 >= 6 时自动使用半行布局（默认）
            - 'half': 强制半行布局
            - 'full': 强制整行布局（不做半行处理）
            - 'word': Word 风格布局（带边框表格样式）
        expand: JS/CSS 增强配置 dict（可选），格式:
            {"js": "...", "css": "...", "url": {"js": "...", "css": "..."}}

    Returns:
        (form_id, title_model)
    """
    form_style = 'word' if layout == 'word' else 'normal'

    if layout == 'word':
        top_items, all_models = _apply_word_layout(widgets, form_name=name)
    elif layout == 'half' or (layout == 'auto' and len(widgets) >= 6):
        top_items, all_models = _apply_half_layout(widgets)
    else:
        # 原有逻辑：逐个解包
        top_items = []
        all_models = []
        for item in widgets:
            if isinstance(item, tuple):
                top_items.append(item[0])
                all_models.append((item[1], item[2]))
            else:
                top_items.append(item)
                all_models.append((item.get('key', ''), item.get('model', '')))

    # 确定标题字段
    title_model = all_models[title_index][1] if title_index < len(all_models) else all_models[0][1]

    # 查找或创建
    form_id, uc, actual_code = find_or_create_form(name, code)
    print(f'  ID={form_id}, success=True')

    # 保存设计
    save_design(form_id, actual_code, top_items, title_model, uc, form_style, expand=expand)
    # 更新缓存
    _cache_put(actual_code, form_id, uc + 1)

    # 自动创建字段权限
    try:
        add_auth_batch(actual_code, top_items, form_id=form_id)
    except Exception as e:
        print(f'  [警告] {actual_code} 字段权限创建失败: {e}')

    return form_id, title_model


# ============================================================
# 表单复制
# ============================================================
def copy_form(source_code, new_code=None):
    """复制表单

    Args:
        source_code: 源表单编码
        new_code: 新表单编码（可选，不传则自动生成）

    Returns:
        新表单信息 dict

    注意:
        后端 LowAppCopyMenu 不支持 newFormName 参数，新表单名称由后端自动生成。
    """
    body = {"originFormCode": source_code}
    if new_code:
        body["newFormCode"] = new_code
    r = api_request('/desform/api/copyDesignForm', data=body, method='PUT')
    if r.get('success'):
        print(f"[copy_form] 复制成功: {source_code} → {new_code or '(自动编码)'}")
        return r.get('result')
    else:
        raise RuntimeError(f"复制失败: {r.get('message', '未知错误')}")


# ============================================================
# 版本管理
# ============================================================
def create_version(code, remarks=''):
    """为表单创建版本快照

    Args:
        code: 表单编码
        remarks: 版本备注
    """
    # desformCode 是 @RequestParam（URL 参数），remarks 在 body 中
    import urllib.parse
    encoded_code = urllib.parse.quote(code, safe='')
    r = api_request(f'/desform/version/create?desformCode={encoded_code}', data={
        "remarks": remarks
    })
    if r.get('success'):
        print(f"[create_version] 版本创建成功: {code}")
    else:
        print(f"[create_version] 版本创建失败: {r.get('message', '')}")
    return r


def list_versions(code, page=1, size=10):
    """列出表单版本历史"""
    r = api_request(f'/desform/version/list?desformCode={code}&pageNo={page}&pageSize={size}', method='GET')
    if r.get('success') and r.get('result'):
        return r['result'].get('records', [])
    return []


# ============================================================
# 视图创建
# ============================================================
def create_view(parent_code, view_name, view_code, design_json=None, is_mobile=False):
    """创建子视图（desformType=2）

    Args:
        parent_code: 主视图编码
        view_name: 视图名称
        view_code: 视图编码
        design_json: 设计JSON字符串（不传则复制主视图）
        is_mobile: 是否设为移动端视图
    """
    # 获取主视图信息
    parent_id, _ = get_form_id(parent_code)
    if not parent_id:
        raise RuntimeError(f"主视图不存在: {parent_code}")

    # 如果没有传 design_json，复制主视图的设计
    if design_json is None:
        parent_form = query_form(parent_code)
        if parent_form and parent_form.get('desformDesignJson'):
            design_json = parent_form['desformDesignJson']
        else:
            raise RuntimeError(f"无法获取主视图设计JSON: {parent_code}")

    # 移动端视图设置
    if is_mobile:
        import json as _json
        dj = _json.loads(design_json) if isinstance(design_json, str) else design_json
        dj['config']['designMobileView'] = True
        design_json = _json.dumps(dj, ensure_ascii=False)

    body = {
        "desformName": view_name,
        "desformCode": view_code,
        "desformType": 2,
        "parentId": parent_id,
        "parentCode": parent_code,
        "izMobileView": 1 if is_mobile else 0,
        "desformDesignJson": design_json if isinstance(design_json, str) else json.dumps(design_json, ensure_ascii=False),
    }
    r = api_request('/desform/add', data=body)
    if r.get('success'):
        print(f"[create_view] 视图创建成功: {view_code} (mobile={is_mobile})")
        return r.get('result')
    else:
        raise RuntimeError(f"视图创建失败: {r.get('message', '未知错误')}")


# ============================================================
# 字典创建
# ============================================================
def create_dict(dict_code, dict_name, items, description=''):
    """创建新字典及其字典项

    Args:
        dict_code: 字典编码（唯一）
        dict_name: 字典名称
        items: 字典项列表 [{'value': '1', 'label': '事假'}, ...]
        description: 描述

    Returns:
        字典ID
    """
    # 创建字典主表
    r = api_request('/sys/dict/add', data={
        "dictCode": dict_code,
        "dictName": dict_name,
        "description": description,
        "type": 0
    })
    if not r.get('success'):
        raise RuntimeError(f"创建字典失败: {r.get('message', '')}")

    dict_id = r.get('result', {}).get('id') if isinstance(r.get('result'), dict) else r.get('result')
    if not dict_id:
        # 尝试查询刚创建的字典
        search_results = search_dict(dict_code)
        for sr in search_results:
            if sr.get('dictCode') == dict_code:
                dict_id = sr['id']
                break

    if not dict_id:
        raise RuntimeError(f"无法获取字典ID: {dict_code}")

    # 逐条添加字典项
    for i, item in enumerate(items):
        item_text = item.get('label', item.get('text', ''))
        item_value = str(item.get('value', ''))
        api_request('/sys/dictItem/add', data={
            "dictId": dict_id,
            "itemText": item_text,
            "itemValue": item_value,
            "sortOrder": i + 1,
            "status": 1
        })

    print(f"[create_dict] 字典创建成功: {dict_code} ({len(items)} 项)")
    return dict_id


def query_or_create_dict(dict_code, dict_name, items, description=''):
    """查询字典，不存在则创建

    Returns:
        (dict_id, items_list)
    """
    existing = query_dict(dict_code)
    if existing:
        print(f"[query_or_create_dict] 字典已存在: {dict_code}")
        return None, existing

    dict_id = create_dict(dict_code, dict_name, items, description)
    return dict_id, items


# ============================================================
# 字段级操作
# ============================================================
def add_widget(code, widget_or_widgets):
    """向已有表单追加控件

    Args:
        code: 表单编码
        widget_or_widgets: 单个控件 dict 或控件列表（多个时逐个添加）
    """
    widgets = widget_or_widgets if isinstance(widget_or_widgets, list) else [widget_or_widgets]
    last_r = None
    for i, w in enumerate(widgets):
        # 后端 @RequestBody JSONObject 期望单个对象，逐个发送
        r = api_request(f'/desform/api/{code}/addWidget', data=w, method='PUT')
        last_r = r
        if not r.get('success'):
            print(f"[add_widget] 第 {i + 1} 个控件添加失败: {r.get('message', '')}")
            return r
    print(f"[add_widget] 成功添加 {len(widgets)} 个控件到 {code}")
    return last_r


def update_widget(code, key_or_model, changes_dict):
    """修改指定控件的属性

    Args:
        code: 表单编码
        key_or_model: 控件的 key 或 model
        changes_dict: 要修改的属性字典，如 {"name": "新名称", "options": {"required": True}}
    """
    body = {"key": key_or_model, "action": "update", "widget": changes_dict}
    r = api_request(f'/desform/api/{code}/updateWidget', data=body, method='PUT')
    if r.get('success'):
        print(f"[update_widget] 成功更新控件 {key_or_model}")
    else:
        print(f"[update_widget] 更新失败: {r.get('message', '')}")
    return r


def delete_widget(code, key_or_model):
    """删除指定控件

    Args:
        code: 表单编码
        key_or_model: 控件的 key 或 model
    """
    body = {"key": key_or_model, "action": "delete"}
    r = api_request(f'/desform/api/{code}/updateWidget', data=body, method='PUT')
    if r.get('success'):
        print(f"[delete_widget] 成功删除控件 {key_or_model}")
    else:
        print(f"[delete_widget] 删除失败: {r.get('message', '')}")
    return r
