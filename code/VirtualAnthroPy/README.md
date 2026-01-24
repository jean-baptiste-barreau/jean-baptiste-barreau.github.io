# VirtualAnthroPy

**CSV to 3D conversion tool for virtual anthropology**

---

## 📘 Associated scientific publication

This repository contains the source code associated with the following peer-reviewed publication:

**Barreau, J.-B. & [Second author] (2021)**
*Virtual anthropology: a Python tool for 3D visualization and analysis of archaeological data*
Open Access Journal of Archaeology and Anthropology (OAJAA)
[https://irispublishers.com/oajaa/pdf/OAJAA.MS.ID.000546.pdf](https://irispublishers.com/oajaa/pdf/OAJAA.MS.ID.000546.pdf)

---

## 🧭 Scientific context

VirtualAnthroPy was developed in the framework of archaeological and anthropological research requiring:

* quantitative analysis of spatial data,
* reproducible measurements,
* and 3D visualization of field-recorded remains.

The tool focuses on **primary archaeological data recorded in CSV format**, typically produced during excavation or laboratory work, and transforms them into **geometrically structured 3D models** suitable for interpretation, comparison, and visualization.

---

## 🎯 Objectives of the software

The main objectives of VirtualAnthroPy are:

* to bridge the gap between **field data (CSV tables)** and **3D visualization**,
* to provide **transparent and reproducible geometric constructions**,
* to allow **quantitative and spatial analysis** within a virtual environment,
* to remain usable by archaeologists without advanced programming skills.

---

## 🧩 Main functionalities

### 1. CSV → 3D conversion

The software converts CSV datasets into:

* `.obj` geometry files
* `.mtl` material files
* automatically generated texture images

These outputs are compatible with standard 3D software such as:

* Blender
* MeshLab
* CloudCompare

---

### 2. Footprint analysis module

For footprint datasets, the tool computes:

* footprint length
* footprint width
* footprint orientation (angle of rotation)
* average altitude

It also provides:

* automatic width estimation from footprint length,
* color gradients based on selected variables (height, angle),
* descriptive statistics.

---

### 3. Skeleton representation module

For human remains, the software supports:

* head–pelvis–feet spatial coordinates,
* partial or complete skeleton representations,
* individual identification via textures,
* visualization of burial organization within the grave.

Each skeleton is represented as a simplified but metrically coherent 3D object.

---

### 4. Automatic texture generation

Textures are generated dynamically and may include:

* individual identifiers,
* archaeological context information,
* metric values,
* neutral or colored overlays.

This allows direct visual interpretation inside 3D viewers without external databases.

---

### 5. Statistical analysis

The program automatically computes and displays:

* mean values
* medians
* standard deviations
* minima and maxima

For:

* lengths
* widths
* altitudes
* orientations

Results are visualized through:

* histograms
* boxplots

(using Matplotlib).

---

### 6. Spatial reference system

A 3D reference frame is automatically generated:

* X, Y, Z axes
* grid system
* measurement units defined by the user

This ensures spatial coherence between datasets and visual comparability.

---

## 🖥️ Graphical interface

The application uses a **Tkinter-based GUI**, allowing:

* file selection,
* parameter configuration,
* progress visualization,
* result summaries.

No command-line interaction is required for standard use.

---

## 📁 Input data format

The software expects CSV files containing:

* spatial coordinates (X, Y, Z),
* archaeological identifiers,
* descriptive attributes depending on the module used.

The exact structure of the CSV files is described in detail in the associated publication.

---

## ⚙️ Technical information

### Programming language

* Python 3

### Main libraries

* `numpy`
* `opencv-python`
* `matplotlib`
* `colour`
* `tkinter`

---

## ▶️ Installation and execution

### 1. Install dependencies

```bash
pip install numpy opencv-python matplotlib colour
```

### 2. Run the program

```bash
python main.py
```

---

## 📤 Output

For each processed CSV file, the software produces:

* `.obj` file (geometry)
* `.mtl` file (materials)
* texture folder (PNG / JPG images)

These outputs can be imported directly into any compatible 3D visualization software.

---

## 📚 Citation

If you use this software for academic or research purposes, please cite the following publication:

> Barreau, J.-B. & [Second author] (2021).
> *Virtual anthropology: a Python tool for 3D visualization and analysis of archaeological data*.
> Open Access Journal of Archaeology and Anthropology.

---

## ⚠️ Disclaimer

This software is provided for **research and educational purposes only**.

The authors make no guarantee regarding suitability for commercial or clinical use.

---

## 👥 Authors

* Jean-Baptiste Barreau
* [Second author]

---

## 📜 License

This code is distributed for academic use.
Please refer to the publication for methodological and ethical context.
