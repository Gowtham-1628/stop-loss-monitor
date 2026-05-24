# Testing & QA Guide

## Test Coverage

### Phase 1: Infrastructure Tests

- ✅ Python version check
- ✅ Dependencies validation
- ✅ File structure verification
- ✅ Config module import
- ✅ Environment variables

Run: `python test_phase1.py`

### Phase 2: Unit Tests

- ✅ Position reader (Google Sheets mocking)
- ✅ Webull market data (API response parsing)
- ✅ Stop loss validator (hit detection logic)
- ✅ WhatsApp notifier (message formatting)
- ✅ Alert manager (cooldown & coordination)
- ✅ Scheduler (market hours detection)

Run: `python run_comprehensive_tests.py`

### Phase 3: Integration Tests

- ✅ End-to-end workflow (full check cycle)
- ✅ Duplicate alert prevention
- ✅ Error recovery & handling
- ✅ Multi-position validation

Run: `python -m pytest tests/test_integration.py -v`

---

## Running All Tests

### Quick Test (All Unit Tests)

```bash
cd "/Users/sai/Documents/Github 2/monthly-returns"
python run_comprehensive_tests.py
```
