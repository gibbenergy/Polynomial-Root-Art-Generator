MPSolve Windows Solver Package (bin/)
====================================

Purpose
- This folder contains a Windows-native build of MPSolve and a thin C shim used by the app to solve univariate complex polynomials at high accuracy. It exists so the app can call a single, flat C function from Python/FFI without pulling in MPSolve’s full API.

Contents (what each file is)
- MPSolve.dll                  : The shim + entry point the app loads. Exports a flat C function for solving polynomials (see Interface below).
- libmps-3.dll                 : The MPSolve shared library (core numerical solver).
- libgmp-10.dll                : GNU Multiple Precision Arithmetic runtime.
- libgmpxx-4.dll               : C++ binding layer used by MPSolve.
- libmpfr-6.dll                : MPFR runtime (floating-point with correct rounding).
- libwinpthread-1.dll          : MinGW pthreads runtime.
- libstdc++-6.dll              : C++ standard library runtime (MinGW).
- libgcc_s_seh-1.dll           : GCC support runtime (structured exception handling).
- libMPSolve.dll.a (optional)  : Import library for linking from other C/C++ code (not required for Python/ctypes).

Interface (exported from MPSolve.dll)
- int mps_solve_monomial_complex(
    int n,
    const double* coeff_re,
    const double* coeff_im,
    int out_digits,
    double* roots_re,
    double* roots_im);

Concepts
- The polynomial is provided in monomial form p(x) = sum_{i=0..n} (coeff[i] * x^i).
- Inputs coeff_re/coeff_im have length n+1 (coeff for x^0 … x^n), outputs roots_re/roots_im have length at least n.
- The solver internally uses adaptive precision and returns n roots (including exact zeros where appropriate). The shim requests isolation of roots and will retry with higher precision once if needed.

How to load/use from Python (preferred)
- Use the provided helper: mps_adapter.py with roots_mpsolve(coeffs: numpy.ndarray, out_digits=80) -> numpy.ndarray (complex128).
- Ensure this bin/ directory is on the DLL search path.
  - PowerShell example:  $env:PATH = (Resolve-Path .\bin).Path + ";" + $env:PATH
  - Or in Python on Windows 10+: os.add_dll_directory(path_to_bin)
- Example (ctypes directly):
  1) Load: dll = ctypes.CDLL("./bin/MPSolve.dll")
  2) Prepare numpy float64 arrays for coeff_re/coeff_im and roots_re/roots_im
  3) Call mps_solve_monomial_complex with n = degree
  4) Combine roots as roots_re + 1j*roots_im

How to validate installation
- Dependency check: tools\check_deps.ps1 (verifies required DLLs and exported symbol).
- Full tests: run_all_tests.ps1 (installs NumPy if missing, runs unit tests and perf smoke).
- Individual Python tests are under tests/:
  - test_smoke.py (DLL loads)
  - test_known_polys.py (correctness on standard polynomials)
  - test_random_sets.py (randomized stress, residual checks)
  - test_multiprocessing.py (parallel runs)
  - perf_smoke.py (throughput; no strict threshold)

Licensing and packaging
- MPSolve is licensed under GPLv3+ (see upstream notices). 
- GMP and MPFR are (L)GPL; MinGW runtime DLLs are under their respective licenses.


Notes
- This build targets MSYS2 UCRT64 (Windows, x86_64). If you update MSYS2 or rebuild, re-run the test suite to confirm compatibility.
- For non-Python FFI (e.g., C/C++/Rust), link to MPSolve.dll (or use libMPSolve.dll.a) and pass contiguous double buffers as described above.

