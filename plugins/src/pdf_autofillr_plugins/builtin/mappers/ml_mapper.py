"""
Built-in: MLMapperPlugin

Fuzzy-matching mapper that maps extracted fields to a target schema using
a configurable keyword synonym table. No ML libraries required — pure Python.
In production, swap _predict_target_field() for a real embedding-based lookup.

Registered under category="mapper", name="ml-mapper".
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import MapperPlugin, PluginMetadata

# Default synonym table — maps common source field name variants to
# canonical target names. Extend via config["synonyms"].
_DEFAULT_SYNONYMS: Dict[str, str] = {
    "first_name": "firstName",
    "firstname": "firstName",
    "fname": "firstName",
    "last_name": "lastName",
    "lastname": "lastName",
    "lname": "lastName",
    "email": "emailAddress",
    "email_address": "emailAddress",
    "e_mail": "emailAddress",
    "phone": "phoneNumber",
    "telephone": "phoneNumber",
    "mobile": "phoneNumber",
    "phone_number": "phoneNumber",
    "invoice_number": "invoiceNo",
    "invoice_no": "invoiceNo",
    "inv_number": "invoiceNo",
    "invoice_date": "invoiceDate",
    "date": "invoiceDate",
    "total": "totalAmount",
    "total_amount": "totalAmount",
    "amount": "totalAmount",
    "vendor": "vendorName",
    "vendor_name": "vendorName",
    "supplier": "vendorName",
}


@plugin(
    category="mapper",
    name="ml-mapper",
    version="1.0.0",
    author="PDF AutoFillr Team",
    description="Fuzzy synonym mapper — maps fields via a configurable keyword table. "
    "Swap _predict_target_field() for real ML embeddings in production.",
    tags=["ml", "fuzzy", "synonym", "builtin"],
    priority=150,  # above identity-mapper (100), below custom ML mappers
)
class MLMapperPlugin(MapperPlugin):
    """
    Keyword-synonym mapper.

    Strategy (in order):
    1. Exact key lookup in synonym table.
    2. Lowercased + underscore-normalised lookup.
    3. Schema key exact match (passthrough).
    4. Field left unmapped.

    Config options:
        synonyms (dict): Extra synonym mappings that extend the built-in table.
        confidence (float): Fixed confidence score reported (default 0.85).
    """

    def initialize(self) -> None:
        extra = self.get_config_value("synonyms", {})
        self._synonyms = {**_DEFAULT_SYNONYMS, **extra}
        self._confidence = float(self.get_config_value("confidence", 0.85))
        super().initialize()

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ml-mapper",
            version="1.0.0",
            author="PDF AutoFillr Team",
            description="Fuzzy synonym mapper — configurable keyword table",
            category="mapper",
            tags=["ml", "fuzzy", "synonym", "builtin"],
            dependencies=[],
        )

    def supports_schema(self, schema: Dict[str, Any]) -> bool:
        return True  # accepts any schema

    def map_fields(
        self,
        extracted_fields: List[Dict[str, Any]],
        target_schema: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        mapped: Dict[str, Any] = {}
        unmapped: List[str] = []
        mapping_info: List[Dict[str, Any]] = []

        schema_keys = set(target_schema.keys()) if target_schema else set()

        for field in extracted_fields:
            name = field.get("name", "")
            value = field.get("value", "")

            target = self._predict_target_field(name, schema_keys)

            if target:
                mapped[target] = value
                mapping_info.append(
                    {
                        "source": name,
                        "target": target,
                        "confidence": self._confidence,
                        "method": "ml-synonym",
                    }
                )
            else:
                unmapped.append(name)

        total = len(extracted_fields)
        avg_conf = self._confidence if mapped else 0.0

        return {
            "mapped_fields": mapped,
            "unmapped_fields": unmapped,
            "mapping_info": mapping_info,
            "mapper": "ml-mapper",
            "confidence": avg_conf,
            "coverage": len(mapped) / total if total else 0.0,
        }

    def _predict_target_field(
        self,
        source: str,
        schema_keys: set,
    ) -> Optional[str]:
        """
        Predict target field name.

        1. Check synonym table (exact).
        2. Check synonym table (lowercased + underscored).
        3. Check if source is already a schema key.
        4. Return None (unmapped).

        In production, replace with embedding similarity against schema_keys.
        """
        # 1. Exact synonym lookup
        if source in self._synonyms:
            return self._synonyms[source]

        # 2. Normalised synonym lookup
        normalised = source.lower().replace(" ", "_").replace("-", "_")
        if normalised in self._synonyms:
            return self._synonyms[normalised]

        # 3. Direct schema key match
        if source in schema_keys:
            return source
        if normalised in schema_keys:
            return normalised

        return None

    def get_mapping_confidence(
        self,
        extracted_fields: List[Dict[str, Any]],
        target_schema: Dict[str, Any],
    ) -> float:
        result = self.map_fields(extracted_fields, target_schema)
        return float(result.get("confidence", 0.0))
