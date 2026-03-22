"""
JeecgBoot 设计器表单通用创建脚本
=================================
通过 JSON 配置文件创建/更新设计器表单，避免每次编写大量 Python 代码。

用法:
  python desform_creator.py --api-base <URL> --token <TOKEN> --config <config.json>
  python desform_creator.py --api-base <URL> --token <TOKEN> --config <config.json> --force

参数:
  --api-base   JeecgBoot 后端地址
  --token      X-Access-Token
  --config     JSON 配置文件路径
  --force      强制覆盖已存在的表单（默认检测到已存在时退出）

JSON 配置格式:
{
  "formName": "工程竣工验收申请表",
  "formCode": "eng_completion_acceptance",
  "layout": "word",            // auto|half|full|word，默认 auto
  "titleIndex": 0,             // 标题字段索引，默认 0（第一个非分隔符字段）
  "fields": [
    {"name": "自动编号", "type": "auto-number", "prefix": "GCYS"},
    {"name": "条码", "type": "barcode"},
    {"name": "工程名称", "type": "input", "required": true},
    {"name": "工程类别", "type": "radio", "options": ["土建", "安装"]},
    {"name": "开工时间", "type": "date"},
    {"name": "工程量清单", "type": "textarea"},
    {"name": "图片上传", "type": "imgupload"},
    {"name": "定位", "type": "location"},
    {"name": "签字", "type": "hand-sign"},
    {"name": "---", "type": "divider", "text": "第二部分"},
    {"name": "金额", "type": "money", "unit": "万元"},
    {"name": "状态", "type": "select", "options": ["启用", "禁用"]},
    {"name": "性别", "type": "radio", "dictCode": "sex",
     "options": [{"value": "1", "label": "男"}, {"value": "2", "label": "女"}]}
  ],
  "menuParent": "工程管理",     // 可选，生成菜单 SQL 的父菜单名称
  "menuIcon": "ant-design:tool-outlined"  // 可选，父菜单图标
}

支持的 type 值:
  基础: input, textarea, number, integer, money, date, time, switch, slider, rate, color
  选择: radio, select, checkbox（支持 options + dictCode）
  系统: select-user, select-depart, phone, email, area-linkage
  文件: file-upload, imgupload, hand-sign
  高级: auto-number, formula, barcode, location, link-record, link-field
  布局: divider, editor, markdown
"""

import argparse
import json
import sys
import os

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 自动定位 desform_utils.py
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPT_DIR)
for _path in [os.getcwd(), _SCRIPT_DIR]:
    if os.path.exists(os.path.join(_path, 'desform_utils.py')):
        sys.path.insert(0, _path)
        break

from desform_utils import *


# ============================================================
# desform_utils 未内置的控件
# ============================================================
def _BARCODE(name, width=100, **kw):
    """条码控件"""
    code_type = kw.pop('codeType', 'barcode')
    w, k, m = make_widget("barcode", name, "form-barcode", "icon-tiaoma", {
        "maxWidth": 180, "codeType": code_type, "sourceModel": "",
        "hidden": False, "hiddenOnAdd": False, "fieldNote": "", "autoWidth": width
    })
    return make_card(w), k, m


def _LOCATION(name, required=False, width=100, **kw):
    """定位控件"""
    w, k, m = make_widget("location", name, "form-location", "icon-location", {
        "width": "100%", "defaultValue": "", "defaultCurrent": False,
        "showLngLat": False, "showMap": False, "disabled": False,
        "hidden": False, "hiddenOnAdd": False, "required": required,
        "fieldNote": "", "autoWidth": width
    }, required=required)
    return make_card(w), k, m


# ============================================================
# type → 工厂函数 映射
# ============================================================
_TYPE_MAP = {
    # 基础
    'input': INPUT,
    'textarea': TEXTAREA,
    'number': NUMBER,
    'integer': INTEGER,
    'money': MONEY,
    'date': DATE,
    'time': TIME,
    'switch': SWITCH,
    'slider': SLIDER,
    'rate': RATE,
    'color': COLOR,
    # 选择
    'radio': RADIO,
    'select': SELECT,
    'checkbox': CHECKBOX,
    # 系统
    'select-user': USER,
    'select-depart': DEPART,
    'phone': PHONE,
    'email': EMAIL,
    'area-linkage': AREA,
    # 文件
    'file-upload': FILE,
    'imgupload': IMGUPLOAD,
    'hand-sign': HANDSIGN,
    # 高级
    'auto-number': AUTONUMBER,
    'formula': FORMULA,
    'barcode': _BARCODE,
    'location': _LOCATION,
    'link-record': LINK_RECORD,
    'link-field': LINK_FIELD,
    # 布局
    'divider': DIVIDER,
    'editor': EDITOR,
    'markdown': MARKDOWN,
}

# 需要 options 参数的控件类型（options 作为第二个位置参数）
_OPTION_TYPES = {'radio', 'select', 'checkbox'}

# 参数名映射：JSON key → 函数参数名
_PARAM_MAP = {
    'required': 'required',
    'width': 'width',
    'prefix': 'prefix',
    'unit': 'unit',
    'placeholder': 'placeholder',
    'multiple': 'multiple',
    'dictCode': 'dict_code',
    'unique': 'unique',
    'precision': 'precision',
    'fmt': 'fmt',
    'codeType': 'codeType',
    # formula
    'mode': 'mode',
    'expression': 'expression',
    'decimal': 'decimal',
    # link-record
    'sourceCode': 'source_code',
    'titleField': 'title_field',
    'showFields': 'show_fields',
    'showMode': 'show_mode',
    'showType': 'show_type',
    # link-field
    'linkRecordKey': 'link_record_key',
    'showField': 'show_field',
    'fieldType': 'field_type',
    'fieldOptions': 'field_options',
}


def build_widget(field_def):
    """根据 JSON 字段定义构建控件 tuple"""
    ftype = field_def['type']
    name = field_def['name']

    factory = _TYPE_MAP.get(ftype)
    if not factory:
        raise ValueError(f'未知的控件类型: {ftype}')

    # 构建关键字参数
    kwargs = {}
    for json_key, param_name in _PARAM_MAP.items():
        if json_key in field_def:
            kwargs[param_name] = field_def[json_key]

    # divider 特殊处理：text 参数
    if ftype == 'divider':
        text = field_def.get('text', name)
        return factory(text)

    # 需要 options 的控件
    if ftype in _OPTION_TYPES:
        options = field_def.get('options', [])
        return factory(name, options, **kwargs)

    # auto-number 特殊处理
    if ftype == 'auto-number':
        return factory(name, **kwargs)

    # 其余控件：name + kwargs
    return factory(name, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='JeecgBoot 设计器表单通用创建工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='JSON 配置文件路径')
    parser.add_argument('--force', action='store_true', help='强制覆盖已存在的表单')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    form_name = config['formName']
    form_code = config['formCode']
    layout = config.get('layout', 'auto')
    title_index = config.get('titleIndex', 0)

    init_api(args.api_base, args.token)

    # 防覆盖检查
    existing_id, _ = get_form_id(form_code)
    if existing_id and not args.force:
        print(f'[阻止] 表单 {form_code} 已存在 (ID={existing_id})')
        print(f'如需覆盖，请加 --force 参数')
        sys.exit(1)

    # 构建控件列表
    fields = config.get('fields', [])
    widgets = []
    for fd in fields:
        widget = build_widget(fd)
        widgets.append(widget)

    # 创建表单
    form_id, title_model = create_form(form_name, form_code, widgets,
                                        title_index=title_index, layout=layout)

    print(f'\n{"=" * 50}')
    print(f'表单创建成功')
    print(f'{"=" * 50}')
    print(f'  表单ID:   {form_id}')
    print(f'  表单名称: {form_name}')
    print(f'  表单编码: {form_code}')
    print(f'  标题字段: {title_model}')
    print(f'  布局风格: {layout}')

    # 生成菜单 SQL
    menu_parent = config.get('menuParent')
    if menu_parent:
        menu_icon = config.get('menuIcon', 'ant-design:appstore-outlined')
        sql = gen_menu_sql(menu_parent, [
            (form_name, form_code, 1),
        ], icon=menu_icon)
        print(f'\n--- 菜单 SQL ---\n{sql}')


if __name__ == '__main__':
    main()
