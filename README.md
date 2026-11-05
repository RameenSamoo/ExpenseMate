# 💰 ExpenseMate — Personal Expense Manager

> **Software Construction & Development — Evolution: Migration, Layered Refactoring & Rewriting**

ExpenseMate is a full-featured web-based personal finance manager designed to track income and expenditures, manage monthly budgets with smart alerts, monitor long-term savings goals, and visualize cash-flow trends through interactive charts.

---

## 🌐 Localhost Web Address

Once the server is running, access ExpenseMate in your web browser at:

* **Primary Address**: [**http://localhost:5000**](http://localhost:5000)
* **Alternative IP**: [**http://127.0.0.1:5000**](http://127.0.0.1:5000)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* Python 3.10+ (tested on Python 3.11)
* Git

### 2. Setup Virtual Environment
```bash
# Clone the repository (if not already local)
git clone https://github.com/RameenSamoo/ExpenseMate.git
cd ExpenseMate

# Checkout the Assignment 02 evolution branch
git checkout assignment-02

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations & Initialization
ExpenseMate includes a repeatable, version-controlled database migration framework:
```bash
# Apply pending migrations
python manage_migrations.py up

# Check migration status
python manage_migrations.py status
```

### 5. Launch Application
```bash
python app.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser!

---

## 🧪 Running Automated Tests

ExpenseMate has an automated test suite comprising **25 test cases** (unit tests, repository tests, migration tests, and end-to-end integration workflows):

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test suites
pytest tests/test_integration_workflows.py
pytest tests/test_migration.py
pytest tests/test_repositories.py
pytest tests/test_rewritten_classes.py
```

To run the maintainability and cyclomatic complexity analyzer:
```bash
python tools/metrics_calculator.py
```

---

## 🏗️ Software Evolution & Architecture (Assignment 02)

ExpenseMate has undergone three mandatory software evolution stages:

### 1. Part A — Database Schema & Data Migration
* **Framework**: Implemented a versioned, atomic migration runner with rollback capabilities ([`migrations/migrator.py`](migrations/migrator.py) and [`manage_migrations.py`](manage_migrations.py)).
* **Schema Evolution**: Added `payment_method` (`Cash`, `Credit Card`, `Debit Card`, `Bank Transfer`, `Mobile Wallet`) and `notes` to `transactions`, and `rollover_amount` to `budgets`.
* **Data Migration**: Automatically backfilled legacy records without data loss.
* 📄 Full details: [`docs/migration_report.md`](docs/migration_report.md)

### 2. Part B — Layered Architecture Refactoring
* Refactored into a strict 4-tier architecture with unidirectional dependency flow:
  $$\text{Controller} \longrightarrow \text{Services} \longrightarrow \text{Repository} \longrightarrow \text{Database}$$
* **Repositories Created**: [`TransactionRepository`](repositories/transaction_repository.py), [`BudgetRepository`](repositories/budget_repository.py), [`CategoryRepository`](repositories/category_repository.py).
* **Refactored Features**: *Add Expense* and *Monthly Budget Summary* enforce zero SQL in controllers and services, and zero business math in repositories.
* 📄 Full details: [`docs/refactoring_report.md`](docs/refactoring_report.md)

### 3. Part C — Rewriting Selected Classes
* **Rewritten Class 1**: Procedural calculations in `utils/calculations.py` were rewritten into object-oriented domain engines in [`engines/financial_calculator.py`](engines/financial_calculator.py) (`FinancialCalculator`, `BudgetAnalyzer`, `GoalTracker`).
* **Rewritten Class 2**: Monolithic 350-line `services/analytics_service.py` was rewritten into [`AnalyticsEngine`](services/analytics_service.py), removing all SQL and reducing max cyclomatic complexity from 14 down to 5 (-64%).
* 📄 Full details: [`docs/rewriting_report.md`](docs/rewriting_report.md)

---

## 📁 Project Directory Structure

```text
ExpenseMate/
├── app.py                         # Application factory & server entry point
├── config.py                      # Application configuration
├── manage_migrations.py           # CLI tool for database migrations
├── requirements.txt               # Python package dependencies
├── database/
│   ├── database.py                # Database connection context manager
│   ├── schema.sql                 # Baseline database DDL schema
│   └── seed.py                    # Initial seed data utility
├── docs/
│   ├── migration_report.md        # Part A: Migration report
│   ├── refactoring_report.md      # Part B: Layered architecture report
│   ├── rewriting_report.md        # Part C: Class rewrite report
│   └── maintainability_report.md  # Maintainability metrics & change log
├── engines/
│   ├── __init__.py
│   └── financial_calculator.py    # Rewritten domain engines (BudgetAnalyzer, GoalTracker)
├── frontend/
│   ├── static/                    # CSS stylesheets, JavaScript, icons
│   └── templates/                 # Jinja2 HTML dashboard templates
├── migrations/
│   ├── 001_add_payment_method_and_notes.py  # Version 001 schema & data migration
│   └── migrator.py                # Migration runner engine
├── repositories/                  # Part B: Repository Data Access Layer
│   ├── base_repository.py         # Base query execution helper
│   ├── budget_repository.py       # SQL persistence for budgets
│   ├── category_repository.py     # SQL persistence for categories
│   └── transaction_repository.py  # SQL persistence for transactions
├── routes/                        # Presentation / Controller Layer (Blueprints)
│   ├── analytics_routes.py
│   ├── auth_routes.py
│   ├── budget_routes.py
│   ├── dashboard_routes.py
│   ├── expense_routes.py
│   ├── goal_routes.py
│   └── income_routes.py
├── services/                      # Application / Business Logic Layer
│   ├── analytics_service.py       # AnalyticsEngine service
│   ├── auth_service.py            # Authentication & session service
│   ├── budget_service.py          # Budget rules & monthly summaries
│   ├── goal_service.py            # Goal progress & contributions
│   └── transaction_service.py     # Transaction validation & coordination
├── tests/                         # Pytest Suite (25 Tests)
│   ├── conftest.py                # Test fixtures & temporary database setup
│   ├── test_integration_workflows.py # 5 end-to-end integration workflows
│   ├── test_migration.py          # Part A migration verification tests
│   ├── test_repositories.py       # Part B repository unit tests
│   └── test_rewritten_classes.py  # Part C rewritten engines tests
├── tools/
│   └── metrics_calculator.py      # AST Cyclomatic Complexity & LOC analyzer
└── utils/
    ├── calculations.py            # Facade delegating to domain engines
    ├── decorators.py              # Auth & session route decorators
    └── validators.py              # Input validation helpers
```

---

## 👥 Team & Version Control

* **Team Lead / Member 1**: Migration & Layered Repositories (Part A & B)
* **Team Member 2**: Class Rewriting, Integration Testing & Maintainability (Part C)
* **Git Repository**: [https://github.com/RameenSamoo/ExpenseMate](https://github.com/RameenSamoo/ExpenseMate)
* **Baseline Branch**: `baseline-a01` / Tag: `v1.0-assignment1`
* **Evolution Branch**: `assignment-02`
