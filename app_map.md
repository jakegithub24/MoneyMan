# MoneyMan – Application Sitemap (app_map)

This document provides a sitemap and structural hierarchy of the MoneyMan web application. It outlines route access rules, navigation structures, and modal triggers.

---

## 1. Application Architecture Flow

The flowchart below represents the entry gates, auth boundaries, and screen linkages:

```mermaid
graph TD
    %% Gateway Verification
    Entry[User Opens App] --> Guard{Onboarded?}
    Guard -- No --> Onboard[/onboarding]
    Guard -- Yes --> AuthGuard{Session Active?}
    AuthGuard -- No --> Login[/login]
    AuthGuard -- Yes --> MainShell[base.html Navigation Shell]

    %% Main Navigation Shell Connections
    Onboard -->|Submit PIN / Setup| Login
    Login -->|Input Correct PIN| MainShell

    subgraph Navigation Shell Views
        MainShell --> Dash[/dashboard]
        MainShell --> TxList[/transactions]
        MainShell --> Budgets[/budgets]
        MainShell --> EMIs[/emi]
        MainShell --> Goals[/goals]
        MainShell --> AI[/ai-analysis]
        MainShell --> Learn[/learn]
        MainShell --> Settings[/settings]
    end

    %% Contextual Links & Action Flows
    Dash -->|Add Button| AddTx[/add-transaction]
    Dash -->|View Bills Link| EMIs
    Dash -->|Glossary Link| Learn

    TxList -->|Add Button| AddTx
    TxList -->|Edit Icon / Double Click| EditTx[/transaction/edit/id]
    AddTx -->|Save Form| Dash
    EditTx -->|Save Form| TxList

    %% Modals
    Budgets -->|Trigger Modal| BudgetsModal[Create Budget Modal]
    EMIs -->|Trigger Modal| LoanModal[Save Loan Modal]
    Goals -->|Trigger Modal 1| NewGoalModal[Create Goal Modal]
    Goals -->|Trigger Modal 2| UpdateSavedModal[Update Saved Modal]

    %% Session Actions
    Settings -->|Lock| LockRoute[GET /lock] --> Login
    Settings -->|Logout & Reset| LogoutRoute[GET /logout] --> Onboard
```

---

## 2. Directory of Routes & Screen Actions

### Group A: Authentication & Onboarding Gateways
These routes check global states before letting the browser access the application shell.
*   **`/onboarding`** (GET, POST)
    *   *Purpose*: First-use onboarding wizard.
    *   *Transitions*: Submitting the form resets data tables and routes the client to the dashboard.
*   **`/login`** (GET, POST)
    *   *Purpose*: Daily access lock screen.
    *   *Transitions*: Checks PIN and routes to `/dashboard`.
*   **`/lock`** (GET)
    *   *Purpose*: Terminate active cookie session.
    *   *Transitions*: Immediately redirects client to `/login`.
*   **`/logout`** (GET)
    *   *Purpose*: Destroys all database records and profiles.
    *   *Transitions*: Redirects client to `/onboarding`.

---

### Group B: Core Dashboard & Transactions
Primary workspace routes where the user tracks and manages financial entries.
*   **`/dashboard`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Dashboard"), Mobile Bottom Nav ("Home").
    *   *Links & Actions*:
        *   "Add Transaction" button $\rightarrow$ `/add-transaction`
        *   "View All" bills $\rightarrow$ `/emi`
        *   "Learn more in glossary" $\rightarrow$ `/learn`
        *   Profile Avatar Dropdown $\rightarrow$ `/settings`
*   **`/transactions`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Transactions"), Mobile Bottom Nav ("Trans").
    *   *Links & Actions*:
        *   Filter links (type, category tags) $\rightarrow$ updates URL params.
        *   "Add Transaction" button $\rightarrow$ `/add-transaction`
        *   Double-click row / Edit icon $\rightarrow$ `/transaction/edit/<tx_id>`
        *   Delete trash icon $\rightarrow$ `POST /transaction/delete/<tx_id>`
*   **`/add-transaction`** (GET)
    *   *Accessibility*: Shortcuts on dashboard and transactions list.
    *   *Actions*:
        *   Voice speech input $\rightarrow$ transcribes microphone audio.
        *   Back arrow $\rightarrow$ `/dashboard`
        *   Form submission $\rightarrow$ `POST /transaction/add`
*   **`/transaction/edit/<int:tx_id>`** (GET, POST)
    *   *Accessibility*: Contextual links on individual transaction records.
    *   *Actions*:
        *   Back arrow $\rightarrow$ `/transactions`
        *   Form submission $\rightarrow$ updates entry.

---

### Group C: Planners & Budget Calculators
Features designed to model categories, EMI repayment outcomes, and long-term milestones.
*   **`/budgets`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Budgets"), Mobile Bottom Nav ("Budgets").
    *   *Actions & Modals*:
        *   "Create Budget" button $\rightarrow$ Opens **Create Budget Modal** (`POST /budgets/create`).
*   **`/emi`** (GET)
    *   *Accessibility*: Desktop Sidebar ("EMI Tracker"), Mobile Bottom Nav ("EMIs").
    *   *Actions & Modals*:
        *   Prepayment Slider $\rightarrow$ Client-side interest calculations.
        *   "Save to Tracker" button $\rightarrow$ Opens **Save Loan Modal** (`POST /emi/create`).
*   **`/goals`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Savings Goals"), Mobile Bottom Nav ("Goals").
    *   *Actions & Modals*:
        *   "New Goal" button $\rightarrow$ Opens **Create Savings Goal Modal** (`POST /goals/create`).
        *   "Update Amount" card button $\rightarrow$ Opens **Update Savings Modal** (`POST /goals/update`).

---

### Group D: Analysis, Education & Utilities
Background intelligence utilities, settings panels, and glossary directories.
*   **`/ai-analysis`** (GET)
    *   *Accessibility*: Desktop Sidebar ("AI Insights"), Mobile Bottom Nav ("AI").
*   **`/learn`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Learn & Glossary"), Dashboard Daily Tip Link (*Note: unreachable on Mobile Bottom Navigation bar*).
*   **`/settings`** (GET)
    *   *Accessibility*: Desktop Sidebar ("Settings"), Profile Avatar Dropdown Menu.
    *   *Actions*:
        *   Update PIN form $\rightarrow$ `POST /settings/change-pin`
        *   Data sync toggle $\rightarrow$ `POST /settings/update-sync`
        *   Accessibility & Theme toggles $\rightarrow$ Client-side visual updates.
        *   "Lock Application" link $\rightarrow$ `/lock`
        *   "Logout & Reset Profile" link $\rightarrow$ `/logout`
