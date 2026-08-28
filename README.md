# Personal Finance

Personal Finance 是一个使用 Python 和 SQLite 开发的本地个人财务管理 CLI 应用。项目面向单用户场景，通过命令行完成账单的记录、维护、查询与收支统计，并使用 Validator、Service 和 Repository 分层组织输入校验、业务协调与数据访问逻辑。

当前项目配置版本为 `0.1.0`，聚焦于构建完整、可测试的个人账单管理闭环。

## 功能特性

- 添加收入或支出账单
- 查看全部账单
- 按 ID 修改或删除账单，并提供未找到、取消、成功和失败提示
- 按分类、日期范围或分类与日期范围组合查询账单
- 统计全部账单或指定日期范围内的总收入、总支出和收支差额
- 对金额、类型、分类、ID、日期及日期范围进行规范化和校验
- 对空结果和无效输入提供明确提示，并在输入错误后返回主菜单

查询使用以下规则：

- 分类经过首尾空格清理后进行精确匹配
- 日期范围包含开始日期和结束日期
- 组合查询要求分类与日期范围同时匹配
- 查询结果按账单 ID 降序返回

当前交易记录直接使用 `Transaction` dataclass 的字符串表示输出，不提供表格界面。

## 技术栈与环境要求

- Python 3.12（项目要求 Python 3.12 或更高版本）
- SQLite
- Python dataclasses
- pytest 与 pytest-cov
- [uv](https://docs.astral.sh/uv/getting-started/installation/) 环境与依赖管理

uv 会依据 `.python-version`、`pyproject.toml` 和 `uv.lock` 准备项目环境。运行命令时使用 `uv run`，无需手动激活 `.venv`。

## 快速开始

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，然后在 PowerShell 中执行以下命令：

```powershell
git clone https://github.com/zimiao-dev/personal-finance.git
cd personal-finance
uv lock --check
uv sync --frozen
uv run --frozen python database.py
uv run --frozen python main.py
```

首次运行前必须执行数据库初始化命令：

```powershell
uv run --frozen python database.py
```

该命令会创建 `data/finance.db` 和 `transactions` 表。建表使用 `CREATE TABLE IF NOT EXISTS`，因此可以安全重复执行。`data/finance.db` 是运行时生成文件，通过 `.gitignore` 排除，不随仓库提交。

`main.py` 不会自动调用 `create_table()`；如果跳过初始化，应用在首次访问尚不存在的 `transactions` 表时会发生数据库错误。

## 使用方式

启动后显示以下主菜单：

```text
1. 添加账单
2. 查看账单
3. 修改账单
4. 删除账单
5. 查询账单
6. 收支统计
0. 退出
```

修改和删除操作先通过 ID 查询目标账单，并在执行写操作前要求确认。

查询账单提供三种方式：

- `a`：按分类查询
- `b`：按日期范围查询
- `c`：按分类和日期范围组合查询

收支统计提供两种方式：

- `a`：统计全部账单
- `b`：统计指定日期范围内的账单

查询和统计方式均需明确选择；空输入或其他选项会显示输入错误并结束当前操作。

## 输入校验与错误处理

- 金额必须能够转换为有限浮点数，且必须大于 `0`
- 类型会清理首尾空格并转换为小写，只允许 `income` 或 `expense`
- 分类会清理首尾空格，清理后不能为空
- ID 必须是大于 `0` 的整数
- 日期必须严格符合 `YYYY-MM-DD`，并且是真实存在的日历日期
- 开始日期不能晚于结束日期

Validator 校验失败时会抛出 `ValueError`。主循环捕获该异常、显示错误信息、终止当前业务操作并返回主菜单；程序不会停留在当前输入字段内自动重试。

## 架构设计

```text
用户输入
  └─> main.py
       ├─> validators.py
       ├─> models.py
       └─> services/
            └─> repositories/
                 └─> database.py
                      └─> SQLite
```

| 模块 | 职责 |
|---|---|
| `main.py` | 菜单循环、用户输入、操作确认、结果输出和异常展示 |
| `validators.py` | 输入清理、类型转换和业务输入校验 |
| `models.py` | 定义 `Transaction` 和 `TransactionStatistics` 数据模型 |
| `services/` | 协调业务调用；统计服务将 Repository 字典结果转换为模型 |
| `repositories/` | 执行 SQL、组合查询条件、统计聚合和数据库行映射 |
| `database.py` | 管理数据库路径、SQLite 连接和建表逻辑 |

`main.py` 分别调用 Validator 和 Service；Validator 不负责调用 Service 或访问数据库。

## 项目结构

```text
personal-finance/
├── .python-version
├── pyproject.toml
├── uv.lock
├── LICENSE
├── README.md
├── main.py
├── database.py
├── models.py
├── validators.py
├── repositories/
│   ├── __init__.py
│   ├── transaction_repository.py
│   └── statistics_repository.py
├── services/
│   ├── __init__.py
│   ├── transaction_service.py
│   └── statistics_service.py
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_statistics_repository.py
│   ├── test_statistics_service.py
│   ├── test_transaction_repository.py
│   ├── test_transaction_service.py
│   └── test_validators.py
├── docs/
│   ├── requirements.md
│   └── database-design.md
└── data/
    └── finance.db  # 初始化后生成，不提交到 Git
```

## 数据库设计

V1 使用单表 `transactions` 保存交易记录，字段包括：

- `id`
- `amount`
- `type`
- `category`
- `transaction_date`
- `description`
- `created_at`

`created_at` 由 SQLite 自动生成，是当前预留的审计或扩展字段；`Transaction` 模型和 Repository 查询目前不读取或展示该字段。收支余额也不是持久化字段，而是由 `TransactionStatistics` 根据总收入减去总支出计算。

日期在 SQLite 中以 `TEXT NOT NULL` 保存，严格格式和日历合法性由应用层 Validator 保证，而不是由 SQLite 日期 `CHECK` 约束保证。完整字段约束和初始化 SQL 见[数据库设计](docs/database-design.md)。

## 测试与覆盖率

项目采用 pytest，覆盖 Validator、模型、Repository 集成、Service 单元和 CLI 单元测试。

在仓库根目录运行完整测试：

```powershell
uv run --frozen python -m pytest
```

当前项目采用平铺式模块结构，使用 `python -m pytest` 可以确保仓库根目录进入 Python 模块搜索路径，因此不推荐直接执行 `pytest`。

运行覆盖率检查：

```powershell
uv run --frozen python -m pytest `
  --cov=main `
  --cov=models `
  --cov=validators `
  --cov=database `
  --cov=repositories `
  --cov=services `
  --cov-report=term-missing
```

当前 `0.1.0` 测试基线：

- 130 项测试全部通过
- 总覆盖率 99%
- 除脚本入口保护行外，主要生产逻辑均已覆盖

以上为语句覆盖率结果，不代表分支覆盖率达到 99%。

## 当前限制

- 仅支持单用户、本地运行
- 仅提供命令行界面，暂无 Web API 或图形界面
- 数据保存在本地 SQLite，不提供云同步
- 不提供登录、权限管理或多用户数据隔离
- 不提供预算管理、复杂财务分析、数据导入导出或可视化
- 首次运行前需要手动初始化数据库
- 当前版本定位为学习与作品集项目，不声明为生产就绪系统

## 后续规划

- 使用 FastAPI 提供 REST API
- 引入 Pydantic 和 SQLAlchemy
- 增加数据可视化
- 完善 Docker 和 Linux 运行流程
- 改进 CLI 展示和数据库初始化体验

## 相关文档

- [需求文档](docs/requirements.md)
- [数据库设计](docs/database-design.md)

## License

本项目使用 [MIT License](LICENSE)，版权人：zimiao。
