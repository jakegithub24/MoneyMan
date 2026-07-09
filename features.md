# MoneyMan – Features & Requirements Checklist

> Legend: [MVP] – planned for initial release, [FUTURE] – future iteration, [USER] – specific to target audience (Students, Financially Struggling, Elderly)

---

## MVP Requirements

### Transaction Management
- [ ] [MVP] Add income/expense with category, date, amount, and optional note
- [ ] [MVP] Quick‑add button for frequent transactions (e.g., food, transport)
- [ ] [MVP] AI‑powered category suggestions (Gemini Flash) as user types description
- [ ] [MVP] Manual recurring transaction marking (landlord, subscriptions)

### Budget & Spending
- [ ] [MVP] Set monthly spending caps per category
- [ ] [MVP] Visual progress indicators (progress bars with green/yellow/red)
- [ ] [MVP] Push notification when 80% of a category budget is spent
- [ ] [MVP] Simple pie chart of current month’s spending by category

### Savings & Goals
- [ ] [MVP] Create amount‑based savings goals with target date/amount
- [ ] [MVP] Manual progress tracking (user updates saved amount)
- [ ] [MVP] Visual progress bar for each goal on dashboard

### EMI & Debts
- [ ] [MVP] Add EMI with name, total due, monthly payment, due date
- [ ] [MVP] EMI calculator (principal, rate, tenure → monthly payment)
- [ ] [MVP] Prepayment impact: show interest saved if user increases monthly payment

### Dashboard & Analytics
- [ ] [MVP] Summary cards: total income, total expenses, savings progress, upcoming EMIs
- [ ] [MVP] Monthly income vs. expense comparison chart
- [ ] [MVP] One actionable AI insight per month (e.g., “Dining up 15% – cook 2 more days”)

### Notifications & Reminders
- [ ] [MVP] Push reminders for EMI/bill payments (3 days before, 1 day before)
- [ ] [MVP] Monthly expense summary notification

### AI Features (GenAI via Gemini Flash)
- [ ] [MVP] Monthly spending habit analysis and personalized tips
- [ ] [MVP] Simple financial advice based on spending patterns (e.g., “Avoid impulse buys”)

### Financial Education
- [ ] [MVP] Glossary of basic financial terms (EMI, interest, inflation, etc.)
- [ ] [MVP] Rotating tips displayed in dashboard footer

### User Experience
- [ ] [MVP] Light & dark mode
- [ ] [MVP] Simple, intuitive navigation (bottom tabs: Home, Add, Stats, Learn)
- [ ] [MVP] Offline access to cached transaction data
- [ ] [MVP] Gesture‑based quick actions (swipe to delete/edit)

### Security
- [ ] [MVP] Password‑based authentication
- [ ] [MVP] Local data encryption (SQLCipher or equivalent)
- [ ] [MVP] No cloud sync in MVP – data stays on device

---

## Future Enhancements (Phase 2+)

### Transaction Management
- [ ] [FUTURE] Receipt scanning with OCR (photo → transaction)
- [ ] [FUTURE] Bulk CSV import
- [ ] [FUTURE] Recurring transaction templates (auto‑create)
- [ ] [FUTURE] Duplicate transaction detection
- [ ] [FUTURE] Tags and detailed notes
- [ ] [FUTURE] Multi‑currency support

### Budget & Spending
- [ ] [FUTURE] Rolling budget analysis (3‑month, 6‑month views)
- [ ] [FUTURE] Spending trend graphs across quarters/years
- [ ] [FUTURE] Budget comparison with demographic averages (anonymized)
- [ ] [FUTURE] Flexible budget adjustment (carry‑over unused amounts)

### Savings & Goals
- [ ] [FUTURE] Automatic savings suggestions based on spending patterns
- [ ] [FUTURE] Micro‑savings (round‑up transactions to nearest ₹10/50/100)
- [ ] [FUTURE] Goal prioritisation (urgency‑based sorting)
- [ ] [FUTURE] Savings achievement badges / motivational rewards

### EMI & Debts
- [ ] [FUTURE] EMI comparison tool (multiple loan offers)
- [ ] [FUTURE] Prepayment calculator showing interest saved
- [ ] [FUTURE] Debt consolidation suggestions
- [ ] [FUTURE] Credit score impact estimation (India‑specific bureau integration)

### Dashboard & Analytics
- [ ] [FUTURE] Spending heatmap (by day of week / week of month)
- [ ] [FUTURE] Predictive spending forecast for next month
- [ ] [FUTURE] Anomaly detection alerts (“Unusual ₹8,000 spent on groceries”)
- [ ] [FUTURE] AI‑driven expense breakdown with context (e.g., “40% of your eating‑out goes to weekend orders”)

### Notifications & Reminders
- [ ] [FUTURE] Smart reminders based on past behaviour (e.g., “Usually pay electricity by 5th”)
- [ ] [FUTURE] Motivational savings milestone celebrations
- [ ] [FUTURE] Bill payment confirmations (manual tap “paid”)
- [ ] [FUTURE] Real‑time category overspend alerts

### AI Features (GenAI + Chroma)
- [ ] [FUTURE] Personalised financial coaching (context‑aware tips using conversation history)
- [ ] [FUTURE] Auto‑categorisation of transactions via embeddings
- [ ] [FUTURE] Spending anomaly explanation (“This seems high because...”)
- [ ] [FUTURE] “What‑if” scenario analysis (e.g., “If you reduce dining by ₹500, you reach goal 2 months earlier”)
- [ ] [FUTURE] Bill negotiation suggestions (AI notices high gym fee, suggests script)

### Financial Education
- [ ] [FUTURE] 5‑minute interactive financial literacy mini‑courses
- [ ] [FUTURE] Age‑specific guidance (separate modules for students, working adults, elderly)
- [ ] [FUTURE] Money management checklists (end‑of‑month review, tax‑saving tips)
- [ ] [FUTURE] Budgeting templates (student, family, retiree)

### User Experience
- [ ] [FUTURE] Voice input for transactions (“Spent 500 on food” → auto‑fill)
- [ ] [FUTURE] Accessibility mode for elderly: larger fonts, high contrast, simplified flow
- [ ] [FUTURE] Wizard‑based onboarding for first‑time users
- [ ] [FUTURE] Family member read‑only / co‑management mode (for elderly)

### Security & Trust
- [ ] [FUTURE] Biometric login (fingerprint / face unlock)
- [ ] [FUTURE] End‑to‑end encrypted optional cloud backup
- [ ] [FUTURE] Clear, plain‑language data consent and privacy controls

### Accountability & Social
- [ ] [FUTURE] Weekly spending summary email/push
- [ ] [FUTURE] Accountability partner (share goal progress with a trusted friend)
- [ ] [FUTURE] Spending streaks / challenges (e.g., “5 days no eating out”)
- [ ] [FUTURE] Anonymous, category‑based leaderboards (motivation)

### Expense Insights
- [ ] [FUTURE] “Money leak” detection – small, frequent expenses that add up
- [ ] [FUTURE] Spending comparison vs. previous month / same month last year
- [ ] [FUTURE] Category‑wise growth rate analysis (dining +12% MoM)

---

## User‑Specific Feature Checklist

### For Students
- [ ] [USER] Quick‑add categories: food, transport, entertainment, study
- [ ] [USER] Pre‑built student budget template
- [ ] [USER] Spending comparison with peers (anonymised, aggregate data)
- [ ] [USER] Minimalistic, mobile‑first UI to reduce friction

### For Financially Struggling Users
- [ ] [USER] Positive reinforcement on staying under budget (celebrations)
- [ ] [USER] Micro‑savings goals (₹100, ₹500) – achievable targets
- [ ] [USER] Bill negotiation tips (AI‑suggested scripts)
- [ ] [USER] “Emergency fund” starter goal template

### For Elderly Users
- [ ] [USER] Large, high‑contrast UI with simple language (no jargon)
- [ ] [USER] Voice input for transactions
- [ ] [USER] Fraud detection: flag unusually large or out‑of‑pattern transactions
- [ ] [USER] Family co‑management mode (trusted contact can view, help categorise)
- [ ] [USER] One‑tap “Call my advisor” (or preset family member) shortcut

---

## Technical Implementation Goals

- [ ] Set up SQLite local database with encrypted storage
- [ ] Integrate Chroma for transaction embeddings (category matching, anomaly detection)
- [ ] Connect Gemini 2.5 Flash via OpenRouter for monthly analysis and “what‑if” queries
- [ ] Implement Firebase Cloud Messaging (FCM) for push notifications (Android)
- [ ] Design offline‑first sync strategy (local cache, queue updates, sync when online)
- [ ] Build Flask/FastAPI backend (future) to handle cloud sync, AI processing, social features
- [ ] Prepare migration path from SQLite to PostgreSQL for scaling
- [ ] Write privacy policy and data handling documentation in simple language

---

## Notes

- Items marked [MVP] form the baseline for first public release (students, financially struggling, elderly).
- [FUTURE] items are organised by priority and impact; many can be released incrementally.
- [USER] features can be toggled or surfaced based on onboarding profile selection.
- The checklist can be used directly as GitHub Issues or in a project board.
