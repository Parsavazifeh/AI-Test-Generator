


# AI-Based Test Case Generation

## 1. Introduction  
This project automates test case generation using AI models (such as GPT-4 and GPT-3.5-turbo) to analyze Python source code, bug reports, and existing test suites. The system generates unit, integration, and UI tests—accelerating test creation, reducing human bias, and adapting to evolving codebases.

---

## 2. Scope & Objectives  

### Explicit Scope  
- **Primary Language:** Python (future support for Java/JavaScript is planned).  
- **Test Types:**  
  - **Unit Tests:** Generated with PyTest.  
  - **Integration Tests:** Generated with PyTest, including mocked dependencies.  
  - **UI Tests:** Selenium-based tests for web applications.  
- **Data Sources:**  
  - Source code (via AST parsing and GitPython).  
  - Structured bug reports (e.g., JIRA exports).  
  - Existing test cases (for iterative improvements).

### Out-of-Scope  
- Non-Python codebases (to be addressed in Phase 2).  
- Performance/load testing (planned for Phase 3).

---

## 3. Development Environment Setup  

### Virtual Environment  
```bash
python -m venv .venv  
source .venv/bin/activate  # Linux/Mac  
.\.venv\Scripts\activate   # Windows
```

### Dependencies  
```bash
pip install openai langchain pytest selenium beautifulsoup4 gitpython python-dotenv
```

### Security Configuration  
- **.env File:**  
```plaintext
OPENAI_API_KEY="your_key_here"
```

- **Loading Environment Variables:**  
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 4. Project Structure & Implementation Roadmap  

### Directory Layout  
```
ai-test-generator/
├── .github/                   # CI/CD workflows
│   └── workflows/
│       └── tests.yml          
├── config/                    # Configurations (.env, settings.py)
├── core/                      # Main logic
│   ├── code_parser/          
│   │   ├── ast_parser.py     
│   │   └── git_integration.py
│   ├── test_generator/       
│   │   ├── ai_prompts.py     
│   │   ├── test_gen.py       
│   │   └── validation.py     
│   └── ui_testing/           # Selenium-based UI testing
│       └── selenium_utils.py
├── data/                      # Input/output data and logs
│   ├── input_code/           
│   ├── bug_reports/          
│   └── failed_tests.log      
├── tests/                     # Generated tests (unit, integration, ui)
├── reports/                   # Test reports (e.g. results.xml)
├── scripts/                   # Utility scripts (run_tests.sh, setup_env.sh)
├── prompts/                   # AI prompt templates
│   ├── unit_test_template.txt
│   ├── integration_test_template.txt
│   └── ui_test_template.txt
├── requirements.txt           # Dependencies list
├── main.py                    # CLI entry point
└── README.md                  # Project documentation
```

### Implementation Order  
1. **Setup Foundations:**  
   - Create `requirements.txt`, `.env`, and `config/settings.py`.  
2. **Core Modules:**  
   - Develop `ast_parser.py` (AST parsing) → `ai_prompts.py` (prompt templates) → `test_gen.py` (test generation logic).  
3. **Execution Pipeline:**  
   - Add `validation.py` (syntax and structure checks) and a function to run tests (e.g., `run_pytest()`).  
4. **UI Testing:**  
   - Develop `selenium_utils.py` for Selenium-based UI tests with headless mode.  
5. **CI/CD & Documentation:**  
   - Finalize GitHub Actions workflows and `README.md`.  

---

## 5. Extracting Code Information  

### AST Parsing for Python  
```python
import ast

def extract_functions(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                "args": args,
                "docstring": docstring
            })
    return functions
```

### Git Integration  
```python
from git import Repo

def clone_repo(repo_url, local_path):
    Repo.clone_from(repo_url, local_path)
```

---

## 6. AI-Based Test Case Generation  

### Enhanced Prompt Engineering  
```python
template = """  
Given the Python function below:  
{function_code}  

Generate a PyTest unit test suite with:  
1. Happy-path scenarios.  
2. Edge cases (e.g., invalid inputs).  
3. Assertions to verify correct outputs or expected exceptions.  
"""
```

### Validation of Generated Tests  
```python
import ast

def validate_test_case(test_code):
    try:
        ast.parse(test_code)
        return True
    except SyntaxError:
        return False
```

---

## 7. Saving & Executing Test Cases  

### Test Organization  
```python
import hashlib

def save_test_case(function_name, test_code):
    hash_id = hashlib.md5(test_code.encode()).hexdigest()[:6]
    filename = f"tests/unit/test_{function_name}_{hash_id}.py"
    with open(filename, "w") as f:
        f.write(test_code)
```

### Test Execution & Reporting  
```python
import subprocess

def run_pytest():
    result = subprocess.run(["pytest", "tests/", "-v", "--junitxml=reports/results.xml"], capture_output=True)
    print(result.stdout.decode())
    return result.returncode
```

---

## 8. Automating UI Testing  

### Robust Element Selection  
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_selenium_test():
    driver = webdriver.Chrome()
    driver.get("https://example.com")
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submit-button"))
        )
        button.click()
    finally:
        driver.quit()
```

### Headless Mode for CI/CD  
```python
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
```

---

## 9. CI/CD Integration  

### GitHub Actions Workflow  
```yaml
name: AI Test Runner
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run AI Test Generator
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python main.py --input example.py --test-type unit
      - name: Execute Tests
        run: pytest tests/ --junitxml=reports/results.xml
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-reports
          path: reports/
```

---

## 10. Model Evaluation & Feedback Loop  

### Quality Metrics  
- Track test coverage using `pytest-cov`.  
- Compare AI-generated tests with human-written ones (using precision/recall metrics).  

### Retraining the Model  
```python
def log_failed_test(test_code, error):
    with open("failed_tests.log", "a") as f:
        f.write(f"Error: {error}\nTest Code:\n{test_code}\n\n")
```

---

## 11. Security & Compliance  
- **Data Anonymization:** Remove sensitive data from bug reports.  
- **Access Control:** Use SSH keys and proper repository permissions to restrict access.  

---

## 12. Documentation & User Guide  

### Usage Instructions  
```bash
# Generate unit tests for a Python file
python main.py --input example.py --test-type unit

# Generate integration tests for a Python file
python main.py --input example.py --test-type integration

# Generate UI tests for a Python file
python main.py --input example_ui.py --test-type ui

# Run all tests
pytest tests/
```

### Extension Points  
- Add new test types by modifying prompt templates in the `prompts/` folder.  
- Extend AST parsing to support additional languages.  

---
