import os
import re
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from core.test_generator.ai_prompts import generate_unit_test_prompt
from .validation import validate_test_case, log_validation_errors

load_dotenv()
client = OpenAI(api_key=OPENAI_API_KEY)

class TestGenerator:
    def __init__(self, output_dir: str = "tests/unit"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_test_case(self, function_info: Dict, model: str = "gpt-3.5-turbo", prompt_override: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        prompt = prompt_override if prompt_override is not None else generate_unit_test_prompt(function_info)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Python unit tests."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        test_code = response.choices[0].message.content.strip()
        if test_code.startswith("```python") and test_code.endswith("```"):
            lines = test_code.splitlines()
            if len(lines) >= 3:
                test_code = "\n".join(lines[1:-1]).strip()
        if "<think>" in test_code and "</think>" in test_code:
            start_think = test_code.find("<think>")
            end_think = test_code.find("</think>")
            test_code = (test_code[:start_think] + test_code[end_think+len("</think>"):]).strip()
        is_valid, messages = validate_test_case(test_code, function_info)
        if not is_valid:
            log_validation_errors(test_code, messages)
            return False, None
        test_filename = self._generate_test_filename(function_info["name"], test_code)
        self._save_test_case(test_filename, test_code)
        return True, test_code

    def _generate_test_filename(self, function_name: str, test_code: str) -> str:
        hash_id = hashlib.md5(test_code.encode()).hexdigest()[:6]
        return f"test_{function_name}_{hash_id}.py"

    def _save_test_case(self, filename: str, test_code: str):
        filepath = Path(self.output_dir) / filename
        with open(filepath, "w") as f:
            f.write(test_code)