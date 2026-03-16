"""
JeecgBoot 设计器表单（desform）通用工具库
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
                required=False, is_sub=False, parent_key=None, extra=None):
    """创建控件（通用工厂），返回 (widget_dict, key, model)"""
    key = _gen_key()
    model = _gen_model(widget_type)
    _sleep()

    fmt = "number" if widget_type in ("number", "integer", "money", "slider") else "string"
    custom = widget_type in ("radio", "checkbox", "select", "link-record", "sub-table-design")
    split = "," if custom else ""

    w = {
        "type": widget_type, "name": name,
        "className": class_name, "icon": icon,
        "hideTitle": False, "options": options,
        "remoteAPI": {"url": "", "executed": False},
        "key": key, "model": model, "modelType": "main",
        "rules": [{"required": True, "message": "${title}必须填写"}] if required else [],
        "isSubItem": is_sub
    }

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
    """创建 card 容器，包裹 1~2 个控件（半行布局时放 2 个）"""
    key = _gen_key()
    _sleep()
    return {
        "key": key, "type": "card", "isAutoGrid": True,
        "isContainer": True, "list": list(widgets),
        "options": {}, "model": f"card_{key}"
    }


# ============================================================
# 子表
# ============================================================
def make_sub_table(name, sub_widgets):
    """创建子表容器，sub_widgets 为子控件列表，返回 (sub_table_dict, sub_key)"""
    key = _gen_key()
    model = _gen_model("sub-table-design")
    _sleep()
    return {
        "type": "sub-table-design", "name": name,
        "className": "form-sub-table", "icon": "icon-table",
        "hideTitle": False, "class": ["data-j-editable-design"],
        "isContainer": True,
        "columns": [{"span": 24, "list": sub_widgets}],
        "options": {
            "isWordStyle": False, "isWordInnerGrid": False, "gutter": 0,
            "columnNumber": 2, "operationMode": 1, "justify": "start", "align": "top",
            "defaultValue": [], "subTableName": "", "defaultRows": 0,
            "showCheckbox": True, "showNumber": True, "showRowButton": False,
            "allowAdd": True, "autoHeight": True, "defaultValType": "none",
            "hidden": False, "hiddenOnAdd": False, "required": False, "fieldNote": ""
        },
        "advancedSetting": _adv("string", True, ""),
        "key": key, "model": model, "modelType": "main",
        "rules": [], "isSubItem": False
    }, key


# ============================================================
# 快捷控件工厂函数（大写命名，直接返回 card 包裹的控件）
# 每个函数返回 (card_dict, widget_key, widget_model)
# ============================================================

def _card_wrap(w, key, model):
    """包裹控件到 card 并返回 (card, key, model)"""
    return make_card(w), key, model


def INPUT(name, required=False, width=100, placeholder='', unique=False, **kw):
    w, k, m = make_widget("input", name, "form-input", "icon-input", {
        "width": "100%", "defaultValue": "", "required": required,
        "dataType": None, "pattern": "", "patternMessage": "",
        "placeholder": placeholder, "clearable": False, "readonly": False,
        "disabled": False, "fillRuleCode": "", "showPassword": False,
        "unique": unique, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def TEXTAREA(name, required=False, width=100, **kw):
    w, k, m = make_widget("textarea", name, "form-textarea", "icon-textarea", {
        "width": "100%", "defaultValue": "", "required": required,
        "disabled": False, "pattern": "", "patternMessage": "",
        "placeholder": "", "readonly": False, "unique": False,
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def NUMBER(name, required=False, width=100, unit='', precision=None, **kw):
    w, k, m = make_widget("number", name, "form-number", "icon-number", {
        "width": "", "required": required, "defaultValue": 0,
        "placeholder": "", "controls": False,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "disabled": False, "controlsPosition": "right",
        "unitText": unit, "unitPosition": "suffix", "showPercent": False,
        "align": "left", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def INTEGER(name, required=False, width=100, unit='', **kw):
    w, k, m = make_widget("integer", name, "form-integer", "icon-integer", {
        "width": "", "placeholder": "请输入整数", "required": required,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "precision": 0, "controls": True, "disabled": False,
        "controlsPosition": "right", "unitText": unit, "unitPosition": "suffix",
        "showPercent": False, "align": "left", "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def MONEY(name, required=False, width=100, unit='元', **kw):
    w, k, m = make_widget("money", name, "form-money", "icon-money", {
        "width": "180px", "placeholder": "请输入金额", "required": required,
        "unitText": unit, "unitPosition": "suffix", "precision": 2,
        "hidden": False, "disabled": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def DATE(name, required=False, width=100, fmt='yyyy-MM-dd', **kw):
    w, k, m = make_widget("date", name, "form-date", "icon-date", {
        "defaultValue": "", "defaultValueType": 1,
        "readonly": False, "disabled": False, "editable": True,
        "clearable": True, "placeholder": "", "startPlaceholder": "",
        "endPlaceholder": "", "designType": "date", "type": "date",
        "format": fmt, "timestamp": True, "required": required,
        "width": "", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def TIME(name, required=False, width=100, **kw):
    w, k, m = make_widget("time", name, "form-time", "icon-time", {
        "defaultValue": "", "inputDefVal": False,
        "readonly": False, "disabled": False, "editable": True,
        "clearable": True, "placeholder": "", "startPlaceholder": "",
        "endPlaceholder": "", "isRange": False, "arrowControl": False,
        "format": "HH:mm:ss", "required": required, "width": "",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def SWITCH(name, active='Y', inactive='N', width=100, **kw):
    w, k, m = make_widget("switch", name, "form-switch", "icon-switch", {
        "defaultValue": False, "disabled": False,
        "activeValue": active, "inactiveValue": inactive,
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, **kw)
    return _card_wrap(w, k, m)


def _make_options_list(options, colors=None):
    """将简单字符串列表转为 options 数组"""
    default_colors = ["#2196F3", "#08C9C9", "#00C345", "#FF9800", "#9C27B0", "#795548", "#607D8B", "#E91E63"]
    result = []
    for i, opt in enumerate(options):
        c = (colors[i] if colors and i < len(colors)
             else default_colors[i % len(default_colors)])
        result.append({"value": opt, "itemColor": c})
    return result


def RADIO(name, options, required=False, width=100, dict_code=None, **kw):
    """单选框组。options: 字符串列表 或 dict_code 指定系统字典"""
    opts = {
        "inline": True, "matrixWidth": 120, "defaultValue": "",
        "showType": "default", "showLabel": False, "useColor": False,
        "colorIteratorIndex": 3,
        "options": _make_options_list(options) if options else [],
        "required": required, "width": "", "remote": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "disabled": False, "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("radio", name, "form-radio", "icon-radio-active", opts,
                          required=required, extra=extra, **kw)
    return _card_wrap(w, k, m)


def CHECKBOX(name, options, required=False, width=100, dict_code=None, **kw):
    opts = {
        "inline": True, "matrixWidth": 120, "defaultValue": [],
        "showLabel": False, "showType": "default", "useColor": False,
        "colorIteratorIndex": 3,
        "options": _make_options_list(options) if options else [],
        "required": required, "width": "", "remote": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "disabled": False, "hidden": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("checkbox", name, "form-checkbox", "icon-checkbox", opts,
                          required=required, extra=extra, **kw)
    return _card_wrap(w, k, m)


def SELECT(name, options, required=False, width=100, multiple=False, dict_code=None, **kw):
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
        "fieldNote": "", "autoWidth": width
    }
    extra = {}
    if dict_code:
        opts["remote"] = "dict"
        opts["dictCode"] = dict_code
        opts["showLabel"] = True
        opts["options"] = []
        extra["dictOptions"] = options if isinstance(options[0], dict) else []
    w, k, m = make_widget("select", name, "form-select", "icon-select", opts,
                          required=required, extra=extra, **kw)
    return _card_wrap(w, k, m)


def PHONE(name, required=False, width=100, **kw):
    w, k, m = make_widget("phone", name, "form-input-phone", "icon-mobile-phone", {
        "width": "300px", "defaultValue": "", "required": required,
        "placeholder": "", "readonly": False, "disabled": False,
        "unique": False, "hidden": False, "showVerifyCode": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, extra={
        "defaultRules": [
            {"type": "phone", "message": "请输入正确的手机号码"},
            {"type": "validator", "message": "", "trigger": "blur"}
        ]
    }, **kw)
    return _card_wrap(w, k, m)


def EMAIL(name, required=False, width=100, **kw):
    w, k, m = make_widget("email", name, "form-input-email", "icon-email", {
        "width": "300px", "defaultValue": "", "required": required,
        "placeholder": "", "readonly": False, "disabled": False,
        "unique": False, "hidden": False, "showVerifyCode": False,
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, required=required, extra={
        "defaultRules": [
            {"type": "email", "message": "请输入正确的邮箱地址"},
            {"type": "validator", "message": "", "trigger": "blur"}
        ]
    }, **kw)
    return _card_wrap(w, k, m)


def USER(name, required=False, width=100, multiple=False, default_login=False, **kw):
    w, k, m = make_widget("select-user", name, "form-select-user", "icon-user-circle", {
        "keyMaps": [], "defaultValue": "", "defaultLogin": default_login,
        "placeholder": "", "width": "100%", "multiple": multiple,
        "disabled": False, "customReturnField": "username",
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def DEPART(name, required=False, width=100, multiple=False, **kw):
    w, k, m = make_widget("select-depart", name, "form-select-depart", "icon-depart", {
        "keyMaps": [], "defaultValue": "", "defaultLogin": False,
        "placeholder": "", "width": "100%", "multiple": multiple,
        "disabled": False, "customReturnField": "id",
        "hidden": False, "dataAuthType": "member",
        "hiddenOnAdd": False, "required": required, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def AREA(name, required=False, width=100, level=3, **kw):
    w, k, m = make_widget("area-linkage", name, "form-area-linkage", "icon-jilianxuanze", {
        "width": "", "placeholder": "请选择", "areaLevel": level,
        "defaultValue": "", "clearable": True, "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def IMGUPLOAD(name, required=False, width=100, length=9, **kw):
    w, k, m = make_widget("imgupload", name, "form-tupian", "icon-tupian", {
        "defaultValue": [], "size": {"width": 100, "height": 100},
        "width": "", "tokenFunc": "funcGetToken", "token": "",
        "domain": "http://img.h5huodong.com", "disabled": False,
        "length": length, "multiple": True, "hidden": False,
        "hiddenOnAdd": False, "required": required,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def FILE(name, required=False, width=100, **kw):
    w, k, m = make_widget("file-upload", name, "form-file-upload", "icon-shangchuan", {
        "defaultValue": [], "token": "", "length": 0,
        "drag": False, "listStyleType": "card", "multiple": False,
        "multipleDown": True, "disabled": False, "buttonText": "点击上传文件",
        "tokenFunc": "funcGetToken", "hidden": False, "hiddenOnAdd": False,
        "required": required, "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def SLIDER(name, required=False, width=100, min_val=0, max_val=100, show_input=False, **kw):
    w, k, m = make_widget("slider", name, "form-slider", "icon-slider", {
        "defaultValue": 0, "disabled": False, "required": required,
        "min": min_val, "max": max_val, "step": 1,
        "showInput": show_input, "showPercent": False, "range": False,
        "width": "", "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


def RATE(name, required=False, width=100, max_val=5, **kw):
    w, k, m = make_widget("rate", name, "form-rate", "icon-rate", {
        "defaultValue": 0, "max": max_val, "disabled": False,
        "allowHalf": False, "required": required,
        "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, required=required, extra={
        "defaultRules": [{"type": "validator", "message": "", "trigger": "change"}]
    }, **kw)
    return _card_wrap(w, k, m)


def COLOR(name, width=100, **kw):
    w, k, m = make_widget("color", name, "form-color", "icon-color", {
        "defaultValue": "", "disabled": False, "showAlpha": False,
        "required": False, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }, **kw)
    return _card_wrap(w, k, m)


def AUTONUMBER(name, prefix='', width=100, **kw):
    """自动编号控件"""
    rules = [{"type": "number", "mode": 1, "start": 1, "reset": 0, "length": 4, "continue": False}]
    if prefix:
        rules.insert(0, {"type": "text", "value": prefix})
        rules.insert(1, {"type": "date", "format": "yyyyMMdd"})
    w, k, m = make_widget("auto-number", name, "form-auto-number", "icon-hashtag", {
        "numberRules": rules,
        "generateOnAdd": True,
        "placeholder": "自动生成，不需要填写",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }, **kw)
    return _card_wrap(w, k, m)


def HANDSIGN(name, required=False, width=100, **kw):
    w, k, m = make_widget("hand-sign", name, "form-hand-sign", "icon-qianming", {
        "width": "100%", "height": "200px", "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required,
        "fieldNote": "", "autoWidth": width
    }, required=required, **kw)
    return _card_wrap(w, k, m)


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


# ============================================================
# 关联控件
# ============================================================

def LINK_RECORD(name, source_code, title_field, show_fields=None,
                required=False, width=100, show_mode='single', show_type='card',
                is_sub=False, parent_key=None, **kw):
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
        "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }
    w, k, m = make_widget("link-record", name, "form-link-record", "icon-link", opts,
                          required=required, is_sub=is_sub, parent_key=parent_key, **kw)
    # 需要 card 包裹（除非 showMode=many 或 showType=table）
    if show_mode == 'single' and show_type != 'table':
        return _card_wrap(w, k, m)
    return w, k, m


def LINK_FIELD(name, link_record_key, show_field, field_type='input',
               field_options=None, width=100, is_sub=False, parent_key=None, **kw):
    """他表字段控件（与 link-record 配对使用）"""
    opts = {
        "linkRecordKey": link_record_key, "showField": show_field,
        "saveType": "view", "fieldType": field_type,
        "fieldOptions": field_options or {},
        "width": "100%", "defaultValue": "", "readonly": False,
        "disabled": False, "hidden": False, "hiddenOnAdd": False,
        "fieldNote": "", "autoWidth": width
    }
    w, k, m = make_widget("link-field", name, "form-link-field", "icon-field", opts,
                          is_sub=is_sub, parent_key=parent_key, **kw)
    return _card_wrap(w, k, m)


def FORMULA(name, mode='custom', expression='', fields=None,
            width=100, unit='', decimal=2, **kw):
    """公式控件

    Args:
        mode: 'SUM', 'avg', 'max', 'min', 'product', 'custom'
        expression: 自定义表达式（mode='custom' 时使用）
        fields: SUM/avg 等模式时的字段 model 列表
    """
    opts = {
        "type": "number", "mode": mode, "expression": expression,
        "decimal": decimal, "thousand": True, "percent": False,
        "unitPosition": "suffix", "unitText": unit, "emptyAsZero": True,
        "dateBegin": "", "dateEnd": "", "dateFormatMethod": 1,
        "datePrintUnit": "m", "dateAddExp": "", "datePrintFormat": "YYYY-MM-DD",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    }
    if fields and mode != 'custom':
        opts["fields"] = fields
    w, k, m = make_widget("formula", name, "form-formula", "icon-gongshibianji", opts, **kw)
    return _card_wrap(w, k, m)


# ============================================================
# 子表内控件（不需要 card，返回裸控件）
# ============================================================

def SUB_INPUT(name, parent_key, required=False, col_width='200px'):
    w, k, m = make_widget("input", name, "form-input", "icon-input", {
        "width": "100%", "defaultValue": "", "required": required,
        "dataType": None, "pattern": "", "patternMessage": "",
        "placeholder": "", "clearable": False, "readonly": False,
        "disabled": False, "fillRuleCode": "", "showPassword": False,
        "unique": False, "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_INTEGER(name, parent_key, required=False, col_width='120px', unit=''):
    w, k, m = make_widget("integer", name, "form-integer", "icon-integer", {
        "width": "", "placeholder": "", "required": required,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "precision": 0, "controls": True, "disabled": False,
        "controlsPosition": "right", "unitText": unit, "unitPosition": "suffix",
        "showPercent": False, "align": "left", "hidden": False,
        "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_NUMBER(name, parent_key, required=False, col_width='120px', unit=''):
    w, k, m = make_widget("number", name, "form-number", "icon-number", {
        "width": "", "required": required, "defaultValue": 0,
        "placeholder": "", "controls": False,
        "min": 0, "minUnlimited": True, "max": 100, "maxUnlimited": True,
        "step": 1, "disabled": False, "controlsPosition": "right",
        "unitText": unit, "unitPosition": "suffix", "showPercent": False,
        "align": "left", "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_MONEY(name, parent_key, required=False, col_width='150px', unit='元'):
    w, k, m = make_widget("money", name, "form-money", "icon-money", {
        "width": "180px", "placeholder": "", "required": required,
        "unitText": unit, "unitPosition": "suffix", "precision": 2,
        "hidden": False, "disabled": False, "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_SELECT(name, parent_key, options, required=False, col_width='150px'):
    w, k, m = make_widget("select", name, "form-select", "icon-select", {
        "defaultValue": "", "multiple": False, "disabled": False, "clearable": True,
        "placeholder": "", "required": required, "showLabel": False,
        "showType": "default", "width": "", "useColor": False, "colorIteratorIndex": 3,
        "options": _make_options_list(options),
        "remote": False, "filterable": False,
        "remoteOptions": [], "props": {"value": "value", "label": "label"},
        "remoteFunc": "", "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_DATE(name, parent_key, required=False, col_width='180px'):
    w, k, m = make_widget("date", name, "form-date", "icon-date", {
        "defaultValue": "", "defaultValueType": 1,
        "readonly": False, "disabled": False, "editable": True,
        "clearable": True, "placeholder": "", "startPlaceholder": "",
        "endPlaceholder": "", "designType": "date", "type": "date",
        "format": "yyyy-MM-dd", "timestamp": True, "required": required,
        "width": "", "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }, required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_LINK_RECORD(name, parent_key, source_code, title_field, show_fields=None,
                    required=False, col_width='200px'):
    opts = {
        "sourceCode": source_code, "showMode": "single", "showType": "card",
        "titleField": title_field, "showFields": show_fields or [],
        "allowView": True, "allowEdit": True, "allowAdd": True, "allowSelect": True,
        "buttonText": "添加记录", "twoWayModel": "", "dataSelectAuth": "all",
        "filters": [{"matchType": "AND", "rules": []}],
        "search": {"enabled": False, "field": "", "rule": "like", "afterShow": False, "fields": []},
        "createMode": {"add": True, "select": False, "params": {"selectLinkModel": ""}},
        "width": "100%", "defaultValue": "", "defaultValType": "none",
        "required": required, "disabled": False, "hidden": False,
        "isSubTable": False, "isSelf": False,
        "hiddenOnAdd": False, "fieldNote": ""
    }
    w, k, m = make_widget("link-record", name, "form-link-record", "icon-link", opts,
                          required=required, is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_LINK_FIELD(name, parent_key, link_record_key, show_field,
                   field_type='input', field_options=None, col_width='150px'):
    opts = {
        "linkRecordKey": link_record_key, "showField": show_field,
        "saveType": "view", "fieldType": field_type,
        "fieldOptions": field_options or {},
        "width": "100%", "defaultValue": "", "readonly": False,
        "disabled": False, "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }
    w, k, m = make_widget("link-field", name, "form-link-field", "icon-field", opts,
                          is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


def SUB_FORMULA(name, parent_key, mode='custom', expression='', col_width='150px', unit=''):
    opts = {
        "type": "number", "mode": mode, "expression": expression,
        "decimal": 2, "thousand": True, "percent": False,
        "unitPosition": "suffix", "unitText": unit, "emptyAsZero": True,
        "dateBegin": "", "dateEnd": "", "dateFormatMethod": 1,
        "datePrintUnit": "m", "dateAddExp": "", "datePrintFormat": "YYYY-MM-DD",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": ""
    }
    w, k, m = make_widget("formula", name, "form-formula", "icon-gongshibianji", opts,
                          is_sub=True, parent_key=parent_key)
    w["subOptions"]["width"] = col_width
    return w, k, m


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

    真实 Word 风格通过 CSS class `form-grid form-grid-word-theme` + 外部 CSS
    `/desform/expand/css/theme-word.css` 实现表格边框效果。

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


def _apply_word_layout(widgets, form_name=''):
    """将 widgets 列表转换为 Word 风格布局（匹配 JeecgBoot 真实实现）

    真实 Word 风格特征：
    - 顶部有独立的 text 标题控件（24px 加粗居中）
    - 每行是 grid 容器，className = 'form-grid form-grid-word-theme'
    - 适合半行的控件两两配对（标签6+值6 | 标签4+值8）
    - textarea/file-upload/hand-sign 等宽控件独占一行（标签6+值18）
    - formStyle 保持 'normal'，样式由外部 CSS theme-word.css 驱动

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

            # 宽控件独占一行
            grid = make_word_grid(item, cols_per_row=1)
            top_items.append(grid)
            all_models.append((key, model))

    if half_buffer is not None:
        grid = make_word_grid(half_buffer[0], cols_per_row=1)
        top_items.append(grid)
        all_models.append((half_buffer[1], half_buffer[2]))

    return top_items, all_models


def build_design_json(widgets, title_model, form_style='normal'):
    """组装完整的 desformDesignJson

    Args:
        widgets: 顶层控件列表（card 包裹的和不需要 card 的混合）
        title_model: 标题字段的 model
        form_style: 表单风格 'normal' 或 'word'
            - 'normal': 默认风格
            - 'word': Word 风格（formStyle 保持 normal，通过 CSS class + 外部 CSS 实现）
    """
    is_word = (form_style == 'word')
    has_widgets = sorted(list(_collect_types(widgets)))

    # Word 风格：加载外部 theme-word.css，关闭自动栅格和顶部标题
    if is_word:
        expand = {"js": "", "css": "", "url": {"js": "", "css": "/desform/expand/css/theme-word.css"}}
        show_header = False
        disabled_auto_grid = True
        dialog_top = 60
        dialog_width = 1100
        allow_print = True
    else:
        expand = {"js": "", "css": "", "url": {"js": "", "css": ""}}
        show_header = True
        disabled_auto_grid = False
        dialog_top = 20
        dialog_width = 1000
        allow_print = False

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


def save_design(form_id, form_code, widgets, title_model, update_count=1, form_style='normal'):
    """保存表单设计到 API

    Args:
        form_id: 表单 ID
        form_code: 表单编码（用于日志）
        widgets: 顶层控件列表
        title_model: 标题字段 model
        update_count: 当前 updateCount（从 find_or_create_form 获取）
        form_style: 表单风格 'normal' 或 'word'

    Returns:
        API 响应 dict
    """
    design_json = build_design_json(widgets, title_model, form_style)
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


def create_form(name, code, widgets, title_index=0, layout='auto'):
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
    save_design(form_id, actual_code, top_items, title_model, uc, form_style)
    # 更新缓存
    _cache_put(actual_code, form_id, uc + 1)

    return form_id, title_model
