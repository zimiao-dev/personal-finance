# Personal Finance V2 需求文档

## 1. 版本定位

本阶段称为 V2，计划发布版本为 `v0.2.0`。

`v0.1.0` 是已经发布的本地个人财务 CLI 完整版本，其源码、测试和使用方式由 Git Tag 与 GitHub Release 保存。需要使用 CLI 的用户应选择 `v0.1.0`。

从 `v0.2.0` 开始，项目转型为面向 Python 后端开发求职的 API-only FastAPI 项目，不再提供或维护 CLI，不保留旧 Service 函数签名或 CLI 兼容包装层，也不要求 V1 的 130 项测试按原样或固定数量保留。

V2 仍定位为本地、单用户、同步数据库访问的普通个人财务学习与作品集项目。业务金额使用 `Decimal`，避免将二进制浮点作为核心金额类型。它不是证券交易、汇率或基金净值、会计总账、任意精度计算或面向无限数据规模的金融基础设施，也不声明为生产级财务系统。

### 1.1 V1 迁移基线

V1 已实现并需要按业务价值迁移的语义包括：

- 交易的创建、查看、修改和删除
- 按分类、日期范围或组合条件查询交易
- 全部收支统计和日期范围收支统计
- 金额、类型、分类、ID、日期及日期范围规则
- 分类规范化后的精确匹配
- 包含起止日期的闭区间查询
- 分类与日期条件同时满足的组合查询
- 查询结果按交易 ID 降序返回
- 空查询结果和零值统计
- 数据库测试与真实运行数据库隔离

V1 的 `main.py`、`validators.py`、旧 Service、旧 Repository 及其测试只作为迁移依据，不构成 V2 的兼容接口。

### 1.2 V2 计划能力

V2 计划实现：

- 基于 FastAPI 的 REST API
- 基于 Pydantic 的 HTTP 请求、查询参数和响应 Schema
- 基于 SQLAlchemy 2 同步 ORM 的数据访问
- 基于 Alembic 的数据库结构迁移
- 健康检查、交易 CRUD、条件查询和收支统计 API
- Domain、Application、Infrastructure、API 四层模块化单体
- 自动化的 Domain、Application、Infrastructure 和 API 测试
- 由 uv 管理并锁定的可复现环境

目标技术栈包括：

- Python 3.12
- FastAPI 与 Pydantic
- SQLAlchemy 2 同步 ORM 与 Alembic
- SQLite
- `pydantic-settings`
- pytest、FastAPI `TestClient` 或 HTTPX，以及 pytest-cov
- uv

详细 HTTP 契约见 [API 契约设计](api-design.md)，详细分层与迁移设计见 [V2 架构设计](architecture.md)。

## 2. V2 核心目标

1. 使用 FastAPI 提供清晰、可测试的同步 REST API。
2. 使用 Pydantic 定义并验证 HTTP 边界。
3. 使用 SQLAlchemy 2 和 Alembic 建立 ORM、Session、事务及 Schema 迁移体系。
4. 使用 `src/` 包布局组织 API-only 模块化单体。
5. 通过 Repository Port 和轻量 Unit of Work 隔离 Application 与具体数据库实现。
6. 分离 Domain Entity、Application DTO、SQLAlchemy ORM Model 和 Pydantic Schema。
7. 将 V1 中有价值的业务规则和数据语义迁移到新的 Domain、Application 和 Infrastructure 测试。
8. 继续使用 SQLite，但使用独立的 V2 数据库文件，避免隐式修改 V1 数据。
9. 使用 uv 管理 FastAPI、Pydantic、SQLAlchemy、Alembic、测试和配置依赖。

## 3. 用户角色与使用方式

### 3.1 API 调用方

API 调用方通过 HTTP 管理本地个人交易数据并获取收支统计。

V2 不引入登录、身份认证或多用户身份概念，因此 API 仍属于本地单用户应用边界。V2 不提供终端菜单、`input()` 交互或 CLI 操作确认。

## 4. API 功能需求

本节描述业务能力和可验证行为。路径、HTTP 方法、Schema、状态码和错误响应由 [API 契约设计](api-design.md) 定义。

### 4.1 健康检查

用户故事：

作为 API 调用方，我希望检查应用是否能够响应，以确认 API 进程已经启动。

验收标准：

- 提供无需业务输入的健康检查
- 正常运行时返回明确、稳定的健康状态
- 不创建、修改或删除交易
- 不访问数据库、Application Service 或 Repository
- 具有独立自动化测试

### 4.2 创建交易

用户故事：

作为 API 调用方，我希望创建一条收入或支出交易，以保存个人财务记录。

验收标准：

- 接收符合创建 Schema 的 JSON 请求
- 请求体不接受交易 ID 或未定义字段
- 金额使用普通十进制 JSON string，解析后必须满足 `0 < amount <= 99999999999.9999`
- 金额整数部分为 1 至 11 位，小数部分如存在则为 1 至 4 位，不要求固定两位小数
- 非法格式、超出金额范围、JSON number 或布尔值返回 `422`，不得通过舍入、量化或截断转成合法输入
- 类型规范化后只允许 `income` 或 `expense`
- 分类规范化后不能为空
- 日期严格符合 `YYYY-MM-DD` 且是真实合法日期
- 合法输入通过 Application Service 创建交易
- 创建成功返回包含数据库生成 ID 的完整交易资源
- 非法输入返回明确、稳定的 HTTP 错误
- API 不直接操作 Session、Repository 或 SQL

### 4.3 获取全部交易

用户故事：

作为 API 调用方，我希望获取全部交易，以查看已有财务记录。

验收标准：

- 通过 Application Service 获取交易列表
- 结果按交易 ID 降序返回
- 没有交易时返回稳定空列表
- API 不自行实现排序或数据库查询

### 4.4 按 ID 获取交易

用户故事：

作为 API 调用方，我希望通过交易 ID 获取单条记录，以查看指定交易。

验收标准：

- 路径 ID 必须是正整数
- 记录存在时返回对应交易
- 记录不存在时返回稳定的未找到响应
- 不存在的记录不会触发写操作

### 4.5 完整更新交易

用户故事：

作为 API 调用方，我希望完整更新指定交易，以修正已有财务记录。

验收标准：

- 路径 ID 是唯一目标 ID，请求体不接受或覆盖 ID
- 更新请求必须显式提供全部业务字段
- 更新输入使用与创建相同的金额、类型、分类和日期规则
- 通过 Application Service 执行目标存在性判断和更新
- 更新成功返回完整交易资源，且 ID 保持不变
- 更新为与原数据相同的内容仍视为成功
- 目标不存在时返回稳定的未找到响应
- API 不直接操作 ORM Model、Session、Repository 或 SQL

### 4.6 删除交易

用户故事：

作为 API 调用方，我希望删除指定交易，以移除不再需要的记录。

验收标准：

- 路径 ID 必须是正整数
- 通过 Application Service 删除目标交易
- 删除成功返回空响应体
- 目标不存在时返回稳定的未找到响应
- 删除一个 ID 不影响其他交易
- API 不读取数据库 `rowcount` 或直接调用 Repository

### 4.7 条件查询交易

用户故事：

作为 API 调用方，我希望按分类、日期范围或两者组合查询交易，以快速定位记录。

验收标准：

- 支持仅分类、仅日期范围以及分类与日期范围组合条件
- 分类清理首尾空格后进行精确匹配，并保留大小写
- 开始日期和结束日期必须同时提供或同时省略
- 日期范围包含开始日期和结束日期
- 开始日期不能晚于结束日期
- 组合查询要求分类和日期条件同时满足
- 查询结果按交易 ID 降序返回
- 没有匹配记录时返回稳定空列表
- 筛选和排序不在 API Router 中实现

### 4.8 获取收支统计

用户故事：

作为 API 调用方，我希望获取全部或指定日期范围内的收支统计，以了解总体财务情况。

验收标准：

- 支持全部统计和日期范围统计
- 日期参数必须成对提供
- 日期范围包含开始日期和结束日期
- 开始日期不能晚于结束日期
- 分别返回总收入、总支出、交易数量和收支差额
- 金额统计值使用规范化普通十进制字符串
- 没有匹配交易时返回稳定零值统计
- `balance = total_income - total_expense`
- 收入和支出总额有限且非负；余额有限并允许为正数、零或负数
- `balance` 不作为数据库字段持久化

## 5. 数据与业务规则

### 5.1 核心类型

- Domain 和 Application 中的交易金额与统计金额使用 `Decimal`
- 交易金额必须有限且严格大于零
- `total_income` 和 `total_expense` 有限且大于等于零
- `balance` 有限，可以为正数、零或负数
- Domain 和 Application 中的日期使用 `datetime.date`
- SQLAlchemy 金额字段使用 `Numeric(15, 4)`
- SQLAlchemy 日期字段使用 `Date`
- 交易 ID 必须是正整数
- 交易类型只允许 `income` 或 `expense`
- 分类清理首尾空格后不能为空
- 单笔交易金额的最小正值为 `0.0001`，最大值为 `99999999999.9999`

### 5.2 HTTP 金额表示

- 交易金额请求和金额响应必须是普通十进制 JSON string
- 整数部分为 1 至 11 位；除单独的 `"0"` 外，整数部分不得以 `0` 开头
- 小数部分如存在则为 1 至 4 位；整数金额同样合法，不要求固定两位小数
- 输入不允许前后空白、正负号、不完整小数、JSON number、布尔值、科学计数法、`NaN`、正无穷或负无穷
- 输入解析为 `Decimal` 后必须满足 `0 < amount <= 99999999999.9999`，Application/Domain 执行相同范围校验
- Schema、Application、Repository 和数据库边界不得通过舍入、`quantize` 或截断接受非法金额
- 响应使用 `Decimal` 的普通定点表示，不使用科学计数法，删除小数部分末尾无意义的零和孤立小数点，任意零值统一为 `"0"`
- 响应不保留请求字符串的原始 scale，例如请求 `"128.50"` 的规范响应金额为 `"128.5"`
- 完整 HTTP 示例、规范化规则和测试边界由 [API 契约设计](api-design.md#41-通用字段规则) 定义

### 5.3 金额持久化与统计

- ORM 和 Alembic migration 使用 SQLAlchemy `Numeric(15, 4)` 表达 V2 的目标 precision 与 scale，并通过 Mapper 与 Domain `Decimal` 转换
- 金额写入和读取不得经过 V1 的 `float` 核心类型
- API Schema、Domain 和 Application 必须在写库前拒绝超过 11 位整数、超过 4 位小数或超过最大值的金额
- Repository 不得通过舍入或截断修正超界金额
- Repository 负责收入、支出和记录数量聚合
- Application 使用 `TransactionStatistics` 表达统计结果
- `balance` 根据收入和支出计算，不作为持久化字段
- `Numeric(15, 4)` 是单笔交易金额输入边界，不是统计总额的业务上限；统计响应继续使用普通十进制字符串
- SQLite 使用动态类型和 NUMERIC affinity，不保证像 PostgreSQL 一样严格执行 `Numeric(15, 4)` 的 precision 与 scale
- Infrastructure 必须使用真实 SQLite 集成测试验证公开边界值的 round-trip 和聚合，不承诺极端规模下的生产级财务精度

完整 ORM、Mapper、统计取舍和学习说明见 [V2 架构设计](architecture.md#12-sqlalchemy-orm-与-repository-实现)。

### 5.4 描述字段规范化

- `TransactionCreate.description` 可以缺省或显式为 `null`，两者均映射为 Domain `None`
- `TransactionUpdate` 是完整替换，`description` 字段必须出现，但可以为 `null`
- 描述为字符串时清理首尾空白；清理后为空则规范化为 `None`，否则保存清理后的字符串
- API 响应只返回规范化后的字符串或 `null`
- 这是 V2 HTTP/Domain 边界的新规则，不表示 V1 CLI 已采用相同规范

### 5.5 数据库隔离

- V2 继续使用 SQLite，默认数据库文件计划为 `data/finance_v2.db`
- V1 的 `data/finance.db` 不自动迁移、不覆盖、不删除
- 新用户通过 Alembic 从空数据库升级到最新 Schema
- V2 不再以直接运行旧 `database.py` 作为初始化方式
- V1 数据导入不属于隐式启动流程，也不属于首阶段实现
- 所有数据库测试必须使用独立临时数据库
- 测试不得读取或修改真实 V1 或 V2 运行数据库

## 6. 架构与依赖要求

V2 采用 `src/` 包布局的模块化单体，分为 Domain、Application、Infrastructure 和 API 四层。

- Domain 保存入口和持久化无关的实体、枚举、异常与业务规则
- Application 定义 DTO、Repository Port、Unit of Work Port 和业务用例
- Infrastructure 使用 SQLAlchemy 实现 ORM、Repository、Session 和 Unit of Work
- API 使用 FastAPI、Pydantic、Router、Mapper、依赖装配和异常处理；`api/dependencies.py` 是 Composition Root

必须满足：

- Domain 不依赖 FastAPI、Pydantic、SQLAlchemy 或数据库
- Application 只依赖 Domain 和自身定义的 Port
- Infrastructure 实现 Application Port
- API Router、Schema、Mapper 和异常处理依赖 Application，通过依赖装配获得 Service
- `api/dependencies.py` 是 API 中唯一允许同时依赖 Application 和 Infrastructure 的 Composition Root 例外
- Composition Root 负责取得配置、Session factory、创建 SQLAlchemy UoW 和装配 Service，但不承载业务规则或 SQL
- Infrastructure 不依赖 API
- Router 不直接使用 ORM Session 或 Repository
- Service 不返回 HTTP 状态码，也不抛 FastAPI `HTTPException`
- ORM Model 不直接作为 API 响应
- Pydantic Schema 不直接进入 Repository
- Repository 不暴露 ORM Model、Session、`lastrowid` 或 `rowcount`
- 写用例的提交和回滚由轻量 Unit of Work 管理
- Transaction Service 和 Statistics Service 只依赖 Unit of Work Port，并通过 `uow.transactions` 使用 Transaction Repository Port
- 除不访问 Application Service、Repository 或 UoW 的 `/health` 外，每个业务 API 请求创建新的 request-scoped UoW；当前一个请求只执行一个 Application use case，因此该 UoW 同时是 use-case scoped
- Router 只取得已装配的 Service，不取得 Session、UoW 或 Repository

具体目录、契约与事务设计见 [V2 架构设计](architecture.md)。

## 7. 输入校验与错误处理

- Pydantic Schema 负责 HTTP 请求体、路径和查询参数的解析与边界校验
- Domain/Application 必须再次保护入口无关的业务规则，不能只信任 API Adapter
- Pydantic 请求解析或 Schema 校验失败返回 `422 Unprocessable Entity`
- 请求数据触发已知 Domain/Application 业务校验失败返回 `422`
- 交易不存在返回稳定的 `404 Not Found`
- 持久化数据破坏内部不变量、未处理异常或数据库异常返回稳定的 `500 Internal Server Error`
- V2 当前没有需要映射为 `409 Conflict` 的业务场景
- Router 或全局异常处理器按 [API 异常映射矩阵](api-design.md#71-异常映射矩阵) 显式映射入口无关异常
- 预期业务错误不能被笼统转换为 `500`
- `500` 不得泄露 SQL、数据库路径、Python 异常文本或 Traceback
- Service、Repository 和 Unit of Work 不依赖 FastAPI 错误类型

## 8. 自动化测试要求

### 8.1 测试分层

- Domain 单元测试验证金额、类型、分类、ID、日期和统计规则
- Application 单元测试使用提供 fake Transaction Repository 的 fake Unit of Work 验证用例和事务编排
- Infrastructure 集成测试使用临时 SQLite 验证 ORM/Domain 映射、金额 round-trip、CRUD、筛选、排序、统计和真实 UoW
- API 测试验证 Schema、Mapper、Router、依赖覆盖和异常映射
- Alembic 测试验证空数据库可以升级到最新 Schema

金额测试至少覆盖合法边界 `"0.0001"`、`"0.1"`、`"1"`、`"128.50"`、`"99999999999.9999"`，以及非法边界 `"0"`、`"0.00001"`、`"100000000000"`、`"99999999999.99999"`、JSON number、布尔值、科学计数法和非有限值。测试还必须验证 `Decimal` 映射、无静默舍入或截断、canonical 响应和统计行为。完整案例见 [API 测试契约](api-design.md#8-api-测试契约)。

描述字段测试至少覆盖创建时缺省、显式 `null`、空字符串、纯空白、首尾空白，以及 PUT 缺少 `description` 时返回 `422`。

真实 SQLAlchemy UoW 集成测试至少覆盖成功提交、异常回滚、Repository 不自行提交和 Session 正确关闭；完整分层见 [架构测试分层](architecture.md#18-测试分层)。

### 8.2 迁移原则

- V1 测试按业务价值迁移，不按 130 项数量保留
- 应迁移金额、类型、分类、ID、日期、CRUD、筛选、排序、统计和隔离语义
- CLI 菜单、输入顺序、中文终端提示、确认流程和主循环测试最终删除
- 旧薄转发 Service 的 ID、对象身份和 `rowcount` 断言最终由新 Application 测试替代
- 旧代码不会在第一步全部删除；必须先建立替代实现和测试，再移除对应模块

### 8.3 隔离与质量

- API 单元测试使用 FastAPI 依赖覆盖，不连接真实数据库
- 数据库集成测试不依赖固定自增 ID 或执行顺序
- 所有测试执行前后真实数据库保持不变
- 测试总数不设置固定值，但所有公开业务与 HTTP 契约必须得到保护
- 发布前完整测试必须全部通过，并使用 pytest-cov 同时检查 statement 和 branch coverage
- 项目总体覆盖率发布门槛不低于 `90%`
- Domain 和 Application 的金额、日期、类型、分类、用例成功、未找到、提交和回滚等核心公共业务分支以 `100%` 覆盖为测试目标；该目标不能替代具体行为断言
- 七个 API 路径必须覆盖成功、关键 `422`、`404` 和稳定 `500`
- Infrastructure 集成测试必须覆盖 CRUD、筛选、排序、统计、真实 UoW 和 migration
- 隔离的端到端 API 测试必须证明合法边界金额可以写入并读取，返回的 `Decimal` 数值与请求数值相等，HTTP 响应符合 canonical 规则
- 上述覆盖率是 `v0.2.0` 发布门槛与目标，不表示当前已经达到
- 发布前运行完整测试、覆盖率检查和干净克隆验收

## 9. 非功能需求

### 9.1 可维护性

- 分层职责和依赖方向清晰
- 不在 Router 中堆积业务编排或数据库逻辑
- Domain、DTO、ORM Model 和 Schema 的转换由明确 Mapper 完成
- 不引入当前规模不需要的企业级抽象

### 9.2 依赖与配置

- Python 版本保持 3.12
- FastAPI、Pydantic、SQLAlchemy 2、Alembic、`pydantic-settings` 和测试依赖通过 uv 管理
- 修改依赖时同步更新 `pyproject.toml` 和 `uv.lock`
- 数据库 URL 等配置由 `pydantic-settings` 管理
- 常规开发和验收使用锁定依赖环境

### 9.3 文档与发布验收

- 本文记录 V2 产品和验收范围
- [API 契约设计](api-design.md) 记录 HTTP 契约
- [V2 架构设计](architecture.md) 记录分层、依赖、事务和迁移设计
- README 仅在 API 实现并验收后更新为真实可运行说明
- 计划能力不得提前描述为已经实现
- 发布前从干净克隆验证依赖同步、Alembic 升级、API 启动和完整测试

## 10. V2 暂不实现的内容

以下内容不属于 `v0.2.0`：

- PostgreSQL
- Docker
- 异步 SQLAlchemy 或异步数据库访问
- 登录、身份认证、权限管理和多用户隔离
- Web 前端或桌面 GUI
- Redis、Celery 和后台任务系统
- 云数据库、云同步或云部署
- 预算管理、复杂财务分析和数据可视化
- 数据导入导出，包括 V1 数据自动导入
- Generic Repository、完整 DDD 聚合、CQRS 和事件总线
- 微服务拆分或第三方依赖注入容器
- 生产级安全、可用性、合规或性能承诺

上述能力只能作为后续版本可能考虑的方向，不得描述为 V2 当前能力。

## 11. 建议实施阶段

### 阶段一：API-only 范围与架构文档

- 修订 V2 需求和 API 契约
- 新增架构文档
- 固定核心类型、数据库隔离和测试迁移原则
- 文档阶段不安装依赖或实现代码

### 阶段二：项目骨架和健康检查

- 建立 `src/` 包和项目包配置
- 添加依赖、配置、应用工厂和健康检查，并固定 Composition Root 模块边界；本阶段不创建数据库依赖
- 建立基础 API 测试
- 不在本阶段实现全部业务

### 阶段三：Domain 与 Application

- 定义 Entity、DTO、业务异常和规则
- 定义 Repository Port 和轻量 Unit of Work Port
- 实现 Transaction Service 和 Statistics Service
- 使用 fake 依赖完成单元测试
- 不依赖 FastAPI 或 SQLAlchemy

### 阶段四：SQLAlchemy 与 Alembic

- 定义 ORM Model、Mapper、Engine、Session 和 Unit of Work
- 实现 SQLAlchemy Repository
- 在 `api/dependencies.py` 中完成 Settings、Session factory、UoW 和 Service 的具体装配
- 建立 Alembic baseline migration
- 完成临时 SQLite、金额 round-trip、聚合和真实 UoW 集成测试
- 不在本阶段直接实现 HTTP Router

### 阶段五：Transaction API

- 实现交易 Schema、Mapper、Router 和异常映射
- 完成 CRUD、条件查询和 HTTP 契约测试

### 阶段六：Statistics API

- 实现统计 Schema、Mapper 和 Router
- 完成全部统计、日期范围统计和零值测试

### 阶段七：旧代码清理与发布验收

- 在替代业务实现和测试完成后删除旧 CLI、Validator、Service 和 Repository
- 更新 README 和相关历史说明
- 运行完整测试、覆盖率和真实数据库隔离检查
- 从干净克隆验证环境、迁移、启动和测试流程
- 完成 `v0.2.0` 发布验收

## 12. V2 完成标准

满足以下条件后，V2 才可进入 `v0.2.0` 发布准备：

- 本文范围内的七个 API 接口全部实现并通过契约测试
- FastAPI 应用可以按照文档启动
- OpenAPI 文档可以生成
- Pydantic Schema、API Mapper 和异常映射符合公开契约
- Domain 和 Application 不依赖 FastAPI、Pydantic、SQLAlchemy 或具体数据库
- SQLAlchemy Repository、Mapper 和轻量 Unit of Work 工作正常
- `api/dependencies.py` 是唯一 Composition Root 例外，Router 仍只依赖 Application Service
- 交易金额、统计金额和响应规范化规则全部通过边界测试
- `Decimal`、SQLAlchemy `Numeric(15, 4)` 和 SQLite 的合法边界 round-trip、无静默舍入或截断及聚合行为得到验证
- 请求校验、未找到和未预期内部异常按契约映射
- 真实 SQLAlchemy UoW 的提交、回滚和 Session 生命周期测试全部通过
- Alembic 可以将空数据库升级到最新 Schema
- API Router 不直接使用 Session 或 Repository
- Domain、Application、Infrastructure 和 API 测试全部通过
- 测试没有访问或修改真实 `data/finance.db` 或 `data/finance_v2.db`
- V1 数据库没有被隐式迁移、覆盖或删除
- uv 锁文件与实际依赖一致
- README 包含经过验证的 API 初始化、启动和测试步骤
- 完整测试全部通过，总体 statement 和 branch coverage 不低于 `90%`，核心 Domain/Application 公共业务分支达到既定 `100%` 测试目标，并完成干净克隆验收
- 暂不实现的能力没有被写成当前功能
- 项目继续明确定位为本地单用户学习与作品集项目，而非生产级财务系统
