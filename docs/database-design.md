# Database Design

## 1. 数据库选择

V1版本采用 SQLite 作为数据存储方案。

选择原因：

- 无需额外部署数据库服务
- 单文件存储，方便本地运行
- 支持标准 SQL 查询
- 适合单用户本地应用场景

## 2. 数据库设计目标

数据库主要用于保存用户交易记录，支持以下功能：

- 添加账单
- 查看账单
- 修改账单
- 删除账单
- 按日期查询
- 按分类查询
- 按分类和日期组合查询
- 收支统计

## 3. 数据模型设计

V1版本采用单表设计。

核心实体为 Transaction（交易记录）。一条交易记录表示用户的一次收入或支出行为。

数据库表额外保存 `created_at` 字段，但该字段当前未进入 `Transaction` 模型。

## 4. 表结构设计

### transactions

用于保存用户所有收入和支出记录。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 交易ID |
| amount | REAL | NOT NULL CHECK(amount > 0) | 金额 |
| type | TEXT | NOT NULL CHECK(type IN ('income','expense')) | 收入或支出类型 |
| category | TEXT | NOT NULL | 分类 |
| transaction_date | TEXT | NOT NULL | 交易日期 |
| description | TEXT | 无，允许NULL | 备注 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 5. 字段详细说明

### id

`id` 是自增整数主键，用于唯一标识一条交易记录。修改、删除和按ID查询账单时通过该字段定位目标记录。

### amount

`amount` 使用 `REAL` 保存交易金额。数据库要求该字段不能为空且必须大于0。

### type

`type` 使用 `TEXT` 保存交易类型。数据库要求该字段不能为空，且只允许以下值：

- `income`
- `expense`

### category

`category` 使用 `TEXT` 保存交易分类，例如 `food`、`transport`、`salary`。数据库要求该字段不能为空，分类查询使用该字段进行精确匹配。

### transaction_date

`transaction_date` 使用 `TEXT` 保存交易发生日期，并用于日期范围查询和统计。数据库层仅要求该字段为 `TEXT NOT NULL`。

严格的 `YYYY-MM-DD` 格式和真实日历日期合法性由应用层的 `validators.validate_date()` 保证，不是 SQLite `CHECK` 约束。

### description

`description` 使用 `TEXT` 保存用户补充说明，允许为 `NULL`。

### created_at

`created_at` 使用 `TEXT` 保存创建时间，由 SQLite 通过 `CURRENT_TIMESTAMP` 自动生成。

该字段是 V1 预留的审计或扩展字段。当前 `Transaction` 模型不包含该字段，Repository 查询也不读取或映射该字段，当前业务展示、排序和筛选均不使用它。

## 6. 数据库约束与应用层校验

### 数据库约束

SQLite 表结构直接保证：

- `id` 为自增整数主键
- `amount` 不为空且大于0
- `type` 不为空且只能为 `income` 或 `expense`
- `category` 不为空
- `transaction_date` 不为空
- `description` 可以为 `NULL`
- `created_at` 默认使用 `CURRENT_TIMESTAMP`

数据库没有为分类空字符串、日期格式或真实日历日期增加额外的 `CHECK` 约束。

### 应用层校验

CLI 输入在写入数据库前通过 Validator 进行更完整的规范化和校验：

- 金额清理首尾空格后转换为有限浮点数，并且必须大于0
- 类型清理首尾空格并转换为小写，只允许 `income` 或 `expense`
- 分类清理首尾空格后不能为空
- ID必须是大于0的整数
- 日期必须是严格且真实合法的 `YYYY-MM-DD` 日历日期
- 开始日期不能晚于结束日期

应用层校验失败时会抛出 `ValueError` 并由 CLI 显示错误提示。这些输入规范化和提示行为不属于数据库表约束。

## 7. 查询与统计行为

Transaction Repository 提供以下查询行为：

- 分类使用规范化后的分类值进行精确匹配
- 日期范围包含开始日期和结束日期
- 分类与日期组合查询要求同时满足两个条件
- 查询结果按照ID降序返回

Statistics Repository 分别聚合：

- 收入总额
- 支出总额
- 交易记录数量

日期范围统计包含开始日期和结束日期。没有匹配记录时，收入、支出和数量均返回0。

收支余额不是数据库字段，也不会持久化。Service 将统计结果转换为 `TransactionStatistics` 模型后，由模型根据总收入减去总支出计算余额。

## 8. 数据库初始化

数据库路径为项目根目录下的 `data/finance.db`。

加载 `database.py` 时会在需要时创建 `data/` 目录，但只有执行 `create_table()` 才会创建 `transactions` 表。直接运行数据库模块会调用 `create_table()` 并完成初始化：

```powershell
uv run --frozen python database.py
```

初始化使用 `CREATE TABLE IF NOT EXISTS`，因此可以安全重复执行。`finance.db` 是运行时生成文件，并通过 `.gitignore` 中的 `*.db` 规则忽略。

实际建表 SQL如下：

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK(amount > 0),
    type TEXT NOT NULL CHECK(type IN ('income','expense')),
    category TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 9. 示例数据

```SQL
INSERT INTO transactions
(amount,type,category,transaction_date,description)
VALUES
(8000,'income','salary','2026-08-01','工资');

INSERT INTO transactions
(amount,type,category,transaction_date,description)
VALUES
(35,'expense','food','2026-08-19','午餐');
```

在空表中依次插入以上记录时，完整结果示意如下。`created_at` 的实际值取决于插入时间：

| id | amount | type | category | transaction_date | description | created_at |
|---:|---:|---|---|---|---|---|
| 1 | 8000 | income | salary | 2026-08-01 | 工资 | 由SQLite自动生成 |
| 2 | 35 | expense | food | 2026-08-19 | 午餐 | 由SQLite自动生成 |
