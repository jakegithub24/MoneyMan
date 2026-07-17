# MoneyMan – Exhaustive Screens & UI Documentation

This document provides a comprehensive, page-by-page mapping of all screens in the MoneyMan web application. It outlines the visual layouts, interactive components, Javascript behaviors, database operations, and backend routing defined in [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py).

---

## 1. Application Navigation & Layout Shell
The visual container for the application is defined in the base layout template, [base.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/base.html).
- **Simulated Viewport**: Restricts the UI to a simulated mobile viewport on desktop (`max-w-md mx-auto sm:h-[850px] sm:max-h-[100dvh] sm:rounded-[32px] sm:border`).
- **Responsive Layouts**:
  - **Desktop Navigation**: A persistent left-hand sidebar containing navigation items: *Dashboard*, *Transactions*, *Budgets*, *EMI Tracker*, *Savings Goals*, *AI Insights*, *Learn & Glossary*, and *Settings*.
  - **Mobile Navigation**: A sticky bottom tab bar containing shortcuts: *Home*, *Trans*, *Budgets*, *EMIs*, *Goals*, and *AI*.
- **Global Preferences**: Includes scripts to control light/dark theme modes (`toggleTheme()`) and accessible text sizing (`toggleAccessibility()`).

---

## 2. Page-by-Page Specifications

### Page 1: Welcome & Onboarding Wizard
- **Template File**: [onboarding.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/onboarding.html)
- **URL Route**: `/onboarding` (GET, POST)
- **Controller Action**: `onboarding()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L138)
- **Purpose**: Collects initial user profiling details and sets up the security environment.

#### Multi-Screen Step Flow:
1. **Screen 1: Welcome & Privacy Consent**
   - *Visuals*: Features the wallet logo, application title, and descriptions.
   - *Interactions*: A checkbox `#privacyToggle` must be checked to enable the "Get Started" button (`#btnNext1`). Clicking `#btnNext1` triggers a slide transition to Screen 2.
2. **Screen 2: Persona Selection**
   - *Visuals*: Custom cards for three selectable user personas:
     - **Student**: Configured to track allowances and study costs.
     - **Gig Worker**: Configured for variable income and vehicle expenses.
     - **Retired / Elderly**: Tailored to focus on predictable medical and grocery spend.
   - *Interactions*: Clicking a card checks a hidden `<input radio name="persona">`, applies selected active styles (highlighted green background and checkmark), and enables the "Continue" button (`#btnNext2`).
3. **Screen 3: Account Configuration**
   - *Visuals*: Text fields for name (`#fullName`), username (`#usernameInput`), and a profile avatar picture file selector (`#profilePic`). Contains a toggle switch (`#cloudSyncToggle`) for online cloud synchronization.
   - *Interactions*: Activating `#cloudSyncToggle` reveals the hidden password input block `#cloudPasswordSection`. Form validation checks that name and username fields are populated before letting the user proceed.
4. **Screen 4: Security PIN Selection**
   - *Visuals*: Visual digit dots representing security PIN input.
   - *Interactions*: Captures a 4-digit PIN (`#pinInput`) and requires confirmation (`#pinConfirmInput`). Valid inputs unlock the "Start using MoneyMan" button (`#btnFinish`).
   - *Database Operations*: A `POST` submission deletes all previous user data and inserts a new record into the `users` table with the name, username, selected persona, Argon2-hashed PIN, optional sync settings, and profile picture local paths. It sets `session['logged_in'] = True` and redirects to `/dashboard`.

---

### Page 2: Lock / Unlock Screen
- **Template File**: [login.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/login.html)
- **URL Route**: `/login` (GET, POST)
- **Controller Action**: `login()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L191)
- **Purpose**: Security gateway that blocks authenticated access until a valid PIN is entered.

#### Key Interactive Elements:
- **Visual Digit Indicators**: Four circles (`#dot1` to `#dot4`) that fill up as digits are entered.
- **On-Screen Numeric Keypad**: Keypad digits `1-9` and `0` append to a local Javascript string buffer. A backspace button handles character deletion.
- **Physical Key Bindings**: Listens to numeric physical keyboard keys.
- **Auto-Submit**: Once the PIN reaches 4 characters, it updates a hidden field `#pinInput` and automatically submits `#pinForm` via a `POST` request.
- **Error Shake**: If verification fails, the backend returns an error message, and the dots shake visually (`.animate-shake`).
- **Database Operations**: Queries the `users` table to match and verify the hashed PIN using `verify_pin()` in [db.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/db.py). Successful entry sets `session['logged_in'] = True`.

---

### Page 3: Dashboard (Home)
- **Template File**: [dashboard.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/dashboard.html)
- **URL Route**: `/dashboard` (GET)
- **Controller Action**: `dashboard()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L307)
- **Purpose**: Central command center providing financial overviews, actionable AI tips, and quick access to actions.

#### Key Sections:
- **Profile Header**: Displays username and persona role. Features a clickable avatar button triggering the dropdown menu (`#profileDropdownMenu`) for Settings, Accessibility scaling, Theme toggling, and Lock controls.
- **Summary Cards**: Displays metrics compiled via database aggregates:
  - *Total Income*: Sum of all income transactions.
  - *Total Expenses*: Sum of all expense transactions.
  - *Savings Progress*: Sum of saved amounts across savings goals.
  - *Upcoming EMIs*: Sum of monthly payments in active loans.
- **Weekly Spending Chart**: Interactive vertical bar chart representing weekly expenses for the current month. Hovering over a week bar highlights it.
- **Upcoming Bills**: A list of outstanding bills populated from active EMI records, with fallbacks to mock bills (e.g. electricity, broadband) if none exist.
- **Action Shortcuts**: Quick buttons for "Add Transaction" (redirects to `/add-transaction`) and links to other modules.
- **AI Insights Card**: Displays a dynamic, context-aware alert (e.g., alerting when food spending exceeds threshold or when net expenses surpass income).

---

### Page 4: Add Transaction
- **Template File**: [add_transaction.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/add_transaction.html)
- **URL Route**: `/add-transaction` (GET) and `/transaction/add` (POST)
- **Controller Action**: `add_transaction()` and `transaction_add()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L415)
- **Purpose**: Provides forms to record new income and expenses.

#### Key Interactive Elements:
- **Type Toggle**: Selectable buttons for *Expense* (sets visual theme colors to red) and *Income* (sets colors to green). Updates a hidden input field `#transactionType`.
- **Amount Input**: Numerical field (`#amountInput`) with placeholder formatting.
- **Category Chips**: Selecting a chip (e.g., Food, Transport, Rent, Entertainment, Study, Shopping) highlights it and copies the choice to `#selectedCategory`.
- **Note Input with Auto-Categorization**: Users enter text notes. As they type, client-side scripts parse keyword matches (e.g., typing "bus" auto-selects the *Transport* chip; "lunch" selects the *Food* chip).
- **Voice Recognition (Web Speech API)**: Clicking `#voiceBtn` starts speech transcription. The microphone icon pulses red. Captured transcripts are written into the note input, and auto-categorization is triggered.
- **Date Picker & Recurring Toggle**: Users specify dates (defaults to today) and optionally flag transactions as recurring.
- **Database Operations**: Form submissions write a new row to the `transactions` table.

---

### Page 5: Edit Transaction
- **Template File**: [edit_transaction.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/edit_transaction.html)
- **URL Route**: `/transaction/edit/<int:tx_id>` (GET, POST)
- **Controller Action**: `transaction_edit()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L508)
- **Purpose**: Updates details of an existing transaction.

#### Key Interactive Elements:
- Functional behavior is identical to the **Add Transaction** screen.
- Form inputs are pre-populated with database values belonging to the specified transaction ID.
- Replaces the "Save Transaction" submit button with "Save Changes".
- **Database Operations**: `POST` queries update matching values in the `transactions` table based on the primary key `tx_id`.

---

### Page 6: Transactions List
- **Template File**: [transactions.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/transactions.html)
- **URL Route**: `/transactions` (GET)
- **Controller Action**: `transactions()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L445)
- **Purpose**: History ledger for all logged entries with filtering tools.

#### Key Interactive Elements:
- **Ledger Filters**: Quick filters for transaction type ("All Types", "Income only", "Expense only") and a category selector. Selecting values triggers full page reloads with query parameters (e.g. `/transactions?type=expense&category=food`).
- **Transaction Rows**: Displays details (date, category icon, note, amount). Double-clicking a row redirects users to `/transaction/edit/<id>`.
- **Edit/Delete Actions**: Hovering on desktop reveals Edit (pencil icon) and Delete (trash can icon) links. Delete triggers a native prompt dialog.
- **Swipe Left Delete (Mobile)**: Users can swipe left on touch devices. Exceeding `80px` translation slides the row open, turning the background red and displaying a confirmation to delete.
- **Database Operations**: Performs conditional `SELECT` queries with filters. Deletion maps to a `POST` request to `/transaction/delete/<id>`, removing the row from `transactions`.

---

### Page 7: Budgets Settings & Overviews
- **Template File**: [budgets.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/budgets.html)
- **URL Route**: `/budgets` (GET) and `/budgets/create` (POST)
- **Controller Action**: `budgets()` and `budgets_create()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L710)
- **Purpose**: Set and check spending caps against real-time expenditures.

#### Key Interactive Elements:
- **"Create Budget" Button**: Opens a modal dialog (`#budgetModal`) to set category limits.
- **Create Budget Modal Form**: Inputs category, max spending limit, and a threshold checkmark for 80% spending notifications.
- **Interactive Budget Cards**:
  - Displays progress bars indicating what percentage of the budget is spent.
  - Progress bar colors are dynamic: green (<80%), yellow (80-99%), and red (>=100% or overspent), accompanied by status labels ("good", "warning", "danger").
- **Database Operations**: Queries `budgets` alongside aggregates of `transactions` filtered by the active month and category. Creating a budget performs an `INSERT OR REPLACE INTO budgets` operation.

---

### Page 8: EMI Tracker & Calculator
- **Template File**: [emi.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/emi.html)
- **URL Route**: `/emi` (GET) and `/emi/create` (POST)
- **Controller Action**: `emi()` and `emi_create()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L770)
- **Purpose**: Calculators and trackers for loans, debts, and equated monthly payments.

#### Key Interactive Elements:
- **EMI Calculator Inputs**: Fields for Loan Amount (`#loanAmount`), Interest Rate (`#interestRate`), and Tenure (`#tenure`). An event listener calculates monthly payments instantly and displays them.
- **"Save to Tracker" Action**: Opens a secondary modal pre-filled with calculator metrics, prompting for the Loan Name and Bank/Lender.
- **Prepayment Impact Slider**: A range slider (`#prepaymentSlider`) lets users slide to add extra monthly payments. The UI instantly updates parameters showing:
  - *Monthly Payment Display*: New calculated payment.
  - *Time Saved*: Number of months shaved off.
  - *Interest Saved*: Total money saved in interest over the lifetime of the loan.
- **Active EMI Cards**: Displays list cards showing loan details (total amount, bank, tenure progress bar).
- **Database Operations**: Submitting a loan inserts records into the `emis` table. The calculator maps icons (home, phone, car, calculate) based on loan name keywords.

---

### Page 9: Savings Goals
- **Template File**: [goals.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/goals.html)
- **URL Route**: `/goals` (GET), `/goals/create` (POST), and `/goals/update` (POST)
- **Controller Action**: `goals()`, `goals_create()`, and `goals_update()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L832)
- **Purpose**: Track targets for future savings objectives.

#### Key Interactive Elements:
- **"New Goal" Button**: Opens the creation modal (`#goalModal`).
- **Create Goal Modal Form**: Inputs Name, Target Amount, Category Tag dropdown (Safety Net, Tech, Travel, Education, Other), and Target Date. Selecting a category maps custom card layouts (icons and colors).
- **"Update Amount" Card Action**: Triggers the update modal (`#updateModal`).
- **Update Savings Modal Form**: Displays active progress, prompting the user for an updated saved amount (`#savedAmount`).
- **Savings Cards**: Displays progress cards showing target date, status tags ("On Track" or "Needs Attention"), percentage progress bar, and saved vs. target values.
- **Database Operations**: Fetches records from the `goals` table. Creating a goal inserts a new row. Updating a goal executes an `UPDATE goals SET saved_amount=? WHERE id=?` command.

---

### Page 10: AI Insights
- **Template File**: [ai_analysis.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/ai_analysis.html)
- **URL Route**: `/ai-analysis` (GET)
- **Controller Action**: `ai_analysis()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L558)
- **Purpose**: Deep financial analysis using AI-generated reports.

#### Key Visual Components:
- **Monthly Savings Rate Gauge**: Radial gauge chart illustrating the user's savings rate.
- **Financial Summary Metrics**: Visual cards for total income, total expense, and net savings.
- **AI Summary Paragraph**: Detailed explanation of monthly spending habits.
- **AI Observations**: Bulleted card deck showing key takeaways.
- **AI Action Recommendations**: Actionable cards suggesting savings behaviors.
- **AI API Integration**: If `GEMINI_API_KEY` is present in the environment variables, the system queries the `gemini-2.5-flash` model with compiled transaction JSON structures. If offline, the controller falls back to generating local insights based on user persona and database state.

---

### Page 11: Learn & Glossary Hub
- **Template File**: [learn.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/learn.html)
- **URL Route**: `/learn` (GET)
- **Controller Action**: `learn()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L927)
- **Purpose**: Glossary search and financial advice resource directory.

#### Key Interactive Elements:
- **Ask MoneyMan AI**: Chat text input field with a send button (displays production alert).
- **Financial Wisdom Cards**: Accordion-like cards explaining rules (50/30/20 Rule, Emergency Funds, Debt Snowball). Clicking triggers a script to toggle `line-clamp-3` styling classes, expanding details.
- **Glossary Search Bar**: Input field `#glossarySearch` filters glossary cards by matching user strings with the `data-term` attribute. Non-matching glossary cards are dynamically hidden.
- **Glossary Details Accordion**: Alphabetical glossary terms (e.g. Budgeting, EMI, Inflation, Interest Rate, Net Worth, Savings Rate, Yield) using `<details>` and `<summary>` wrappers. Arrow indicators rotate dynamically when items are toggled.

---

### Page 12: App Settings
- **Template File**: [settings.html](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/templates/settings.html)
- **URL Route**: `/settings` (GET) and routes for form actions (POST)
- **Controller Action**: `settings()`, `settings_change_pin()`, and `settings_update_sync()` inside [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L233)
- **Purpose**: Session actions, display settings, and local database security configurations.

#### Key Forms & Actions:
- **Security PIN Section**: Inputs current PIN, new PIN, and confirm PIN. Form updates the security PIN in the database.
- **Data Sync & Privacy Section**: Toggles online backup sync state.
- **Display Preferences**: Action cards to trigger `toggleTheme()` (light/dark theme toggle) and `toggleAccessibility()` (accessible text size multiplier).
- **Lock Application Action**: Links to `/lock`, clears session credentials, and redirects to `/login`.
- **Logout & Reset Profile Action**: Links to `/logout`. Triggers a confirmation dialogue warning that doing so clears all device logs. Confirming executes database drop tables, wipes the database clean, clears cookies, and redirects the user to `/onboarding`.
- **Database Operations**: Read/writes to user profile parameters in the `users` table.

---

## 3. UI/UX Reachability Boundary Rules

1. **Authentication Boundary Guards**:
   - An interceptor (`check_auth()` in [app.py](file:///home/champ/Storage/Github/Repositories/MoneyMan/WebApp/app.py#L18)) checks authorization before any route resolution.
   - Unonboarded users are immediately redirected to `/onboarding`.
   - Onboarded but unauthenticated users (session cookie missing `logged_in = True`) are immediately redirected to `/login`.
   - Authenticated users attempting to reach `/onboarding` or `/login` directly are automatically redirected back to `/dashboard`.
2. **Mobile Nav Reachability Gaps**:
   - The `/learn` path is accessible in the sidebar layout for desktop screens, but is absent from the mobile bottom navigation bar and the profile menu. Mobile users can only access the Learn page through a contextual link on the dashboard's daily tip card.
