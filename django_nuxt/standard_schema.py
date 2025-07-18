from typing import Dict, Any

def convert_to_standard_schema_v1(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DRF action format to StandardSchemaV1 compatible format."""
        
    # Generate TypeScript-like type definition
    types = generate_types(fields)
        
    # Create validation function
    validate_function = create_validate_function(fields)
        
    # Build StandardSchemaV1 structure
    standard_schema = {
        "version": 1,
        "vendor": "django-rest-framework",
        "validate": validate_function,
        "types": types
    }
    
    return standard_schema
    
def generate_types(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Generate TypeScript-like type definitions from DRF fields."""
    input_type = {}
    output_type = {}
    
    for field_name, field_config in fields.items():
        field_type = map_drf_type_to_ts(field_config.get("type", "string"))
        
        # For input type, exclude read-only fields
        if not field_config.get("read_only", False):
            input_type[field_name] = field_type
        
        # For output type, include all fields
        output_type[field_name] = field_type
    
    return {
        "input": input_type,
        "output": output_type
    }

def map_drf_type_to_ts(drf_type: str) -> str:
    """Map DRF field types to TypeScript types."""
    type_mapping = {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "date": "string",  # ISO date string
        "datetime": "string",  # ISO datetime string
        "time": "string",  # ISO time string
        "email": "string",
        "url": "string",
        "file": "string",  # File path/URL
        "image": "string",  # Image path/URL
        "json": "unknown",
        "array": "unknown[]",
        "object": "Record<string, unknown>"
    }
    
    return type_mapping.get(drf_type, "unknown")

def create_validate_function(fields: Dict[str, Any]) -> str:
    """Create a JavaScript validation function as a string."""
    
    validation_rules = []
    field_validations = []
    
    for field_name, field_config in fields.items():
        field_type = field_config.get("type", "string")
        required = field_config.get("required", False)
        read_only = field_config.get("read_only", False)
        max_length = field_config.get("max_length")
        
        # Skip read-only fields for input validation
        if read_only:
            continue
        
        field_validation = f"""
        // Validate {field_name}
        if (!(value && typeof value === 'object' && '{field_name}' in value && value['{field_name}'] !== undefined && value['{field_name}'] !== null && value['{field_name}'] !== '')) {{
            if ({str(required).lower()}) {{
                issues.push({{ message: '{field_name} is required', path: ['{field_name}'] }});
            }}
        }} else {{
            const {field_name}Value = value['{field_name}'];
            {generate_field_validation(field_name, field_config)}
            {generate_field_common_validation(field_name, field_config)}
        }}"""
        
        field_validations.append(field_validation)
    
    validate_function = f"""
        const issues = [];
        
        if (!value || typeof value !== 'object') {{
            return {{ issues: [{{ message: 'Value must be an object' }}] }};
        }}
        
        {''.join(field_validations)}
        
        if (issues.length > 0) {{
            return {{ issues }};
        }}
        
        return {{ value }};
    """
    
    return validate_function

def generate_field_common_validation(field_name: str, field_config: Dict[str, Any]) -> str:
    """Generate common validation logic for a specific field."""
    validation_code = []

    validators = field_config.get("validators", [])
    if validators:
        for validator in validators:
            if validator.get("name") == "RegexValidator":
                validation_code.append(f"""
                    if (!(new RegExp('{validator.get("regex")}').test({field_name}Value))) {{
                        issues.push({{ message: '{validator.get("message")}', path: ['{field_name}'] }});
                    }}""")
    
    return ''.join(validation_code)

def generate_field_validation(field_name: str, field_config: Dict[str, Any]) -> str:
    """Generate validation logic for a specific field."""
    field_type = field_config.get("type", "string")
    max_length = field_config.get("max_length")
    
    validation_code = []
    
    # Type validation
    if field_type == "string":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'string') {{
                issues.push({{ message: '{field_name} must be a string', path: ['{field_name}'] }});
            }} else {{""")
        
        if max_length:
            validation_code.append(f"""
                if ({field_name}Value.length > {max_length}) {{
                    issues.push({{ message: '{field_name} must be at most {max_length} characters', path: ['{field_name}'] }});
                }}""")
        
        validation_code.append("}")
        
    elif field_type == "integer":
        validation_code.append(f"""
            if (!Number.isInteger({field_name}Value)) {{
                issues.push({{ message: '{field_name} must be an integer', path: ['{field_name}'] }});
            }}""")
        
    elif field_type == "number":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'number' || isNaN({field_name}Value)) {{
                issues.push({{ message: '{field_name} must be a number', path: ['{field_name}'] }});
            }}""")
        
    elif field_type == "boolean":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'boolean') {{
                issues.push({{ message: '{field_name} must be a boolean', path: ['{field_name}'] }});
            }}""")
        
    elif field_type == "date":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'string' || !/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test({field_name}Value)) {{
                issues.push({{ message: '{field_name} must be a valid date string (YYYY-MM-DD)', path: ['{field_name}'] }});
            }}""")
        
    elif field_type == "datetime":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'string' || isNaN(Date.parse({field_name}Value))) {{
                issues.push({{ message: '{field_name} must be a valid datetime string', path: ['{field_name}'] }});
            }}""")
        
    elif field_type == "email":
        validation_code.append(f"""
            if (typeof {field_name}Value !== 'string' || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test({field_name}Value)) {{
                issues.push({{ message: '{field_name} must be a valid email address', path: ['{field_name}'] }});
            }}""")
        
    else:
        # Default validation for unknown types
        validation_code.append(f"""
            // No specific validation for {field_name} (type: {field_type})""")
    
    return ''.join(validation_code)