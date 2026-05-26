"""
Built-in plugins — ready to use out of the box.

LLM Adapters::

    from pdf_autofillr_plugins.builtin.llm_adapters.noop_llm_adapter import NoOpLLMAdapter
    from pdf_autofillr_plugins.builtin.llm_adapters.litellm_adapter import LiteLLMAdapter

Extractors::

    from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
    from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin

Mappers::

    from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
    from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin

Validators::

    from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

Output Formatters::

    from pdf_autofillr_plugins.builtin.output_formatters.json_report_formatter import JSONReportFormatter
    from pdf_autofillr_plugins.builtin.output_formatters.passthrough_formatter import PassthroughFormatter

Data Connectors::

    from pdf_autofillr_plugins.builtin.data_connectors.dict_connector import DictConnector
    from pdf_autofillr_plugins.builtin.data_connectors.json_file_connector import JSONFileConnector
"""
