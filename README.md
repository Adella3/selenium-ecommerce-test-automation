# E-commerce Web Test Automation (Selenium + Python)

> **"How do you make UI tests that keep working when the page doesn't behave perfectly?"**

End-to-end functional test automation for a demo e-commerce site ([LambdaTest eCommerce Playground](https://ecommerce-playground.lambdatest.io/)), built for UTS 31282 Systems Testing and Quality Management.

---

## Test Coverage

| ID | Feature | Scenarios |
|---|---|---|
| T01 | User registration | missing required fields · password mismatch · privacy policy unchecked · valid registration |
| T02 | Login | invalid password · valid login |
| T03 | Add to cart | add product, verify cart contents |
| T04 | Update quantity | change quantity, verify updated total |
| T05 | Remove item | remove product, verify empty cart |
| T06 | Search | keyword + category combination search |

Each test runs independently (creates its own throwaway account when needed) and saves a screenshot as evidence.

---

## Design

```
tests/
├── common_web.py          shared helpers: driver setup, waits, robust click, screenshots,
│                          fallback selectors, test-account creation
├── t01_register.py
├── t02_login.py
├── t03_add_to_cart.py
├── t04_update_quantity.py
├── t05_remove_item.py
└── t06_search.py
```

- **Shared helper module**: one place for driver setup and common actions, so each test reads like a scenario.
- **Explicit waits** (`WebDriverWait`) instead of fixed sleeps.
- **Robust interactions**: falls back to a JavaScript click when an element is overlapped, and tries multiple selectors before failing.
- **Negative + positive cases**: validation errors are asserted by message content, not just by "no crash".
- **Cross-platform**: `webdriver-manager` resolves the right ChromeDriver on macOS (ARM) and Windows (x86).

## How to Run

```bash
pip install -r requirements.txt
cd tests
python t01_register.py      # each script launches Chrome, runs, and closes
```

Requires Google Chrome. Test data (names, emails, passwords) is randomly generated dummy data.

## Screenshots

See [`screenshots/`](screenshots/) for captured evidence per test case.

## Credits

- Minjung (Adella) Koo, T01, T04, T06, shared module, integration
- Henry Han, T02, T03, T05
