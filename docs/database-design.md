# Database Design

## 1. 数据库选择

V1版本采用 SQLite 作为数据存储方案。

选择原因：

- 无需额外部署数据库服务
- 单文件存储，方便本地运行
- 支持标准 SQL 查询
- 适合单用户本地应用场景

## 2. 数据库设计目标

数据库主要用于保存用户交易记录，
支持以下功能：

- 添加账单
- 查看账单
- 修改账单
- 删除账单
- 按日期查询
- 按分类查询
- 收支统计

##  3. 数据模型设计

V1版本采用单表设计。

核心实体：

Transaction（交易记录）

一条交易记录表示用户的一次收入或支出行为。

## 4. 表结构设计

### transactions

用于保存用户所有收入和支出记录。

| 字段 | 类型 | 约束 | 说明 |
|------|---------|---|------|
| id | INTEGER | PRIMARY KEY | 交易ID |
| amount | REAL | NOT NULL | 金额 |
| type | TEXT | NOT NULL | 收入/支出 |
| category | TEXT | NOT NULL | 分类 |
| transaction_date | TEXT | NOT NULL | 交易日期 |
| description | TEXT | NULL | 备注 |
| created_at | TEXT | DEFAULT | 创建时间 |

## 5. 字段详细说明

### id

类型：

INTEGER

作用：

唯一标识一条交易记录。

设计原因：

修改和删除账单时，
通过id定位目标记录。

例如：

UPDATE transactions
WHERE id=1

### amount

类型：

REAL

说明：

保存交易金额。

约束：

- 必须大于0
- 不允许为空

### type

取值：

income

expense

说明：

表示交易类型。

例如：

工资收入：

income

午餐消费：

expense

## 6. 数据约束设计


### 金额约束

amount必须大于0。


### 类型约束

type只能是：

- income
- expense


### 日期约束

transaction_date必须符合：

YYYY-MM-DD

格式。

## 7. 初始化SQL

```SQL
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK(amount > 0),
    type TEXT NOT NULL 
        CHECK(type IN ('income','expense')),
    category TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```
## 8. 示例数据

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

数据库：

id	amount	type	category

1	8000	income	salary

2	35	    expense	food