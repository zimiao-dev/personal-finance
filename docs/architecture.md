# Personal Finance V2 架构设计

## 1. 文档目的与适用版本

本文档定义 Personal Finance `v0.2.0` 的目标架构、依赖方向、数据访问边界、事务边界和旧代码迁移原则。

本文描述的是尚未实现的目标设计。当前仓库在 `a77b6bb` 基线上仍采用 V1 的平铺模块、CLI、`sqlite3` Repository 和旧 Service，不能把本文件中的 `src/` 目录、SQLAlchemy、Alembic 或新 Service 描述为当前已有能力。

产品和验收范围见 [V2 需求文档](v2-requirements.md)，HTTP 契约见 [API 契约设计](api-design.md)。

## 2. V1 与 V2 的关系

`v0.1.0` 是历史 CLI 完整版本，由 Git Tag 和 GitHub Release 保存。V2 不再提供或维护 CLI，也不保留旧 Service 函数签名或兼容包装层。

V1 代码仍是迁移阶段的重要事实来源，用于识别并迁移以下业务语义：

- 交易 CRUD
- 分类精确匹配
- 日期闭区间
- 分类和日期组合查询
- ID 降序
- 全部统计和日期范围统计
- 零值统计
- 金额、类型、分类、ID 和日期规则
- 测试数据库隔离

需要使用旧 CLI 的用户应使用 `v0.1.0`。V2 不通过保留旧入口或包装函数提供兼容性。

## 3. 架构目标

V2 是面向后端求职作品集的轻量模块化单体，服务于普通单用户个人财务场景。业务金额使用 `Decimal`，避免将二进制浮点作为核心金额类型。它不是证券交易、汇率或基金净值、会计总账、任意精度计算或面向无限数据规模的金融基础设施。目标是：

- 使用 FastAPI 和 Pydantic 提供清晰 HTTP 边界
- 使用 Domain 和 Application 保存入口无关的业务语义
- 使用 Repository Port 隔离业务用例与数据访问实现
- 使用轻量 Unit of Work 明确一次用例的事务边界
- 使用 SQLAlchemy 2 同步 ORM 实现 SQLite 持久化
- 使用 Alembic 管理 Schema 版本和数据库初始化
- 分离 Domain Entity、Application DTO、ORM Model 和 Pydantic Schema
- 允许通过替换 Infrastructure 在后续版本评估 PostgreSQL
- 保持当前项目规模所需的最小抽象，不建立企业级框架

## 4. 模块化单体总体结构

```text
HTTP Request
  -> FastAPI Router
  -> Pydantic Schema
  -> API Mapper
  -> Application Service
  -> Unit of Work Port
  -> uow.transactions: Transaction Repository Port
  -> SQLAlchemy Unit of Work / Repository
  -> Session / Engine
  -> SQLite
```

响应沿相反方向返回：

```text
SQLite Row / ORM Model
  -> Infrastructure Mapper
  -> Domain Entity / Statistics
  -> API Mapper
  -> Pydantic Response Schema
  -> JSON Response
```

API Router 不承担跨层业务编排，Application 不感知 HTTP，Domain 不感知入口和数据库。

## 5. 推荐目录树

以下目录是 `v0.2.0` 的目标设计，目前尚未创建：

```text
personal-finance/
├── alembic.ini
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── src/
│   └── personal_finance/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       │   ├── entities.py
│       │   ├── enums.py
│       │   ├── exceptions.py
│       │   └── rules.py
│       ├── application/
│       │   ├── dto.py
│       │   ├── ports/
│       │   │   ├── repositories.py
│       │   │   └── unit_of_work.py
│       │   └── services/
│       │       ├── transaction_service.py
│       │       └── statistics_service.py
│       ├── infrastructure/
│       │   ├── database/
│       │   │   ├── base.py
│       │   │   ├── engine.py
│       │   │   ├── models.py
│       │   │   ├── mappers.py
│       │   │   └── unit_of_work.py
│       │   └── repositories/
│       │       └── sqlalchemy_transaction_repository.py
│       └── api/
│           ├── app.py
│           ├── dependencies.py
│           ├── exception_handlers.py
│           ├── mappers.py
│           ├── routers/
│           │   ├── health.py
│           │   ├── transactions.py
│           │   └── statistics.py
│           └── schemas/
│               ├── transactions.py
│               ├── statistics.py
│               └── errors.py
└── tests/
    ├── unit/
    │   ├── domain/
    │   └── application/
    ├── integration/
    │   └── infrastructure/
    └── api/
```

`pyproject.toml` 计划配置为可安装的 `src/` 包。V2 应通过包内应用工厂提供 FastAPI App，不继续把根目录旧 `main.py` 作为入口。

## 6. 分层职责

### 6.1 Domain

Domain 负责：

- 交易和统计业务实体
- 交易类型等入口无关枚举
- 金额、类型、分类、ID、日期和统计规则
- 入口无关的业务异常
- `balance = total_income - total_expense`

Domain 不导入 FastAPI、Pydantic、SQLAlchemy、数据库配置、HTTP 状态码或文件路径。

### 6.2 Application

Application 负责：

- 用例输入 DTO 和查询对象
- Repository Port 和 Unit of Work Port
- Transaction Service 和 Statistics Service
- 目标存在性、创建、完整更新、删除和统计用例
- 调用 Domain 规则并协调事务
- 将 Infrastructure 的低层结果转换为应用级结果或异常

Application 不导入 FastAPI、Pydantic、SQLAlchemy ORM Model、具体 Session 或 SQLite。

### 6.3 Infrastructure

Infrastructure 负责：

- SQLAlchemy Declarative Base 和 ORM Model
- Engine、Session factory 和 SQLite 配置
- ORM 与 Domain 的双向 Mapper
- Repository Port 的 SQLAlchemy 实现
- Unit of Work Port 的 SQLAlchemy 实现
- 查询条件、ID 降序和统计聚合
- Alembic 所需的 ORM metadata

Infrastructure 可以依赖 Domain 和 Application Port，但不能反向要求 Application 依赖 SQLAlchemy。

### 6.4 API

API 负责：

- FastAPI 应用工厂和 Router
- Pydantic 请求、查询和响应 Schema
- HTTP 与 DTO/Domain 的 Mapper
- FastAPI 依赖装配
- HTTP 状态码和异常响应
- OpenAPI 描述

Router 只获取并调用 Service，不直接获取 Session、Repository 或 ORM Model。

## 7. 依赖方向

目标依赖规则：

```text
API ----------> Application ----------> Domain
                    ^                    ^
                    |                    |
Infrastructure -----+--------------------+
```

- Domain 不依赖任何外层
- Application 依赖 Domain，并在内部定义 Port
- Infrastructure 实现 Application Port
- API 依赖 Application，并通过装配获得 Service
- FastAPI 和 Pydantic 只存在于 API 边界
- SQLAlchemy 和 SQLite 只存在于 Infrastructure

禁止出现：

- Domain 导入 Application、API 或 Infrastructure
- Application 导入 FastAPI、Pydantic 或 SQLAlchemy
- Infrastructure 导入 API Schema
- API Router 直接导入 SQLAlchemy Repository 或 Session
- ORM Model 直接作为响应模型
- Pydantic Schema 直接作为 Repository 参数

## 8. Domain 模型与业务规则

### 8.1 交易实体

目标 `Transaction` Domain Entity 表示已经具有持久化 ID 的交易，至少包含：

- `id: int`
- `amount: Decimal`
- `type: TransactionType`
- `category: str`
- `transaction_date: date`
- `description: str | None`

创建输入没有 ID。更新目标 ID 作为独立用例参数传入，不由请求体覆盖。

### 8.2 统计模型

目标统计模型至少包含：

- `total_income: Decimal`
- `total_expense: Decimal`
- `transaction_count: int`
- 根据前两项计算的 `balance: Decimal`

`balance` 不持久化。

### 8.3 共享规则

Domain/Application 至少保护：

- ID 为正整数
- 交易金额为 `Decimal`，有限且严格大于零
- `total_income` 和 `total_expense` 为有限且大于等于零的 `Decimal`
- `balance` 为有限 `Decimal`，可以为正数、零或负数
- 类型只允许 `income` 或 `expense`
- 分类清理首尾空格后不能为空
- 描述字符串清理首尾空白后，为空则规范化为 `None`，否则保留清理后的字符串
- 日期具有合法日历语义
- 日期范围参数成对提供
- 开始日期不得晚于结束日期

Pydantic 可以更早拒绝无效 HTTP 输入，但不能成为共享业务规则的唯一保护层。Application/Domain 必须继续保护金额有限且大于零等入口无关规则。

## 9. Application DTO、Service 和异常

### 9.1 DTO

Application DTO 是用例输入和查询条件，不是 Pydantic Schema，也不是 ORM Model。

建议至少定义：

- `CreateTransactionData`
- `ReplaceTransactionData`
- `TransactionQuery`
- `StatisticsQuery`

创建和更新 DTO 包含 `Decimal`、`TransactionType`、规范化分类、`date` 和可空描述，不包含 ID。

### 9.2 Service

Service 使用构造注入的类：

- `TransactionService`
- `StatisticsService`

目标用例提示：

```python
TransactionService.create(data) -> Transaction
TransactionService.get(transaction_id) -> Transaction
TransactionService.list(query) -> list[Transaction]
TransactionService.replace(transaction_id, data) -> Transaction
TransactionService.delete(transaction_id) -> None
StatisticsService.get(query) -> TransactionStatistics
```

这些只是目标契约提示，不是当前已实现代码。

Service：

- 只依赖 Unit of Work Port，并通过 `uow.transactions` 使用 Transaction Repository Port
- 接收 Application DTO
- 返回 Domain Entity 或统计模型
- 保护共享规则
- 在获取、更新或删除目标不存在时抛入口无关的应用异常
- 不返回 HTTP 状态码
- 不抛 FastAPI `HTTPException`
- 不返回 ORM Model、`lastrowid` 或 `rowcount`
- 不保留 V1 旧函数或兼容包装层

### 9.3 应用异常

使用可区分的入口无关异常类别，例如 `TransactionNotFoundError` 和业务规则异常。API Router 或全局异常处理器按 [API 异常映射矩阵](api-design.md#71-异常映射矩阵) 转换为 HTTP 响应。Domain/Application 异常不导入 FastAPI `HTTPException`。

## 10. Repository Port

Repository Port 使用 `typing.Protocol`，定义于 Application 层，只暴露当前业务需要的方法：

```python
class TransactionRepository(Protocol):
    def add(self, data: CreateTransactionData) -> Transaction: ...
    def get(self, transaction_id: int) -> Transaction | None: ...
    def list(self, query: TransactionQuery) -> list[Transaction]: ...
    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction | None: ...
    def delete(self, transaction_id: int) -> bool: ...
    def summarize(self, query: StatisticsQuery) -> TransactionStatistics: ...
```

签名是设计提示，实现阶段可在不改变语义的前提下调整名称。

契约要求：

- 输入为 Application DTO 或查询对象
- 返回 Domain Entity、统计模型、`None` 或删除布尔结果
- 创建直接返回完整 Domain Entity
- 更新不存在返回 `None`
- 删除不存在返回 `False`
- 列表空结果返回 `[]`
- 不返回 ORM Model
- 不暴露 Session、SQL、`lastrowid` 或 `rowcount`
- Repository 可以 `flush` 以获得数据库生成值，但不自行提交事务
- 分类筛选、日期闭区间、组合 AND、ID 降序和统计由具体 Repository 实现

V2 不使用 Generic Repository。当前只有一个核心聚合和少量明确查询，通用 CRUD 基类会隐藏业务语义而没有实际收益。

## 11. Unit of Work

V2 使用轻量 Unit of Work，定义 Application Port 并由 Infrastructure 实现。

Transaction Service 和 Statistics Service 不再单独注入同一个 Repository。除不访问 Application Service、Repository 或 UoW 的 `/health` 外，每个业务 API 请求创建新的 request-scoped UoW；当前一个 HTTP 请求只执行一个 Application use case，因此它同时是 use-case scoped UoW。

目标职责：

- 为一次 Application 用例管理一个 SQLAlchemy Session
- 通过 `uow.transactions` 提供 Transaction Repository Port
- 提供 `commit()` 和 `rollback()`
- 上下文退出时对未提交事务回滚
- 始终关闭 Session
- 避免 Router 或 Repository 决定事务提交

目标关系：

```text
Application Service
  -> UnitOfWork Port
       -> TransactionRepository Port

SQLAlchemy UnitOfWork
  -> Session
       -> SQLAlchemyTransactionRepository
```

Repository 可以执行查询、写入和 `flush`，但不调用 `commit()`。Service 在用例成功时提交；异常时由 UoW 回滚并继续传播适当异常。

正常和异常退出都关闭 Session；异常退出回滚未提交事务。读用例可以使用同一 UoW 生命周期，但不执行无意义的 `commit()`。Application 只依赖 UoW Protocol，不依赖 SQLAlchemy；Application 单元测试使用提供 fake Repository 的 fake UoW。

当前不加入事件队列、嵌套事务框架、多聚合协调器或复杂工作流机制。

## 12. SQLAlchemy ORM 与 Repository 实现

### 12.1 ORM Model

ORM Model 位于 Infrastructure，只描述数据库映射，不继承 Domain Entity 或 Pydantic Schema。

目标字段语义：

- ID 使用整数主键和数据库生成值
- 金额使用 SQLAlchemy `Numeric(15, 4)`
- 类型、分类和描述使用文本类型
- 日期使用 SQLAlchemy `Date`
- `created_at` 可以继续由数据库生成，但当前不进入 API 响应
- 数据库保留金额正数和交易类型约束

`Numeric(15, 4)` 明确表达 V2 单笔交易金额最多 11 位整数和 4 位小数的目标 precision 与 scale。金额必须满足 `0 < amount <= 99999999999.9999`，不要求固定两位小数。ORM 和 Alembic migration 均声明该类型。

SQLite 使用动态类型和 NUMERIC affinity，不像某些数据库一样严格执行 `Numeric(15, 4)` 的 precision 与 scale。因此 API Schema、Domain 和 Application 必须在写库前拒绝超界值，Repository 不得通过舍入、`quantize` 或截断修正金额。不能声称 SQLite 可以无限制精确保存所有 `Decimal`，也不能声称它与 PostgreSQL 的定点约束完全相同。

### 12.2 Infrastructure Mapper

Mapper 负责：

- ORM Model -> Domain Entity
- Application DTO -> 新 ORM Model 或更新字段
- `Decimal` 与 SQLAlchemy `Numeric(15, 4)` 值的安全传递
- SQLAlchemy `Date` 与 `datetime.date` 的安全传递

Mapper 不得通过 `float` 中转金额，也不得把 ORM Model 返回给 Application。

### 12.3 Repository 实现

SQLAlchemy Repository 负责：

- ORM 查询和写入
- ORM 与 Domain 映射
- 分类精确匹配
- 日期闭区间
- 组合 AND
- ID 降序
- 收入、支出和记录数量聚合

Repository 不感知 HTTP、Pydantic、OpenAPI 或 FastAPI 依赖。

### 12.4 学习说明与架构取舍

SQLite 的 NUMERIC 亲和性与 PostgreSQL 定点类型并不完全相同，因此接受边界值的 `Decimal` round-trip、聚合和无静默舍入行为必须通过真实 SQLite 集成测试固定。该验收只覆盖 V2 公开样例和本地项目规模，不承诺无限交易数量或极端大数据下的生产级财务精度。Repository Port、Application Service、Domain `Decimal` 和 API 字符串契约不依赖具体数据库；PostgreSQL 不属于 `v0.2.0`，后续迁移时主要替换 Infrastructure、配置和迁移脚本。

## 13. Pydantic Schema 和 API Mapper

Pydantic Schema 只存在于 API 层，负责：

- JSON、路径和查询参数解析
- 必填字段和额外字段策略
- 原始 JSON 金额必须为 string，并按格式、`Decimal`、位数和范围顺序严格校验
- 金额有限且大于零
- 类型和分类规范化
- 严格日期格式及日历合法性
- 日期参数成对和范围顺序
- 响应序列化和 OpenAPI 描述

API Mapper 负责：

- 合法交易金额 string -> `Decimal`
- `Decimal` -> 普通定点、无科学计数法、去除无意义尾随零和孤立小数点且零统一为 `"0"` 的 canonical 金额 string
- Schema `date` -> Application DTO `date`
- Domain Entity -> Response Schema
- Domain 统计模型 -> Statistics Response

金额 Mapper 不保留请求字符串的原始 scale，也不使用 `float`。例如 `Decimal("128.50")` 输出 `"128.5"`、`Decimal("5000.00")` 输出 `"5000"`、`Decimal("1.2300")` 输出 `"1.23"`、`Decimal("0.0001")` 输出 `"0.0001"`，任意正负零输出 `"0"`。

描述字段由 API/Domain 边界统一规范化：创建时缺省或显式 `null` 均为 `None`；PUT 必须提供字段但允许 `null`；字符串清理首尾空白后为空则为 `None`，否则保存清理后的字符串。API 响应只返回规范化字符串或 `null`。

四类模型不得互相继承：

| 类型 | 所在层 | 职责 |
| --- | --- | --- |
| Domain Entity | Domain | 业务实体和业务语义 |
| Application DTO | Application | 用例输入和查询条件 |
| ORM Model | Infrastructure | 数据库映射和持久化状态 |
| Pydantic Schema | API | HTTP 输入、输出和 OpenAPI 契约 |

## 14. FastAPI 依赖装配

目标装配链：

```text
FastAPI Dependency
  -> request-scoped SQLAlchemy UnitOfWork
  -> Application Service
       -> uow.transactions
```

- `config.py` 使用 `pydantic-settings` 读取数据库 URL 等配置
- Engine 和 Session factory 在 Infrastructure 初始化
- 请求级依赖创建 UoW 并装配 Service
- Router 只声明 Service 依赖
- Router 不取得 Session、UoW 或 Repository
- 测试通过 FastAPI dependency override 提供 fake Service 或测试 UoW
- 不使用第三方依赖注入容器

应用工厂负责创建 FastAPI App、注册 Router 和异常处理器。导入应用模块不应隐式运行 Alembic 或创建生产数据库。

## 15. 事务边界

一个写 Application 用例对应一个明确事务：

```text
Service enters UnitOfWork
  -> Repository query/write/flush
  -> Service validates result
  -> commit on success
  -> rollback on exception
  -> close Session
```

事务规则：

- Router 不调用 `commit()` 或 `rollback()`
- Repository 不调用 `commit()`
- Service 通过 UoW 控制成功提交
- UoW 保证异常回滚和 Session 关闭
- 读取用例不执行无意义提交
- Repository 返回 Domain 结果后不向外泄露依附 Session 的 ORM 实例

V2 使用同步 Session 和同步数据库访问，不引入 AsyncSession。

## 16. Alembic 与数据库初始化

Alembic 是 V2 Schema 的唯一版本化迁移入口。

目标行为：

- ORM metadata 提供 Alembic autogenerate 的比较基础
- migration 文件必须人工 Review，不能盲目信任自动生成结果
- baseline migration 可以从空 SQLite 数据库创建最新 Schema
- 新用户通过 Alembic upgrade 创建或升级 V2 数据库
- FastAPI App 导入和启动不隐式执行迁移
- 旧 `database.py` 的直接建表方式不再作为 V2 初始化流程

Alembic 目录、配置和首个 migration 尚未创建，本文件不表示其已经可运行。

## 17. V1/V2 数据库隔离

V1 数据库：

```text
data/finance.db
```

V2 默认数据库：

```text
data/finance_v2.db
```

隔离要求：

- V2 不自动迁移、覆盖、删除或重命名 V1 数据库
- V2 默认连接不得指向 `data/finance.db`
- Alembic 不应在没有明确用户操作时连接 V1 数据库
- V1 数据导入不属于应用启动行为，也不属于第一阶段实现
- 测试使用临时路径和独立数据库 URL
- 新用户从空数据库执行 Alembic upgrade

若未来增加 V1 数据导入，必须采用显式流程：

1. 创建并验证备份；
2. 仅在副本上检查 Schema 和数据；
3. 验证日期、金额和类型；
4. 明确 `float` 到 `Decimal` 的转换策略；
5. 导入后核对行数、ID 和统计总额；
6. 用户确认后才允许替换目标数据。

本轮和文档 PR 不执行任何数据库迁移或写操作。

## 18. 测试分层

目标目录：

```text
tests/
├── unit/
│   ├── domain/
│   └── application/
├── integration/
│   └── infrastructure/
└── api/
```

### 18.1 Domain 单元测试

覆盖：

- 交易金额 `Decimal` 的有限且正数规则
- 统计总额非负、余额允许正数/零/负数
- 类型、分类和 ID 规则
- `datetime.date` 及日期范围规则
- 统计和 `balance`

### 18.2 Application 单元测试

- 使用通过 `uow.transactions` 提供 fake Repository 的 fake Unit of Work
- 验证创建、获取、列表、完整更新、删除和统计
- 验证业务校验、未找到和内部不变量异常类型可区分
- 验证成功提交和异常回滚
- 不连接数据库或 FastAPI

Fake UoW 只用于验证 Application 编排，不能代替 SQLAlchemy UoW 集成测试。

### 18.3 Infrastructure 集成测试

- 使用临时 SQLite 数据库
- 通过 Alembic 或测试 Schema 建立数据库
- 验证 ORM/Domain round-trip
- 验证 `Decimal`/`Numeric(15, 4)` 和 `date`/`Date`
- 验证金额 round-trip 不经过 `float`
- 合法边界至少覆盖 `0.0001`、`0.1`、`1`、`128.50` 和 `99999999999.9999`
- 非法边界至少覆盖 `0`、`0.00001`、`100000000000` 和 `99999999999.99999`
- 验证合法输入写入并读取后的 `Decimal` 数值相等，且不发生静默舍入或截断
- 验证收入、支出、零统计和负余额
- 验证 CRUD、分类精确匹配、日期闭区间、组合 AND、ID 降序和统计
- 不依赖固定自增 ID

真实 SQLAlchemy Unit of Work 在隔离的 V2 测试数据库中覆盖成功提交、异常回滚、Repository 不自行提交和 Session 正确关闭。

### 18.4 API 测试

- Schema、Mapper 和 Router 测试
- FastAPI 依赖覆盖
- 验证请求解析错误为 `422`、未找到为 `404`、内部/数据库错误为稳定 `500`
- 验证金额响应使用普通十进制字符串、零统一为 `"0"` 且不使用科学计数法
- 验证金额响应删除无意义尾随零，不保留请求 scale
- 验证描述缺省、显式 `null`、空字符串、纯空白、首尾空白，以及 PUT 缺少描述时的 `422`
- 默认不连接真实数据库
- 必要端到端测试使用独立临时数据库

V1 测试不按 130 项数量保留。旧 CLI 测试和旧薄转发 Service 测试在替代测试建立后删除。

发布验收使用 pytest-cov 同时检查 statement 和 branch coverage：项目总体覆盖率不得低于 `90%`；Domain/Application 的金额、日期、类型、分类、成功、未找到、提交和回滚等核心公共业务分支以 `100%` 覆盖为测试目标。覆盖率数字不能替代行为断言，且这些是 `v0.2.0` 发布目标，不表示当前已经达到。

## 19. 旧代码迁移和删除顺序

旧代码不能在迁移第一步全部删除。推荐顺序：

1. 固定 V2 文档和测试迁移清单；
2. 建立 `src/` 包、配置、应用工厂和健康检查；
3. 实现 Domain、DTO、Port、Service 和 UoW 单元测试；
4. 实现 ORM/Mapper、SQLAlchemy、Alembic、Repository 和真实 UoW 集成测试；
5. 实现交易和统计 API；
6. 确认 CRUD、查询、统计及错误闭环已有替代测试；
7. 删除 `main.py`、`validators.py`、旧 Service、旧 Repository 和失去意义的测试；
8. 更新 README 和发布验收流程。

旧文件的处理原则：

- `main.py` 最终删除，不作为 V2 入口
- `validators.py` 的业务语义迁入 Domain/Schema 后删除
- `models.py` 由 Domain Entity 替代
- `database.py` 由配置、Engine、Session 和 Alembic 替代
- 旧 Service 不保留兼容函数
- 旧 `sqlite3` Repository 由 SQLAlchemy Repository 替代
- CLI 菜单、输入顺序、中文提示、确认和主循环测试最终删除
- V1 的需求与数据库设计文档暂时作为历史文档保留
- README 在 API 可运行并验收前不提前声明 V2 已实现

## 20. 明确不采用的复杂模式

`v0.2.0` 不采用：

- Generic Repository
- 完整 DDD 聚合和领域事件体系
- CQRS
- 事件总线
- 微服务
- 第三方依赖注入容器
- 异步 SQLAlchemy
- Redis
- Celery
- PostgreSQL
- Docker

这些能力只有在后续出现明确需求时再评估，不能为了目录完整或技术名词数量提前引入。

## 21. 架构完成标准

架构实现完成时应满足：

- 实际目录和依赖方向与本文一致
- Domain/Application 没有 FastAPI、Pydantic 或 SQLAlchemy 依赖
- API Router 只依赖 Application Service
- Infrastructure 实现 Port 且不向外泄露 ORM Model
- Repository 不暴露 Session、`lastrowid` 或 `rowcount`
- 真实 SQLAlchemy Unit of Work 的提交、异常回滚、未提交回滚、flush 未提交、多步原子性、提交失败和 Session 关闭测试全部通过
- `Decimal`、SQLAlchemy `Numeric(15, 4)` 和 SQLite 的边界 round-trip、无静默舍入或截断及统计行为已通过隔离集成测试
- FastAPI 依赖可以在测试中替换
- Alembic 可以从空数据库创建最新 V2 Schema
- V1 与 V2 数据库保持隔离
- Domain、Application、Infrastructure 和 API 测试全部通过
- pytest-cov 的总体 statement 和 branch coverage 不低于 `90%`，核心 Domain/Application 公共业务分支达到既定 `100%` 测试目标
- 新 API 达成功能闭环后，V1 CLI 代码和无意义测试已经清理
- README 与实际初始化、启动和测试命令一致
- 未引入本文明确排除的复杂模式

本文通过 Review 只表示可以进入分阶段实现，不表示目标架构已经存在。
