"""
JeecgBoot Online 表单创建/编辑工具脚本

用法:
  python onlform_creator.py --api-base <URL> --token <TOKEN> --config <config.json>

config.json 格式见下方示例。

支持的操作:
  - 单表创建 (tableType=1)
  - 主子表创建 (主表 tableType=2 + 子表 tableType=3)
  - 树表创建 (tableType=1, isTree='Y')
  - 编辑表单 (action='edit')
"""

import urllib.request
import json
import sys
import random
import string

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import argparse


# ====== 工具函数 ======

def rand_id(prefix=''):
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f'{prefix}{suffix}'


def api_request(api_base, token, path, data=None, method='POST'):
    url = f'{api_base}{path}'
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode('utf-8'))


def make_system_fields():
    """生成6个系统默认字段"""
    return [
        {"id": rand_id("id"), "dbFieldName": "id", "dbFieldTxt": "主键", "queryConfigFlag": "0", "fieldMustInput": "1", "isShowForm": 0, "isShowList": 0, "isReadOnly": 1, "fieldShowType": "text", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 36, "dbPointLength": 0, "dbType": "string", "dbIsKey": 1, "dbIsNull": 0, "orderNum": 0},
        {"id": rand_id("createby"), "dbFieldName": "create_by", "dbFieldTxt": "创建人", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": 0, "isShowList": 0, "sortFlag": "0", "isReadOnly": 0, "fieldShowType": "text", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "string", "dbIsKey": 0, "dbIsNull": 1, "orderNum": 1},
        {"id": rand_id("createti"), "dbFieldName": "create_time", "dbFieldTxt": "创建时间", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": 0, "isShowList": 0, "sortFlag": "0", "isReadOnly": 0, "fieldShowType": "datetime", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "Datetime", "dbIsKey": 0, "dbIsNull": 1, "orderNum": 2},
        {"id": rand_id("updateby"), "dbFieldName": "update_by", "dbFieldTxt": "更新人", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": 0, "isShowList": 0, "sortFlag": "0", "isReadOnly": 0, "fieldShowType": "text", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "string", "dbIsKey": 0, "dbIsNull": 1, "orderNum": 3},
        {"id": rand_id("updateti"), "dbFieldName": "update_time", "dbFieldTxt": "更新时间", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": 0, "isShowList": 0, "sortFlag": "0", "isReadOnly": 0, "fieldShowType": "datetime", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "Datetime", "dbIsKey": 0, "dbIsNull": 1, "orderNum": 4},
        {"id": rand_id("sysorgco"), "dbFieldName": "sys_org_code", "dbFieldTxt": "所属部门", "queryConfigFlag": "0", "fieldMustInput": "0", "isShowForm": 0, "isShowList": 0, "sortFlag": "0", "isReadOnly": 0, "fieldShowType": "text", "fieldLength": 120, "isQuery": 0, "queryMode": "single", "dbLength": 50, "dbPointLength": 0, "dbType": "string", "dbIsKey": 0, "dbIsNull": 1, "orderNum": 5},
    ]


def make_field(order, db_name, db_txt, show_type='text', db_type='string', db_length=100,
               db_point=0, must_input='0', is_query=0, query_mode='single',
               is_show_form=1, is_show_list=1, is_read_only=0, sort_flag='0',
               dict_field='', dict_table='', dict_text='',
               field_valid_type='', field_default_value='', field_extend_json='',
               field_length=120, main_table='', main_field='',
               query_config_flag='0', query_show_type=None,
               query_dict_field='', query_dict_table='', query_dict_text='', query_def_val=''):
    """生成业务字段配置"""
    return {
        "id": rand_id(db_name[:8]),
        "dbFieldName": db_name,
        "dbFieldTxt": db_txt,
        "queryShowType": query_show_type,
        "queryDictTable": query_dict_table,
        "queryDictField": query_dict_field,
        "queryDictText": query_dict_text,
        "queryDefVal": query_def_val,
        "queryConfigFlag": query_config_flag,
        "mainTable": main_table,
        "mainField": main_field,
        "fieldHref": "",
        "fieldValidType": field_valid_type,
        "fieldMustInput": must_input,
        "dictTable": dict_table,
        "dictField": dict_field,
        "dictText": dict_text,
        "isShowForm": is_show_form,
        "isShowList": is_show_list,
        "sortFlag": sort_flag,
        "isReadOnly": is_read_only,
        "fieldShowType": show_type,
        "fieldLength": field_length,
        "isQuery": is_query,
        "queryMode": query_mode,
        "fieldDefaultValue": field_default_value,
        "converter": "",
        "fieldExtendJson": field_extend_json,
        "dbLength": db_length,
        "dbPointLength": db_point,
        "dbType": db_type,
        "dbIsKey": 0,
        "dbIsNull": 1,
        "orderNum": order,
    }


def make_ext_config():
    """生成默认扩展配置JSON字符串"""
    return json.dumps({
        "reportPrintShow": 0, "reportPrintUrl": "",
        "joinQuery": 0, "modelFullscreen": 0, "modalMinWidth": "",
        "commentStatus": 0, "tableFixedAction": 1,
        "tableFixedActionType": "right",
        "formLabelLengthShow": 0, "formLabelLength": None,
        "enableExternalLink": 0, "externalLinkActions": "add,edit,detail"
    }, ensure_ascii=False)


def build_fields_from_config(field_configs):
    """从配置列表构建字段数组（含系统字段）"""
    fields = make_system_fields()
    for i, fc in enumerate(field_configs):
        order = 6 + i
        fields.append(make_field(
            order=order,
            db_name=fc['dbFieldName'],
            db_txt=fc['dbFieldTxt'],
            show_type=fc.get('fieldShowType', 'text'),
            db_type=fc.get('dbType', 'string'),
            db_length=fc.get('dbLength', 100),
            db_point=fc.get('dbPointLength', 0),
            must_input=fc.get('fieldMustInput', '0'),
            is_query=fc.get('isQuery', 0),
            query_mode=fc.get('queryMode', 'single'),
            is_show_form=fc.get('isShowForm', 1),
            is_show_list=fc.get('isShowList', 1),
            is_read_only=fc.get('isReadOnly', 0),
            sort_flag=fc.get('sortFlag', '0'),
            dict_field=fc.get('dictField', ''),
            dict_table=fc.get('dictTable', ''),
            dict_text=fc.get('dictText', ''),
            field_valid_type=fc.get('fieldValidType', ''),
            field_default_value=fc.get('fieldDefaultValue', ''),
            field_extend_json=fc.get('fieldExtendJson', ''),
            field_length=fc.get('fieldLength', 120),
            main_table=fc.get('mainTable', ''),
            main_field=fc.get('mainField', ''),
            query_config_flag=fc.get('queryConfigFlag', '0'),
            query_show_type=fc.get('queryShowType', None),
            query_dict_field=fc.get('queryDictField', ''),
            query_dict_table=fc.get('queryDictTable', ''),
            query_dict_text=fc.get('queryDictText', ''),
            query_def_val=fc.get('queryDefVal', ''),
        ))
    return fields


def build_head(table_config):
    """从表配置构建 head 对象"""
    head = {
        "tableVersion": "1",
        "tableName": table_config['tableName'],
        "tableTxt": table_config['tableTxt'],
        "tableType": table_config.get('tableType', 1),
        "formCategory": table_config.get('formCategory', 'temp'),
        "idType": table_config.get('idType', 'UUID'),
        "isCheckbox": table_config.get('isCheckbox', 'Y'),
        "themeTemplate": table_config.get('themeTemplate', 'normal'),
        "formTemplate": table_config.get('formTemplate', '1'),
        "scroll": table_config.get('scroll', 1),
        "isPage": table_config.get('isPage', 'Y'),
        "isTree": table_config.get('isTree', 'N'),
        "extConfigJson": table_config.get('extConfigJson', make_ext_config()),
        "isDesForm": "N",
        "desFormCode": ""
    }
    # 主表额外字段
    if table_config.get('tableType') == 2:
        head['subTableStr'] = table_config.get('subTableStr', '')
    # 子表额外字段
    if table_config.get('tableType') == 3:
        head['relationType'] = table_config.get('relationType', 0)
        head['tabOrderNum'] = table_config.get('tabOrderNum', 1)
    # 树表额外字段
    if table_config.get('isTree') == 'Y':
        head['treeParentIdField'] = table_config.get('treeParentIdField', 'pid')
        head['treeIdField'] = table_config.get('treeIdField', 'has_child')
        head['treeFieldname'] = table_config.get('treeFieldname', 'name')
    return head


def build_indexs(index_configs):
    """从索引配置列表构建索引数组"""
    indexs = []
    for ic in (index_configs or []):
        indexs.append({
            "id": rand_id("idx"),
            "indexName": ic['indexName'],
            "indexField": ic['indexField'],
            "indexType": ic.get('indexType', 'normal')
        })
    return indexs


def create_table(api_base, token, table_config):
    """创建单个表并返回 headId"""
    table_name = table_config['tableName']
    table_txt = table_config['tableTxt']
    print(f'\n{"=" * 50}')
    print(f'创建表: {table_name} ({table_txt})')
    print(f'{"=" * 50}')

    fields = build_fields_from_config(table_config.get('fields', []))
    head = build_head(table_config)
    indexs = build_indexs(table_config.get('indexs'))

    form_data = {
        "head": head,
        "fields": fields,
        "indexs": indexs,
        "deleteFieldIds": [],
        "deleteIndexIds": []
    }

    result = api_request(api_base, token, '/online/cgform/api/addAll', form_data)
    print(f'创建结果: success={result.get("success")}, message={result.get("message")}')

    if not result.get('success'):
        print(f'创建失败: {result.get("message")}')
        return None

    # 查询 headId
    list_result = api_request(api_base, token,
                              f'/online/cgform/head/list?tableName={table_name}&pageNo=1&pageSize=1',
                              method='GET')
    if list_result.get('success') and list_result['result']['records']:
        head_id = list_result['result']['records'][0]['id']
        print(f'headId: {head_id}')

        # 同步数据库
        sync = api_request(api_base, token,
                           f'/online/cgform/api/doDbSynch/{head_id}/normal',
                           method='POST')
        print(f'同步数据库: success={sync.get("success")}, message={sync.get("message")}')
        return head_id
    else:
        print('查询 headId 失败，请手动同步数据库')
        return None


def edit_table(api_base, token, edit_config):
    """编辑现有表单"""
    head_id = edit_config['headId']
    print(f'\n{"=" * 50}')
    print(f'编辑表单: headId={head_id}')
    print(f'{"=" * 50}')

    # 查询现有配置
    detail = api_request(api_base, token,
                         f'/online/cgform/api/getByHead?id={head_id}',
                         method='GET')
    if not detail.get('success'):
        print(f'查询失败: {detail.get("message")}')
        return None

    head = detail['result']['head']
    fields = detail['result']['fields']
    indexs = detail['result'].get('indexs', [])
    delete_field_ids = []

    # 添加新字段
    for fc in edit_config.get('addFields', []):
        new_order = max(f['orderNum'] for f in fields) + 1
        fields.append(make_field(
            order=new_order,
            db_name=fc['dbFieldName'],
            db_txt=fc['dbFieldTxt'],
            show_type=fc.get('fieldShowType', 'text'),
            db_type=fc.get('dbType', 'string'),
            db_length=fc.get('dbLength', 100),
            db_point=fc.get('dbPointLength', 0),
            must_input=fc.get('fieldMustInput', '0'),
            is_query=fc.get('isQuery', 0),
            query_mode=fc.get('queryMode', 'single'),
            is_show_form=fc.get('isShowForm', 1),
            is_show_list=fc.get('isShowList', 1),
            dict_field=fc.get('dictField', ''),
            dict_table=fc.get('dictTable', ''),
            dict_text=fc.get('dictText', ''),
            field_extend_json=fc.get('fieldExtendJson', ''),
            field_length=fc.get('fieldLength', 120),
        ))
        print(f'  新增字段: {fc["dbFieldName"]} ({fc["dbFieldTxt"]})')

    # 删除字段
    for field_name in edit_config.get('deleteFields', []):
        for f in fields:
            if f['dbFieldName'] == field_name:
                delete_field_ids.append(f['id'])
                fields.remove(f)
                print(f'  删除字段: {field_name}')
                break

    # 修改字段
    for mc in edit_config.get('modifyFields', []):
        target_name = mc['dbFieldName']
        for f in fields:
            if f['dbFieldName'] == target_name:
                for key, val in mc.items():
                    if key != 'dbFieldName':
                        f[key] = val
                print(f'  修改字段: {target_name}')
                break

    edit_data = {
        "head": head,
        "fields": fields,
        "indexs": indexs,
        "deleteFieldIds": delete_field_ids,
        "deleteIndexIds": []
    }

    result = api_request(api_base, token, '/online/cgform/api/editAll', edit_data, method='PUT')
    print(f'编辑结果: success={result.get("success")}, message={result.get("message")}')

    if result.get('success'):
        # 同步数据库
        sync = api_request(api_base, token,
                           f'/online/cgform/api/doDbSynch/{head_id}/normal',
                           method='POST')
        print(f'同步数据库: success={sync.get("success")}, message={sync.get("message")}')
    return head_id


def print_menu_sql(head_id, table_txt):
    """输出菜单SQL"""
    menu_id = head_id.replace('-', '')[:32]
    print(f"""
--- 菜单 SQL（可选）---

INSERT INTO sys_permission(id, parent_id, name, url, component, component_name, redirect, menu_type, perms, perms_type, sort_no, always_show, icon, is_route, is_leaf, keep_alive, hidden, hide_tab, description, status, del_flag, rule_flag, create_by, create_time, update_by, update_time, internal_or_external)
VALUES ('{menu_id}', NULL, '{table_txt}', '/online/cgformList/{head_id}', '1', 'OnlineAutoList', NULL, 0, NULL, '1', 0.00, 0, NULL, 0, 1, 0, 0, 0, NULL, '1', 0, 0, 'admin', now(), NULL, NULL, 0);
""")


def main():
    parser = argparse.ArgumentParser(description='JeecgBoot Online 表单创建/编辑工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    action = config.get('action', 'create')

    if action == 'create':
        # 创建表单（支持单表、主子表、树表）
        tables = config.get('tables', [])
        if not tables:
            print('错误: 配置文件中没有 tables 定义')
            sys.exit(1)

        head_ids = {}
        for table_config in tables:
            head_id = create_table(args.api_base, args.token, table_config)
            if head_id:
                head_ids[table_config['tableName']] = head_id

        # 输出汇总
        print(f'\n{"=" * 50}')
        print('创建完成汇总')
        print(f'{"=" * 50}')
        for tname, hid in head_ids.items():
            print(f'  {tname} -> headId: {hid}')

        # 为主表输出菜单SQL
        main_table = tables[0]
        main_head_id = head_ids.get(main_table['tableName'])
        if main_head_id:
            print_menu_sql(main_head_id, main_table['tableTxt'])

    elif action == 'edit':
        head_id = edit_table(args.api_base, args.token, config)
        if head_id:
            print('\n编辑完成!')

    else:
        print(f'未知操作类型: {action}')
        sys.exit(1)


if __name__ == '__main__':
    main()
