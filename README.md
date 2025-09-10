# Polynomial Root Art Generator

In the generative AI field today, users typically enter a text prompt describing what they want to draw into platforms like Automatic1111 or ComfyUI, running models such as Qwen, Flux, and SDXL. The results can be impressive.

But as a researcher, I think of math equations as a universal language. Equations already capture simplified versions of reality without needing verbose descriptions. I asked myself: what if we could feed an equation into a platform and generate art from it?

To achieve this, I developed this platform that takes equations as input and produces visual art. For the first step, I chose polynomials, simple yet powerful, and explored their root distributions. This has practical value in areas like control theory and signal processing, supports education, and also opens new doors in generative art.

<table>
  <tr>
    <td><img src="asset/collagae.png" alt="Collage of generated art" width="100%"></td>
    <td><img src="asset/App.jpg" alt="Application Interface" width="100%"></td>
  </tr>
</table>

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

### 1. Run the Installer (One-Time Setup)

First, run the `install.bat` script by double-clicking it.

```bash
.\install.bat
```

This will download and set up a self-contained Python environment in a local `miniconda3` folder. It will not affect your system's PATH or any other Python installations. You only need to do this once.

### 2. Start the Application

Once the installation is complete, run `start.bat` to launch the application.

```bash
.\start.bat
```

This will create the environment (if it's the first time), install all the necessary dependencies, and start the web server. It will also open the application in your default web browser.

## How to Use the Generator

1.  **Define Polynomial Structure:**
    -   Set the desired **degree** of the polynomial.
    -   Fill in the **coefficients** for each power of `x`. You can use constants (e.g., `-1`, `2.5`) or refer to parameters (e.g., `P1`, `P2`).

2.  **Define Sampling Domains:**
    -   Choose the geometric domain (e.g., Unit Circle, Line Segment) from which the variables `t1` and `t2` will be randomly sampled.

3.  **Define Parameters:**
    -   Add named parameters (like `P1`) that were used in the coefficient fields.
    -   Define their value as a mathematical expression. These expressions can use the sampled variables `t1` and `t2`, complex numbers (`I` for the imaginary unit), and standard mathematical functions (`exp`, `sin`, etc.).

4.  **Set Computation Settings:**
    -   **Samples:** The number of `(t1, t2)` pairs to sample. More samples lead to a higher quality image but take longer to compute.
    -   **Seed:** A random seed for reproducibility.
    -   **Parallel Processing:** Enable this to use multiple CPU cores and speed up the computation.

5.  **Generate and Visualize:**
    -   Click the **Generate Roots** button. The backend will compute the roots for all sampled parameter sets.
    -   Once computed, you can select different **Color Palettes** and **Render Styles** to change the artwork's appearance.
    -   Click **Apply Visual Effects** to see your changes.

6.  **Download:**
    -   Use the **Download Image** button to save your creation. You can also add a signature or the equation to the image before downloading.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.
