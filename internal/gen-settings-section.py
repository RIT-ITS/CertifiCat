#!/usr/bin/env python
from __future__ import annotations

import json
import os
import sys
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from certificat.settings.dynamic import ConfigFile
from certificat.settings.examples import example_map

HERE = os.path.dirname(__file__)


@dataclass
class Schema:
    _def: dict[str, Any]
    _refs: dict[str, dict]

    def properties(self, parent: PropertyInfo = None) -> list[PropertyInfo]:
        props = []
        for name, schema_def in self._def.get("properties", {}).items():
            props.append(
                PropertyInfo(name, Schema(schema_def, self._refs), self, parent)
            )

        return props

    def get_ref(self, ref: str) -> any:
        if not ref.startswith("#/$defs/"):
            raise ValueError(f"Unsupported ref: {ref}")

        ref_name = ref.split("/")[-1]
        return self._refs[ref_name]

    def replace_immediate_refs(self, root: dict[str, Any]):
        # Replace $ref with referenced properties if it exists
        if "$ref" in root:
            ref: str = root["$ref"]
            if not ref.startswith("#/$defs/"):
                raise ValueError(f"Unsupported ref: {ref}")

            ref_name = ref.split("/")[-1]
            resolved = self._refs[ref_name]
            for key, value in resolved.items():
                root[key] = value


def ref_name(ref: str) -> str:
    if not ref.startswith("#/$defs/"):
        raise ValueError(f"Unsupported ref: {ref}")

    return ref.split("/")[-1]


def ref_link(ref: str) -> str:
    return "#refs." + ref_name(ref)


def def_link(definition: dict) -> str:
    return "#def." + definition.get("title")


def section_link(prop: PropertyInfo) -> str:
    return "#" + prop.key_path + ".section"


def polymorphic_link(prop: PropertyInfo) -> str:
    return "#" + prop.key_path + "[]"


def defaults_badge(default: str):
    icon = "material-water"
    if default == "null":
        return ""

    return badge(
        icon=f"[:{icon}:]({'../convention#default'} 'Default value')", text=default
    )


def type_badge(type: str):
    icon = "material-shape"
    return badge(icon=f"[:{icon}:]({'../convention#type'} 'Type')", text=type)


def required_badge():
    icon = "material-alert"
    return badge(
        icon=f"[:{icon}:]({'../convention#required'} 'Required value')", text="required"
    )


def badge(icon: str, text: str = "", type: str = "", title: str = ""):
    classes = f"mdx-badge mdx-badge--{type}" if type else "mdx-badge"
    return "".join(
        [
            f'<span class="{classes}" title="{title}">',
            *([f'<span class="mdx-badge__icon">{icon}</span>'] if icon else []),
            *([f'<span class="mdx-badge__text">{text}</span>'] if text else []),
            "</span>",
        ]
    )


class PropertyInfo:
    name: str
    key_path: str
    anchor: str
    root_schema: Schema
    schema: Schema
    properties: list[PropertyInfo]
    _ref: bool
    unique_by: str | None

    def __init__(
        self,
        name: str,
        schema: Schema,
        root_schema: Schema,
        parent: PropertyInfo = None,
        ref: bool = False,
        unique_by: str | None = None,
    ):
        self.name = name
        self.schema = schema
        self.root_schema = root_schema
        self.parent = parent
        self._ref = ref
        self.unique_by = unique_by

        parents: list[PropertyInfo] = []
        curr_parent = self.parent
        while curr_parent:
            parents.insert(0, curr_parent)
            curr_parent = curr_parent.parent

        self.key_path = ".".join([p.name for p in parents] + [self.name])
        self.key_path = self.key_path.lstrip(".")

        self.anchor = ".".join(
            [p.name + p.unique_by_anchor() for p in parents]
            + [self.name + self.unique_by_anchor()]
        )

        self.schema.replace_immediate_refs(self.schema._def)

    def unique_by_anchor(self) -> str:
        if self.unique_by:
            return f"[{self.unique_by}]"
        else:
            return ""

    def properties(self):
        return self.schema.properties(self)

    def is_polymorphic(self):
        return "discriminator" in self.schema._def

    def is_object(self):
        return self.schema._def.get("type") == "object"

    def is_enum(self):
        return self.enum() is not None

    def enum(self):
        return self.schema._def.get("enum")

    def examples(self) -> list[str]:
        return self.schema._def.get("examples", [])

    def has_ref(self):
        return "$ref" in self.schema._def

    def ref(self):
        return self.schema._def.get("$ref")

    def required(self):
        if not self.parent:
            return True

        return self.name in self.parent.schema._def.get("required", [])

    def anyOf(self):
        return self.schema._def.get("anyOf")

    def type(self):
        return self.schema._def.get("type")

    def items(self):
        return self.schema._def.get("items", {})

    def default(self):
        return self.schema._def.get("default")

    def deprecated(self):
        return self.schema._def.get("deprecated", False)

    def discriminator(self):
        disc = self.schema._def.get("discriminator", {})
        mappings = disc.get("mapping", {})

        for key, mapping in mappings.items():
            mappings[key] = self.root_schema.get_ref(mapping)
            mappings[key]["$ref"] = mapping

        return self.schema._def.get("discriminator", {})

    def description(self):
        return self.schema._def.get("description")


@dataclass
class DiscriminatorOption:
    mapping_key: str
    schema: dict[str, Any]
    anchor_key: str


@dataclass
class WalkOpts:
    level: int


@dataclass
class PropertyVisitor:
    properties: list[PropertyInfo]

    def __init__(self, properties: list[PropertyInfo]):
        self.properties = properties

    def walk(
        self,
        callback: Callable[[PropertyInfo, WalkOpts], None],
        *,
        recursive: bool = True,
    ):
        def _walk(properties: list[PropertyInfo], level: int):
            for prop in properties:
                callback(prop, WalkOpts(level))

                if recursive:
                    _walk(prop.properties(), level + 1)

        _walk(self.properties, 1)


def extract_types(prop: PropertyInfo) -> str:
    # Can be a "type" or a composite type with "anyOf"
    if prop.type():
        return prop.type()
    elif prop.anyOf():
        type_builder: list[str] = []
        for info in prop.anyOf():
            type_builder.append(info.get("type"))
        return " | ".join(type_builder)
    else:
        raise Exception(f"Can't generate, type for {prop.name} not handled.")  # noqa: TRY002


@dataclass
class PropFormatter:
    property: PropertyInfo

    def create_markdown(
        self, context: PropertyInfo, gen_type: GenType, level=4
    ) -> list[str]:
        lines = []
        required_marker = (
            "*" if self.property.required() and self.property.parent.required() else ""
        )
        lines.append(
            f"{'#' * level} `{self.property.key_path}` {{data-toc-label='{self.property.key_path.replace(context.key_path, '').lstrip('.')}{required_marker}' : #{self.property.anchor}}}"
        )

        if self.property.required():
            lines.append(required_badge())

        if self.property.is_object():
            lines.append(type_badge("object"))
            default = json.dumps(self.property.default(), indent=2)
            if default != "null":
                lines.append(f"``` json title='default' \n{default}\n```")
        else:
            default = json.dumps(self.property.default())
            if default != "null":
                lines.append(defaults_badge(default))

            if self.property.is_polymorphic():
                lines.append(type_badge("polymorphic"))
            elif self.property.items():
                types = []
                items = self.property.items()
                if "type" in items:
                    types.append(f"array&lt;{items['type']}&gt;")
                if "$ref" in items:
                    types.append(
                        f"array&lt;[{ref_name(items['$ref'])}]({ref_link(items['$ref'])})&gt;"
                    )

                lines.append(type_badge(",".join(types)))
            else:
                lines.append(type_badge(extract_types(self.property)))

        if self.property.description():
            lines.append(f"\n{self.property.description()}")

        for example in self.property.examples():
            formatted_example = "\n".join([f"    {e}" for e in example.splitlines()])
            lines.append(f"!!! example\n\n{formatted_example}")

        if self.property.is_polymorphic():
            discriminator = self.property.discriminator()
            discriminatorProp = discriminator.get("propertyName")
            # This generates differently depending on if it's a certificat. property or a #refs property
            # certificat. properties should link to a descriptive section, #refs should link to
            # another ref
            if self.property.key_path.startswith("certificat."):
                links = "\n".join(
                    [
                        f" - [{k}](#{self.property.key_path}[{k}])"
                        for k, m in discriminator["mapping"].items()
                    ]
                )
            else:
                links = "\n".join(
                    [
                        f" - [{k}]({ref_link(m['$ref'])})"
                        for k, m in discriminator["mapping"].items()
                    ]
                )

            lines.append(
                textwrap.dedent(f"""\
                    \nThis is a polymorphic property controlled by the `{self.property.key_path}.{discriminatorProp}` key, which means the shape of the configuration is different depending on the implementation. This property can be configured using the following types:\n
                """)
            )
            lines.append(links)

        # If an object is added it needs to link to a separate configuration section
        if self.property.is_object():  # noqa: SIM102
            if gen_type == GenType.shallow:
                # top-level objects should always link to a detailed configuration section
                # anything else should link to reference objects
                if self.property.parent.name == "certificat":
                    lines.append(
                        f"\n[:material-link: View Configuration Section]({section_link(self.property)})"
                    )

                elif self.property.has_ref():
                    lines.append(
                        f"\n[:material-shape: View Type Reference](#refs.{ref_name(self.property.ref())})"
                    )

        return lines


class SchemaDocGenerator:
    props: dict[str, PropertyInfo]
    schema: Schema
    definitions: dict

    def __init__(self, schema_def: dict[str, Any]) -> None:
        self.props = {}
        self.schema = Schema(schema_def, schema_def.get("$defs"))

        top_level_props = self.schema.properties()

        prop_stack = top_level_props
        while len(prop_stack) > 0:
            prop = prop_stack.pop()
            self.props[prop.key_path] = prop
            prop_stack.extend(prop.properties())

    def generate_refs(self) -> str:
        result_builder: list[str] = []
        for name, ref in self.schema._refs.items():
            result_builder.append(f"### {name} {{: #refs.{name}}}")
            ref_to_prop = PropertyInfo(
                name, Schema(ref, self.schema._refs), self.schema, ref=True
            )

            if ref_to_prop.is_enum():
                # TODO: This is very naive, may cause issues in the future if
                # the enumeration objects are refs
                result_builder.append(type_badge("enum") + "\n")
                for val in ref_to_prop.enum():
                    result_builder.append(f" - `{json.dumps(val)}`")

            result_builder.append(self.generate(ref_to_prop, GenType.shallow))
            if len(ref_to_prop.properties()) == 0:
                result_builder.append("\n---\n")

        return "\n".join(result_builder)

    def generate(self, section: str | PropertyInfo, gen_type: GenType) -> str:
        if isinstance(section, str):
            if section == "$ref":
                return self.generate_refs()
            else:
                section_prop = self.props[section]
        else:
            section_prop = section

        documented_props: list[PropertyInfo] = []
        lines: list[str] = []

        if section_prop.is_polymorphic():
            discriminator = section_prop.discriminator()
            discriminatorProp = discriminator.get("propertyName")
            lines.append(
                textwrap.dedent(f"""\
                    This is a polymorphic property controlled by the `{discriminatorProp}` key. The following sections will show common configuration options as well as full documentation for every property.\n
                """)
            )

            for key, mapping in discriminator["mapping"].items():
                lines.append(
                    f"### `{section}.{discriminatorProp}: {key}` {{data-toc-label='{key}' : #{section}[{key}]}}"
                )

                example_key = f"{section}.{discriminatorProp}.{key}"
                if example_key in example_map:
                    lines.append(example_map[example_key])

                # gather all lines for nested properties and shove them under this polymorphic example
                mapping_to_prop = PropertyInfo(
                    f"{section_prop.key_path}",
                    Schema(mapping, self.schema._refs),
                    self.schema,
                    unique_by=key,
                )
                child_lines = self.generate(mapping_to_prop, GenType.deep)
                lines.append(child_lines)
        else:
            documented_props = section_prop.properties()

        property_visitor = PropertyVisitor(documented_props)

        selected_props: list[PropertyInfo] = []

        def on_visit(prop: PropertyInfo, opts: WalkOpts):
            selected_props.append(prop)

        property_visitor.walk(on_visit, recursive=gen_type != GenType.shallow)

        def sort_props(prop: PropertyInfo):
            return (not (prop.required() and prop.parent.required()), prop.key_path)

        selected_props.sort(key=sort_props)

        for prop in selected_props:
            if prop.deprecated():
                continue

            if (
                prop.is_object()
                and len(prop.properties()) > 0
                and gen_type != GenType.shallow
            ):
                continue

            lines.extend(PropFormatter(prop).create_markdown(section_prop, gen_type))
            lines.append("\n---\n")

        return "\n".join(lines)


if len(sys.argv) < 4:
    print("Error: Please provide exactly three arguments.")
    print("Usage: gen-settings-section <section> <output> <type>")
    sys.exit(1)


class GenType(Enum):
    shallow = "shallow"
    deep = "deep"


section = sys.argv[1]
settings_file = sys.argv[2]
gen_type: GenType = GenType[sys.argv[3]]

schema = ConfigFile.model_json_schema()
markdown = SchemaDocGenerator(schema).generate(section, gen_type)

with open(settings_file, "w") as file:
    file.write(markdown)
