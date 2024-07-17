import pytest

from django.core.management import call_command
from django.conf import settings
from playwright.sync_api import BrowserType, Page, expect
from pytest_django.live_server_helper import LiveServer

from rdmo.accounts.utils import set_group_permissions


@pytest.fixture
def _e2e_tests_django_db_setup(django_db_setup, django_db_blocker, fixtures):
    """Set up database and populate with fixtures, that get restored for every test case."""
    with django_db_blocker.unblock():
        call_command("loaddata", *fixtures)
        set_group_permissions()



@pytest.fixture
def base_url_page(
        django_user_model,
        username,
        live_server: LiveServer, 
        browser: BrowserType) -> Page:
    """Enable playwright to address URLs with base URL automatically prefixed."""
    # context = browser.new_context(base_url=live_server.url)
    user = django_user_model.objects.get(username=username)
    print(user)
    page = browser.new_page()
    yield page
    # context.close()


# # helper function for logging in the user
# def login_user(page: Page, username: str, password: str) -> Page:
#     page.goto("/account/login")
#     page.get_by_label("Username").fill(username, timeout=5000)
#     page.get_by_label("Password").fill(password)
#     page.get_by_role("button", name="Login").click()
#     page.goto("/management")
#     return page

# def logout_user(page: Page):
#     page.goto("/account/logout")
#     page.get_by_role("button", name="Logout").click()
#     expect(page).to_have_url('/')
#     return page

@pytest.fixture
def logged_in_user(_e2e_tests_django_db_setup, django_user_model, base_url_page, client, username:str, password: str) -> Page:
    """Log in as admin user through Django login UI, returns logged in page for e2e tests."""

    print()
    user = django_user_model.objects.get(username=username)
    print(user)
    print(client)
    client.force_login(user)
    print(client.cookies)
    session_cookie = client.cookies[settings.SESSION_COOKIE_NAME]
    assert session_cookie
    print(session_cookie)

    # Inject the session Cookie to playwright browser:
    cookie = {
        'name': session_cookie.key,
        'value': session_cookie.value,
        # 'url': live_server_url,
    }
    print(cookie)
    
    # page.context.add_cookies([cookie])


    page = login_user(base_url_page, username, password)
    yield page
    logout_user(page)
