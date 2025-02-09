"""
A simple example Python file for testing UI test case generation.
"""

# A single UI element definition
UI_ELEMENT = {
    "element_id": "login-button",
    "element_xpath": "//button[@id='login-button']",
    "element_name": "Login Button",
    "dependencies": "None"
}

def get_ui_element() -> dict:
    return UI_ELEMENT

# A class representing a login page with several UI elements
class LoginPage:
    UI_ELEMENTS = {
        "username_field": {
            "element_id": "username",
            "element_xpath": "//input[@id='username']",
            "element_name": "Username Field",
            "dependencies": "None"
        },
        "password_field": {
            "element_id": "password",
            "element_xpath": "//input[@id='password']",
            "element_name": "Password Field",
            "dependencies": "None"
        },
        "login_button": {
            "element_id": "login-button",
            "element_xpath": "//button[@id='login-button']",
            "element_name": "Login Button",
            "dependencies": "None"
        }
    }

    def get_element(self, key: str) -> dict:
        return self.UI_ELEMENTS.get(key, {})