#!/usr/bin/env python
from __future__ import annotations
from certificat.settings.dynamic import ConfigFile
from certificat.settings.examples import example_map

import json
from dataclasses import dataclass
from typing import Any
import os

HERE = os.path.dirname(__file__)


@dataclass
class PropertyInfo:
    name: str
    key_path: str
    schema: dict[str, Any]
    required: str


@dataclass
class DiscriminatorOption:
    mapping_key: str
    schema: dict[str, Any]
    anchor_key: str


class SchemaDocGenerator:
    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema
        self.definitions = schema.get("$defs", {})

    def generate(self) -> str:
        summary_entries = sorted(
            self._collect_summary_entries(),
            key=lambda entry: entry.key_path,
        )
        detail_entries = sorted(
            self._collect_detail_entries(),
            key=lambda entry: entry.key_path,
        )
        lines = [
            "# Settings Documentation",
            "",
            "| Key | Required | Default | Description |",
            "| --- | --- | --- | --- |",
        ]

        for entry in summary_entries:
            if entry.schema.get("type") == "object":
                continue
            lines.append(
                "| "
                f"[`{entry.key_path}`](#{self._anchor(entry.key_path)}) | "
                f"{'✓' if entry.required == 'Yes' else ''} | "
                f"`{self._extract_default(entry.schema, suppress=self._has_discriminator(entry.schema))}` | "
                f"{self._escape_pipes(self._extract_description(entry.schema) or '-')}"
                " |"
            )

        for entry in detail_entries:
            if self._has_discriminator(entry.schema):
                lines.extend(self._render_property_section(entry, level=2))

        lines.append("")
        return "\n".join(lines)

    def _collect_detail_entries(self) -> list[PropertyInfo]:
        entries: list[PropertyInfo] = []
        root_properties = self._collect_direct_properties(self.schema, parent_path="")
        for root_entry in root_properties:
            entries.extend(
                self._collect_direct_properties(
                    root_entry.schema,
                    parent_path=root_entry.key_path,
                )
            )
        return entries

    def _collect_summary_entries(self) -> list[PropertyInfo]:
        entries: list[PropertyInfo] = []
        root_properties = self._collect_direct_properties(self.schema, parent_path="")
        for root_entry in root_properties:
            for child_entry in self._collect_direct_properties(
                root_entry.schema,
                parent_path=root_entry.key_path,
            ):
                entries.extend(self._flatten_summary_entries(child_entry))
        return entries

    def _flatten_summary_entries(self, entry: PropertyInfo) -> list[PropertyInfo]:
        entries = [entry]
        if self._has_discriminator(entry.schema):
            return entries

        for child_entry in self._collect_direct_properties(
            entry.schema,
            parent_path=entry.key_path,
        ):
            entries.extend(self._flatten_summary_entries(child_entry))
        return entries

    def _flatten_discriminator_entries(self, entry: PropertyInfo) -> list[PropertyInfo]:
        entries = [entry]

        for child_entry in self._collect_direct_properties(
            entry.schema,
            parent_path=entry.key_path,
        ):
            entries.extend(self._flatten_discriminator_entries(child_entry))
        return entries

    def _render_property_section(self, entry: PropertyInfo, level: int) -> list[str]:
        schema = entry.schema
        discriminator = self._get_discriminator(schema)
        children = self._collect_direct_properties(schema, parent_path=entry.key_path)

        default = self._extract_default(schema, suppress=bool(discriminator))

        lines = [
            "",
            f'<a id="{self._anchor(entry.key_path)}" name="{self._anchor(entry.key_path)}"></a>',
            "",
            f"{'#' * level} `{entry.key_path}`",
            f"This is a polymorphic property controlled by the `{discriminator['propertyName']}` attribute. Use the following templates as an example of how to configure different `{entry.name}` types.",
            f"- Required: `{entry.required}`",
            f"- Description: {self._extract_description(schema) or 'No description provided.'}",
        ]

        if discriminator:
            options = sorted(
                self._collect_discriminator_options(
                    schema,
                    entry.key_path,
                    discriminator["propertyName"],
                ),
                key=lambda option: option.mapping_key,
            )
            mapping_links = ", ".join(
                f"[`{option.mapping_key}`](#{self._anchor(option.anchor_key)})"
                for option in options
            )
            lines.append(f"- Types: {mapping_links}")
            for option in options:
                lines.extend(
                    self._render_discriminator_option(
                        parent_key=entry.key_path,
                        option=option,
                        discriminator_name=discriminator["propertyName"],
                        level=level + 1,
                    )
                )
            return lines

        if children:
            child_links = ", ".join(
                f"[`{child.name}`](#{self._anchor(child.key_path)})"
                for child in sorted(children, key=lambda child: child.key_path)
            )
            lines.append(f"- Children: {child_links}")
            for child in sorted(children, key=lambda child: child.key_path):
                lines.extend(self._render_property_section(child, level=level + 1))

        return lines

    def _render_discriminator_option(
        self,
        *,
        parent_key: str,
        option: DiscriminatorOption,
        discriminator_name: str,
        level: int,
    ) -> list[str]:
        children = []

        for child_entry in self._collect_direct_properties(
            option.schema,
            parent_path=parent_key,
        ):
            children.extend(self._flatten_discriminator_entries(child_entry))

        example = example_map.get(f"{parent_key}.type.{option.mapping_key}")
        lines = [
            "",
            f'<a id="{self._anchor(option.anchor_key)}"></a>',
            "",
            f"{'#' * level} `{parent_key}.type: {option.mapping_key}`",
            "" if not example else f"```{example}```",
            "| Key | Required | Default | Description |",
            "| --- | --- | --- | --- |",
        ]

        for child in sorted(
            children, key=lambda child: "" if child.name == "type" else child.key_path
        ):
            if child.schema.get("type") == "object":
                continue

            default = self._extract_default(
                child.schema, suppress=self._has_discriminator(child.schema)
            )
            lines.append(
                "| "
                f"[`{child.key_path}`](#{self._anchor(child.key_path)}) | "
                f"{'✓' if child.required == 'Yes' else ''} | "
                f"`{'""' if default == '' else default}` | "
                f"{self._escape_pipes(self._extract_description(child.schema) or '-')}"
                " |"
            )

        return lines

    def _collect_direct_properties(
        self,
        schema: dict[str, Any],
        *,
        parent_path: str,
        exclude: set[str] | None = None,
    ) -> list[PropertyInfo]:
        resolved = self._resolve_schema(schema)
        properties = resolved.get("properties", {})

        required_value = resolved.get("required", [])
        required = set(required_value) if isinstance(required_value, list) else set()
        exclude = exclude or set()

        direct_properties = []
        for name, property_schema in properties.items():
            property_schema = self._resolve_schema(property_schema)
            if name not in exclude and not self._is_deprecated(property_schema):
                direct_properties.append(
                    PropertyInfo(
                        name=name,
                        key_path=f"{parent_path}.{name}" if parent_path else name,
                        schema=property_schema,
                        required="Yes" if name in required else "No",
                    )
                )

        return direct_properties

    def _collect_discriminator_options(
        self,
        schema: dict[str, Any],
        parent_key: str,
        discriminator_name: str,
    ) -> list[DiscriminatorOption]:
        resolved = self._resolve_schema(schema)
        mapping = resolved["discriminator"].get("mapping", {})
        options: list[DiscriminatorOption] = []
        for mapping_key, ref in mapping.items():
            option_schema = {"$ref": ref} if isinstance(ref, str) else ref
            options.append(
                DiscriminatorOption(
                    mapping_key=mapping_key,
                    schema=option_schema,
                    anchor_key=f"{parent_key}.{discriminator_name}.{mapping_key}",
                )
            )
        return options

    def _resolve_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        if "$ref" not in schema:
            return schema

        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise ValueError(f"Unsupported ref: {ref}")

        ref_name = ref.split("/")[-1]
        resolved = dict(self.definitions[ref_name])
        for key, value in schema.items():
            if key != "$ref":
                resolved[key] = value
        return resolved

    def _extract_description(self, schema: dict[str, Any]) -> str:
        resolved = self._resolve_schema(schema)
        if "description" in resolved:
            return str(resolved["description"])
        return ""

    def _extract_default(self, schema: dict[str, Any], suppress: bool = False) -> str:
        if suppress:
            return "-"
        resolved = self._resolve_schema(schema)
        if "default" in resolved:
            default_value = resolved["default"]
            # if isinstance(default_value, (dict, list)):
            #    return "-"
            return self._format_value(default_value)
        return "-"

    def _get_discriminator(self, schema: dict[str, Any]) -> dict[str, Any] | None:
        resolved = self._resolve_schema(schema)
        discriminator = resolved.get("discriminator")
        return discriminator if discriminator else None

    def _has_discriminator(self, schema: dict[str, Any]) -> bool:
        return self._get_discriminator(schema) is not None

    def _has_detail_children(self, schema: dict[str, Any]) -> bool:
        return self._has_discriminator(schema) or bool(
            self._collect_direct_properties(schema, parent_path="placeholder")
        )

    def _is_deprecated(self, schema: dict[str, Any]) -> bool:
        resolved = self._resolve_schema(schema)
        return bool(resolved.get("deprecated"))

    @staticmethod
    def _format_value(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, (dict, list, bool, int, float)):
            return json.dumps(value, sort_keys=True)
        return str(value)

    @staticmethod
    def _anchor(key: str) -> str:
        return key.lower().replace(".", "-")

    @staticmethod
    def _escape_pipes(value: str) -> str:
        return value.replace("|", "\\|")


schema = ConfigFile.model_json_schema()
markdown = SchemaDocGenerator(schema).generate()

settings_file = os.path.join(HERE, "../SETTINGS.md")
with open(settings_file, "w") as file:
    file.write(markdown)
