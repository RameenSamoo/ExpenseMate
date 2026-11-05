# Part C — Rewriting Report: Selected Classes Evolution

| Item | Details |
| :--- | :--- |
| **System** | ExpenseMate — Personal Expense Manager |
| **Selected Class 1** | `utils/calculations.py` $\rightarrow$ Rewritten into `engines/financial_calculator.py` (`FinancialCalculator`, `BudgetAnalyzer`, `GoalTracker`) |
| **Selected Class 2** | `services/analytics_service.py` $\rightarrow$ Rewritten into `AnalyticsEngine` |
| **Public Interface** | 100% backward compatible via facade proxies |

---

## 1. Class 1: `utils/calculations.py` $\rightarrow$ `FinancialCalculator`, `BudgetAnalyzer`, `GoalTracker`

### Old Responsibilities & Design Problems
* **Lack of Encapsulation**: Financial calculations, budget threshold evaluations, and goal timeline tracking were all thrown into a single global procedural file.
* **Repetitive Defensive Casting**: `float(val or 0.0)` was copy-pasted over 15 times across functions to guard against `NoneType` and empty strings.
* **Scattered Magic Numbers**: Threshold numbers (`80.0%`, `100.0%`, `30 days`, `10.0%` progress buffer) were hardcoded directly in conditionals, making it impossible to adjust alert sensitivities per user or category.
* **Poor Extensibility**: Adding new status states or custom thresholds required modifying fragile nested `if/elif` statements.

### New Rewritten Design
The procedural module was replaced by three distinct object-oriented domain classes in [`engines/financial_calculator.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/expensemate/engines/financial_calculator.py):
1. **`FinancialCalculator`**:
   - High-precision monetary operations, centralized safe float parsing (`to_float`), division-by-zero protection, and percentage delta computations.
2. **`BudgetAnalyzer`**:
   - Encapsulates budget health evaluation with configurable threshold policies (`warning_threshold=80.0`, `exceeded_threshold=100.0`).
   - Generates unified analysis dictionaries (`budget`, `spent`, `remaining`, `percentage`, `status`).
3. **`GoalTracker`**:
   - Dedicated timeline analysis engine managing velocity, date normalization, required monthly contribution forecasting, and deadline proximity detection.

### Why a Full Rewrite Was More Appropriate Than a Small Refactor
A minor refactoring would only extract a few helper functions while leaving the fundamental architecture procedural and without domain models. A complete rewrite established true object-oriented domain engines with configurable instance state, clean separation of concern, and isolated unit testability.

### Verification of Preserved Behavior
All existing utility functions (`calculate_balance`, `calculate_budget_remaining`, `determine_budget_status`, etc.) were retained in [`utils/calculations.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/expensemate/utils/calculations.py) as delegation proxies routing to the new engines. Every existing test and new test passed without regression.

---

## 2. Class 2: `services/analytics_service.py` $\rightarrow$ `AnalyticsEngine`

### Old Responsibilities & Design Problems
* **Monolithic God Module (350 LOC)**: Mixed 5 distinct concerns:
  1. Direct raw SQL database queries using `execute_query`.
  2. Aggregations of income and expense totals.
  3. Formatting Chart.js presentation datasets (`labels`, `trend`, `datasets`).
  4. Financial indicator computations (savings, net savings rate).
  5. Multi-service alert coordination.
* **Extreme SQL Query Duplication**: Monthly expense sum queries with identical `CAST(strftime(...))` SQL snippets were repeated across 4 separate functions.
* **Zero Unit Testability**: Impossible to unit test calculation or chart formatting logic without maintaining an active SQLite database on disk.

### New Rewritten Design
Rewritten into the `AnalyticsEngine` class:
1. **Zero Raw SQL in Engine**: All data access is delegated to `TransactionRepository` and `BudgetRepository` via constructor dependency injection (`__init__(self, tx_repo=None, budget_repo=None)`).
2. **Normalized Aggregation Pipeline**: Pure data extraction methods in repository supply data feeds to domain calculation helpers.
3. **Structured Response Objects**: Produces standardized KPI metric cards and chart DTOs cleanly separated from persistence code.

### Why a Full Rewrite Was More Appropriate Than a Small Refactor
Attempting to incrementally patch `analytics_service.py` while keeping raw SQL embedded would fail the core Part B architectural requirements and leave cyclomatic complexity high (previously CC 14). A full rewrite cleanly extracted SQL into `TransactionRepository` and turned `AnalyticsEngine` into a pure, testable domain analytics coordinator.

### Verification of Preserved Behavior
* Unit tests in [`tests/test_rewritten_classes.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/expensemate/tests/test_rewritten_classes.py) verify that `AnalyticsEngine` computes dashboard summaries, income analytics, and month-over-month comparisons with 100% precision.
* All original frontend templates (`dashboard.html`, `analytics.html`) consume the exact same JSON keys without modification.
