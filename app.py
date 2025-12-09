from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np
import io
import time
import concurrent.futures
import multiprocessing
from sympy import symbols, Poly, I, lambdify
from sympy.parsing.sympy_parser import parse_expr

from domains.samplers import get_sampler
from polynomial_templates.generators import get_polynomial_generator

app = Flask(__name__)

def find_roots_for_chunk_numpy(coeffs_chunk):
    """Find roots for a 2D array (chunk) using NumPy."""
    return [np.roots(coeffs) for coeffs in coeffs_chunk]

def find_roots_for_chunk_mps(coeffs_chunk, out_digits=80):
    """Find roots for a 2D array (chunk) using MPSolve backend."""
    from backends.mps_adapter import roots_mpsolve
    results = []
    for coeffs in coeffs_chunk:
        try:
            results.append(roots_mpsolve(coeffs, out_digits=out_digits))
        except Exception:
            results.append(np.array([]))
    return results

def find_roots_parallel(coeffs_batch, max_workers=6, solver='numpy', mps_out_digits=80):
    """Find roots for a batch of coefficient arrays using batched parallel processing."""
    # Split the entire batch of coefficients into chunks for each worker
    chunks = np.array_split(coeffs_batch, max_workers)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {}
        for i, chunk in enumerate(chunks):
            if solver == 'mpsolve':
                future = executor.submit(find_roots_for_chunk_mps, chunk, mps_out_digits)
            else:
                future = executor.submit(find_roots_for_chunk_numpy, chunk)
            future_to_chunk[future] = i

        # Collect results in order
        results_in_chunks = [None] * len(chunks)
        for future in concurrent.futures.as_completed(future_to_chunk):
            index = future_to_chunk[future]
            try:
                results_in_chunks[index] = future.result()
            except Exception as exc:
                print(f'Chunk {index} failed: {exc}')
                results_in_chunks[index] = [] # Handle failure of a whole chunk

        # Flatten the list of lists into a single list of root arrays
        return [root for chunk_result in results_in_chunks for root in chunk_result]

# --- Art Generation Logic (Returns Raw Root Data) ---
def generate_root_coordinates(payload):
    """Calculates all roots and returns their raw coordinates."""
    
    start_time = time.time()
    
    # --- Unpack Payload ---
    degree = payload.get('degree', 0)
    terms_list = payload.get('terms', [])
    params_def = payload.get('params', {})
    n_pairs = int(payload.get('n_pairs', 20000)) 
    seed = int(payload.get('seed', 7))
    grid_size = int(payload.get('grid_resolution', 1080))  # User-selectable resolution
    use_parallel = payload.get('use_parallel', True)
    solver_choice = str(payload.get('solver', 'numpy')).lower()
    mps_out_digits = int(payload.get('mps_out_digits', 80))
    
    # Calculate max_workers based on system's cores
    default_workers = max(1, multiprocessing.cpu_count() // 4)
    max_workers = int(payload.get('max_workers', default_workers))
    rng = np.random.default_rng(seed) 

    # --- Domain-Based Sampling ---
    try:
        t1_spec = payload.get('t1_domain', {'domain_type': 'unit_circle'})
        t2_spec = payload.get('t2_domain', {'domain_type': 'unit_circle'})

        # Update both specs with the required server-side values
        t1_spec.update({'n_samples': n_pairs, 'seed': seed})
        t2_spec.update({'n_samples': n_pairs, 'seed': seed + 1 if seed is not None else None})

        t1_sampler = get_sampler(t1_spec)
        t2_sampler = get_sampler(t2_spec)

        t1_complex = t1_sampler.sample()
        t2_complex = t2_sampler.sample()
        
    except Exception as e:
        return {'error': f"Domain sampling error: {e}"}

    # --- Sympy Parsing and Compilation ---
    sympy_start = time.time()
    x, t1_sym, t2_sym = symbols('x t1 t2')
    
    try:
        # --- Build Parameter Expressions ---
        param_symbols = {name: symbols(name) for name in params_def.keys()}
        
        # Lambdify parameter definitions
        param_funcs = {}
        for name, spec in params_def.items():
            param_type = spec.get('type')
            
            if param_type == 'freeform':
                expr_str = spec.get('definition', '0')
                expr = parse_expr(expr_str, local_dict={'t1': t1_sym, 't2': t2_sym, 'I': I})
                param_funcs[name] = lambdify([t1_sym, t2_sym], expr, 'numpy')
            else:
                generator = get_polynomial_generator(spec, rng)
                input_var_str = spec.get('input_variable', 't1')
                input_sym = t1_sym if input_var_str == 't1' else t2_sym
                expr = generator.get_expression(input_sym)
                # This parameter only depends on one variable
                param_funcs[name] = lambdify(input_sym, expr, 'numpy')

        # --- Lambdify Main Polynomial Coefficients (Sparse Terms) ---
        # Validate and parse sparse terms: [{k, coeff, note?}]
        coeff_exprs = {}
        seen_exponents = set()
        for term in terms_list:
            try:
                k = int(term.get('k'))
            except Exception:
                return {'error': 'Invalid exponent k in terms.'}
            if k > degree:
                return {'error': 'Exponent k is higher than maximum degree N. Please fix it.'}
            if k in seen_exponents:
                return {'error': 'Exponent k is already defined. Please fix it.'}
            seen_exponents.add(k)
            coeff_str = str(term.get('coeff', '0'))
            if not coeff_str.strip():
                continue
            coeff_exprs[k] = parse_expr(coeff_str, local_dict=param_symbols)

        ordered_param_symbols = list(param_symbols.values())
        
        # Create a single function that calculates all coefficients at once
        # This is more efficient than calling one function per coefficient
        all_coeffs_expr = [coeff_exprs.get(i, 0) for i in range(degree, -1, -1)]
        coeff_calculator = lambdify(ordered_param_symbols, all_coeffs_expr, 'numpy')

    except Exception as e:
        return {'error': str(e)}

    sympy_time = time.time() - sympy_start
    print(f"SymPy parsing & compilation: {sympy_time:.3f}s")

    # --- Single-Pass Coefficient Calculation, Root Finding, and Post-processing ---
    vector_time = 0
    roots_time = 0
    post_time = 0

    # Vectorized coefficient calculation
    vector_start = time.time()
    
    # 1. Calculate numeric values for all parameters
    param_values = {}
    for name, func in param_funcs.items():
        # Check if the function takes one (t1 or t2) or two arguments
        sig = list(func.__code__.co_varnames)
        if 't1' in sig and 't2' in sig:
             param_values[name] = func(t1_complex, t2_complex)
        elif 't1' in sig:
             param_values[name] = func(t1_complex)
        else: # Must be t2
             param_values[name] = func(t2_complex)

    # 2. Use numeric parameter values to calculate final coefficients
    ordered_param_values = [param_values[name] for name in param_symbols.keys()]
    calculated_coeffs = coeff_calculator(*ordered_param_values)
    
    uniform_coeffs = []
    for c in calculated_coeffs:
        if np.isscalar(c):
            uniform_coeffs.append(np.full(n_pairs, c, dtype=np.complex128))
        else:
            uniform_coeffs.append(c)
    
    all_coeffs = np.array(uniform_coeffs).T
    vector_time = time.time() - vector_start

    # Root Finding
    roots_start = time.time()
    if use_parallel and max_workers > 1:
        all_roots = find_roots_parallel(all_coeffs, max_workers, solver_choice, mps_out_digits)
    else:
        all_roots = []
        for j in range(n_pairs):
            try:
                if solver_choice == 'mpsolve':
                    from backends.mps_adapter import roots_mpsolve
                    all_roots.append(roots_mpsolve(all_coeffs[j, :], out_digits=mps_out_digits))
                else:
                    all_roots.append(np.roots(all_coeffs[j, :]))
            except Exception:
                all_roots.append(np.array([]))
    roots_time = time.time() - roots_start
    
    # Post-processing
    post_start = time.time()
    valid_roots = [r for r in all_roots if r.size > 0]
    
    if not valid_roots:
        return {'error': 'No valid roots found.'}
        
    roots_flat = np.concatenate(valid_roots)
    x_coords = np.real(roots_flat)
    y_coords = np.imag(roots_flat)
    
    mask = np.isfinite(x_coords) & np.isfinite(y_coords)
    x_coords = x_coords[mask]
    y_coords = y_coords[mask]
    post_time = time.time() - post_start

    print(f"Vectorized coefficient calculation: {vector_time:.3f}s")
    backend_name = f"MPSolve" if solver_choice == 'mpsolve' else 'NumPy'
    print(f"Root finding ({n_pairs} pairs, {'parallel' if use_parallel and max_workers > 1 else 'sequential'}) [{backend_name}]: {roots_time:.3f}s")
    print(f"Root finding per pair: {roots_time/n_pairs*1000:.2f}ms")
    print(f"Post-processing: {post_time:.3f}s")

    # --- High-Resolution Density Grid on Backend (Fast NumPy) ---
    grid_start = time.time()
    # Calculate bounds for auto-zoom
    xlo, xhi = np.quantile(x_coords, [0.005, 0.995])
    ylo, yhi = np.quantile(y_coords, [0.005, 0.995])
    
    # Add small padding
    x_range = xhi - xlo
    y_range = yhi - ylo
    padding = 0.05
    
    xlo -= x_range * padding
    xhi += x_range * padding
    ylo -= y_range * padding
    yhi += y_range * padding
    
    # Make bounds square for proper aspect ratio
    max_range = max(x_range, y_range) * (1 + 2 * padding)
    x_center = (xlo + xhi) / 2
    y_center = (ylo + yhi) / 2
    
    xlo = x_center - max_range / 2
    xhi = x_center + max_range / 2
    ylo = y_center - max_range / 2
    yhi = y_center + max_range / 2
    
    # Create density grid using user-selected resolution
    density_grid, x_edges, y_edges = np.histogram2d(
        x_coords, y_coords, 
        bins=grid_size, 
        range=[[xlo, xhi], [ylo, yhi]]
    )
    
    # Apply log scaling for better visualization
    density_grid = np.log1p(density_grid)  # log(1 + x) to handle zeros
    
    # Normalize to 0-1 range
    if density_grid.max() > 0:
        density_grid = density_grid / density_grid.max()
    
    # Convert to list for JSON serialization (transpose for correct orientation)
    density_list = density_grid.T.tolist()
    grid_time = time.time() - grid_start
    print(f"Grid creation ({grid_size}x{grid_size}): {grid_time:.3f}s")

    total_time = time.time() - start_time
    print(f"=== TOTAL TIME: {total_time:.3f}s ===")
    print(f"Root finding: {roots_time/total_time*100:.1f}% of total time")

    return {
        'density_grid': density_list,
        'grid_size': grid_size,
        'bounds': {'x_min': xlo, 'x_max': xhi, 'y_min': ylo, 'y_max': yhi},
        'total_roots': len(x_coords),
        'timing': {
            'total': total_time,
            'sympy': sympy_time,
            'vector': vector_time,
            'roots': roots_time,
            'post': post_time,
            'grid': grid_time
        }
    }

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/asset/<path:filename>')
def serve_asset(filename):
    """Serve files from the asset folder."""
    return send_from_directory('asset', filename)

@app.route('/api/generate-roots', methods=['POST'])
def generate_api():
    payload = request.json
    root_data = generate_root_coordinates(payload)
    return jsonify(root_data)

@app.route('/api/system-info', methods=['GET'])
def system_info():
    """Return system information including max CPU cores."""
    return jsonify({
        'max_cores': multiprocessing.cpu_count(),
        'platform': multiprocessing.get_start_method()
    })

# Preset management routes
@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get all saved presets."""
    # In a production app, this would read from a database
    # For now, this is handled client-side with localStorage
    return jsonify({'presets': []})

@app.route('/api/presets', methods=['POST'])
def save_preset():
    """Save a new preset."""
    # In a production app, this would save to a database
    preset = request.json
    return jsonify({'success': True, 'message': 'Preset saved'})

@app.route('/api/presets/<preset_id>', methods=['GET'])
def get_preset(preset_id):
    """Get a specific preset."""
    # In a production app, this would query a database
    return jsonify({'preset': {}})


_mps_smoke_done = False

# --- Optional MPSolve Smoke Test (runs once on first request) ---
@app.before_request
def _mpsolve_smoke_once():
    global _mps_smoke_done
    if _mps_smoke_done:
        return
    try:
        from backends.mps_adapter import roots_mpsolve
        coeffs_desc = np.array([1.0, 0.0, 0.0, -1.0], dtype=np.complex128)  # x^3 - 1
        roots = roots_mpsolve(coeffs_desc, out_digits=80)
        if roots.size == 3:
            resid = np.max(np.abs(roots**3 - 1.0))
            if resid < 1e-8:
                print('MPSolve backend available and validated.')
            else:
                print(f'MPSolve validation residual too high: {resid}')
        else:
            print(f'MPSolve validation failed: expected 3 roots, got {roots.size}')
    except Exception as e:
        print(f'MPSolve backend not available: {e}')
    finally:
        _mps_smoke_done = True

if __name__ == '__main__':
    app.run(debug=True)
