# 🧪 Pyk’n’Fit

## General Overview

**Pyk’n’Fit** is a scientific Python application with a graphical interface (Tkinter) dedicated to the **multimodal decomposition of particle size distributions** using **Gaussian mixture models** in the **φ (phi) scale**.

The software is designed for advanced granulometric analyses in fields such as:

* sedimentology
* geology
* environmental sciences
* material sciences
* particle population studies

Pyk’n’Fit allows:

* import of experimental datasets (Excel / CSV)
* interactive data visualization
* manual selection of population centers
* automatic Gaussian mixture fitting
* computation of statistical quality indicators
* complete export of numerical and graphical results

---

## 🧠 Scientific Background

Particle size data are commonly expressed using the phi (φ) scale:

φ = − log₂(d / 1000)

where:
- d is the particle diameter in micrometers (µm)

The measured distribution is modeled as a sum of Gaussian functions:

f(x) = Σ Ai · exp( − (x − μi)² / (2 σi²) )

Each Gaussian component represents a distinct granulometric population.

---

## 🖥️ Main Features

### ✔ Data Import

* Supported formats:

  * `.xlsx`, `.xls`
  * `.csv` (semicolon or tab separator)
* Automatic decimal conversion (comma / dot)
* Dynamic sample selection from file columns

### ✔ Interactive Interface

* Tkinter-based GUI
* Multilingual support (🇫🇷 French / 🇬🇧 English)
* Manual data entry or file-based workflow
* Automatic inversion of the φ axis

### ✔ Interactive Selection of Gaussian Centers

* **Left click** → add a Gaussian center
* **Right click** → contextual menu:

  * edit σ (standard deviation)
  * edit amplitude A
  * delete component

All parameters are displayed and editable directly on the plot.

### ✔ Model Fitting

* Automatic construction of multi-Gaussian models
* Non-linear optimization using `lmfit`
* Physical constraints applied:

  * σ ≥ σ_min
* Robust convergence for multimodal signals

### ✔ Computed Results

For each component:

* center in φ
* center in µm
* σ (dispersion)
* normalized amplitude
* surface proportion (%)

For the global model:

* absolute error
* relative error (%)
* Mean Squared Error (MSE)
* coefficient of determination (R²)

---

## 📊 Visualization

Two main figures are generated:

1. **Experimental data view**

   * raw distribution
   * interactive selection of centers

2. **Multimodal decomposition view**

   * global fitted curve
   * individual Gaussian components
   * percentage contribution of each population
   * embedded parameter summary table

---

## 💾 Export Capabilities

### Graphs

* PNG
* JPG
* SVG

### Decomposition Results (Excel)

Exported table includes:

* sample name
* computation date
* component index
* center (µm)
* center (φ)
* σ
* amplitude
* proportion
* error metrics

### Gaussian Sampled Points (Excel)

* φ coordinates
* µm coordinates
* global fitted curve
* each Gaussian component

Sampling density is user-defined (50 → 50,000 points).

---

## 📁 Project Structure

```
PyknFit/
│
├── main.py                     # Application entry point
├── app.py                      # Core application controller
│
├── ui.py                       # GUI management
├── data.py                     # Import / export logic
├── plotting.py                 # Matplotlib display & interactions
├── model.py                    # Statistical modeling & fitting
├── i18n.py                     # Internationalization (FR / EN)
│
├── install_dependencies.py     # Automatic dependency installer
├── logo.png                    # Application icon
└── README.md
```

---

## ⚙️ Dependencies

Required Python libraries:

* numpy
* pandas
* matplotlib
* scipy
* lmfit
* pillow
* openpyxl

Automatic installation:

```bash
python install_dependencies.py
```

---

## ▶️ Running the Application

```bash
python main.py
```

---

## 🌍 Supported Languages

* French 🇫🇷
* English 🇬🇧

Language can be changed dynamically via the menu.

---

## 🧩 Software Architecture

The application follows a modular architecture:

* **PyknFitApp**

  * global application state
  * shared data container

* **UIManager**

  * widgets
  * menus
  * Tkinter events

* **DataManager**

  * file import
  * export routines

* **PlotManager**

  * matplotlib figures
  * mouse interactions

* **ModelManager**

  * Gaussian model construction
  * optimization
  * statistical metrics

This design facilitates:

* maintainability
* scientific transparency
* future extensions (e.g. Weibull, log-normal models)

---

## 🔬 Typical Use Cases

* granulometric population decomposition
* sedimentary process interpretation
* multimodal distribution analysis
* inter-sample comparison
* export toward external statistical workflows

---

## 👤 Authorship & Scientific Lineage

**Developed by**
**Jean-Baptiste Barreau**

**Project initiated and tested by**
**François Pustoc'h**

**Based on the methodological work of**
**Alain Queffelec**

Reference implementation and conceptual foundation:

Particle Size Analysis — A. Queffelec
[https://github.com/AQueff/ParticleSizeAnalysis](https://github.com/AQueff/ParticleSizeAnalysis)

---

## 📜 License

Open-source project — license to be defined depending on distribution and usage.
