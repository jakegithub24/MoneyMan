# 4. KNOWN LIMITATIONS (MVP)

- **Offline‑only, No Cloud Sync**: Data lives only on the device. If the app is uninstalled, data is lost (no backup). We’ll communicate this clearly.
- **Single User, Single Device**: No multi‑profile or family sharing.
- **Local AI Embeddings**: Chroma runs on‑device (via `chromadb_dart` or similar), which may increase app size. Category suggestions might be slow on low‑end devices initially.
- **Currency & Locale**: Hard‑coded to Indian Rupee (₹) and Indian date formats. No internationalisation yet.
- **EMI Calculator**: Simple straight‑line calculation, no floating/adjustable rate support.
- **No Bank Integration**: Manual entry only; no SMS parsing or account linking.
- **Notifications**: Reliant on FCM; may be delayed on some OEMs.
- **Android‑First MVP**: iOS version will follow after core Android stabilisation due to team capacity.
