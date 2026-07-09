# 5. DEVELOPMENT TODO CHECKLIST

## Phase 0: Foundation & Setup (Week 1–2)
- [ ] Set up GitHub repository with README, license, contributing guide.
- [ ] Create Flutter project, configure `analysis_options.yaml`, add `.gitignore`.
- [ ] Integrate SQLite + SQLCipher; define local DB schema.
- [ ] Set up basic folder structure (models, services, screens, widgets).
- [ ] Implement user registration/login locally (hashed password).
- [ ] Build onboarding flow with privacy consent and persona selection.
- [ ] Write PRD, TRD, limitations, and rules docs (this file) and commit.

## Phase 1: Core Features MVP (Week 3–8)
- [ ] Transaction CRUD (add, edit, delete, list) with categories.
- [ ] Implement AI category suggestion (on‑device Chroma + Gemini Flash if offline fallback? Use on‑device embeddings only for MVP to avoid internet dependency; or use a light on‑device model. Decide: Use a pre‑trained local TFLite model for MVP to keep fully offline; Gemini can be used for monthly analysis when internet is available.)
- [ ] Budget creation and progress bar widget.
- [ ] Savings goals tracker (manual current amount updates).
- [ ] EMI tracker + basic calculator (principal/rate/tenure).
- [ ] Dashboard screen with summary cards and a simple bar chart.
- [ ] Monthly AI analysis screen (requires internet): collect last month’s transactions, send anonymized summary to Gemini Flash, display result.
- [ ] Push notifications for EMI/bill reminders (schedule local notifications for MVP; FCM for future).
- [ ] Financial tips & glossary screens (static content).
- [ ] Light/dark theme toggle.

## Phase 2: Polish, UX & Accessibility (Week 9–10)
- [ ] Implement gesture‑based actions (swipe to delete, long‑press for edit).
- [ ] Add offline caching and sync state indicators.
- [ ] Design high‑contrast, large‑text mode (accessible theme).
- [ ] Voice input experiment (speech‑to‑text on transaction description) – basic integration.
- [ ] Write unit tests for critical logic (budget overspend detection, EMI calculation).
- [ ] Perform manual accessibility audit with TalkBack.
- [ ] Fix all UI glitches and responsiveness issues.

## Phase 3: Testing & Pre‑Launch (Week 11–12)
- [ ] Internal beta testing with 10–15 target users (students, elderly, gig workers).
- [ ] Gather feedback, prioritise crash fixes and UX friction points.
- [ ] Prepare app store listing (screenshots, description, privacy policy URL).
- [ ] Set up basic analytics (Firebase Analytics) to measure retention (opt‑in, anonymised).
- [ ] Final security review of local encryption.
- [ ] Release version 1.0.0 on Google Play Store (Android).

## Phase 4: Post‑MVP Iterations (Ongoing)
- [ ] Cloud sync and backup feature (migration to FastAPI backend).
- [ ] Receipt OCR (using device camera + Google ML Kit or Gemini).
- [ ] Voice input fully integrated with NLP.
- [ ] Accountability partner feature.
- [ ] “What‑if” scenario engine.
- [ ] Family co‑management mode for elderly.
- [ ] Internationalisation (multi‑currency, localised tips).
