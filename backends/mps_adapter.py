import os
import sys
from pathlib import Path
import ctypes
from ctypes import c_int, c_double, POINTER
import numpy as np


_DLL = None
_LOADED_ERROR = None


def _resolve_mpsolver_dir() -> Path:
    # Locate project root from this file and then bin/mpsolver
    here = Path(__file__).resolve()
    project_root = here.parent.parent
    return project_root / 'bin' / 'mpsolver'


def _add_dll_dir_win(path: Path) -> None:
    # Add directory to DLL search path on Windows 10+
    try:
        os.add_dll_directory(str(path))  # type: ignore[attr-defined]
    except Exception:
        # Fallback: prepend to PATH for older environments
        os.environ['PATH'] = str(path) + os.pathsep + os.environ.get('PATH', '')


def _load_dll() -> ctypes.CDLL:
    global _DLL, _LOADED_ERROR
    if _DLL is not None:
        return _DLL

    mps_dir = _resolve_mpsolver_dir()
    dll_path = mps_dir / 'MPSolve.dll'
    if not dll_path.exists():
        _LOADED_ERROR = FileNotFoundError(f"MPSolve.dll not found at {dll_path}")
        raise _LOADED_ERROR

    if sys.platform.startswith('win'):
        _add_dll_dir_win(mps_dir)

    try:
        dll = ctypes.CDLL(str(dll_path))
    except OSError as e:
        _LOADED_ERROR = e
        raise

    # Configure function signature
    solve_fn = getattr(dll, 'mps_solve_monomial_complex', None)
    if solve_fn is None:
        _LOADED_ERROR = RuntimeError('mps_solve_monomial_complex symbol not found in MPSolve.dll')
        raise _LOADED_ERROR

    solve_fn.argtypes = [
        c_int,                              # n
        POINTER(c_double),                  # coeff_re (len n+1)
        POINTER(c_double),                  # coeff_im (len n+1)
        c_int,                              # out_digits
        POINTER(c_double),                  # roots_re (len n)
        POINTER(c_double),                  # roots_im (len n)
    ]
    solve_fn.restype = c_int

    _DLL = dll
    return _DLL


def roots_mpsolve(coeffs: np.ndarray, out_digits: int = 80) -> np.ndarray:
    """
    Compute complex roots of a polynomial using MPSolve shim.

    Parameters
    - coeffs: 1D numpy array of complex128 or real64, length n+1.
              Accepts either descending (x^n..x^0) or ascending (x^0..x^n) order.
    - out_digits: target decimal digits of precision.

    Returns
    - numpy.ndarray of dtype complex128 with length n (roots).
    """
    if coeffs.ndim != 1:
        raise ValueError('coeffs must be a 1D array of length n+1')

    n_plus_1 = coeffs.shape[0]
    if n_plus_1 < 2:
        return np.array([], dtype=np.complex128)

    # Ensure complex128 type
    coeffs = np.asarray(coeffs, dtype=np.complex128)

    # Convert to ascending order for the shim
    # If already ascending, reversing twice is harmless for correctness of call preparation.
    coeffs_asc = coeffs[::-1]

    degree = n_plus_1 - 1
    coeff_re = np.ascontiguousarray(np.real(coeffs_asc), dtype=np.float64)
    coeff_im = np.ascontiguousarray(np.imag(coeffs_asc), dtype=np.float64)
    roots_re = np.empty(degree, dtype=np.float64)
    roots_im = np.empty(degree, dtype=np.float64)

    dll = _load_dll()
    solve_fn = dll.mps_solve_monomial_complex

    status = solve_fn(
        c_int(degree),
        coeff_re.ctypes.data_as(POINTER(c_double)),
        coeff_im.ctypes.data_as(POINTER(c_double)),
        c_int(int(out_digits)),
        roots_re.ctypes.data_as(POINTER(c_double)),
        roots_im.ctypes.data_as(POINTER(c_double)),
    )

    # Interpret status: expect number of roots == degree on success. Any other value indicates failure.
    if int(status) != degree:
        raise RuntimeError(f"MPSolve failed (status={int(status)}), expected {degree} roots")

    roots = roots_re.astype(np.float64) + 1j * roots_im.astype(np.float64)
    return roots.astype(np.complex128, copy=False)



