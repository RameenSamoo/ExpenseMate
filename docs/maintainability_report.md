# ExpenseMate: Maintainability Metrics & Evolution Change Log

| Item | Details |
| :--- | :--- |
| **Project** | ExpenseMate — Personal Expense Manager |
| **Evolution Scope** | Assignment 02: Migration, Layered Refactoring, Class Rewriting |
| **Measurement Tool** | Python AST Cyclomatic Complexity Analyzer (`tools/metrics_calculator.py`) & Pytest Suite |

---

## 1. Before vs. After Maintainability Comparison

### Indicator 1: Cyclomatic Complexity (McCabe Complexity)
* **Measurement Method**: Calculated via AST AST tree walking counting decision branch nodes (`If`, `For`, `While`, `ExceptHandler`, `BoolOp`, `IfExp`) + 1.

| Target Module | Baseline Avg CC | Baseline Max CC | Assignment 02 Avg CC | Assignment 02 Max CC | Complexity Reduction |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `analytics_service.py` | 7.80 | 14.0 | **2.55** | **5.0** | **-67.3%** |
| `calculations.py` (Facade) | 3.20 | 8.0 | **1.00** | **1.0** | **-68.8%** |
| `budget_service.py` | 5.60 | 15.0 | **2.71** | **9.0** | **-51.6%** |
| `transaction_service.py` | 6.40 | 18.0 | **3.00** | **13.0** | **-53.1%** |

*Key Takeaway*: Decoupling SQL queries and separating concern drastically slashed cyclomatic branch complexity. Functions are shorter, linear, and significantly less error-prone.

---

### Indicator 2: Separation of Concerns & Responsibility Count
* **Measurement Method**: Count of explicit architectural layers and direct SQL access points.

| Metric | Assignment 01 Baseline | Assignment 02 Evolved | Improvement Description |
| :--- | :---: | :---: | :--- |
| **Architectural Layers** | 2 (Routes + Mixed Services) | **4 Strict Layers** (`Controller → Service → Repository → Database`) | Clean, unidirectional dependency structure. |
| **SQL Execution Spread** | 28 SQL points scattered in routes & services | **0 in routes/services** (100% centralized in `repositories/`) | Single source of truth for all database queries. |
| **Repository Classes** | 0 | **4 Repositories** (`Base`, `Transaction`, `Budget`, `Category`) | Independent data access units. |
| **Domain Engine Classes** | 0 | **3 Engines** (`FinancialCalculator`, `BudgetAnalyzer`, `GoalTracker`) | Encapsulated domain logic. |

---

### Indicator 3: Test Coverage & Regression Safety
* **Measurement Method**: Pytest automated test execution suite.

| Metric | Assignment 01 Baseline | Assignment 02 Evolved | Growth / Status |
| :--- | :---: | :---: | :--- |
| **Total Test Count** | 10 tests | **25 automated tests** | **+150% test expansion** |
| **Migration Tests** | 0 | **3 tests** (`test_migration.py`) | Tests schema evolution, data preservation, and rollback |
| **Repository Tests** | 0 | **3 tests** (`test_repositories.py`) | Tests isolated data access CRUD & aggregations |
| **Rewritten Class Tests** | 0 | **4 tests** (`test_rewritten_classes.py`) | Tests calculation engines & threshold boundary logic |
| **Integration Workflows**| 0 | **5 end-to-end tests** (`test_integration_workflows.py`) | Tests full user journeys through all 4 layers |
| **Regression Pass Rate** | 100% (10/10) | **100% (25/25)** | **Zero regression** on all existing features |

---

## 2. Comprehensive Evolution Change Log

| Version / Commit | Milestone | Affected Files & Classes | Engineering Reason |
| :--- | :--- | :--- | :--- |
| **`1cbf5c5`** | Baseline Setup | All Assignment 01 files | Initialized Assignment 01 baseline branch (`baseline-a01`) and tag `v1.0-assignment1`. |
| **`91e5a75`** | **Part A: Migration** | `migrations/001_add_payment_method_and_notes.py`<br/>`migrations/migrator.py`<br/>`manage_migrations.py`<br/>`database/schema.sql`<br/>`database/database.py`<br/>`tests/test_migration.py`<br/>`docs/migration_report.md` | Implemented versioned migration framework with rollback; evolved database schema to support `payment_method`, `notes`, and `rollover_amount`; verified zero data loss on legacy records. |
| **`6143d27`** | **Part B: Refactoring** | `repositories/base_repository.py`<br/>`repositories/transaction_repository.py`<br/>`repositories/budget_repository.py`<br/>`repositories/category_repository.py`<br/>`services/transaction_service.py`<br/>`services/budget_service.py`<br/>`tests/test_repositories.py`<br/>`docs/refactoring_report.md` | Extracted Repository layer. Refactored "Add Expense" and "Monthly Budget Summary" into strict `Controller → Services → Repository → Database` dependency order. |
| **`[Upcoming]`** | **Part C: Rewriting & Tests** | `engines/financial_calculator.py`<br/>`utils/calculations.py`<br/>`services/analytics_service.py`<br/>`tests/test_rewritten_classes.py`<br/>`tests/test_integration_workflows.py`<br/>`tools/metrics_calculator.py`<br/>`docs/rewriting_report.md`<br/>`docs/maintainability_report.md` | Rewrote procedural calculations into `FinancialCalculator`, `BudgetAnalyzer`, `GoalTracker`, and `AnalyticsEngine`; added 5 end-to-end integration workflows and maintainability reports. |

---

## 3. Team Contribution Summary

| Member | Primary Responsibility | Key Deliverables & Explanations |
| :--- | :--- | :--- |
| **Team Member 1** | Migration & Layered Repositories (Part A & B) | Designed migration script `001_add_payment_method_and_notes.py`, built the `migrations/migrator.py` runner, implemented `TransactionRepository` and `BudgetRepository`, and refactored the Add Expense and Monthly Budget Summary flows. |
| **Team Member 2** | Class Rewriting, Testing & Metrics (Part C) | Designed and implemented the object-oriented `FinancialCalculator`, `BudgetAnalyzer`, and `AnalyticsEngine`, authored the 5 integration workflow tests, and conducted the before/after AST cyclomatic complexity measurements. |
