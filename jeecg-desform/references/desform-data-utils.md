# desform_data_utils.py 数据操作工具使用指南

位于 `scripts/desform_data_utils.py`，提供表单数据的 CRUD、批量操作、回收站等功能。

## 基本用法

```python
from desform_utils import init_api
from desform_data_utils import *

init_api('https://boot3.jeecg.com/jeecgboot', 'your-token')

# 新增
result = add_data('form_code', {'input_xxx': '张三', 'phone_xxx': '138xxx'})
data_id = result['id']

# 查询列表
page = list_data('form_code', page=1, size=10)
for record in page['records']:
    print(record)

# 查询单条
data = get_data('form_code', data_id)

# 编辑
edit_data('form_code', data_id, {'input_xxx': '李四'})

# 删除（逻辑删除）
delete_data('form_code', data_id)

# 物理删除
delete_data('form_code', data_id, hard=True)
```

## 可用函数

- **CRUD**: `add_data`, `edit_data`, `get_data`, `list_data`, `delete_data`, `delete_data_batch`
- **复制**: `copy_record`, `copy_records`
- **批量**: `batch_update`
- **回收站**: `restore_data`, `clear_recycle`
- **唯一性**: `check_unique`
- **统计**: `get_statistical`
