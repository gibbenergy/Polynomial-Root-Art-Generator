from sympy import symbols, Poly, I, chebyshevt, summation, pi, E, sin, cos, exp
from sympy.parsing.sympy_parser import parse_expr
from pydantic import BaseModel, Field
from typing import Literal, Optional
import numpy as np


# --- Pydantic Schemas for Template Specifications ---

class ParamSpec(BaseModel):
    """Base model for any parameter type."""
    template_type: str

class FreeformSpec(ParamSpec):
    template_type: Literal['freeform'] = 'freeform'
    definition: str

class InputVariableTemplateSpec(ParamSpec):
    """Base model for templates that require an input variable like t1 or t2."""
    input_variable: Literal['t1', 't2']

class AlternatingGeometricSpec(InputVariableTemplateSpec):
    template_type: Literal['alternating_geometric'] = 'alternating_geometric'
    amplitude: str = "1.0"
    k: int = 10

class ChebyshevSpec(InputVariableTemplateSpec):
    template_type: Literal['chebyshev'] = 'chebyshev'
    n: int = 12


# --- Generator Implementations ---

class BasePolynomialGenerator:
    def __init__(self, spec, rng):
        self.spec = spec
        self.rng = rng

    def get_expression(self, var):
        """Returns a symbolic SymPy expression in terms of `var`."""
        raise NotImplementedError

class FreeformGenerator(BasePolynomialGenerator):
    def get_expression(self, var):
        # Freeform expressions are parsed directly in the main app
        raise NotImplementedError("Freeform is handled by the main app.")

class AlternatingGeometricGenerator(BasePolynomialGenerator):
    def get_expression(self, var):
        # Parse the amplitude string into a SymPy expression
        math_env = {
            'I': I,
            'pi': pi,
            'E': E,
            'sin': sin,
            'cos': cos,
            'exp': exp
        }
        A1 = parse_expr(self.spec.amplitude, local_dict=math_env)
        k = self.spec.k
        i = symbols('i', integer=True)
        # Summation: A1 * Sum_{i=0 to k} [(-1)^i * x^(k-i)]
        return A1 * summation(((-1)**i) * var**(k - i), (i, 0, k))

class ChebyshevGenerator(BasePolynomialGenerator):
    def get_expression(self, var):
        n = self.spec.n
        # Returns the Chebyshev polynomial T_n(var)
        return chebyshevt(n, var)


# --- Factory Function ---
def get_polynomial_generator(spec: dict, rng):
    """Factory function to get the correct generator class from a spec dictionary."""
    cls_map = {
        'freeform': (FreeformGenerator, FreeformSpec),
        'alternating_geometric': (AlternatingGeometricGenerator, AlternatingGeometricSpec),
        'chebyshev': (ChebyshevGenerator, ChebyshevSpec),
    }
    
    template_type = spec.get('type') 
    if template_type not in cls_map:
        raise ValueError(f"Unknown template type: {template_type}")
    
    # Restore proper Pydantic validation
    GenClass, SpecClass = cls_map[template_type]
    
    spec_for_validation = spec.copy()
    spec_for_validation['template_type'] = spec_for_validation.pop('type')
    
    validated_spec = SpecClass(**spec_for_validation)
    return GenClass(validated_spec, rng)
