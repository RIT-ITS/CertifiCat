#!/workspaces/certificat/.venv/bin/python

from dataclasses import dataclass, field
from inspect import isclass
import re
from typing import Self
from certificat.settings.dynamic import ConfigFile, SAMLSettings
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings
import os

HERE = os.path.dirname(__file__)


@dataclass
class Field:
    name: str
    model_field: FieldInfo = None
    env_name: str = ""
    children: list[Self] = field(default_factory=list)


markdown: list[str] = []

root = Field("root")


def recurse_settings(
    settings_klass: BaseModel,
    parent_field: Field,
    env_prefix: str,
    env_nested_delimiter: str,
):
    for field_name, model_field in settings_klass.model_fields.items():
        field = Field(field_name, model_field, env_prefix + field_name)
        parent_field.children.append(field)

        if model_field.validation_alias is not None:
            if isinstance(model_field.validation_alias, str):
                field.name = model_field.validation_alias
        elif isclass(model_field.annotation) and issubclass(
            model_field.annotation, BaseModel
        ):
            if issubclass(model_field.annotation, BaseSettings):
                recurse_settings(
                    model_field.annotation,
                    field,
                    model_field.annotation.model_config["env_prefix"],
                    model_field.annotation.model_config["env_nested_delimiter"],
                )
            else:  # BaseModel
                recurse_settings(
                    model_field.annotation,
                    field,
                    env_prefix + field_name + env_nested_delimiter,
                    env_nested_delimiter,
                )


recurse_settings(
    ConfigFile,
    root,
    ConfigFile.model_config["env_prefix"],
    ConfigFile.model_config["env_nested_delimiter"],
)

excluded_keys = ("SAML", "ACME", "SECTIGO_FINALIZER", "LOCAL_FINALIZER")


def print_yaml(field: Field, level: int = 0):
    indent = "  " * level
    env_name = field.env_name.upper()
    if env_name in excluded_keys:
        return

    def iprint(msg: str):
        nonlocal indent
        markdown.append(f"{indent}{msg}")

    value = ""
    if not field.children and field.model_field.default is not PydanticUndefined:
        if type(field.model_field.default) is str:
            value = f"'{field.model_field.default}'"
        else:
            value = field.model_field.default

    annotations = []
    if not field.children:
        if field.model_field.is_required():
            annotations.append("Required")
        if field.model_field.description:
            annotations.append(field.model_field.description)

    if annotations:
        iprint("# " + " - ".join(annotations))

    # if not field.children:
    #    iprint(f"# [{field.env_name.upper()}](#{field.env_name})")

    iprint(f"{field.name}: {value}")
    for field in field.children:
        print_yaml(field, level + 1)


markdown.append("```yaml")
for child in root.children:
    print_yaml(child)

saml_root = Field("root")
saml_settings = recurse_settings(
    SAMLSettings,
    saml_root,
    SAMLSettings.model_config["env_prefix"],
    SAMLSettings.model_config["env_nested_delimiter"],
)

markdown.append("saml:")
for child in saml_root.children:
    print_yaml(child, 1)
markdown.append("```\n")

markdown_str = "\n".join(markdown)
readme_path = os.path.join(HERE, "../README.md")
with open(readme_path, encoding="utf-8") as file:
    content = file.read()

with open(readme_path, "w", encoding="utf-8") as file:
    update_between = (
        "<!-- generated start -->",
        "<!-- generated end -->",
    )

    pattern = re.compile(
        f"({re.escape(update_between[0])}\n?).*(\n?{re.escape(update_between[1])})",
        re.DOTALL,
    )

    new_content = pattern.sub(f"\\1{markdown_str}\\2", content, count=1)

    file.write(new_content)
