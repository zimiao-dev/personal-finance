# Personal Finance API 契约设计

## 1. 设计目标与范围

本文档定义 Personal Finance V2 计划发布版本 `v0.2.0` 的 Web API 契约，作为后续实现和自动化测试的依据。本文描述的是计划实现的行为，不代表当前仓库已经提供 Web API。

V2 将在保留 V1 命令行界面的基础上，使用 FastAPI 和 Pydantic 增加 REST API。API 将复用现有 Service 与 Repository 层，继续使用 Python 标准库 `sqlite3` 和本地 SQLite 数据库，不建立第二套业务流程。

`v0.2.0` 的范围包括：

- FastAPI 应用骨架、健康检查和交互式 API 文档；
- 交易的新增、读取、完整更新和删除接口；
- 分类、日期范围及组合条件查询；
- 全部或指定日期范围的收支统计；
- Pydantic 请求、查询参数和响应模型；
- 稳定的 HTTP 成功与错误语义；
- API 自动化测试及现有 CLI 回归测试。

SQLAlchemy ORM 迁移不属于 `v0.2.0`，计划留给后续版本。当前项目仍定位为本地、单用户的学习与作品集项目，不承诺生产环境能力。

本文后续描述的 FastAPI 路由、Pydantic Schema、`TransactionData` 和完整共享应用用例均为 `v0.2.0` 的目标设计，目前尚未实现。V1 现有 Transaction Service 函数仍是 Repository 的薄转发入口，计划在迁移期间作为 CLI 兼容层暂时保留。

## 2. API 基础约定

| 项目 | 约定 |
| --- | --- |
| API 名称 | Personal Finance API |
| 应用版本 | `0.2.0` |
| 业务接口前缀 | `/api/v1` |
| 健康检查路径 | `/health` |
| 数据格式 | JSON，媒体类型为 `application/json` |
| 日期格式 | 严格的 `YYYY-MM-DD` 字符串，且必须是真实合法日期 |
| OpenAPI 文档 | `/docs` |
| OpenAPI 描述 | `/openapi.json` |

应用版本 `0.2.0` 与 URL 中的契约版本 `v1` 含义不同：前者表示项目发布版本，后者表示首版稳定 HTTP 契约。健康检查不使用业务接口前缀。

V2 暂不提供认证、分页和内容协商扩展。除 `204 No Content` 外，成功响应和错误响应均使用 JSON。

## 3. 资源与路径总览

| 方法 | 路径 | 用途 | 成功状态码 |
| --- | --- | --- | --- |
| `GET` | `/health` | 检查 API 进程是否可响应 | `200` |
| `POST` | `/api/v1/transactions` | 新增交易 | `201` |
| `GET` | `/api/v1/transactions` | 获取全部交易或按条件查询 | `200` |
| `GET` | `/api/v1/transactions/{transaction_id}` | 按 ID 获取交易 | `200` |
| `PUT` | `/api/v1/transactions/{transaction_id}` | 完整更新交易 | `200` |
| `DELETE` | `/api/v1/transactions/{transaction_id}` | 删除交易 | `204` |
| `GET` | `/api/v1/statistics` | 获取全部或日期范围统计 | `200` |

## 4. 数据模型契约

### 4.1 TransactionType

交易类型只允许：

- `income`：收入；
- `expense`：支出。

API 接收类型时应先清理首尾空格并转换为小写，再校验允许值。例如 `" Income "` 规范化为 `"income"`。响应始终使用规范化后的值。

### 4.2 TransactionCreate

用于新增交易的 JSON 请求体。

| 字段 | JSON 类型 | 必填 | 规则 |
| --- | --- | --- | --- |
| `amount` | number | 是 | 必须是有限且大于 `0` 的数值；字符串和布尔值无效 |
| `type` | string | 是 | 清理首尾空格并转为小写后，只允许 `income` 或 `expense` |
| `category` | string | 是 | 清理首尾空格后不能为空；保留原有大小写 |
| `transaction_date` | string | 是 | 必须严格符合 `YYYY-MM-DD`，且是真实合法日期 |
| `description` | string 或 null | 否 | 默认值为 `null` |

请求体不允许出现 `id`、`created_at` 或其他未定义字段。整数或小数形式的 JSON number 均可作为金额输入，并在业务模型中规范化为浮点数。

### 4.3 TransactionUpdate

用于完整更新交易的 JSON 请求体。字段及校验规则与 `TransactionCreate` 相同，但五个业务字段均必须显式提供；其中 `description` 必填但允许为 `null`。

请求体不包含 `id`，交易 ID 只来自路径参数。该接口采用完整替换语义，不提供 `PATCH` 式部分更新。请求体同样禁止 `created_at` 和其他未定义字段。

### 4.4 TransactionResponse

用于返回一条交易记录。

| 字段 | JSON 类型 | 规则 |
| --- | --- | --- |
| `id` | integer | 大于 `0` |
| `amount` | number | 浮点数形式，且大于 `0` |
| `type` | string | `income` 或 `expense` |
| `category` | string | 非空分类文本 |
| `transaction_date` | string | `YYYY-MM-DD` |
| `description` | string 或 null | 可为空 |

数据库自动生成的 `created_at` 不进入当前 `Transaction` 模型，也不在 V2 API 响应中公开。

### 4.5 TransactionQuery

用于 `GET /api/v1/transactions` 的可选查询参数。

| 参数 | 类型 | 默认值 | 规则 |
| --- | --- | --- | --- |
| `category` | string 或 null | `null` | 提供时清理首尾空格，不能为空；保留大小写并进行精确匹配 |
| `start_date` | string 或 null | `null` | 与 `end_date` 成对提供，格式及日期合法性同交易日期 |
| `end_date` | string 或 null | `null` | 与 `start_date` 成对提供，且不得早于开始日期 |

三个参数均未提供时返回全部交易。分类和日期范围同时提供时，两项条件必须同时满足。

### 4.6 StatisticsQuery

用于 `GET /api/v1/statistics` 的可选查询参数。

| 参数 | 类型 | 默认值 | 规则 |
| --- | --- | --- | --- |
| `start_date` | string 或 null | `null` | 与 `end_date` 成对提供 |
| `end_date` | string 或 null | `null` | 与 `start_date` 成对提供，且不得早于开始日期 |

两个参数均未提供时统计全部交易；同时提供时统计包含起止边界的日期范围。

### 4.7 StatisticsResponse

| 字段 | JSON 类型 | 含义 |
| --- | --- | --- |
| `total_income` | number | 匹配交易的收入总额 |
| `total_expense` | number | 匹配交易的支出总额 |
| `transaction_count` | integer | 匹配交易的总数量 |
| `balance` | number | `total_income - total_expense` |

`balance` 由 `TransactionStatistics` 模型根据收入和支出计算，不作为数据库字段持久化。

### 4.8 HealthResponse

健康检查固定返回：

```json
{
  "status": "ok"
}
```

健康检查只证明 API 进程能够响应，不访问 Service、Repository 或数据库。

### 4.9 ErrorResponse

API 自定义错误响应使用统一字段：

```json
{
  "detail": "Transaction not found"
}
```

该模型用于业务层面的 `404` 和服务端 `500` 响应。请求校验失败的 `422` 响应保留 FastAPI 的默认校验错误结构，不强制转换为 `ErrorResponse`。

## 5. 接口详细契约

### 5.1 健康检查

`GET /health`

- 不接收业务参数；
- 不访问数据库；
- 成功时返回 `200 OK` 和 `HealthResponse`。

响应示例：

```json
{
  "status": "ok"
}
```

### 5.2 新增交易

`POST /api/v1/transactions`

- 请求体使用 `TransactionCreate`；
- API mapper 将已校验数据转换为不含 ID 的内部 TransactionData；
- 新增成功后返回 `201 Created` 和完整的 `TransactionResponse`；
- 请求校验失败时返回 `422 Unprocessable Entity`。

请求示例：

```json
{
  "amount": 128.5,
  "type": " expense ",
  "category": " 餐饮 ",
  "transaction_date": "2026-08-30",
  "description": "周末晚餐"
}
```

响应示例：

```json
{
  "id": 42,
  "amount": 128.5,
  "type": "expense",
  "category": "餐饮",
  "transaction_date": "2026-08-30",
  "description": "周末晚餐"
}
```

目标实现中，API mapper 将 `TransactionCreate` 转换为不含 ID 的内部 `TransactionData`，路由只调用一次完整创建用例。共享用例负责把 Repository 生成的 ID 转换为带 ID 的完整 `Transaction`，API 再将该实体转换为 `TransactionResponse`。共享用例内部是否需要回读记录属于实现细节，不属于 HTTP 契约；路由不得为拼装响应而直接调用 Repository 或协调多次旧 Service 调用。

### 5.3 获取全部交易或条件查询

`GET /api/v1/transactions`

支持以下调用方式：

- 不提供参数：获取全部交易；
- 仅提供 `category`：按规范化后的分类精确匹配；
- 同时提供 `start_date` 和 `end_date`：按包含两个边界的日期范围查询；
- 同时提供分类和完整日期范围：使用 AND 语义组合条件。

示例：

```text
GET /api/v1/transactions?category=餐饮&start_date=2026-08-01&end_date=2026-08-31
```

成功时返回 `200 OK` 和 `TransactionResponse` 数组。结果按交易 ID 降序排列；没有匹配记录时返回空数组 `[]`。日期只提供一端、日期顺序错误或其他查询参数校验失败时返回 `422 Unprocessable Entity`。

响应示例：

```json
[
  {
    "id": 42,
    "amount": 128.5,
    "type": "expense",
    "category": "餐饮",
    "transaction_date": "2026-08-30",
    "description": "周末晚餐"
  },
  {
    "id": 37,
    "amount": 35.0,
    "type": "expense",
    "category": "餐饮",
    "transaction_date": "2026-08-10",
    "description": null
  }
]
```

### 5.4 按 ID 获取交易

`GET /api/v1/transactions/{transaction_id}`

- `transaction_id` 必须是大于 `0` 的整数；
- 找到记录时返回 `200 OK` 和 `TransactionResponse`；
- 合法 ID 不存在时返回 `404 Not Found`；
- 路径参数校验失败时返回 `422 Unprocessable Entity`。

未找到响应：

```json
{
  "detail": "Transaction not found"
}
```

### 5.5 完整更新交易

`PUT /api/v1/transactions/{transaction_id}`

- `transaction_id` 必须是大于 `0` 的整数；
- 请求体使用 `TransactionUpdate`，所有业务字段必须提供；
- 更新成功后返回 `200 OK` 和更新后的完整 `TransactionResponse`；
- 响应中的 ID 必须与路径 ID 相同；
- 提交与现有记录相同的内容仍视为成功；
- 只有目标记录不存在时返回 `404 Not Found`；
- 路径或请求体校验失败时返回 `422 Unprocessable Entity`。

请求示例：

```json
{
  "amount": 150.0,
  "type": "expense",
  "category": "餐饮",
  "transaction_date": "2026-08-30",
  "description": "更新后的晚餐记录"
}
```

成功响应示例：

```json
{
  "id": 42,
  "amount": 150.0,
  "type": "expense",
  "category": "餐饮",
  "transaction_date": "2026-08-30",
  "description": "更新后的晚餐记录"
}
```

目标实现中，路径 ID 独立表示目标交易，API mapper 将 `TransactionUpdate` 转换为不含 ID 的 `TransactionData`，路由只调用一次完整更新用例。共享用例负责目标存在性语义、Repository 更新和完整结果生成。API 不得仅凭 SQLite `rowcount` 为 `0` 判断记录不存在，因为相同内容的更新也必须保持成功语义；目标不存在应由明确的应用级未找到结果表达并映射为 `404`。先查询、更新和必要回读的具体顺序属于共享用例内部实现，不在路由或 HTTP 契约中固定。

### 5.6 删除交易

`DELETE /api/v1/transactions/{transaction_id}`

- `transaction_id` 必须是大于 `0` 的整数；
- 删除成功时返回 `204 No Content`，响应体为空；
- 合法 ID 不存在时返回 `404 Not Found`；
- 路径参数校验失败时返回 `422 Unprocessable Entity`。

删除接口不返回被删除对象，也不返回 JSON 成功消息。

目标实现中，路由只调用一次完整删除用例。Repository 的 `rowcount` 只允许在共享应用层内部解释；删除用例成功时不返回业务响应对象，目标不存在时产生明确的应用级未找到结果。API 将两者分别映射为无响应体的 `204` 和稳定的 `404`，不直接读取或解释 SQLite `rowcount`。CLI 为展示记录并请求用户确认，可以在调用删除用例前查询交易；这是 CLI 交互职责，不是 API 路由或共享删除用例的必需流程。

### 5.7 获取收支统计

`GET /api/v1/statistics`

- 不提供日期参数时统计全部交易；
- 同时提供 `start_date` 和 `end_date` 时统计包含两个边界的日期范围；
- 成功时返回 `200 OK` 和 `StatisticsResponse`；
- 无匹配交易时四个统计值均为零；
- 日期只提供一端、日期顺序错误或日期校验失败时返回 `422 Unprocessable Entity`。

响应示例：

```json
{
  "total_income": 5000.0,
  "total_expense": 1850.5,
  "transaction_count": 12,
  "balance": 3149.5
}
```

无统计数据时的响应示例：

```json
{
  "total_income": 0.0,
  "total_expense": 0.0,
  "transaction_count": 0,
  "balance": 0.0
}
```

## 6. 输入校验与共享业务规则

CLI 与 API 使用不同的输入解析机制，但最终必须形成相同的业务语义。输入职责分为以下三层。

### 6.1 CLI 输入边界

现有 `validators.py` 继续负责：

- 清理终端输入字符串；
- 将字符串金额和 ID 转换为浮点数和整数；
- 将日期文本转换为规范的日期字符串；
- 生成 CLI 使用的中文 `ValueError` 信息；
- 配合 `main.py` 在输入错误后结束当前操作并返回菜单。

这些行为属于 CLI Adapter，不要求 API 直接调用现有 Validator。

### 6.2 API 输入边界

Pydantic Schema 计划负责 JSON、路径和查询参数解析，以及以下 HTTP 输入规则：

- 金额必须由 JSON number 表示，必须有限且大于 `0`；字符串、布尔值、`NaN` 和无穷值均无效；
- 类型清理首尾空格并转换为小写后，只允许 `income` 或 `expense`；
- 分类清理首尾空格后不能为空，规范化后保留大小写；
- 交易 ID 必须是大于 `0` 的整数；
- 日期必须严格符合 `YYYY-MM-DD`，且是真实合法日期；
- 日期范围参数必须成对提供；
- 开始日期不得晚于结束日期；
- 创建和更新请求体缺少必填字段或包含未声明字段时必须被拒绝。

Pydantic 输入校验在调用共享应用用例之前完成。API 不得依赖 Pydantic 的宽松转换来接受字符串金额、布尔金额或不符合契约的宽松日期形式。

### 6.3 共享核心不变量

共享应用层仍应保护入口无关的业务不变量，至少包括：

- ID 为正整数；
- 金额有限且大于 `0`；
- 类型只能是 `income` 或 `expense`；
- 分类规范化后不能为空；
- 日期具有合法业务语义；
- 日期范围参数成对提供；
- 开始日期不得晚于结束日期。

本文不规定具体校验函数或要求建立大型领域验证框架。实现可以提取少量共享规则或通过内部输入对象保证不变量，但不能只依赖某一个 Adapter。Repository 可以保留防御性检查，但不负责 HTTP 参数清理、HTTP 状态码、终端提示或入口级错误格式。

## 7. 错误响应策略

| 场景 | 应用层表达 | 状态码 | 响应约定 |
| --- | --- | --- | --- |
| Pydantic 请求体、路径或查询参数校验失败 | 调用共享用例前失败 | `422` | FastAPI 默认校验错误结构 |
| 按 ID 获取不到交易 | `get_transaction()` 返回 `None` | `404` | `{"detail": "Transaction not found"}` |
| 更新或删除目标不存在 | 明确的应用级未找到异常或等价结果 | `404` | `{"detail": "Transaction not found"}` |
| 已知的共享业务规则失败 | 仅显式映射已定义的应用级校验异常 | 由后续契约明确 | 不得宽泛捕获所有 `ValueError` |
| 未预期的 Service、Repository、SQLite 或模型转换异常 | 未分类内部异常 | `500` | `{"detail": "Internal server error"}` |

代表性的 `422` 响应结构如下。具体错误位置和说明由所使用的 FastAPI、Pydantic 版本根据失败字段生成：

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

Pydantic `422` 发生在调用共享应用用例之前，因此失败请求不得访问 Service 或 Repository。共享业务规则失败正常情况下也应被 Pydantic 提前阻止；如果共享核心后续定义了明确的应用级校验异常，API 只能对已知异常进行显式映射。不得捕获所有 `ValueError` 并机械返回 `422`，任意未分类的 `ValueError` 也属于内部异常。

API 层负责将查询的 `None` 和更新、删除的应用级未找到结果映射为稳定的 `404`。目标设计可以使用不依赖 FastAPI 的 `TransactionNotFoundError` 或等价结果，但共享 Service 不返回 HTTP 状态码，也不抛出 FastAPI `HTTPException`。

未预期异常应在服务端记录，并向客户端返回稳定的通用 `500` 消息，不得泄露 SQL、数据库路径、Python 异常文本、Traceback 或其他内部实现细节。日志格式、日志存储和部署平台配置不属于本契约范围。

CLI 继续使用自身的终端错误提示；Repository 和共享应用用例不生成 HTTP 响应，也不负责 CLI 展示。

## 8. 分层职责与模型转换边界

### 8.1 目标依赖关系

`v0.2.0` 采用以下目标结构：

```text
CLI Adapter ─┐
             ├─> 共享应用用例 ─> Repository ─> database.py ─> SQLite
API Adapter ─┘
```

该结构为目标设计，目前尚未实现。V1 的 Transaction Service 仍以 Repository 薄转发为主，迁移完成前不得把目标用例描述为现有能力。

职责边界如下：

- CLI Adapter 负责菜单、`input()`、终端字符串解析、修改和删除前的用户确认、终端输出，以及将共享结果转换为 CLI 提示；
- API Adapter 负责 FastAPI 路由、Pydantic 请求与响应 Schema、查询参数、HTTP 与内部模型转换、状态码和错误响应；
- 共享应用用例负责创建完整资源、获取和条件查询、更新与删除的存在性语义、解释 Repository 的新增 ID 和 `rowcount`，以及保护入口无关的日期范围等业务规则；
- Repository 负责 SQL、SQLite 持久化、数据库行映射、查询条件组合、ID 降序和统计聚合；
- `database.py` 负责 SQLite 连接路径、数据目录和表初始化。

Pydantic Schema 不调用 Service 或数据库。API 不调用 CLI 函数，CLI 不调用 FastAPI 路由。路由不得直接编写 SQL、访问 Repository、解释 `rowcount` 或复制共享业务编排。共享应用用例不依赖 FastAPI、Pydantic、HTTP、`input()`、`print()` 或终端提示。

### 8.2 目标共享应用用例契约

以下签名只表示 `v0.2.0` 的目标契约提示，目前尚未实现：

```python
create_transaction(data: TransactionData) -> Transaction

get_transaction(transaction_id: int) -> Transaction | None

list_transactions(
    *,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[Transaction]

replace_transaction(
    transaction_id: int,
    data: TransactionData,
) -> Transaction

remove_transaction(transaction_id: int) -> None

get_transaction_statistics(
    start_date: str | None = None,
    end_date: str | None = None,
) -> TransactionStatistics
```

`TransactionData` 是入口无关的内部输入对象，不是 Pydantic Schema。它包含 `amount: float`、`type: str`、`category: str`、`transaction_date: str` 和 `description: str | None`，不包含交易 ID。

契约语义：

- `create_transaction()` 解释 Repository 生成的 ID 并返回完整 `Transaction`；
- `get_transaction()` 在目标不存在时返回 `None`；
- `list_transactions()` 统一支持全部、分类、日期范围和组合查询，空结果为 `[]`；
- `replace_transaction()` 接收独立的路径 ID 和完整业务数据，返回更新后的 `Transaction`，目标不存在时产生应用级未找到结果，相同内容更新仍成功；
- `remove_transaction()` 成功时无业务返回值，目标不存在时产生应用级未找到结果；
- `get_transaction_statistics()` 返回 `TransactionStatistics`，无匹配数据时保持零值语义。

Repository 可以继续在内部返回新增 ID 和 `rowcount`，但新的 API 调用方不得直接读取或解释这些持久化结果。共享用例内部的 Repository 调用次数、查询顺序和是否回读不属于 API 契约。

### 8.3 CLI 兼容包装层

现有 `add_transaction()`、`update_transaction()` 和 `delete_transaction()` 可以在 CLI 迁移期间暂时保留，但目标是让它们委托给新的共享应用用例，而不是维持第二套业务流程。API 只依赖新的完整共享用例，不调用这些旧薄转发函数。CLI 完成迁移后可以删除兼容包装层，本文不承诺旧 Service 函数永久保留。

### 8.4 HTTP 与内部模型转换

HTTP Schema、`TransactionData` 和现有 dataclass 是不同边界的模型。模型转换应位于 API mapper 或等价的 API 边界组件中，不进入 Repository，也不能使共享应用用例依赖 Pydantic。

请求方向：

- 日期在 JSON 和 URL 中表现为严格的 `YYYY-MM-DD` 字符串；
- Pydantic Schema 内部计划使用日期类型完成日历合法性校验，并额外保证原始输入严格符合 `YYYY-MM-DD`；
- API mapper 在构造 `TransactionData` 或调用查询、统计用例前，使用日期对象的 `isoformat()` 转换为内部规范字符串；
- 现有 Model、Service 和 Repository 继续使用 `YYYY-MM-DD` 字符串，不直接接收 Pydantic 日期对象；
- 创建请求转换为不含 ID 的 `TransactionData`；
- 更新请求也转换为 `TransactionData`，路径 ID 作为独立参数传给完整更新用例；
- `description: str | None` 在 Schema、`TransactionData` 和 `Transaction` 之间原样传递。

响应方向：

- 共享用例返回的 `Transaction.transaction_date` 当前是字符串；
- API mapper 将内部日期字符串解析或验证为 API 使用的日期类型，再由响应 Schema 序列化为 `YYYY-MM-DD` JSON 字符串；
- 内部日期字符串违反既定格式时属于内部数据或实现异常，应进入稳定 `500` 路径，不能伪装成客户端 `422`；
- `created_at` 不进入当前 `Transaction` 模型或 API 响应；
- `TransactionStatistics` 的 `total_income`、`total_expense` 和 `transaction_count` 映射到 `StatisticsResponse`；
- `balance` 从 `TransactionStatistics.balance` 计算属性读取，不持久化。

## 9. API 测试矩阵

### 9.1 路由与公开结果

| 接口或领域 | 最小必要场景 | 主要断言 |
| --- | --- | --- |
| 健康检查 | 正常响应 | `200`、固定 JSON、共享用例与数据库未调用 |
| 新增交易 | 合法请求、完整创建结果 | `201` 完整对象；路由调用一次完整创建用例；不解释新增 ID |
| 获取全部交易 | 多条记录、空结果 | `200`、响应数组、空结果为 `[]` |
| 分类查询 | 精确匹配、首尾空格、无匹配 | 规范化分类传给共享用例，稳定空数组 |
| 日期范围查询 | 起止边界、单边日期、反向日期 | 两个边界包含；非法组合为 `422` |
| 组合查询 | 分类与日期同时提供 | 三个规范化参数同时传递，使用 AND 语义 |
| 按 ID 获取 | 找到、不存在、非法 ID | `200`、稳定 `404`、`422` |
| 完整更新 | 字段全部更新、相同内容、不存在、缺字段 | 路由调用一次完整更新用例；`200` 且 ID 不变；稳定 `404`；`422` |
| 删除 | 成功、不存在、非法 ID | 路由调用一次完整删除用例；`204` 空响应；稳定 `404`；`422` |
| 全部统计 | 混合收支、无记录 | 四个统计字段正确，无数据为零值 |
| 日期范围统计 | 边界记录、无匹配、非法日期组合 | 边界包含、零值、`422` |
| 未预期异常 | 共享用例抛出测试专用内部异常 | `500` 通用消息，不泄露原始异常或内部细节 |

路由测试还应证明 API 不调用 Repository，不解释新增 ID 或 `rowcount`，且获取、更新和删除的未找到结果均映射为相同稳定的 `404`。

### 9.2 Schema 与请求校验

至少覆盖：

- 金额小于或等于零；
- `NaN`、正无穷和负无穷等非有限金额；
- 不应被宽松接受的字符串金额和布尔金额；
- 非法交易类型，以及类型清理和小写规范化；
- 分类清理后为空；
- 不存在的日历日期和非严格 `YYYY-MM-DD` 日期；
- 创建或更新请求体包含额外字段；
- 创建缺少必填字段；
- 更新缺少任一必填字段或请求体携带 ID；
- 路径 ID 为零、负数或非法类型；
- 日期范围只提供一端或开始日期晚于结束日期。

### 9.3 模型转换

至少覆盖：

- Pydantic 日期对象转换为内部 `YYYY-MM-DD` 字符串；
- 内部日期字符串转换为响应日期；
- 创建时 `TransactionData` 不包含 ID；
- 更新时路径 ID 独立传入完整更新用例；
- `description` 的字符串和 `null`；
- 统计响应从 `TransactionStatistics` 取得三个原始字段和 `balance`；
- 非法内部日期进入内部错误路径，而不是客户端 `422`。

### 9.4 测试分层与隔离

- API 路由单元测试应替换 Route 实际引用的完整共享用例，验证 HTTP 契约、参数转换、调用次数和错误映射，不连接真实数据库；
- Pydantic Schema 测试应覆盖字段规则、规范化和跨字段校验；
- 需要数据库的 API 集成测试必须使用隔离的临时 SQLite 数据库；
- 现有 Repository 测试继续验证 SQL、筛选、日期边界、排序、聚合，API 测试不重复这些实现细节；
- API 测试不得断言 SQL 文本、Repository 函数调用次数、固定自增 ID 或 SQLite `rowcount`；
- 所有数据库测试不得读取或修改真实的 `data/finance.db`，不得依赖执行顺序；
- V1 已承诺的行为必须继续得到回归保护，但测试总数不要求永久保持 130 项。

## 10. `v0.2.0` 暂不实现

以下能力不属于本版本：

- 登录、身份认证、权限管理和多用户数据隔离；
- Web 前端或桌面 GUI；
- 云数据库和云同步；
- 预算管理、复杂财务分析和数据可视化；
- 数据导入导出；
- 异步数据库访问；
- 微服务拆分；
- SQLAlchemy ORM 迁移；
- `PATCH` 部分更新接口；
- 生产环境部署、高可用、安全合规或性能承诺。

未来可以评估上述能力，但不得在 `v0.2.0` 文档或发布说明中描述为已实现功能。

## 11. API 契约完成标准

进入实现阶段前，本契约应满足：

- 所有计划公开的路径、方法、输入模型、响应模型和主要状态码已经定义；
- CRUD、条件查询、统计和健康检查均有可验证的成功与错误行为；
- 日期边界、查询顺序、空结果、零值统计和完整更新语义没有歧义；
- HTTP、Schema、Service、Repository 和数据库职责清晰，且不复制 CLI 业务流程；
- SQLAlchemy 明确排除在 `v0.2.0` 范围之外；
- API 测试矩阵覆盖关键契约，并明确真实数据库隔离要求；
- 文档通过只读 Review，未解决的契约问题在编码前完成决策。

`v0.2.0` 发布前还应完成 FastAPI 与 Pydantic 依赖锁定、API 实现及测试、现有 130 项测试回归、README 更新，以及从干净克隆执行环境同步、数据库初始化、CLI、API 和完整测试的发布验收。
