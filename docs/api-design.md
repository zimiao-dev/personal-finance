# Personal Finance API 契约设计

## 1. 文档目的与范围

本文档定义 Personal Finance V2 计划发布版本 `v0.2.0` 的 HTTP 契约，作为后续 FastAPI、Pydantic Schema、Mapper、Router 和 API 测试的依据。

本文描述的是尚未实现的目标行为。当前仓库在 `a77b6bb` 基线上仍是 V1 CLI 代码，不代表 FastAPI、Pydantic、SQLAlchemy、Alembic 或以下 API 已经可用。

V2 是 API-only 的本地单用户后端项目，不提供或维护 CLI。应用分层、Repository Port、Unit of Work、SQLAlchemy 和迁移设计见 [V2 架构设计](architecture.md)，产品范围和验收要求见 [V2 需求文档](v2-requirements.md)。

## 2. API 基础约定

| 项目 | 约定 |
| --- | --- |
| API 名称 | Personal Finance API |
| 应用版本 | `0.2.0` |
| 业务接口前缀 | `/api/v1` |
| 健康检查路径 | `/health` |
| 数据格式 | JSON，媒体类型为 `application/json` |
| 金额格式 | 普通十进制字符串 |
| 日期格式 | 严格的 `YYYY-MM-DD` 字符串 |
| OpenAPI 文档 | `/docs` |
| OpenAPI 描述 | `/openapi.json` |

应用版本 `0.2.0` 与 URL 中的契约版本 `v1` 含义不同：前者表示项目发布版本，后者表示首版 HTTP 契约。健康检查不使用业务接口前缀。

除 `204 No Content` 外，成功响应和错误响应均使用 JSON。V2 不提供认证、分页、`PATCH` 或内容协商扩展。

## 3. 资源与路径总览

| 方法 | 路径 | 用途 | 成功状态码 |
| --- | --- | --- | --- |
| `GET` | `/health` | 检查 API 进程是否可响应 | `200` |
| `POST` | `/api/v1/transactions` | 创建交易 | `201` |
| `GET` | `/api/v1/transactions` | 获取全部交易或按条件查询 | `200` |
| `GET` | `/api/v1/transactions/{transaction_id}` | 按 ID 获取交易 | `200` |
| `PUT` | `/api/v1/transactions/{transaction_id}` | 完整更新交易 | `200` |
| `DELETE` | `/api/v1/transactions/{transaction_id}` | 删除交易 | `204` |
| `GET` | `/api/v1/statistics` | 获取全部或日期范围统计 | `200` |

## 4. Schema 契约

### 4.1 通用字段规则

#### 交易金额 `amount`

API 请求和响应中的交易金额均使用 JSON string，而不是 JSON number。以下是请求表示示例；响应使用本节后文定义的 canonical 格式：

```json
{
  "amount": "128.50"
}
```

HTTP 边界必须先确认原始 JSON 值确实是 string，再校验字符串完整匹配：

```text
^(0|[1-9]\d{0,10})(\.\d{1,4})?$
```

并同时满足：

- 整数部分为 1 至 11 位；除单独的 `"0"` 外不得以 `0` 开头
- 小数部分如存在则为 1 至 4 位；整数金额合法，不要求固定两位小数
- 解析为有限 `Decimal` 后满足 `0 < amount <= 99999999999.9999`
- 不接受科学计数法、`NaN`、无穷或其他非有限形式
- 不接受 JSON number 或布尔值
- 不通过隐式转换接受字符串以外的金额输入
- 不接受前后空白、正负号或缺少完整整数/小数部分的形式
- 不通过舍入、`quantize` 或截断把非法输入转换为合法输入

合法示例包括 `"1"`、`"0.1"`、`"128.50"`、`"0.0001"` 和 `"99999999999.9999"`。

非法示例包括 JSON number `0.1`、布尔值 `true`、`"1e3"`、`"NaN"`、`"Infinity"`、`"-Infinity"`、`"+1"`、`"-1"`、`".5"`、`"1."`、`" 1.00 "`、`"0"`、`"0.00001"`、`"00.1"`、`"01"`、`"01.25"` 和 `"100000000000.0000"`。

目标校验顺序为：

1. 检查原始 JSON 类型为 string；
2. 检查严格普通十进制格式；
3. 转换为 `Decimal`；
4. 检查有限性、大于零、整数位数、小数位数和最大值。

不能只将 Schema 字段声明为 `Decimal` 并依赖 Pydantic 隐式转换。以上任一步失败均返回 `422`，且不得进入 Application 或持久化边界。

Infrastructure 使用 SQLAlchemy `Numeric(15, 4)` 持久化，API Schema、Domain 和 Application 使用 `Decimal`；完整设计见 [V2 架构设计](architecture.md#12-sqlalchemy-orm-与-repository-实现)。

#### 统计金额

- `total_income` 必须是有限且大于等于零的 `Decimal`
- `total_expense` 必须是有限且大于等于零的 `Decimal`
- `balance` 必须是有限的 `Decimal`，可以为正数、零或负数

所有金额响应均序列化为普通十进制 JSON string：

- 禁止科学计数法
- 正零和负零统一输出为 `"0"`
- 删除小数部分末尾无意义的零和末尾孤立的小数点
- 不要求固定小数位数，也不保留输入字符串的原始 scale
- 负余额可以输出为 `"-20.5"`
- 不通过浮点转换或科学计数法表示金额

canonical 示例：

- `Decimal("128.50")` -> `"128.5"`
- `Decimal("36.80")` -> `"36.8"`
- `Decimal("5000.00")` -> `"5000"`
- `Decimal("1.2300")` -> `"1.23"`
- `Decimal("0.1000")` -> `"0.1"`
- `Decimal("0.0001")` -> `"0.0001"`
- `Decimal("0")` -> `"0"`
- `Decimal("-0.0000")` -> `"0"`

请求中的尾随零不保证在响应中保留，例如请求金额 `"128.50"` 的响应金额为 `"128.5"`。`Numeric(15, 4)` 是单笔交易金额边界，不限制统计总额；统计金额仍按同一 canonical 规则输出。

#### 交易类型

交易类型必须是 JSON string。清理首尾空格并转换为小写后，只允许：

- `income`
- `expense`

响应始终使用规范化后的值。

#### 分类

分类必须是 JSON string。清理首尾空格后不能为空，并保留原有大小写。查询使用规范化后的分类进行精确匹配。

#### 日期

日期在 JSON 和 URL 中表现为严格的 `YYYY-MM-DD` 字符串，并且必须是真实合法的日历日期。

Pydantic Schema 计划在内部使用 `datetime.date`，但仍必须在解析前或解析过程中检查原始输入严格符合该格式，不能依赖可能接受时间戳或宽松形式的默认转换。

#### ID

路径 ID 必须是大于零的整数。零、负数、小数、布尔形式或非整数字符串无效。

### 4.2 `TransactionCreate`

用于 `POST /api/v1/transactions`。

| 字段 | JSON 类型 | 必填 | 规则 |
| --- | --- | --- | --- |
| `amount` | string | 是 | 严格格式；解析后满足 `0 < amount <= 99999999999.9999` |
| `type` | string | 是 | 规范化后为 `income` 或 `expense` |
| `category` | string | 是 | 清理首尾空格后不能为空 |
| `transaction_date` | string | 是 | 严格合法的 `YYYY-MM-DD` |
| `description` | string 或 null | 否 | 缺省或 `null` 规范化为 `null`；字符串按描述规则规范化 |

请求体拒绝 `id`、`created_at` 和其他未定义字段。

请求示例：

```json
{
  "amount": "36.80",
  "type": "expense",
  "category": "餐饮",
  "transaction_date": "2026-09-01",
  "description": "午餐"
}
```

### 4.3 `TransactionUpdate`

用于 `PUT /api/v1/transactions/{transaction_id}`，表示完整替换。

字段和规则与 `TransactionCreate` 相同，但五个业务字段必须全部显式提供；`description` 必填但允许为 `null`。

请求体不包含 `id`，目标 ID 只来自路径参数。请求体同样拒绝 `created_at` 和其他未定义字段。

描述字段统一规则：

- 创建时缺省或显式 `null` 均映射为 Domain `None`
- 更新时字段必须出现，但值可以为 `null`
- 字符串先清理首尾空白；清理后为空则规范化为 `null`
- 清理后非空则保存清理后的字符串，例如 `"  lunch  "` 保存为 `"lunch"`
- API 响应只返回规范化字符串或 `null`

因此 `""`、`"   "` 和 `null` 均产生 `null`；该规则是 V2 新契约，不表示 V1 CLI 已实施相同行为。

### 4.4 `TransactionResponse`

用于返回一条交易记录。

| 字段 | JSON 类型 | 规则 |
| --- | --- | --- |
| `id` | integer | 大于 `0` |
| `amount` | string | 规范化普通十进制字符串，表示范围内的有限正数 |
| `type` | string | `income` 或 `expense` |
| `category` | string | 非空规范化文本 |
| `transaction_date` | string | `YYYY-MM-DD` |
| `description` | string 或 null | 可为 `null` |

响应示例：

```json
{
  "id": 15,
  "amount": "36.8",
  "type": "expense",
  "category": "餐饮",
  "transaction_date": "2026-09-01",
  "description": "午餐"
}
```

V2 当前响应不公开 `created_at`。

### 4.5 `TransactionQuery`

用于 `GET /api/v1/transactions`。

| 参数 | HTTP 表示 | 默认值 | 规则 |
| --- | --- | --- | --- |
| `category` | string | 未提供 | 提供时清理首尾空格，不能为空；精确匹配 |
| `start_date` | string | 未提供 | 与 `end_date` 成对提供；严格合法日期 |
| `end_date` | string | 未提供 | 与 `start_date` 成对提供；不得早于开始日期 |

三个参数均未提供时返回全部交易。分类和完整日期范围同时提供时，两个条件使用 AND 语义。

### 4.6 `StatisticsQuery`

用于 `GET /api/v1/statistics`。

| 参数 | HTTP 表示 | 默认值 | 规则 |
| --- | --- | --- | --- |
| `start_date` | string | 未提供 | 与 `end_date` 成对提供；严格合法日期 |
| `end_date` | string | 未提供 | 与 `start_date` 成对提供；不得早于开始日期 |

两个参数均未提供时统计全部交易；同时提供时统计包含起止边界的日期范围。

### 4.7 `StatisticsResponse`

| 字段 | JSON 类型 | 含义 |
| --- | --- | --- |
| `total_income` | string | 普通十进制字符串形式的收入总额 |
| `total_expense` | string | 普通十进制字符串形式的支出总额 |
| `transaction_count` | integer | 匹配交易数量 |
| `balance` | string | `total_income - total_expense` |

示例：

```json
{
  "total_income": "5000",
  "total_expense": "1850.5",
  "transaction_count": 12,
  "balance": "3149.5"
}
```

当支出大于收入时，余额为负数，例如：

```json
{
  "total_income": "10",
  "total_expense": "30.5",
  "transaction_count": 2,
  "balance": "-20.5"
}
```

无匹配数据时返回：

```json
{
  "total_income": "0",
  "total_expense": "0",
  "transaction_count": 0,
  "balance": "0"
}
```

`balance` 由 Domain 统计模型计算，不作为数据库字段持久化。

### 4.8 `HealthResponse`

固定响应：

```json
{
  "status": "ok"
}
```

### 4.9 `ErrorResponse`

除 FastAPI/Pydantic 默认 `422` 校验详情外，稳定的业务错误和内部错误均使用同一顶层结构：

```json
{
  "detail": "Transaction not found"
}
```

Pydantic 请求校验失败保留 FastAPI 的 `422` 校验错误结构，不强制转换为 `ErrorResponse`，也不承诺其每个内部字段的固定文本。

本契约只有一套错误顶层格式：字段名始终为 `detail`。默认 `422` 的 `detail` 是校验错误数组；已映射的业务错误和 `500` 的 `detail` 是稳定字符串。不得另建第二套错误 envelope。

## 5. 接口详细契约

### 5.1 健康检查

```http
GET /health
```

成功响应：`200 OK`

```json
{
  "status": "ok"
}
```

健康检查只证明 API 进程能够响应，不访问数据库、Application Service、Repository 或 Unit of Work。

### 5.2 创建交易

```http
POST /api/v1/transactions
```

- 请求体：`TransactionCreate`
- 成功状态：`201 Created`
- 成功响应：`TransactionResponse`

Router 将 Schema 交给 API Mapper，转换为包含 `Decimal` 和 `datetime.date` 的 Application DTO，然后只调用 Transaction Service 的完整创建用例。Service 返回完整 Domain Entity，API Mapper 再生成响应 Schema。

Router 不通过旧式“先新增取得 ID，再查询一次”的流程拼装响应，也不直接读取数据库生成 ID。

### 5.3 获取全部或条件查询交易

```http
GET /api/v1/transactions
```

- 查询参数：`TransactionQuery`
- 成功状态：`200 OK`
- 成功响应：`TransactionResponse` 数组

行为：

- 无参数时返回全部交易
- 仅分类时使用规范化分类精确匹配
- 提供完整日期范围时包含开始和结束边界
- 分类和日期同时提供时使用 AND 条件
- 结果按 ID 降序
- 无匹配结果时返回 `[]`

日期只提供一端、日期反向或其他查询参数错误返回 `422 Unprocessable Entity`。

### 5.4 按 ID 获取交易

```http
GET /api/v1/transactions/{transaction_id}
```

- 成功状态：`200 OK`
- 成功响应：`TransactionResponse`
- 目标不存在：`404 Not Found`
- 非法路径 ID：`422 Unprocessable Entity`

未找到响应：

```json
{
  "detail": "Transaction not found"
}
```

### 5.5 完整更新交易

```http
PUT /api/v1/transactions/{transaction_id}
```

- 请求体：`TransactionUpdate`
- 成功状态：`200 OK`
- 成功响应：`TransactionResponse`
- 目标不存在：`404 Not Found`
- 非法路径或请求：`422 Unprocessable Entity`

路径 ID 与 Application DTO 独立传递。Router 只调用一次完整更新用例，不直接操作 Session、查询 Repository 或解释 `rowcount`。

更新为与当前内容相同的数据仍返回成功。更新后资源 ID 与路径 ID 一致。

### 5.6 删除交易

```http
DELETE /api/v1/transactions/{transaction_id}
```

- 成功状态：`204 No Content`
- 成功响应体：空
- 目标不存在：`404 Not Found`
- 非法路径 ID：`422 Unprocessable Entity`

Router 只调用删除用例，不读取 SQLAlchemy 或数据库受影响行数。

### 5.7 获取统计

```http
GET /api/v1/statistics
```

- 查询参数：`StatisticsQuery`
- 成功状态：`200 OK`
- 成功响应：`StatisticsResponse`

无日期参数时统计全部交易；完整日期范围包含起止边界。日期只提供一端、日期反向或日期格式错误返回 `422 Unprocessable Entity`。

## 6. HTTP 与内部模型转换

目标请求方向：

```text
HTTP JSON
  -> Pydantic Schema
  -> API Mapper
  -> Application DTO / Domain 类型
  -> Application Service
```

目标响应方向：

```text
Domain Entity / Application Result
  -> API Mapper
  -> Pydantic Response Schema
  -> JSON
```

转换规则：

- 交易金额字符串先完成格式、有限性和正数校验，再由 Schema/Mapper 转换为 `Decimal`
- Domain/Application 的交易金额和统计金额始终保持 `Decimal`
- 响应 Mapper 使用普通定点格式输出 `Decimal`，删除小数部分末尾无意义的零和孤立小数点，并将正零和负零统一为 `"0"`；不得经过 `float`
- HTTP 日期字符串经严格格式和日历校验后成为 `datetime.date`
- Application DTO 和 Domain Entity 继续使用 `date`，不转换成 V1 风格内部字符串
- SQLAlchemy ORM 在 Infrastructure 中使用 `Numeric(15, 4)` 和 `Date`
- `description` 按本契约规范化后，以 `str | None` 在各边界间传递
- 创建 DTO 不包含 ID；更新 ID 只来自路径
- ORM Model 不直接进入响应，Pydantic Schema 不直接进入 Repository
- `created_at` 不进入当前 API Schema
- 统计响应中的 `balance` 来自 Domain 统计结果，不从数据库持久化字段读取

如果 Infrastructure 返回违反 Domain 类型或规则的数据，应视为内部数据或实现错误并进入统一 `500`，不能伪装成客户端 `422`。金额转换不得经过 `float`。

## 7. 校验与错误边界

### 7.1 异常映射矩阵

| 来源或条件 | HTTP 状态 | `detail` 语义 | 事务与访问要求 |
| --- | --- | --- | --- |
| Pydantic 请求解析或 Schema 校验失败 | `422 Unprocessable Entity` | FastAPI/Pydantic 默认校验详情数组 | Application Service 调用前失败，不访问 Repository 或数据库 |
| 请求数据触发已知 Domain/Application 业务校验失败 | `422 Unprocessable Entity` | `"Business validation failed"` | 写事务必须回滚，不暴露内部异常文本 |
| 获取、更新或删除的资源不存在 | `404 Not Found` | `"Transaction not found"` | 不把 `rowcount` 或 ORM 状态暴露给 API |
| 持久化数据破坏内部不变量，或出现不应由合法请求触发的内部业务错误 | `500 Internal Server Error` | `"Internal server error"` | 回滚并记录内部诊断信息，客户端只收到通用消息 |
| 未处理异常、SQLAlchemy/SQLite/数据库异常或提交失败 | `500 Internal Server Error` | `"Internal server error"` | 回滚并关闭 Session |

V2 当前没有唯一性冲突、版本冲突或其他需要映射为 `409 Conflict` 的业务场景，因此不定义 `409` 响应。

### 7.2 映射责任与边界

- Router 或应用工厂注册的全局异常处理器负责把明确的 Domain/Application 异常映射为 HTTP 响应
- Domain/Application 异常不得依赖 FastAPI `HTTPException`、HTTP 状态码或响应 Schema
- 预期业务错误必须按矩阵显式映射，不能被笼统转换为 `500`
- 只有明确声明的业务异常可以映射为 `422`；不得捕获所有 `ValueError` 并机械转换
- 持久化脏数据、Mapper 不变量破坏和未分类异常必须进入 `500`，不能伪装成客户端错误
- 内部异常文本、SQL、数据库 URL 或路径、ORM 状态和 Traceback 不得泄漏给客户端

未找到响应固定为：

```json
{
  "detail": "Transaction not found"
}
```

已知业务校验失败响应固定为：

```json
{
  "detail": "Business validation failed"
}
```

该通用消息用于避免把 Domain/Application 内部异常文本当作公开契约。具体字段级错误应尽量在 Pydantic Schema 阶段产生默认 `422` 校验详情。

内部错误响应固定为：

```json
{
  "detail": "Internal server error"
}
```

## 8. API 测试契约

### 8.1 Schema 测试

至少覆盖：

- 合法普通十进制金额字符串
- 合法边界 `"0.0001"`、`"0.1"`、`"1"`、`"128.50"` 和 `"99999999999.9999"`
- 非法边界 `"0"`、`"0.00001"`、`"100000000000"` 和 `"99999999999.99999"`
- 负金额、前导零、前后空白、正负号和不完整小数
- 科学计数法、`NaN` 和正负无穷
- JSON number 和布尔值
- 非法金额返回 `422`，不得通过舍入、量化或截断变成合法值，且不得进入 Application 或持久化边界
- 类型规范化和非法类型
- 分类规范化及清理后为空
- 不存在的日历日期和非严格 `YYYY-MM-DD`
- 请求体额外字段
- 创建缺少必填字段
- 更新缺少任一字段或携带 ID
- `description` 创建缺省、显式 `null`、空字符串、纯空白及首尾空白规范化
- PUT 缺少 `description` 返回 `422`
- 路径 ID 为零、负数、小数或非法类型
- 日期只提供一端和开始日期晚于结束日期

### 8.2 Mapper 测试

至少覆盖：

- 金额字符串到 `Decimal`，且不经过 `float`
- `Decimal` 到 canonical 普通十进制响应字符串，包括尾随零删除、零值和负余额
- `datetime.date` 在 Schema、DTO 和 Domain 间传递
- 创建 DTO 不含 ID
- 更新路径 ID 独立传递
- `description` 的规范化字符串和 `null`
- Domain Entity 到 `TransactionResponse`
- 统计金额和 `balance` 的字符串表示
- 非法 Infrastructure 数据进入内部错误路径

### 8.3 Router 与异常处理测试

至少覆盖：

- 七个接口的成功状态和响应
- 创建 `201`、查询/更新 `200`、删除 `204`
- 空列表和零值统计
- 获取、更新和删除未找到的稳定 `404`
- 输入错误的 `422`
- 未预期异常的稳定 `500`
- `500` 不泄露原始错误信息
- 健康检查不调用数据库或 Service
- FastAPI 依赖覆盖提供 fake Service
- Router 只调用 Application Service，不调用 Repository 或 Session

### 8.4 测试边界与隔离

- API 单元测试不连接真实数据库
- API 测试不验证 SQL 文本、ORM 内部状态或数据库 `rowcount`
- SQLAlchemy Repository 的筛选、排序和持久化由 Infrastructure 集成测试负责
- Infrastructure 测试使用真实 SQLite 验证 `Decimal`、SQLAlchemy `Numeric(15, 4)` 和合法金额边界的 round-trip 与统计行为
- 合法金额写入并读取后的 `Decimal` 数值必须与接受的输入数值相等，不得发生静默舍入或截断
- 统计结果使用 Application/Domain 统计模型，HTTP 输出遵守同一 canonical 规则
- 需要数据库的端到端 API 测试必须使用独立临时 SQLite 数据库，并验证合法边界请求可以写入、读取并得到 canonical 金额响应
- 测试不得访问或修改 `data/finance.db` 或 `data/finance_v2.db`
- 测试不依赖执行顺序或固定自增 ID
- `v0.2.0` 发布时完整测试必须全部通过，并以 pytest-cov 检查 statement 和 branch coverage；项目总体最低门槛为 `90%`
- Domain/Application 核心公共业务分支以 `100%` 覆盖为目标，覆盖率数字不能替代七个路径的成功和关键错误行为断言
- 以上是发布门槛与目标，不表示当前测试已经达到

## 9. V2 暂不提供的 HTTP 能力

- `PATCH` 部分更新
- 分页
- 登录、认证、权限和多用户隔离
- Web 前端
- 异步数据库访问
- PostgreSQL、Docker、Redis 或 Celery 集成
- 数据导入导出
- 云部署或生产级能力承诺

## 10. API 契约完成标准

进入实现阶段前，本契约应满足：

- 七个路径的方法、输入、响应和主要状态码明确
- 交易金额普通十进制字符串、有限正数规则和 `422` 行为明确
- 统计总额非负、余额可带符号，金额响应不使用科学计数法
- 日期在 HTTP 中严格为 `YYYY-MM-DD`，内部为 `datetime.date`
- 创建、获取、列表、完整更新、删除和统计行为无歧义
- 分类精确匹配、日期闭区间、组合 AND 和 ID 降序保持一致
- 空列表、零值统计、`404`、`422` 和稳定 `500` 行为明确
- Router、Schema、Mapper 和 Application 的边界明确
- API 不依赖 V1 CLI、旧 Service 或旧 `sqlite3` Repository
- API 测试明确真实数据库隔离要求
- 架构细节与 [V2 架构设计](architecture.md) 一致

本文通过 Review 只表示契约可以进入实现，不表示任何 API 已经实现或测试通过。
