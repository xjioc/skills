#!/usr/bin/env python3
"""
积木报表 — 向已有报表追加图表组件
用法：
  修改底部 if __name__ == "__main__" 中的 BASE_URL / TOKEN / REPORT_ID / chart_type / echarts_config
  然后直接运行：python3 add_chart.py

成功经验：
  - 2026-04-02 首次验证，成功向"测试字典"(1199579170722111488)追加 bar.background 图表
  - 关键：session.trust_env = False 彻底绕过系统代理，proxies=None 不够
  - chartList[].config 和 extData 均需 json.dumps() 序列化为字符串
  - rows 中占位格的 text 固定为 " "（一个空格），virtual 等于 layer_id
"""

import json
import random
import string
import requests


def make_session(base_url: str, token: str) -> tuple:
    """创建 requests session，绕过系统代理。返回 (session, base_url)"""
    s = requests.Session()
    s.trust_env = False  # 彻底忽略 ALL_PROXY 等系统环境变量代理
    s.headers.update({"X-Access-Token": token, "Content-Type": "application/json"})
    return s, base_url


def get_report(session, base_url: str, report_id: str) -> dict:
    """获取报表当前状态，返回解析后的 sheet dict"""
    resp = session.get(f"{base_url}/get/{report_id}")
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"GET report failed: {data}")
    result = data["result"]
    json_str = result.get("jsonStr", "{}")
    sheet = json.loads(json_str) if isinstance(json_str, str) else json_str
    return result, sheet


def gen_layer_id() -> str:
    return "chart_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def build_virtual_rows(existing_rows: dict, layer_id: str,
                       row_start: int, row_end: int,
                       col_start: int, col_end: int) -> dict:
    """在 rows 中为图表写入 virtual 占位格。
    与浏览器行为一致：只标图表第一行，colspan/rowspan 定义完整区域。
    """
    rows = dict(existing_rows)
    cells = {str(c): {"text": " ", "virtual": layer_id}
             for c in range(col_start, col_end + 1)}
    rows[str(row_start)] = {"cells": cells}
    return rows


def build_chart_item(layer_id: str, echarts_config: dict, chart_type: str,
                     row: int, col: int,
                     width: int = 650, height: int = 350,
                     row_end: int = None, col_end: int = None,
                     dataset: dict = None) -> dict:
    """构建 chartList 中的一个图表条目

    关键：与浏览器保存行为一致
    - extData 是 dict 对象（不是 JSON 字符串）
    - backgroud 是 dict 对象（不是空字符串）
    - colspan/rowspan 是实际跨度数值（不是 0）
    - width/height 是 int（不是字符串）
    - virtualCellRange 只标第一行（浏览器行为）

    dataset 参数（可选，绑定数据集时传入）：
    {
        "dataType": "api",           # "sql"/"api"/"json"/"javabean"
        "dataId": "数据集ID",
        "dbCode": "数据集编码",
        "axisX": "name",             # X轴字段名（标准模式，isCustomPropName=False 时生效）
        "axisY": "value",            # Y轴字段名（标准模式）
        "series": "type",            # 系列字段名（单系列传 ""）
        # 自定义属性模式（UI 上开启"自定义属性"开关后）：
        "isCustomPropName": True,    # True=启用自定义属性，False=禁用（默认）
        "xText": "name",             # 分类属性（UI: 分类属性下拉）
        "yText": "value",            # 值属性（UI: 值属性下拉）
        # 定时刷新：
        "isTiming": True,            # True=启用，""=禁用
        "intervalTime": "5",         # 字符串秒数，如 "5"
    }
    """
    if row_end is None:
        row_end = row + 9
    if col_end is None:
        col_end = col + 6
    # 只标图表第一行的占位格（与浏览器行为一致）
    virtual_cell_range = [[row, c] for c in range(col, col_end + 1)]
    col_span = col_end - col + 1
    row_span = row_end - row + 1

    # extData 完整结构（浏览器实测 2026-04-02）
    ext_data = {
        "chartId": layer_id,       # 必须等于 layer_id（联动下拉框依赖）
        "id": layer_id,            # 必须等于 layer_id
        "chartType": chart_type,
        # 数据集绑定字段（无数据集时留空）
        "dataType": "",
        "apiStatus": "1",
        "dataId": "",
        "dataId1": "",             # 第二数据集（graph.simple 等双数据集图表用）
        "dbCode": "",
        "axisX": "name",
        "axisY": "value",
        "series": "type",
        "xText": "",
        "yText": "",
        # 联动/钻取字段
        "linkIds": "",
        "source": "",
        "target": "",
        # 定时刷新字段
        "isTiming": "",
        "intervalTime": "",
        # 其他
        "isCustomPropName": False,
    }
    if dataset:
        ext_data.update({
            "dataType": dataset.get("dataType", "api"),
            "dataId": dataset.get("dataId", ""),
            "dbCode": dataset.get("dbCode", ""),
            "axisX": dataset.get("axisX", "name"),
            "axisY": dataset.get("axisY", "value"),
            "series": dataset.get("series", "type"),
        })
        # 定时刷新（isTiming=True 时启用，intervalTime 为字符串秒数如 "5"）
        # 自定义属性模式（对应 UI 上"自定义属性"开关）
        if "isCustomPropName" in dataset:
            ext_data["isCustomPropName"] = dataset["isCustomPropName"]
        if "xText" in dataset:
            ext_data["xText"] = dataset["xText"]   # 分类属性
        if "yText" in dataset:
            ext_data["yText"] = dataset["yText"]   # 值属性
        # 定时刷新
        if "isTiming" in dataset:
            ext_data["isTiming"] = dataset["isTiming"]
        if "intervalTime" in dataset:
            ext_data["intervalTime"] = dataset["intervalTime"]

    return {
        "row": row,
        "col": col,
        "width": width,
        "height": height,
        "config": json.dumps(echarts_config, ensure_ascii=False),
        "extData": ext_data,
        "layer_id": layer_id,
        "virtualCellRange": virtual_cell_range,
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "colspan": col_span,
        "rowspan": row_span,
        "offsetX": 0,
        "offsetY": 0,
        "url": "",
    }


def build_designer_obj(result: dict) -> dict:
    return {
        "id": result["id"],
        "code": result.get("code", ""),
        "name": result.get("name", ""),
        "reportName": result.get("reportName") or result.get("name", ""),
        "type": result.get("type", "0"),
        "template": result.get("template", 0),
        "delFlag": result.get("delFlag", 0),
        "viewCount": result.get("viewCount", 0),
        "updateCount": result.get("updateCount", 0),
        "submitForm": result.get("submitForm", 0),
    }


def build_save_payload(result: dict, sheet: dict, rows: dict,
                       chart_list: list) -> dict:
    """组装完整的 /jmreport/save 请求体"""
    return {
        "designerObj": build_designer_obj(result),
        "name": sheet.get("name", "sheet1"),
        "freeze": sheet.get("freeze", "A1"),
        "freezeLineColor": sheet.get("freezeLineColor", "rgb(185, 185, 185)"),
        "excel_config_id": result["id"],
        "sheetId": sheet.get("sheetId", "default"),
        "sheetName": sheet.get("sheetName", "默认Sheet"),
        "sheetOrder": sheet.get("sheetOrder", "0"),
        "rows": rows,
        "cols": sheet.get("cols", {"len": 100}),
        "styles": sheet.get("styles", []),
        "merges": sheet.get("merges", []),
        "chartList": chart_list,
        "imgList": sheet.get("imgList", []),
        "barcodeList": sheet.get("barcodeList", []),
        "qrcodeList": sheet.get("qrcodeList", []),
        "displayConfig": sheet.get("displayConfig", {}),
        "printConfig": sheet.get("printConfig", {
            "paper": "A4", "width": 210, "height": 297, "definition": 1,
            "isBackend": False, "marginX": 10, "marginY": 10,
            "layout": "portrait", "printCallBackUrl": ""
        }),
        "rpbar": sheet.get("rpbar", {"show": True, "pageSize": "", "btnList": []}),
        "fillFormToolbar": sheet.get("fillFormToolbar", {
            "show": True,
            "btnList": ["save", "subTable_add", "verify", "subTable_del", "print",
                        "close", "first", "prev", "next", "paging", "total", "last",
                        "exportPDF", "exportExcel", "exportWord"]
        }),
        "querySetting": sheet.get("querySetting", {"izOpenQueryBar": False, "izDefaultQuery": True}),
        "queryFormSetting": sheet.get("queryFormSetting", {"useQueryForm": False, "dbKey": "", "idField": ""}),
        "validations": sheet.get("validations", []),
        "autofilter": sheet.get("autofilter", {}),
        "dbexps": sheet.get("dbexps", []),
        "dicts": sheet.get("dicts", []),
        "loopBlockList": sheet.get("loopBlockList", []),
        "zonedEditionList": sheet.get("zonedEditionList", []),
        "fixedPrintHeadRows": sheet.get("fixedPrintHeadRows", []),
        "fixedPrintTailRows": sheet.get("fixedPrintTailRows", []),
        "hiddenCells": sheet.get("hiddenCells", []),
        "submitHandlers": sheet.get("submitHandlers", []),
        "hidden": sheet.get("hidden", {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}}),
        "fillFormInfo": sheet.get("fillFormInfo", {"layout": {"direction": "horizontal", "width": 200, "height": 45}}),
        "recordSubTableOrCollection": sheet.get("recordSubTableOrCollection", {"group": [], "record": [], "range": []}),
        "area": sheet.get("area", False),
        "background": sheet.get("background", False),
        "pyGroupEngine": sheet.get("pyGroupEngine", False),
        "isViewContentHorizontalCenter": sheet.get("isViewContentHorizontalCenter", False),
        "fillFormStyle": sheet.get("fillFormStyle", "default"),
        "dataRectWidth": sheet.get("dataRectWidth", 700),
    }


def add_chart(base_url: str, token: str, report_id: str,
              chart_type: str, echarts_config: dict,
              row: int = 0, col: int = 0,
              width: int = 650, height: int = 350,
              row_end: int = 13, col_end: int = 6,
              dataset: dict = None) -> dict:
    """
    向指定报表追加一个图表。

    参数：
      base_url       - 积木报表服务地址，如 http://192.168.1.6:8085/jmreport
      token          - X-Access-Token
      report_id      - 报表雪花ID
      chart_type     - 图表类型，如 "bar.background"
      echarts_config - ECharts option 配置对象（dict）
      row/col        - 图表左上角行列（0-based）
      width/height   - 图表尺寸（int，像素）
      row_end/col_end- 图表右下角行列（virtual cell 占位范围）
      dataset        - 绑定数据集（可选），格式：
                       {"dataType": "api", "dataId": "xxx", "dbCode": "xxx",
                        "axisX": "name", "axisY": "value", "series": "type"}

    返回 save 接口响应 dict。
    """
    s, base_url = make_session(base_url, token)
    result, sheet = get_report(s, base_url, report_id)
    print(f"[报表] {result.get('name')} ({report_id})")

    layer_id = gen_layer_id()
    print(f"[layer_id] {layer_id}")

    chart_item = build_chart_item(layer_id, echarts_config, chart_type,
                                  row, col, width, height, row_end, col_end,
                                  dataset=dataset)
    rows = build_virtual_rows(sheet.get("rows", {"len": 200}), layer_id,
                              row, row_end, col, col_end)
    chart_list = sheet.get("chartList", []) + [chart_item]
    payload = build_save_payload(result, sheet, rows, chart_list)

    save_resp = s.post(f"{base_url}/save", json=payload)
    save_resp.raise_for_status()
    save_result = save_resp.json()
    if save_result.get("success"):
        print("[成功] 图表已追加")
    else:
        print("[失败]", save_result.get("message"))
    return save_result


# ─── 示例用法 ────────────────────────────────────────────────

if __name__ == "__main__":
    BASE_URL = "http://192.168.1.6:8085/jmreport"
    TOKEN = "f5cf6d9e-3a62-4f0f-a235-e6d7c21b240b"
    REPORT_ID = "1199579170722111488"  # 测试字典

    # bar.background 带背景柱形图（来自 addChart API 默认值）
    bar_bg_config = {
        "title": {"show": True, "text": "某站点用户访问来源", "top": "5", "left": "left",
                  "padding": [5, 20, 5, 20],
                  "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
        "xAxis": {
            "show": True, "name": "服饰",
            "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
            "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
            "axisLine": {"lineStyle": {"color": "#333"}},
            "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
        },
        "yAxis": {
            "show": True, "name": "销量",
            "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
            "axisLine": {"lineStyle": {"color": "#333"}},
            "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
        },
        "series": [{
            "type": "bar", "name": "销量",
            "data": [5, 20, 36, 10, 10, 20],
            "barWidth": 50, "barMinHeight": 2,
            "showBackground": True,
            "backgroundStyle": {"color": "rgba(220, 220, 220, 0.8)"},
            "itemStyle": {"color": "#c43632", "barBorderRadius": 0},
            "label": {"show": True, "position": "top",
                      "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
        }],
        "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
        "tooltip": {"show": True, "formatter": "{b} : {c}",
                    "textStyle": {"color": "#fff", "fontSize": 18}}
    }

    add_chart(
        base_url=BASE_URL,
        token=TOKEN,
        report_id=REPORT_ID,
        chart_type="bar.background",
        echarts_config=bar_bg_config,
        row=0, col=0, row_end=13, col_end=6,
        width=650, height=350,
    )
