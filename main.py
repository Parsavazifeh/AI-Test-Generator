import argparse
import os
import logging
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from core.code_parser.ast_parser import parse_python_file
from core.test_generator.ai_prompts import (
    generate_unit_test_prompt,
    generate_integration_test_prompt,
    generate_ui_test_prompt
)
from core.test_generator.test_gen import TestGenerator

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

def process_file(input_file: str, test_type: str) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {"generated_tests": [], "errors": []}
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
        parsed_data = parse_python_file(input_file)
        functions = parsed_data.get("functions", [])
        classes = parsed_data.get("classes", [])
        test_gen = TestGenerator(output_dir=f"tests/{test_type}")
        for func in functions:
            try:
                logger.info(f"Processing function: {func['name']}")
                if test_type == "unit":
                    success, test_code = test_gen.generate_test_case(func)
                elif test_type == "integration":
                    dependencies = ["database", "external_service"]
                    prompt = generate_integration_test_prompt(func, dependencies)
                    success, test_code = test_gen.generate_test_case({**func, "prompt_override": prompt}, model="gpt-3.5-turbo")
                elif test_type == "ui":
                    ui_info = {
                        "element_id": func.get("element_id", func.get("name", "")),
                        "element_xpath": func.get("element_xpath", ""),
                        "element_name": func.get("element_name", func.get("name", "")),
                        "dependencies": func.get("dependencies", "None")
                    }
                    prompt = generate_ui_test_prompt(ui_info)
                    success, test_code = test_gen.generate_test_case({**func, "prompt_override": prompt}, model="gpt-3.5-turbo")
                else:
                    raise ValueError(f"Unsupported test type: {test_type}")
                if success:
                    test_filename = test_gen._generate_test_filename(func["name"], test_code)
                    test_path = Path(test_gen.output_dir) / test_filename
                    results["generated_tests"].append(str(test_path))
                    logger.info(f"Successfully generated {test_type} test for {func['name']}")
                else:
                    error_msg = f"Failed to generate test for {func['name']}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            except Exception as func_error:
                error_msg = f"Error processing {func['name']}: {func_error}"
                results["errors"].append(error_msg)
                logger.exception(error_msg)
        for cls in classes:
            try:
                logger.info(f"Processing class: {cls['name']}")
                methods = cls.get("methods", [])
                if methods:
                    for method in methods:
                        logger.info(f"Processing method: {cls['name']}.{method['name']}")
                        if test_type == "unit":
                            success, test_code = test_gen.generate_test_case(method)
                        elif test_type == "integration":
                            dependencies = ["database", "external_service"]
                            prompt = generate_integration_test_prompt(method, dependencies)
                            success, test_code = test_gen.generate_test_case({**method, "prompt_override": prompt}, model="gpt-3.5-turbo")
                        elif test_type == "ui":
                            ui_info = {
                                "element_id": method.get("element_id", f"{cls['name']}_{method['name']}"),
                                "element_xpath": method.get("element_xpath", ""),
                                "element_name": method.get("element_name", method.get("name", f"{cls['name']}_{method['name']}")),
                                "dependencies": method.get("dependencies", "None")
                            }
                            prompt = generate_ui_test_prompt(ui_info)
                            success, test_code = test_gen.generate_test_case({**method, "prompt_override": prompt}, model="gpt-3.5-turbo")
                        else:
                            raise ValueError(f"Unsupported test type: {test_type}")
                        if success:
                            test_filename = test_gen._generate_test_filename(f"{cls['name']}_{method['name']}", test_code)
                            test_path = Path(test_gen.output_dir) / test_filename
                            results["generated_tests"].append(str(test_path))
                            logger.info(f"Successfully generated {test_type} test for {cls['name']}.{method['name']}")
                        else:
                            error_msg = f"Failed to generate test for {cls['name']}.{method['name']}"
                            results["errors"].append(error_msg)
                            logger.error(error_msg)
                else:
                    logger.info(f"Processing class: {cls['name']} (no methods)")
                    if test_type == "unit":
                        success, test_code = test_gen.generate_test_case(cls)
                    elif test_type == "integration":
                        dependencies = ["database", "external_service"]
                        prompt = generate_integration_test_prompt(cls, dependencies)
                        success, test_code = test_gen.generate_test_case({**cls, "prompt_override": prompt}, model="gpt-3.5-turbo")
                    elif test_type == "ui":
                        ui_info = {
                            "element_id": cls.get("element_id", cls.get("name", "")),
                            "element_xpath": cls.get("element_xpath", ""),
                            "element_name": cls.get("element_name", cls.get("name", "")),
                            "dependencies": cls.get("dependencies", "None")
                        }
                        prompt = generate_ui_test_prompt(ui_info)
                        success, test_code = test_gen.generate_test_case({**cls, "prompt_override": prompt}, model="gpt-3.5-turbo")
                    else:
                        raise ValueError(f"Unsupported test type: {test_type}")
                    if success:
                        test_filename = test_gen._generate_test_filename(cls["name"], test_code)
                        test_path = Path(test_gen.output_dir) / test_filename
                        results["generated_tests"].append(str(test_path))
                        logger.info(f"Successfully generated {test_type} test for {cls['name']}")
                    else:
                        error_msg = f"Failed to generate test for {cls['name']}"
                        results["errors"].append(error_msg)
                        logger.error(error_msg)
            except Exception as cls_error:
                error_msg = f"Error processing class {cls['name']}: {cls_error}"
                results["errors"].append(error_msg)
                logger.exception(error_msg)
        return results
    except Exception as e:
        error_msg = f"Fatal error: {e}"
        results["errors"].append(error_msg)
        logger.exception("Fatal error during file processing")
        return results

def main() -> None:
    parser = argparse.ArgumentParser(description="AI Test Case Generator")
    parser.add_argument("--input", required=True, help="Input Python file to analyze")
    parser.add_argument("--test-type", required=True, choices=["unit", "integration", "ui"], help="Type of tests to generate")
    args = parser.parse_args()
    logger.info(f"Generating {args.test_type} tests for: {args.input}")
    results = process_file(args.input, args.test_type)
    logger.info(f"Process completed with {len(results['generated_tests'])} tests generated")
    logger.info(f"Errors encountered: {len(results['errors'])}")
    if results["errors"]:
        logger.error("Error details:")
        for error in results["errors"]:
            logger.error(f"- {error}")

if __name__ == "__main__":
    main()