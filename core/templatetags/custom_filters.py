from django import template
import re

register = template.Library()

@register.filter(name='indian_currency')
def indian_currency(value):
    try:
        # Convert value to string and split into integer and decimal parts
        s = str(float(value))
        integer_part, decimal_part = (s.split('.') + ['00'])[:2]
        decimal_part = decimal_part[:2].ljust(2, '0')

        # Format the integer part with Indian commas
        integer_part = re.sub(r'(\d)(?=(\d\d)+\d$)', r'\1,', integer_part)

        return f"₹{integer_part}.{decimal_part}"
    except (ValueError, TypeError):
        return value