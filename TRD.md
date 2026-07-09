# 2. TECHNICAL REQUIREMENTS DOCUMENT (TRD)

## 2.1 High‑Level Architecture
```
[Mobile App (Flutter)] ←→ [Local SQLite DB (encrypted)]
        ↕ (online sync – future)
[FastAPI Backend] → [PostgreSQL] + [Chroma Vector DB]
        ↓
[OpenRouter → Gemini 2.5 Flash]   [Firebase Cloud Messaging]
```

## 2.2 Technology Stack (MVP)
- **Frontend**: Flutter 3.x (Dart) for cross‑platform (iOS & Android)
- **Local DB**: SQLite with `sqflite` + `sqflite_sqlcipher` for encryption
- **AI/ML**: OpenRouter API (Gemini 2.5 Flash) for monthly analysis; Chroma (embedded) for category suggestion embeddings
- **Notifications**: Firebase Cloud Messaging (Android) / APNs (iOS)
- **Backend (future)**: FastAPI (Python 3.11+), PostgreSQL, Redis for caching
- **Infrastructure**: (future) Docker, AWS/GCP, GitHub Actions CI/CD

## 2.3 Data Models (SQLite – MVP)
- `users` (id, name, email, password_hash, created_at)
- `transactions` (id, user_id, type, amount, category, description, date, is_recurring, created_at)
- `budgets` (id, user_id, category, limit_amount, month_year, created_at)
- `savings_goals` (id, user_id, name, target_amount, current_amount, deadline, created_at)
- `emis` (id, user_id, name, total_amount, monthly_payment, interest_rate, tenure_months, remaining_months, due_day, start_date)
- `notifications` (id, user_id, type, title, message, sent_at, read)

## 2.4 API Endpoints (Future Backend)
- `POST /auth/register`, `POST /auth/login`
- `CRUD /transactions`
- `GET /ai/analysis` → Gemini prompt with last month’s transactions
- `POST /sync` → bulk data sync
- `POST /embeddings/search` → suggest category from description (Chroma)

## 2.5 AI Integration (GenAI)
- **Category Suggestion**: Embedding similarity (NomicEmbedText via Chroma) on typed description.
- **Monthly Analysis**: Send anonymized aggregate to Gemini Flash with a strict prompt → return 3 bullet tips + 1 graph description.
- **Future**: “What‑if” scenario engine.

## 2.6 Security & Privacy
- All local data encrypted at rest (SQLCipher).
- No user financial data leaves the device in MVP.
- Backend (future) will use HTTPS, JWT tokens, request validation.
- Privacy policy must be clear and accessible in simple language.
