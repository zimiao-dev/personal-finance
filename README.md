# Personal Finance

Personal Finance 是一个基于 FastAPI、SQLAlchemy 和 SQLite 开发的个人财务管理后端项目，提供交易记录的新增、查询、完整替换、删除和收支统计 REST API。

项目采用 Domain、Application、Infrastructure 和 API 分层结构，通过 Repository 与 Unit of Work 隔离业务逻辑和数据库访问，并使用 Alembic 管理数据库迁移。

当前版本为 `0.2.0`。V1 CLI 已归档至 [`v0.1.0`](https://github.com/zimiao-dev/personal-finance/tree/v0.1.0)。

## 功能特性

- 创建收入或支出交易
- 查询全部交易或按分类、日期范围筛选
- 按 ID 查询、完整替换和删除交易
- 统计指定日期范围内的总收入、总支出、交易数量和余额
- 对金额、类型、分类、日期和日期范围执行领域校验
- 不存在的交易返回 HTTP 404
- 非法领域数据返回 HTTP 422
- 使用 Alembic 管理数据库结构
- 自动生成 OpenAPI 和 Swagger API 文档

## 技术栈

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- SQLite
- pytest、pytest-cov
- uv

## 快速开始

### 安装依赖

```powershell
git clone https://github.com/zimiao-dev/personal-finance.git
cd personal-finance
uv sync --frozen
```

### 初始化数据库

```powershell
uv run --frozen alembic upgrade head
```

默认数据库文件为：`data/finance_v2.db`

### 启动 API

```powershell
uv run --frozen uvicorn personal_finance.api.app:create_app --factory --reload
```

### 启动后访问：

- Swagger UI：http://127.0.0.1:8000/docs
- OpenAPI：http://127.0.0.1:8000/openapi.json
- 健康检查：http://127.0.0.1:8000/health

## API 接口

| 方法 | 路径 | 功能 | 成功状态码 |
|---|---|---|---:|
| GET | `/health` | 健康检查 | 200 |
| POST | `/transactions` | 创建交易 | 201 |
| GET | `/transactions` | 查询交易列表 | 200 |
| GET | `/transactions/{transaction_id}` | 查询单条交易 | 200 |
| PUT | `/transactions/{transaction_id}` | 完整替换交易 | 200 |
| DELETE | `/transactions/{transaction_id}` | 删除交易 | 204 |
| GET | `/statistics` | 查询收支统计 | 200 |

`GET /transactions` 支持可选的 `category`、`start_date` 和 `end_date` 查询参数；`GET /statistics` 支持可选的开始日期和结束日期。

## 架构设计

```text
HTTP 请求
  └─> FastAPI Router
       └─> Pydantic Schema
            └─> Application DTO
                 └─> Service
                      └─> Unit of Work
                           └─> SQLAlchemy Repository
                                └─> SQLite
```

| 层 | 职责 |
|---|---|
| `domain/` | 实体、枚举、业务规则和领域异常 |
| `application/` | DTO、Service、Repository/UoW 抽象接口和应用异常 |
| `infrastructure/` | SQLAlchemy 模型、映射器、Repository、Engine 和 Unit of Work |
| `api/` | FastAPI 应用、路由、Schema、依赖注入和异常映射 |
| `migrations/` | Alembic 数据库版本迁移 |
| `tests/` | Domain、Application、Infrastructure 和 API 测试 |

## 数据库设计

- `id`：整数主键
- `amount`：`Numeric(15, 4)`，通过 `Decimal` 保持金额精度
- `type`：`income` 或 `expense`
- `category`：交易分类
- `transaction_date`：数据库日期类型
- `description`：可选说明
- `created_at`：数据库自动生成的创建时间

数据库约束保证金额大于零，并限制交易类型。数据库结构由 Alembic 迁移管理，不再通过应用启动脚本直接建表。

## 测试

运行完整测试：

```powershell
uv run --frozen python -m pytest
```

当前 V0.2 测试基线：

- 207 项测试全部通过
- 总覆盖率 98%
- 覆盖 Domain、Application、Infrastructure、Alembic 和 API

## 当前限制

- 仅支持单用户
- 使用本地 SQLite，不提供云同步
- 暂无身份认证和权限管理
- 暂无分页、预算管理、数据导入导出和可视化
- 当前定位为学习和作品集项目，不声明为生产就绪系统

## 后续规划

- 增加 Docker 和 Linux 部署配置
- 增加分页和更丰富的统计维度
- 增加数据可视化
- 根据实际需求评估 PostgreSQL、认证和多用户支持

## License

本项目使用 [MIT License](LICENSE)。
