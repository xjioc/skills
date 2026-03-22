"""
积木报表 (JiMu Report) 创建/编辑工具脚本

用法:
  python jimureport_creator.py --api-base <URL> --token <TOKEN> --config <config.json>

config.json 格式见下方示例。

支持的操作:
  - 创建报表 (action='create')
  - 编辑报表 (action='edit', 需提供 reportId)

config.json 示例（创建）:
{
    "action": "create",
    "reportName": "用户数据统计报表",
    "datasets": [
        {
            "dbCode": "userlist",
            "dbChName": "用户列表",
            "dbDynSql": "SELECT username, realname, sex FROM sys_user WHERE del_flag = 0",
            "isPage": "1"
        },
        {
            "dbCode": "sexchart",
            "dbChName": "性别图表",
            "dbDynSql": "SELECT sex AS name, COUNT(*) AS value FROM sys_user WHERE del_flag = 0 GROUP BY sex",
            "isPage": "0",
            "forChart": true
        }
    ],
    "layout": "chart_top",
    "table": {
        "datasetCode": "userlist",
        "title": "用户数据列表",
        "columns": [
            {"field": "username", "title": "用户账号", "width": 120},
            {"field": "realname", "title": "姓名", "width": 100},
            {"field": "sex", "title": "性别", "width": 80}
        ]
    },
    "chart": {
        "datasetCode": "sexchart",
        "chartType": "pie.doughnut",
        "title": "按性别统计",
        "width": "650",
        "height": "300"
    }
}
"""

import urllib.request
import json
import sys
import time
import random
import hashlib
import ssl
import argparse

# 修复 Windows 控制台中文乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SIGNATURE_SECRET = 'dd05f1c54d63749eda95f9fa6d49v442a'

SIGNED_ENDPOINTS = [
    '/jmreport/queryFieldBySql',
    '/jmreport/executeSelectApi',
    '/jmreport/loadTableData',
    '/jmreport/testConnection',
    '/jmreport/download/image',
    '/jmreport/dictCodeSearch',
    '/jmreport/getDataSourceByPage',
    '/jmreport/getDataSourceById',
]

# 默认样式列表
DEFAULT_STYLES = [
    # 0: 仅边框
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}},
    # 1: 边框+居中
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center"},
    # 2: 边框+居中+垂直居中（数据行）
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle"},
    # 3: 边框+居中+垂直居中+蓝底（表头无白字）
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1"},
    # 4: 边框+居中+垂直居中+蓝底白字（表头推荐）
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1", "color": "#ffffff"},
    # 5: 边框+居中+垂直居中+深蓝底白字加粗（大标题）
    {"border": {"bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"]}, "align": "center", "valign": "middle", "bgcolor": "#4472C4", "color": "#ffffff", "font": {"bold": True}},
]

# 默认图表配色
DEFAULT_CHART_COLORS = ["#5470c6", "#ee6666", "#91cc75", "#fac858", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]


# ====== 工具函数 ======

def gen_id():
    """生成唯一ID"""
    return str(int(time.time() * 1000) * 1000000 + random.randint(100000, 999999))


def compute_sign(params_dict):
    """计算积木报表接口签名"""
    str_params = {}
    for k, v in params_dict.items():
        if v is None:
            continue
        if isinstance(v, bool):
            str_params[k] = str(v).lower()
        elif isinstance(v, (int, float)):
            str_params[k] = str(v)
        elif isinstance(v, (dict, list)):
            str_params[k] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
        else:
            str_params[k] = str(v)
    sorted_params = dict(sorted(str_params.items()))
    params_json = json.dumps(sorted_params, ensure_ascii=False, separators=(',', ':'))
    sign_str = params_json + SIGNATURE_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def create_ssl_context():
    """创建不验证证书的SSL上下文"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


SSL_CTX = create_ssl_context()


def api_request(api_base, token, path, data=None, method=None):
    """发送API请求，自动处理签名"""
    url = f'{api_base}{path}'
    headers = {
        'X-Access-Token': token,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    need_sign = any(path.rstrip('/').endswith(ep.rstrip('/')) for ep in SIGNED_ENDPOINTS)
    if need_sign:
        sign_params = data if data else {}
        headers['X-TIMESTAMP'] = str(int(time.time() * 1000))
        headers['X-Sign'] = compute_sign(sign_params)
    if data is not None:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method or 'POST')
    else:
        req = urllib.request.Request(url, headers=headers, method=method or 'GET')
    resp = urllib.request.urlopen(req, context=SSL_CTX)
    return json.loads(resp.read().decode('utf-8'))


# ====== 数据集相关 ======

def parse_sql_fields(api_base, token, sql, db_source=''):
    """解析SQL获取字段列表"""
    result = api_request(api_base, token, '/jmreport/queryFieldBySql', {
        "sql": sql, "dbSource": db_source, "type": "0"
    })
    if not result.get('success'):
        print(f'  SQL解析失败: {result.get("message")}')
        return [], []
    field_list = result.get('result', {}).get('fieldList', [])
    param_list = result.get('result', {}).get('paramList', [])
    return field_list, param_list


def save_dataset(api_base, token, report_id, ds_config, field_list, param_list):
    """保存数据集，返回数据集ID"""
    db_data = {
        "izSharedSource": 0,
        "jimuReportId": report_id,
        "dbCode": ds_config['dbCode'],
        "dbChName": ds_config.get('dbChName', ds_config['dbCode']),
        "dbType": ds_config.get('dbType', '0'),
        "dbSource": ds_config.get('dbSource', ''),
        "jsonData": ds_config.get('jsonData', ''),
        "apiConvert": ds_config.get('apiConvert', ''),
        "isList": ds_config.get('isList', '1'),
        "isPage": ds_config.get('isPage', '1'),
        "dbDynSql": ds_config.get('dbDynSql', ''),
        "fieldList": field_list,
        "paramList": param_list
    }
    result = api_request(api_base, token, '/jmreport/saveDb', db_data)
    if not result.get('success'):
        print(f'  数据集保存失败: {result.get("message")}')
        return None
    return result['result']['id']


# ====== 报表布局构造 ======

def build_cols(columns):
    """根据列配置构造cols对象"""
    cols = {"len": 100}
    for i, col in enumerate(columns):
        if col.get('width'):
            cols[str(i + 1)] = {"width": col['width']}
    return cols


def build_table_rows(table_config, start_row=1, title_style=5, header_style=4, data_style=2):
    """
    构造数据表格的rows、merges。
    返回 (rows_dict, merges_list, next_row)
    """
    rows = {}
    merges = []
    columns = table_config.get('columns', [])
    ds_code = table_config['datasetCode']
    col_count = len(columns)
    current_row = start_row

    # 标题行
    title = table_config.get('title')
    if title:
        cells = {}
        for i in range(col_count):
            cells[str(i + 1)] = {"text": title if i == 0 else "", "style": title_style}
        rows[str(current_row)] = {"cells": cells, "height": 40}
        if col_count > 1:
            start_col = chr(ord('A') + 1)  # B列开始（列索引1对应B）
            end_col = chr(ord('A') + col_count)
            # merge 使用 UI 行号（代码行号+1，因为代码row 0 = UI row 1）
            ui_row = current_row + 1
            merges.append(f"{start_col}{ui_row}:{end_col}{ui_row}")
        current_row += 1

    # 表头行
    header_cells = {}
    for i, col in enumerate(columns):
        header_cells[str(i + 1)] = {"text": col['title'], "style": header_style}
    rows[str(current_row)] = {"cells": header_cells, "height": 34}
    current_row += 1

    # 数据绑定行
    data_cells = {}
    for i, col in enumerate(columns):
        data_cells[str(i + 1)] = {"text": f"#{{{ds_code}.{col['field']}}}", "style": data_style}
    rows[str(current_row)] = {"cells": data_cells}
    current_row += 1

    return rows, merges, current_row


def build_chart_rows(chart_config, chart_db_id, start_row=1, col_start=1, col_end=6, row_count=1):
    """
    构造图表的虚拟单元格rows和chartList。
    row_count 默认为1行（与设计器行为一致，图表通过width/height属性控制大小，
    虚拟单元格仅作为锚点，不需要覆盖整个图表区域）。
    返回 (rows_dict, chart_list, next_row)
    """
    layer_id = "chart_" + gen_id()
    rows = {}
    virtual_cell_range = []

    for r in range(start_row, start_row + row_count):
        cells = {}
        for c in range(col_start, col_end + 1):
            cells[str(c)] = {"text": " ", "virtual": layer_id}
            virtual_cell_range.append([r, c])
        rows[str(r)] = {"cells": cells}

    # ECharts 配置
    chart_type = chart_config.get('chartType', 'bar.simple')
    echarts_config = build_echarts_config(chart_type, chart_config)

    chart_item = {
        "row": start_row,
        "col": col_start,
        "colspan": 0,
        "rowspan": 0,
        "width": str(chart_config.get('width', '650')),
        "height": str(chart_config.get('height', '350')),
        "config": json.dumps(echarts_config, ensure_ascii=False),
        "url": "",
        "extData": {
            "chartType": chart_type,
            "dataType": chart_config.get('dataType', 'sql'),
            "dataId": chart_db_id,
            "dbCode": chart_config['datasetCode'],
            "axisX": "name",
            "axisY": "value",
            "series": "type",
            "xText": "",
            "yText": "",
            "apiStatus": "1"
        },
        "layer_id": layer_id,
        "offsetX": 0,
        "offsetY": 0,
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "virtualCellRange": virtual_cell_range
    }

    return rows, [chart_item], start_row + row_count


def build_echarts_config(chart_type, chart_config):
    """根据图表类型构造ECharts配置"""
    title_text = chart_config.get('title', '')
    colors = chart_config.get('colors', DEFAULT_CHART_COLORS)

    if chart_type.startswith('pie'):
        # 饼图/环形图/玫瑰图
        radius = ["40%", "70%"] if 'doughnut' in chart_type else "70%"
        if 'rose' in chart_type:
            radius = [20, "70%"]
        return {
            "title": {"text": title_text, "left": "center", "textStyle": {"fontSize": 16}},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
            "legend": {"orient": "vertical", "left": "left", "top": "middle"},
            "series": [{
                "type": "pie",
                "radius": radius,
                "center": ["55%", "55%"],
                "avoidLabelOverlap": True,
                "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": True, "formatter": "{b}: {c}"},
                "emphasis": {"label": {"show": True, "fontSize": 16, "fontWeight": "bold"}},
                "data": [],
                "roseType": "area" if 'rose' in chart_type else None
            }],
            "color": colors
        }
    elif chart_type.startswith('bar'):
        # 柱状图
        is_horizontal = 'horizontal' in chart_type
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"bottom": 0},
            "xAxis": [{"type": "value" if is_horizontal else "category", "data": []}],
            "yAxis": [{"type": "category" if is_horizontal else "value", "data": []}],
            "series": [{"type": "bar", "data": [], "itemStyle": {"color": colors[0]}}],
            "color": colors
        }
    elif chart_type.startswith('line'):
        # 折线图
        smooth = 'smooth' in chart_type
        area_style = {"opacity": 0.3} if 'area' in chart_type else None
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"bottom": 0},
            "xAxis": [{"type": "category", "data": []}],
            "yAxis": [{"type": "value"}],
            "series": [{"type": "line", "data": [], "smooth": smooth, "areaStyle": area_style}],
            "color": colors
        }
    elif chart_type.startswith('gauge'):
        # 仪表盘
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {"formatter": "{b}: {c}"},
            "series": [{"type": "gauge", "data": [], "detail": {"formatter": "{value}"}}]
        }
    elif chart_type.startswith('radar'):
        # 雷达图
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {},
            "legend": {"bottom": 0},
            "radar": {"indicator": []},
            "series": [{"type": "radar", "data": []}],
            "color": colors
        }
    elif chart_type.startswith('funnel'):
        # 漏斗图
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
            "legend": {"bottom": 0},
            "series": [{"type": "funnel", "data": [], "left": "10%", "width": "80%"}],
            "color": colors
        }
    else:
        # 通用默认
        return {
            "title": {"text": title_text, "left": "center"},
            "tooltip": {},
            "series": [{"type": "bar", "data": []}],
            "color": colors
        }


# ====== 报表保存 ======

def build_base_save_data(report_id, designer_obj, rows, cols, styles, merges, chart_list=None, page_size=None, area=None, data_rect_width=None):
    """构造报表保存请求体"""
    return {
        "designerObj": json.dumps(designer_obj, ensure_ascii=False),
        "name": "sheet1",
        "freeze": "A1",
        "freezeLineColor": "rgb(185, 185, 185)",
        "rows": rows,
        "cols": cols,
        "styles": styles,
        "merges": merges,
        "validations": [],
        "autofilter": {},
        "dbexps": [],
        "dicts": [],
        "loopBlockList": [],
        "zonedEditionList": [],
        "fixedPrintHeadRows": [],
        "fixedPrintTailRows": [],
        "hiddenCells": [],
        "submitHandlers": [],
        "rpbar": {"show": True, "pageSize": str(page_size) if page_size else "", "btnList": []},
        "fillFormToolbar": {"show": True, "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"]},
        "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
        "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
        "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
        "displayConfig": {},
        "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1, "isBackend": False, "marginX": 10, "marginY": 10, "layout": "portrait", "printCallBackUrl": ""},
        "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
        "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
        "area": area if area is not None else False,
        "chartList": chart_list or [],
        "background": False,
        "dataRectWidth": data_rect_width if data_rect_width is not None else 700,
        "excel_config_id": report_id,
        "pyGroupEngine": False,
        "isViewContentHorizontalCenter": False,
        "fillFormStyle": "default",
        "sheetId": "default",
        "sheetName": "默认Sheet",
        "sheetOrder": "0"
    }


def save_report(api_base, token, save_data):
    """调用报表保存接口"""
    result = api_request(api_base, token, '/jmreport/save', save_data)
    return result


# ====== 主流程 ======

def create_report(api_base, token, config):
    """创建新报表"""
    report_id = gen_id()
    report_code = str(int(time.time() * 1000))
    report_name = config['reportName']

    print(f'\n{"=" * 50}')
    print(f'创建积木报表: {report_name}')
    print(f'{"=" * 50}')

    # Step 1: 创建空报表
    designer_obj = {
        "id": report_id, "code": report_code, "name": report_name,
        "type": "0", "template": 0, "delFlag": 0, "viewCount": 0,
        "updateCount": 0, "submitForm": config.get('submitForm', 0),
        "reportName": report_name
    }

    empty_save = build_base_save_data(report_id, designer_obj, {"len": 200}, {"len": 100}, [], [])
    print('\n[1/4] 创建空报表...')
    r = save_report(api_base, token, empty_save)
    print(f'  结果: success={r.get("success")}')
    if not r.get('success'):
        print(f'  失败: {r.get("message")}')
        return None

    # Step 2: 解析SQL并保存数据集
    print('\n[2/4] 解析SQL并保存数据集...')
    dataset_ids = {}
    for ds in config.get('datasets', []):
        db_code = ds['dbCode']
        sql = ds.get('dbDynSql', '')
        db_source = ds.get('dbSource', '')
        print(f'  解析数据集 [{db_code}]: {sql[:60]}...' if len(sql) > 60 else f'  解析数据集 [{db_code}]: {sql}')

        field_list, param_list = parse_sql_fields(api_base, token, sql, db_source)
        if not field_list:
            print(f'  警告: 数据集 [{db_code}] 字段为空')
            continue

        ds_id = save_dataset(api_base, token, report_id, ds, field_list, param_list)
        if ds_id:
            dataset_ids[db_code] = ds_id
            print(f'  数据集 [{db_code}] 保存成功, id={ds_id}')
        else:
            print(f'  数据集 [{db_code}] 保存失败')

    # Step 3: 构造布局
    print('\n[3/4] 构造报表布局...')
    layout = config.get('layout', 'table_only')
    table_config = config.get('table')
    chart_config = config.get('chart')

    all_rows = {"len": 200}
    all_merges = []
    chart_list = []
    col_count = len(table_config['columns']) if table_config else 6

    if layout == 'chart_top' and chart_config and table_config:
        # 图表在上，数据表格在下（避免列表展开与图表冲突）
        chart_db_id = dataset_ids.get(chart_config['datasetCode'], '')
        chart_rows, chart_list, next_row = build_chart_rows(
            chart_config, chart_db_id,
            start_row=1, col_start=1, col_end=col_count
        )
        all_rows.update(chart_rows)

        # 分隔行
        all_rows[str(next_row)] = {"cells": {}, "height": 10}
        next_row += 1

        # 数据表格
        table_rows, table_merges, _ = build_table_rows(table_config, start_row=next_row)
        all_rows.update(table_rows)
        all_merges.extend(table_merges)
        print(f'  布局: 图表在上(rows 1-10) + 数据表(rows {next_row}+)')

    elif layout == 'chart_bottom' and chart_config and table_config:
        # 数据表格在上，图表在下
        # 图表虚拟行必须在数据展开区域之后，否则预览会重叠
        table_rows, table_merges, next_row = build_table_rows(table_config, start_row=1)
        all_rows.update(table_rows)
        all_merges.extend(table_merges)

        # data_binding_row = next_row - 1 (数据绑定行)
        # 数据展开后最多占 pageSize 行，图表需在展开区域之后
        page_size = config.get('pageSize', 10)
        gap = config.get('gap', 1)  # 默认1行间距，更紧凑
        data_binding_row = next_row - 1
        chart_start = data_binding_row + page_size + gap

        chart_db_id = dataset_ids.get(chart_config['datasetCode'], '')
        chart_rows, chart_list, chart_end_row = build_chart_rows(
            chart_config, chart_db_id,
            start_row=chart_start, col_start=1, col_end=col_count
        )
        all_rows.update(chart_rows)

        # 添加分页符行（自动触发滚动条计算）
        # 分页符放在图表下方约3行的位置（确保在数据展开区域之外）
        # 使用多个空格作为分页符，避免显示"1"
        pagination_row = chart_start + page_size + 3
        all_rows[str(pagination_row)] = {"cells": {"1": {"text": "   "}}}
        # 确保 len 足够大
        if pagination_row > all_rows.get("len", 200):
            all_rows["len"] = pagination_row + 10

        print(f'  布局: 数据表(rows 1-{next_row - 1}) + 间距({gap}行) + 图表(row {chart_start}+) + 分页符(row {pagination_row})')
        print(f'  pageSize={page_size}, 图表在数据展开区域之后')

    elif layout == 'chart_right' and chart_config and table_config:
        # 数据表格在左，图表在右
        table_rows, table_merges, next_row = build_table_rows(table_config, start_row=1)
        all_rows.update(table_rows)
        all_merges.extend(table_merges)

        chart_db_id = dataset_ids.get(chart_config['datasetCode'], '')
        chart_col_start = col_count + 2  # 留1列间距
        chart_col_end = chart_col_start + 5
        chart_rows, chart_list, _ = build_chart_rows(
            chart_config, chart_db_id,
            start_row=1, col_start=chart_col_start, col_end=chart_col_end
        )
        # 合并chart_rows到all_rows（同行不同列）
        for row_key, row_val in chart_rows.items():
            if row_key in all_rows and row_key != "len":
                all_rows[row_key]["cells"].update(row_val["cells"])
            else:
                all_rows[row_key] = row_val
        print(f'  布局: 数据表(cols 1-{col_count}) + 图表(cols {chart_col_start}-{chart_col_end})')

    elif layout == 'chart_only' and chart_config:
        # 仅图表
        chart_db_id = dataset_ids.get(chart_config['datasetCode'], '')
        chart_rows, chart_list, _ = build_chart_rows(
            chart_config, chart_db_id,
            start_row=1, col_start=1, col_end=6
        )
        all_rows.update(chart_rows)
        print(f'  布局: 仅图表(row 1)')

    elif table_config:
        # 仅数据表格（默认）
        table_rows, table_merges, _ = build_table_rows(table_config, start_row=1)
        all_rows.update(table_rows)
        all_merges.extend(table_merges)
        print(f'  布局: 仅数据表')

    else:
        print('  错误: 未配置 table 或 chart')
        return None

    # 构造列宽
    cols = build_cols(table_config['columns']) if table_config else {"len": 100}

    # 计算 dataRectWidth（列宽总和）
    total_width = sum(col.get('width', 100) for col in cols.values() if isinstance(col, dict))
    data_rect_width = total_width if total_width > 0 else 700

    # 计算 area（内容边界区域）
    # area.sri/eri = 内容区域的起始/结束行（UI行号，从1开始）
    # area.sci/eci = 内容区域的起始/结束列
    # area.width/height = 内容区域的总像素宽高
    title_h = 40
    header_h = 34
    row_h = 25  # 默认行高
    chart_h = int(chart_config.get('height', 350)) if chart_config else 0

    if layout == 'chart_bottom' and chart_config and table_config:
        # 设置 area 为 false，让系统自动计算滚动高度
        # 需要在图表底部添加分页符行，系统才能正确计算
        area = False
    elif layout == 'chart_top' and chart_config and table_config:
        area = {
            "sri": 1,
            "sci": 1,
            "eri": next_row - 1,
            "eci": col_count,
            "width": data_rect_width,
            "height": chart_h + 10 + title_h + header_h + row_h * 2
        }
    elif layout == 'chart_right' and chart_config and table_config:
        chart_w = int(chart_config.get('width', 650))
        area = {
            "sri": 1,
            "sci": 1,
            "eri": next_row - 1,
            "eci": chart_col_end,
            "width": data_rect_width + chart_w,
            "height": title_h + header_h + row_h * 2
        }
    elif layout == 'chart_only' and chart_config:
        area = {
            "sri": 1,
            "sci": 1,
            "eri": 1,
            "eci": col_count,
            "width": data_rect_width,
            "height": chart_h
        }
    else:
        area = {
            "sri": 1,
            "sci": 1,
            "eri": next_row - 1,
            "eci": col_count,
            "width": data_rect_width,
            "height": title_h + header_h + row_h * 2
        }

    # Step 4: 保存完整报表
    print('\n[4/4] 保存报表设计...')
    designer_obj["updateCount"] = 1
    save_data = build_base_save_data(
        report_id, designer_obj, all_rows, cols,
        config.get('styles', DEFAULT_STYLES), all_merges, chart_list,
        page_size=config.get('pageSize'),
        area=area,
        data_rect_width=data_rect_width
    )
    r = save_report(api_base, token, save_data)
    print(f'  结果: success={r.get("success")}')

    if r.get('success'):
        print(f'\n{"=" * 50}')
        print(f'报表创建成功!')
        print(f'  报表ID: {report_id}')
        print(f'  报表名称: {report_name}')
        print(f'  预览地址: {api_base}/jmreport/view/{report_id}')
        print(f'{"=" * 50}')
        return report_id
    else:
        print(f'  保存失败: {r.get("message")}')
        return None


def edit_report(api_base, token, config):
    """编辑已有报表"""
    report_id = config['reportId']
    print(f'\n{"=" * 50}')
    print(f'编辑积木报表: reportId={report_id}')
    print(f'{"=" * 50}')

    # 获取现有报表
    print('\n[1/3] 获取现有报表...')
    r = api_request(api_base, token, f'/jmreport/get/{report_id}', method='GET')
    if not r.get('success'):
        print(f'  获取失败: {r.get("message")}')
        return None
    existing = r['result']
    print(f'  报表名称: {existing.get("name")}')

    # 获取现有数据集
    print('\n[2/3] 获取现有数据集...')
    tree_r = api_request(api_base, token, f'/jmreport/field/tree/{report_id}', method='GET')
    if tree_r.get('success') and tree_r.get('result'):
        for ds in tree_r['result']:
            print(f'  已有数据集: [{ds.get("dbCode")}] {ds.get("dbChName")}')

    # 添加新数据集
    dataset_ids = {}
    for ds in config.get('addDatasets', []):
        db_code = ds['dbCode']
        sql = ds.get('dbDynSql', '')
        db_source = ds.get('dbSource', '')
        print(f'  新增数据集 [{db_code}]...')

        field_list, param_list = parse_sql_fields(api_base, token, sql, db_source)
        ds_id = save_dataset(api_base, token, report_id, ds, field_list, param_list)
        if ds_id:
            dataset_ids[db_code] = ds_id
            print(f'  数据集 [{db_code}] 保存成功, id={ds_id}')

    # 如果需要更新报表设计（jsonStr），在此处理
    if config.get('table') or config.get('chart'):
        print('\n[3/3] 更新报表设计...')
        # 重新构造完整布局
        layout = config.get('layout', 'chart_top')
        table_config = config.get('table')
        chart_config = config.get('chart')

        all_rows = {"len": 200}
        all_merges = []
        chart_list = []
        col_count = len(table_config['columns']) if table_config else 6

        if layout == 'chart_top' and chart_config and table_config:
            chart_db_id = dataset_ids.get(chart_config['datasetCode'], chart_config.get('dataId', ''))
            chart_rows, chart_list, next_row = build_chart_rows(
                chart_config, chart_db_id,
                start_row=1, col_start=1, col_end=col_count
            )
            all_rows.update(chart_rows)
            all_rows[str(next_row)] = {"cells": {}, "height": 10}
            next_row += 1
            table_rows, table_merges, _ = build_table_rows(table_config, start_row=next_row)
            all_rows.update(table_rows)
            all_merges.extend(table_merges)

        cols = build_cols(table_config['columns']) if table_config else {"len": 100}

        designer_obj = {
            "id": report_id,
            "code": existing.get('code', ''),
            "name": config.get('reportName', existing.get('name', '')),
            "type": existing.get('type', '0'),
            "template": existing.get('template', 0),
            "delFlag": 0,
            "viewCount": existing.get('viewCount', 0),
            "updateCount": (existing.get('updateCount') or 0) + 1,
            "submitForm": existing.get('submitForm', 0),
            "reportName": config.get('reportName', existing.get('name', ''))
        }

        save_data = build_base_save_data(
            report_id, designer_obj, all_rows, cols,
            config.get('styles', DEFAULT_STYLES), all_merges, chart_list
        )
        r = save_report(api_base, token, save_data)
        print(f'  结果: success={r.get("success")}')

    print(f'\n编辑完成!')
    print(f'  预览地址: {api_base}/jmreport/view/{report_id}')
    return report_id


def main():
    parser = argparse.ArgumentParser(description='积木报表 (JiMu Report) 创建/编辑工具')
    parser.add_argument('--api-base', required=True, help='JeecgBoot 后端地址')
    parser.add_argument('--token', required=True, help='X-Access-Token')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    action = config.get('action', 'create')

    if action == 'create':
        create_report(args.api_base, args.token, config)
    elif action == 'edit':
        edit_report(args.api_base, args.token, config)
    else:
        print(f'未知操作类型: {action}')
        sys.exit(1)


if __name__ == '__main__':
    main()
