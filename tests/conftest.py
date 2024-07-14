import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "separator: mark test to add a blank line before it")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_logreport(report):
    outcome = yield
    result = outcome.get_result()

    # Print a blank line before the test if it has the 'separator' marker
    if report.when =='setup' and 'separator' in report.keywords:
        print("\n")