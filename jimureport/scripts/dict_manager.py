#!/usr/bin/env python3
"""
积木报表 字典管理脚本
支持：字典的增删改查 + 字典项的增删改查
"""

import requests
import json
import urllib.parse

BASE_URL = "http://192.168.1.6:8085/jmreport"
TOKEN = "f5cf6d9e-3a62-4f0f-a235-e6d7c21b240b"

# 使用 session + trust_env=False 彻底绕过系统代理（proxies=None 不够）
session = requests.Session()
session.trust_env = False
session.headers.update({
    "X-Access-Token": TOKEN,
    "Content-Type": "application/json",
})


def request(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    resp = session.request(method, url, **kwargs)
    data = resp.json()
    if not data.get("success") and data.get("code") != 200:
        print(f"[FAIL] {path} -> {data.get('message')}")
    return data


# ─── 字典（Dict）─────────────────────────────────────────────

def dict_list(dict_code=None, dict_name=None, page_no=1):
    """查询字典列表，支持按 dictCode 或 dictName 过滤"""
    params = {"pageNo": page_no}
    if dict_code:
        params["dictCode"] = dict_code
    if dict_name:
        params["dictName"] = dict_name
    return request("GET", "/dict/list", params=params)


def dict_add(dict_name, dict_code, description=""):
    """添加字典（添加前建议先查询是否已存在）"""
    return request("POST", "/dict/add", json={
        "dictName": dict_name,
        "dictCode": dict_code,
        "description": description,
    })


def dict_edit(dict_id, dict_name, dict_code, description=""):
    """编辑字典"""
    return request("POST", "/dict/edit", json={
        "id": dict_id,
        "dictName": dict_name,
        "dictCode": dict_code,
        "description": description,
    })


def dict_delete(dict_id):
    """删除字典（字典项一并删除）"""
    return request("DELETE", "/dict/delete", params={"id": dict_id})


# ─── 字典项（DictItem）───────────────────────────────────────

def dict_item_list(dict_id, page_no=1):
    """查询字典项列表"""
    return request("GET", "/dictItem/list", params={"dictId": dict_id, "pageNo": page_no})


def dict_item_add(dict_id, item_text, item_value, sort_order=1, status=1):
    """添加字典项
    status: 1=启用, 0=不启用
    """
    return request("POST", "/dictItem/add", json={
        "dictId": dict_id,
        "itemText": item_text,
        "itemValue": item_value,
        "sortOrder": sort_order,
        "status": status,
    })


def dict_item_edit(item_id, dict_id, item_text, item_value, sort_order=1, status=1):
    """编辑字典项"""
    return request("POST", "/dictItem/edit", json={
        "id": item_id,
        "dictId": dict_id,
        "itemText": item_text,
        "itemValue": item_value,
        "sortOrder": sort_order,
        "status": status,
    })


def dict_item_delete(item_id):
    """删除字典项"""
    return request("DELETE", "/dictItem/delete", params={"id": item_id})


# ─── 工具函数 ────────────────────────────────────────────────

def get_or_create_dict(dict_name, dict_code, description=""):
    """查询字典，不存在则创建，返回字典 id"""
    result = dict_list(dict_code=dict_code)
    records = result.get("result", {}).get("records", [])
    if records:
        dict_id = records[0]["id"]
        print(f"[已存在] {dict_code} -> id={dict_id}")
        return dict_id

    result = dict_add(dict_name, dict_code, description)
    if result.get("success"):
        # 重新查询获取 id
        records = dict_list(dict_code=dict_code).get("result", {}).get("records", [])
        dict_id = records[0]["id"]
        print(f"[已创建] {dict_code} -> id={dict_id}")
        return dict_id
    return None


def batch_add_items(dict_id, items):
    """批量添加字典项
    items: [{"itemText": "xxx", "itemValue": "1", "sortOrder": 1, "status": 1}, ...]
    """
    for item in items:
        result = dict_item_add(
            dict_id=dict_id,
            item_text=item["itemText"],
            item_value=item["itemValue"],
            sort_order=item.get("sortOrder", 1),
            status=item.get("status", 1),
        )
        flag = "[OK]" if result.get("success") or result.get("code") == 200 else "[FAIL]"
        print(f"  {flag} 添加字典项: {item['itemText']}={item['itemValue']}")


# ─── 示例用法 ────────────────────────────────────────────────

if __name__ == "__main__":
    # 示例：创建审核状态字典并添加字典项
    dict_id = get_or_create_dict(
        dict_name="审核",
        dict_code="audit_status",
        description="审核项目的类型",
    )

    if dict_id:
        batch_add_items(dict_id, [
            {"itemText": "待审核", "itemValue": "0", "sortOrder": 1},
            {"itemText": "已通过", "itemValue": "1", "sortOrder": 2},
            {"itemText": "不通过", "itemValue": "2", "sortOrder": 3},
        ])

        # 查询字典项
        print("\n当前字典项：")
        result = dict_item_list(dict_id)
        for item in result.get("result", {}).get("records", []):
            status_label = "启用" if item["status"] == 1 else "不启用"
            print(f"  {item['itemText']} = {item['itemValue']} [{status_label}]")
