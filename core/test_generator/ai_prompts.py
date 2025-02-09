import json
from typing import Dict, List
from pathlib import Path

def load_prompt_template(template_name: str) -> str:
    template_path = Path("prompts") / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    with open(template_path, "r") as f:
        return f.read()

def generate_unit_test_prompt(function_info: Dict) -> str:
    function_name = function_info["name"]
    args = function_info["args"]
    return_type = function_info["return_type"]
    docstring = function_info["docstring"]
    arg_descriptions = []
    for arg in args:
        arg_name = arg["name"]
        arg_type = arg["type"]
        is_vararg = arg.get("is_vararg", False)
        is_kwarg = arg.get("is_kwarg", False)
        if is_vararg:
            arg_descriptions.append(f"*{arg_name}: {arg_type} (variable-length arguments)")
        elif is_kwarg:
            arg_descriptions.append(f"**{arg_name}: {arg_type} (keyword arguments)")
        else:
            arg_descriptions.append(f"{arg_name}: {arg_type}")
    template = load_prompt_template("unit_test_template.txt")
    prompt = template.format(
        function_name=function_name,
        arguments=", ".join(arg_descriptions),
        return_type=return_type,
        docstring=docstring if docstring else "No docstring available."
    )
    return prompt

def generate_integration_test_prompt(function_info: Dict, dependencies: List[str]) -> str:
    function_name = function_info["name"]
    args = function_info["args"]
    return_type = function_info["return_type"]
    docstring = function_info["docstring"]
    arg_descriptions = []
    for arg in args:
        arg_name = arg["name"]
        arg_type = arg["type"]
        is_vararg = arg.get("is_vararg", False)
        is_kwarg = arg.get("is_kwarg", False)
        if is_vararg:
            arg_descriptions.append(f"*{arg_name}: {arg_type} (variable-length arguments)")
        elif is_kwarg:
            arg_descriptions.append(f"**{arg_name}: {arg_type} (keyword arguments)")
        else:
            arg_descriptions.append(f"{arg_name}: {arg_type}")
    template = load_prompt_template("integration_test_template.txt")
    prompt = template.format(
        function_name=function_name,
        arguments=", ".join(arg_descriptions),
        return_type=return_type,
        docstring=docstring if docstring else "No docstring available.",
        dependencies=", ".join(dependencies)
    )
    return prompt

def generate_ui_test_prompt(ui_element_info: Dict) -> str:
    element_id = ui_element_info.get("id", "N/A")
    element_xpath = ui_element_info.get("xpath", "N/A")
    element_name = ui_element_info.get("name", "N/A")
    dependencies = ui_element_info.get("dependencies", "None")
    template = load_prompt_template("ui_test_template.txt")
    prompt = template.format(
        element_id=element_id,
        element_xpath=element_xpath,
        element_name=element_name,
        dependencies=dependencies
    )
    return prompt