# Boglefolio

A self-hosted investment portfolio tracker inspired by the Bogleheads philosophy of long-term, low-cost investing. Built with FastAPI and SQLModel for a robust backend, supporting CSV imports, Yahoo Finance integration, and future Plaid API connectivity.

## Current Features

- **Portfolio Management:** Track assets, accounts, transactions, and users with full CRUD operations.
- **CSV Import:** Easily import transactions from CSV files with duplicate detection and error handling.
- **Yahoo Finance Integration:** Fetch real-time and historical price data for assets.
- **Daily Snapshots:** (Planned) Calculate and store end-of-day portfolio values for performance tracking.
- **Plaid API Support:** (Planned) Import transactions from brokerage accounts.
- **Authentication:** (Planned) Secure user access with JWT.
- **Performance Analytics:** (Planned) View portfolio performance over time with charts and reports.

## Usage
**API Endpoints:**
- Assets: /assets - Manage investment assets (CRUD).
- Accounts: /accounts - Manage user accounts (CRUD).
- Transactions: /transactions - Manage transactions (CRUD, CSV import).
- Users: /users - Manage users (CRUD).

**Example: Import Transactions from CSV**
Prepare a CSV with columns: asset_id, account_id, type, quantity, price, fee, date.
Use the /transactions/import-csv endpoint to upload and process the file asynchronously.

## Future Features / Roadmap

- Daily portfolio snapshots.
- Plaid API integration.
- User authentication.
- Frontend dashboard.
- Performance charts.
