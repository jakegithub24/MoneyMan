# MoneyMan 💰

A friendly, AI‑assisted money manager for financial well‑being.

MoneyMan helps students, gig workers, and elderly users take control of their finances without intimidation. It combines simple transaction logging with visual budgets, savings goals, EMI tracking, and plain‑language AI insights – all while keeping your data private and offline‑first.

---

## ✨ Key Features (MVP)

- **Transaction Management** – Add income/expense with categories, dates, notes, and quick‑add buttons.
- **AI Category Suggestions** – Get smart category suggestions as you type a description (on‑device embeddings).
- **Monthly Budgets** – Set spending caps per category with visual progress bars and 80% alerts.
- **Savings Goals** – Create goals with target amounts, track progress manually, and see visual bars.
- **EMI & Debt Tracker** – Add EMIs with due dates, view payment schedules, and use the built‑in EMI calculator.
- **Dashboard** – Summary cards for income/expense, savings progress, upcoming EMIs, and a monthly spending chart.
- **Monthly AI Insights** – Receive a personalised analysis of your spending habits via Gemini Flash (internet required).
- **Reminders** – Push notifications for upcoming bill/EMI payments.
- **Financial Education** – In‑app glossary of basic terms and rotating tips.
- **Security** – Local password authentication with all data encrypted (SQLCipher). No cloud sync in MVP – data stays on your device.
- **Accessibility** – Light/dark theme, high‑contrast mode, and large‑text support.

---

## 🎯 Target Users

- **Students** – Easy expense tracking and student‑friendly budget templates.
- **Financially struggling individuals** – Positive reinforcement, micro‑savings goals, and bill negotiation tips.
- **Elderly users** – Large, high‑contrast UI, voice input, and family co‑management (future).

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Mobile** | Flutter 3.x (Dart) – Android first, iOS later |
| **Local Database** | SQLite + `sqflite_sqlcipher` (encryption) |
| **AI/ML** | OpenRouter (Gemini 2.5 Flash) for monthly analysis; Chroma (on‑device) for category suggestions |
| **Notifications** | Firebase Cloud Messaging (FCM) for push notifications |
| **Backend (future)** | FastAPI (Python 3.11+), PostgreSQL, Redis, Docker, GitHub Actions |

---

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (>=3.0)
- Android Studio / VS Code with Flutter extensions
- Android emulator or physical device

### Setup
```bash
git clone https://github.com/your-username/moneyman.git
cd moneyman
flutter pub get
flutter run
```

*For development, you’ll also need to configure Firebase for notifications (see `docs/firebase.md`).*

---

## 📁 Project Structure (simplified)

```
lib/
├── models/          # Data models (Transaction, Budget, etc.)
├── services/        # DB helpers, AI clients, notification service
├── screens/         # UI screens (Dashboard, AddTransaction, etc.)
├── widgets/         # Reusable widgets (budget bars, charts, etc.)
├── utils/           # Helpers, themes, constants
└── main.dart
```

---

## 🧪 Development Guidelines

- **Code Style**: Follow [Effective Dart](https://dart.dev/guides/language/effective-dart) with strict `analysis_options.yaml`.
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.).
- **Branching**: `main` (production) ← `develop` (integration) ← `feat/description` branches.
- **Testing**: Unit tests for data layer & utility functions; widget tests for key UI components.
- **Accessibility**: WCAG 2.1 AA contrast, text scaling up to 200%, TalkBack/VoiceOver audits.
- **Documentation**: Keep `PRD.md`, `TRD.md`, `features.md`, `LIMITATIONS.md`, and `RULES.md` updated with scope changes.

---

## ⚠️ Known Limitations (MVP)

- **Offline‑only**: No cloud sync – uninstalling the app loses all data.
- **Single user, single device** – no multi‑profile or sharing.
- **Currency & locale**: Hard‑coded to Indian Rupee (₹) and Indian date formats.
- **No bank integration** – manual entry only.
- **Android‑first**: iOS version follows after Android stabilisation.
- **Local AI embeddings** may increase app size and be slower on low‑end devices.

---

## 📚 Documentation

- [Product Requirements (PRD)](PRD.md)
- [Technical Requirements (TRD)](TRD.md)
- [Features Checklist](features.md)
- [Development Rules](RULES.md)
- [Known Limitations](LIMITATIONS.md)
- [Development TODO](DEV_TODO.md)

---

## 📄 License

This project is licensed under the terms specified in the `LICENSE` file.
