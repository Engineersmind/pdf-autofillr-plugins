"""
Full extract → map → validate pipeline using built-in plugins.
"""
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

raw_fields = [
    {"name": "investor_name",  "value": "Jane Smith",       "confidence": 0.99},
    {"name": "email_address",  "value": "jane@example.com", "confidence": 0.98},
    {"name": "commitment_usd", "value": "500000",           "confidence": 0.95},
]
schema = {"investor_name": "string", "email_address": "string", "commitment_usd": "string"}

# 1. Extract
extractor = PassthroughExtractorPlugin(config={"fields": raw_fields})
extractor.initialize()
extraction = extractor.extract("blank_form.pdf")
print(f"Extracted {len(extraction['fields'])} fields")

# 2. Map
manager = PluginManager()
manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")

mapper = manager.load_plugin("identity-mapper", "mapper")
mapping = mapper.map_fields(extraction["fields"], schema)
print(f"Coverage: {mapping['coverage']:.0%}")

# 3. Validate email
validator = manager.load_plugin("email-validator", "validator")
result = validator.validate("email_address", mapping["mapped_fields"]["email_address"])
print(f"Email valid: {result['valid']}")

manager.shutdown()
