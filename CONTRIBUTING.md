# Contributing to MoneyMan 💰

First off, thank you for considering contributing to MoneyMan! Projects like this thrive because of community members like you.

This guide outlines our development process, how to run and test the application, and guidelines for submitting pull requests.

---

## 🛠️ Local Development Setup

We currently have a Python/Flask web prototype of MoneyMan under the `WebApp/` directory.

### Prerequisites
- Python 3.11 or higher
- Git

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/MoneyMan.git
   cd MoneyMan
   ```

2. **Set up virtual environment:**
   We recommend using `venv` or `uv`:
   ```bash
   cd WebApp
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python db.py
   ```

5. **Run the local server:**
   ```bash
   PORT=5005 python app.py
   ```
   Open `http://127.0.0.1:5005/` in your browser to view the application.

---

## 🧪 Testing

We have a comprehensive unit test suite to verify database schemas, onboarding flows, and transaction operations.

To run the unit tests:
```bash
cd WebApp
python test_app.py
```

Make sure all tests pass before proposing any changes.

---

## 💡 Guidelines & Commit Rules

To maintain high code quality, please adhere to the following rules:

1. **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add goal deletion`
   - `fix: correct typo in dashboard`
   - `docs: update contributing guide`

2. **Branching Strategy**:
   - `main` is production-ready and protected.
   - Propose features or bug fixes via branches named `feat/feature-name` or `fix/bug-name`.
   - Submit a Pull Request targeting `main`.

3. **Accessibility (WCAG 2.1 AA)**:
   - Ensure all visual elements support high-contrast theme adjustments.
   - Use semantic tags for accessibility features.

4. **Privacy First**:
   - MoneyMan is offline-first. Never upload raw transaction data or personal details to any backend service.

Thank you for contributing!
