# User Guide - Polynomial Root Art Generator

This guide walks you through the process of creating mathematical artwork using the Polynomial Root Art Generator.

## Quick Start Workflow

The basic workflow consists of 6 steps:
1. Define Polynomial Structure
2. Define Sampling Domains
3. Define Parameters
4. Set Computation Settings
5. Generate and Visualize
6. Download Your Artwork

## Step-by-Step Instructions

### 1. Define Polynomial Structure

**Set the Degree:**
- Enter the maximum degree `N` of your polynomial in the **Degree** field
- Click **Set** to activate the coefficient editor
- Example: For a degree-24 polynomial, enter `24`

**Define Coefficients (Sparse Editor):**
- The sparse editor allows you to define only the non-zero coefficients
- Click **Add Row** to add a new term
- For each row, specify:
  - **Exponent k:** The power of x (e.g., 24, 16, 8, 1, 0)
  - **Coefficient:** A constant (e.g., `-1`, `2.5`) or parameter reference (e.g., `P1`, `P2`)
  - **Notes:** Optional description for your reference

**Advanced Operations:**
- **Duplicate:** Select a row and click **Duplicate** to copy it
- **Remove:** Select rows and click **Remove** to delete them
- **Add Range:** Bulk add multiple exponents with the same coefficient
  - Example: Enter `10, 50, 10, P1` to add k=10, 20, 30, 40, 50 all with coefficient P1
- **Add Set:** Add specific exponents from a list
  - Example: Enter `5 10 15 20` for exponents, then specify the coefficient
- **Zero All Except:** Keep only specific terms and remove all others
- **Clear All:** Remove all rows and start fresh

**Tips:**
- Rows automatically sort by exponent (highest to lowest)
- Validation highlights errors (duplicate exponents, k > degree, etc.)
- You can paste CSV/TSV data with columns: k, coeff, notes

### 2. Define Sampling Domains

Choose the geometric domain from which variables `t1` and `t2` will be sampled:

**Available Domain Types:**

**Unit Circle:**
- Samples points uniformly distributed around the unit circle in the complex plane
- Points have the form: e^(iθ) where θ is uniform in [0, 2π]

**Annulus (Ring):**
- Samples points in a ring-shaped region between two radii
- Parameters:
  - **Min Radius:** Inner radius (e.g., 0.5)
  - **Max Radius:** Outer radius (e.g., 1.0)

**Uniform Disk:**
- Samples points uniformly inside a disk
- Parameter:
  - **Max Radius:** Radius of the disk (e.g., 1.0)

**Line Segment:**
- Samples points uniformly along a line segment in the complex plane
- Parameters:
  - **Start:** Starting point as (real, imag), e.g., `-1, 0`
  - **End:** Ending point as (real, imag), e.g., `1, 0`

**Domain Configuration:**
- Configure separate domains for `t1` and `t2`
- Different domain combinations create different artistic patterns

### 3. Define Parameters

Parameters allow you to create dynamic coefficient expressions that depend on the sampled variables.

**Add a Parameter:**
1. Click **Add Parameter**
2. Enter a **name** (e.g., `P1`, `P2`, `C`)
3. Choose a **type**:
   - **Freeform:** Write any mathematical expression
   - **Alternating Geometric:** Pre-built template for alternating geometric series
   - **Chebyshev:** Pre-built template for Chebyshev polynomials

**Freeform Expressions:**
- Write expressions using `t1` and `t2`
- Use standard math functions: `exp()`, `sin()`, `cos()`, `tan()`, `log()`, `sqrt()`
- Use `I` for the imaginary unit (√-1)
- Examples:
  - `100*exp(I*t1)**5 - 100*exp(I*t2)**4`
  - `t1**2 + t2**2`
  - `sin(t1) + cos(t2)`
  - `(t1 + t2) / 2`

**Template-Based Parameters:**

*Alternating Geometric:*
- Creates an alternating geometric series polynomial
- Parameters:
  - **Input Variable:** Choose `t1` or `t2`
  - **Amplitude (A1):** Coefficient magnitude
  - **Degree (k):** Polynomial degree

*Chebyshev:*
- Creates a Chebyshev polynomial
- Parameters:
  - **Input Variable:** Choose `t1` or `t2`
  - **Degree (n):** Chebyshev polynomial degree

**Using Parameters:**
- Reference parameters in the coefficient editor (e.g., use `P1` in a coefficient field)
- Parameters are evaluated for each sampled (t1, t2) pair
- This creates families of polynomials rather than a single polynomial

### 4. Set Computation Settings

**Samples:**
- Number of (t1, t2) pairs to generate
- More samples = higher quality image, longer computation time
- Recommended: 20,000 - 200,000
- Default: 200,000

**Seed:**
- Random seed for reproducibility
- Use the same seed to regenerate identical artwork
- Change the seed to explore variations

**Grid Resolution:**
- Output image resolution
- Options: 1080x1080 (HD), 2048x2048 (2K), 4096x4096 (4K)
- Higher resolution = better quality, larger file size

**Solver:**
- **NumPy (default):** Fast, standard double-precision
  - Best for: Most use cases, degrees < 50, quick iterations
- **MPSolve:** Slow, arbitrary high-precision (20-200 digits)
  - Best for: High degrees (50+), near-degenerate roots, research

**MPSolve Digits:**
- Output precision when using MPSolve solver
- Range: 20 to 200 digits
- Default: 80 digits
- Higher precision = slower computation

**Parallel Processing:**
- **Enable:** Uses multiple CPU cores for faster computation
- **Number of Cores:** Adjust the slider to control how many cores to use
  - Default: 1/4 of available cores
  - More cores = faster computation (with diminishing returns)
  - Leave some cores free for system responsiveness

### 5. Generate and Visualize

**Generate Roots:**
1. Click **Generate Roots** button
2. Wait for the computation to complete
   - Progress shown in status area
   - Timing breakdown displayed after completion
3. The initial visualization appears automatically

**Visual Effects:**
- **Color Palette:** Choose from 8 different color schemes
  - Inferno (default): Black → Purple → Orange → Yellow
  - Plasma: Dark Blue → Purple → Pink → Yellow
  - Viridis: Dark Purple → Green → Yellow
  - Cool Nebula: Blue → Cyan → White
  - Fire Gradient: Black → Red → Orange → Yellow
  - Ocean Depths: Dark Blue → Cyan → White
  - Emerald Dream: Dark Green → Bright Green
  - Sunset Glow: Purple → Orange → Yellow

- **Render Style:**
  - Pure Pixel: Sharp, crisp rendering
  - Smooth Glow (default): Soft, glowing appearance
  - Smoky Bloom: Ethereal, layered bloom effect

- **Contrast Boost:** Amplifies intensity differences
  - Normal: 1.0x
  - High: 2.0x (default)
  - Extreme: 3.0x
  - Maximum: 5.0x

- **Black Point:** Suppresses low-density regions
  - None: 0.0 (show everything)
  - Light: 0.1
  - Medium: 0.2
  - High: 0.3 (default)
  - Extreme: 0.5
  - Maximum: 0.7

**Applying Changes:**
- Adjust any visualization settings
- Click **Apply Visual Effects** to see the updated artwork
- Experiment with different combinations to find your preferred style

### 6. Download Your Artwork

**Customize Output:**
- **Signature/Watermark:** Enter text to add to the bottom-right corner
  - Check "Add signature to image" to enable
  - Example: Your name, date, or caption

- **Equation Info:** Display the polynomial and parameters on the image
  - Check "Add equation info to image" to enable
  - Shows: polynomial structure, domains, parameter definitions
  - Appears in top-left corner

**Download:**
1. Configure signature/equation options (optional)
2. Click **Download Image** button
3. Image saves as `polynomial_art.png` in your default download folder
4. Resolution matches your selected Grid Resolution setting

## Tips and Tricks

### For Beautiful Artwork:
- Start with the default template and modify incrementally
- Use Unit Circle or Annulus domains for symmetric patterns
- Combine exponential expressions with trigonometry for intricate detail
- Try high contrast boost + high black point for dramatic effect

### For Research/Education:
- Use MPSolve solver for mathematical accuracy
- Add equation info to image for documentation
- Use consistent seeds for reproducible results
- Start with lower sample counts (20k-50k) for faster iteration

### For High-Degree Polynomials:
- Use sparse editor to define only essential terms
- Enable parallel processing with maximum cores
- Consider MPSolve for degrees > 50
- Use "Add Range" or "Add Set" for regular patterns (e.g., all even powers)

### Performance Optimization:
- Lower samples for initial experiments, increase for final render
- Use NumPy solver for fast iteration, switch to MPSolve when needed
- Adjust grid resolution based on usage (1080 for web, 4K for print)
- More CPU cores helps significantly with large sample counts

## Troubleshooting

**"No valid roots found" error:**
- Check that your polynomial coefficients are valid expressions
- Verify parameter definitions are correct
- Ensure parameters used in coefficients are actually defined

**Computation is very slow:**
- Reduce number of samples
- Use NumPy instead of MPSolve
- Lower the degree of your polynomial
- Disable parallel processing if you have few CPU cores

**Image appears blank or very dark:**
- Lower the black point setting
- Decrease contrast boost
- Increase number of samples
- Try a different render style

**Validation errors in coefficient editor:**
- Check for duplicate exponents (same k value used twice)
- Ensure no exponent exceeds the polynomial degree
- Verify coefficient expressions reference defined parameters

## Examples

### Example 1: Simple Symmetric Pattern
```
Degree: 24
Coefficients:
  - x^24: -1
  - x^16: P1
  - x^8: P2
  - x^1: 1
  - x^0: -1

Parameters:
  - P1: 100*exp(I*t1)**5 - 100*exp(I*t2)**4
  - P2: 100*exp(I*t2)**5 - 100*exp(I*t1)**4

Domains: Unit Circle for both t1 and t2
Samples: 200,000
```

### Example 2: High-Degree Sparse Polynomial
```
Degree: 100
Coefficients:
  - x^100: 1
  - x^50: -P1
  - x^25: P2
  - x^0: -1

Parameters:
  - P1: t1**2
  - P2: t2**2

Domains: Line Segment [-1,0] to [1,0] for both
Samples: 100,000
Solver: MPSolve (80 digits)
```

### Example 3: Chebyshev Exploration
```
Degree: 50
Coefficients:
  - x^50: 1
  - x^25: P1
  - x^0: -1

Parameters:
  - P1: Type = Chebyshev, n=12, var=t1

Domains: Unit Circle for both
Samples: 150,000
```

## Further Information

- **Backend Details:** See `bin/mpsolver/readme.txt` for MPSolve technical information
- **License:** See `LICENSE` file for GPLv3+ licensing details
- **Support:** For issues, refer to the main README.md

---

Happy art generation! Experiment, explore, and create something beautiful from mathematics.

