# 从服务配置动态读取数据库连接

当 SQL 数据集需要建表、插入示例数据或探查字段值时，必须先从当前运行的 JeecgBoot/JimuReport 服务配置中动态读取数据库连接参数，**禁止硬编码**。

---

## 获取流程

### Step 1: 定位服务进程和项目路径

```bash
wmic process where "name='java.exe'" get CommandLine
```

从 Java 启动命令中提取项目根目录（如 `-classpath` 或工作目录）。

### Step 2: 确定激活的 Profile

读取 `{项目根目录}/src/main/resources/application.yml`，找到：

```yaml
spring:
  profiles:
    active: dev   # ← 激活的 profile
```

### Step 3: 读取数据库配置

读取对应的 `application-{profile}.yml`（如 `application-dev.yml`），提取数据库连接信息。

**常见配置路径（两种风格）：**

```yaml
# 风格1: dynamic 多数据源（JeecgBoot 常用）
spring:
  datasource:
    dynamic:
      datasource:
        master:
          url: jdbc:mysql://${MYSQL-HOST:127.0.0.1}:${MYSQL-PORT:3306}/${MYSQL-DB:jeecg-boot}?...
          username: root
          password: 123456

# 风格2: 单数据源
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/jeecg-boot?...
    username: root
    password: 123456
```

### Step 4: 解析连接参数

从 JDBC URL 中提取：

```python
import re

jdbc_url = "jdbc:mysql://127.0.0.1:3306/jeecg-boot?characterEncoding=UTF-8&..."
match = re.search(r'jdbc:mysql://([^:]+):(\d+)/([^?]+)', jdbc_url)
host = match.group(1)      # 127.0.0.1
port = int(match.group(2)) # 3306
database = match.group(3)  # jeecg-boot
```

**环境变量占位符处理：** `${MYSQL-HOST:127.0.0.1}` → 取冒号后的默认值 `127.0.0.1`

```python
import re

def resolve_placeholder(value):
    """解析 Spring 占位符 ${ENV:default}，取默认值"""
    return re.sub(r'\$\{[^:}]+:([^}]+)\}', r'\1', value)
```

### Step 5: 用 pymysql 连接

```python
import pymysql

conn = pymysql.connect(
    host=host,
    port=port,
    user=username,
    password=password,
    database=database,
    charset='utf8mb4'
)
cursor = conn.cursor()
# ... 建表、插数据、查询 ...
cursor.close()
conn.close()
```

---

## 完整 Python 工具函数

```python
import re
import os

def read_db_config_from_service():
    """从当前运行的 Java 服务配置中读取数据库连接参数"""
    import subprocess

    # Step 1: 找 Java 进程，定位项目路径
    result = subprocess.run(
        ['wmic', 'process', 'where', "name='java.exe'", 'get', 'CommandLine'],
        capture_output=True, text=True
    )
    # 从命令行中提取项目路径（需根据实际输出解析）

    # Step 2-3: 读取 yml 配置
    # 先读 application.yml 确定 active profile
    # 再读 application-{profile}.yml 提取 datasource 配置

    # Step 4: 解析 JDBC URL
    def resolve_placeholder(value):
        return re.sub(r'\$\{[^:}]+:([^}]+)\}', r'\1', str(value))

    # 返回解析后的连接参数
    return {
        'host': resolve_placeholder(host_raw),
        'port': int(resolve_placeholder(port_raw)),
        'database': resolve_placeholder(db_raw),
        'username': username,
        'password': password
    }
```

---

## API 地址确定

JimuReport API 地址同样从服务获取，格式为 `http://{服务IP}:{端口}`。

- 端口从 `application.yml` 的 `server.port` 或 Java 启动参数 `--server.port` 中获取
- 积木报表接口路径直接拼接，如 `/jmreport/save`，**一般不需要 context-path 前缀**
- 如果 yml 中配置了 `server.servlet.context-path`，则需要加上

---

## 使用场景

| 场景 | 说明 |
|------|------|
| 建表 | 用户要求创建报表但数据库中没有对应表，需先通过 pymysql 执行 CREATE TABLE |
| 插入示例数据 | 建表后插入 demo 数据，方便报表预览 |
| 数据探查 | 需要了解字段值分布（如 `SELECT DISTINCT`）以判断分组字段、字典配置等 |
| 确认表结构 | 验证表是否存在、字段类型是否匹配 |

---

## 重要：建表和插数据前必须先查询已有数据

> **`CREATE TABLE IF NOT EXISTS` 不会报错但也不会覆盖已有表。** 如果表已存在且有数据，盲目 INSERT 会导致新插入的数据与已有数据 ID 冲突或不一致，后续预览地址中使用的 ID 也会出错。

**正确流程：**

```python
cursor = conn.cursor()

# 1. 先检查表是否存在
cursor.execute("SHOW TABLES LIKE 'order_main'")
table_exists = cursor.fetchone() is not None

if table_exists:
    # 2. 表已存在 → 查询已有数据，了解实际 ID 和字段值
    cursor.execute("SELECT id, order_no FROM order_main LIMIT 10")
    rows = cursor.fetchall()
    print("已有数据:", rows)
    # 3. 使用已有数据的真实 ID 生成预览地址，不要插入新数据
else:
    # 4. 表不存在 → 建表 + 插入示例数据
    cursor.execute("CREATE TABLE order_main (...)")
    cursor.execute("INSERT INTO order_main ...")
    conn.commit()
```

**常见错误：**
- 表已存在时仍 INSERT 示例数据 → 预览地址用了新插入的 ID（如 1001），但实际数据用的是旧 ID（如 1、2）
- 没有查询已有数据就假设 ID 格式 → 导致预览链接打开后无数据
