# Polynomial Root Art Generator

**Version 2.0**

In many scientific systems, parameters determine whether behavior is steady, oscillatory, or chaotic. Bifurcation theory studies these transitions by examining how parameters influence equilibria and their stability. It tracks how roots or eigenvalues shift as parameters change, revealing folds, oscillations, and pattern formation. Although bifurcation analysis is well established, its computational tools such as continuation and curve tracing are difficult to scale for large parameter spaces.

While earlier mathematical art such as fractals and polynomiography visualized iterative or self-similar processes, this platform takes a different approach. It generates images directly from the global structure of polynomial roots as parameters vary. The result is an art form based not on iteration or randomness, but on the geometry of algebraic change itself.

<table>
  <tr>
    <td><img src="asset/collagae.png" alt="Collage of generated art" width="100%"></td>
    <td><img src="asset/App.jpg" alt="Application Interface" width="100%"></td>
  </tr>
</table>

## What's New in Version 2.0 (October 2025)

Version 2.0 represents a major upgrade with two key improvements that transform the capabilities of the Polynomial Root Art Generator:

### 1. **High-Precision MPSolve Backend Integration**

**The Problem in v1:**
- Version 1 relied solely on NumPy's root-finding algorithm, which uses standard double-precision (64-bit) floating-point arithmetic
- For high-degree polynomials (degree > 20) or polynomials with roots very close together, numerical errors accumulate
- This limited the quality and complexity of artwork that could be generated

**The Solution in v2:**
- Integrated **MPSolve**, a robust polynomial root solver with arbitrary precision capabilities
- MPSolve uses adaptive multi-precision arithmetic (up to 200+ digits) via GMP and MPFR libraries
- Provides mathematically accurate roots even for extremely high-degree polynomials (degree 100+)

**Benefits:**
- **Higher Accuracy:** Get precise roots where NumPy would fail or produce artifacts
- **Larger Polynomials:** Generate art from degree-100+ polynomials with confidence
- **Better Quality:** Eliminate numerical noise and artifacts in the final artwork
- **User Choice:** Keep NumPy as the fast default; switch to MPSolve when precision matters
- **Configurable Precision:** Adjust output precision from 20 to 200 digits based on your needs

**Example Use Cases:**
- Research and educational applications requiring mathematical rigor
- Creating intricate patterns from polynomials with near-degenerate roots

### 2. **Revamped GUI: Sparse Coefficient Editor for Large Polynomials**

**The Problem in v1:**
- For a degree-N polynomial, v1 displayed N+1 input boxes (one for each coefficient x^N, x^(N-1), ..., x^1, x^0)
- This became impractical for large polynomials: a degree-50 polynomial would show 51 input boxes!
- Most interesting polynomials are **sparse** (only a few non-zero terms), but the old UI couldn't take advantage of this

**The Solution in v2:**
- Completely redesigned **Sparse Coefficient Editor**
- Only define the coefficients you actually need - no more scrolling through dozens of zeros
- Table-based interface shows only the non-zero terms you explicitly add

**Features:**
- **Define Only Non-Zero Terms:** Add rows for x^24, x^16, x^8, x^1, x^0 - skip everything else
- **Flexible Operations:**
  - Add/Remove individual rows
  - Duplicate rows for quick editing
  - Add ranges: e.g., "add k=10,20,30,40 all with coefficient P1"
  - Add sets: e.g., "add all even powers from 0 to 100"
  - Zero all except: quickly isolate specific terms
- **Live Validation:** Instant feedback on duplicate exponents, terms exceeding degree, or invalid expressions
- **Auto-Sort:** Terms automatically sort by exponent for clarity
- **Scalable:** Easily define degree-1000 polynomials with just a handful of terms

**Example:**
- **v1:** To define x^50 - 2x^25 + 1, you'd scroll through 51 input boxes, leaving 48 of them as zero
- **v2:** Just add 3 rows: {k:50, coeff:-1}, {k:25, coeff:-2}, {k:0, coeff:1}

**Result:** You can now explore polynomial families of any degree, making v2 suitable for research, education, and advanced generative art.

### 3. **License Change: MIT → GPLv3+**
- The project has transitioned from the MIT License to the GNU General Public License v3 or later (GPLv3+)
- This change was necessary due to the inclusion of MPSolve and its dependencies (GMP, MPFR), which are licensed under GPLv3+ and (L)GPL
- By distributing MPSolve binaries with the application, the combined work is subject to GPL obligations
- This ensures full legal compliance and allows users to freely use, modify, and redistribute the software while maintaining open-source principles

## Features

-   **Interactive Polynomial Definition:** Define polynomials of any degree and specify coefficients directly or as parameters.
-   **Complex Parameter Equations:** Use mathematical expressions involving complex numbers and variables (`t1`, `t2`) to define coefficients, allowing for dynamic and intricate structures.
-   **Multiple Sampling Domains:** Sample parameter variables from different domains like the unit circle, annuli, or line segments in the complex plane.
-   **High-Performance Computation:** Utilizes parallel processing to significantly speed up the root-finding calculations for a large number of samples.
-   **Advanced Visualization:**
    -   Multiple color palettes (Inferno, Plasma, Viridis, and more).
    -   Different rendering styles like 'Pure Pixel', 'Smooth Glow', and 'Smoky Bloom'.
    -   Adjustable contrast and black point to fine-tune the final image.
-   **Image Export:** Download the generated artwork as a high-resolution PNG file, with options to add a custom signature or the generating equation as a watermark.

## Getting Started

To run this project, you need a 64-bit Windows system.
### 1. Extract the repository correctly

After downloading the ZIP from GitHub, **extract it once only**.

> ⚠️ **Common mistake:**  
> Some archive tools create a nested folder structure like  
> `Polynomial-Root-Art-Generator-main/Polynomial-Root-Art-Generator-main/...`

If you see that duplication, move the **inner folder’s contents** up one level so that your directory looks like this:
``` text
Polynomial-Root-Art-Generator-main/
│
├── app.py
├── install.bat
├── start.bat
├── requirements.txt
├── asset/
├── backends/
└── ...
```

Make sure the file **install.bat** is directly inside the main project folder (not one level deeper).

### 2. Run the Installer (One-Time Setup)

First, run the `install.bat` script by double-clicking it.

```bash
.\install.bat
```

This will download and set up a self-contained Python environment in a local `miniconda3` folder. It will not affect your system's PATH or any other Python installations. You only need to do this once.

### 3. Start the Application

Once the installation is complete, run `start.bat` to launch the application.

```bash
.\start.bat
```

This will create the environment (if it's the first time), install all the necessary dependencies, and start the web server. It will also open the application in your default web browser.

## Optional: High-Precision MPSolve Backend

The app includes an optional Windows-native MPSolve backend for high-accuracy polynomial roots.

- DLLs are bundled under `bin/mpsolver/`. The adapter loads `MPSolve.dll` and required runtimes at startup.
- On first request, the server runs a smoke test (`x^3 - 1`) and logs: "MPSolve backend available and validated." if successful.

How to use:

- In the UI, under Computation Settings, set `Solver` to `MPSolve` and optionally adjust `MPSolve Digits`.
- Programmatically, send `solver: "mpsolve"` and `mps_out_digits: 80` in the POST body to `/api/generate-roots`.

Notes:

- NumPy remains the default solver for speed; MPSolve trades speed for precision.
- See `bin/mpsolver/readme.txt` for DLL details, dependencies, and licensing. Packaging MPSolve may impose GPL obligations.

## Usage

The application provides an intuitive 6-step workflow:

1. **Define Polynomial Structure** - Use the sparse editor to specify degree and non-zero coefficients
2. **Define Sampling Domains** - Choose geometric domains (Unit Circle, Annulus, Line Segment, etc.) for t1 and t2
3. **Define Parameters** - Create dynamic expressions using mathematical functions and variables
4. **Set Computation Settings** - Configure samples, solver (NumPy/MPSolve), resolution, and parallel processing
5. **Generate and Visualize** - Compute roots and apply visual effects (color palettes, render styles, contrast)
6. **Download** - Save high-resolution artwork with optional signature and equation overlay

**→ For detailed step-by-step instructions, examples, and tips, see the [User Guide](USER_GUIDE.md)**

## License

This project is licensed under the GNU General Public License v3 or later (GPLv3+). See the [`LICENSE`](LICENSE) file for details.

### Third-Party Components
This software includes:
- **MPSolve** (GPLv3+) - High-precision polynomial root solver
- **GMP** (LGPLv3+/GPLv2+) - GNU Multiple Precision Arithmetic Library
- **MPFR** (LGPLv3+) - Multiple Precision Floating-Point Library
- **MinGW-w64 Runtime** - Various GPL-compatible licenses

For detailed licensing information, see the LICENSE file.
