const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel,
        AlignmentType, WidthType, BorderStyle, ShadingType, PageBreak, PageOrientation } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerShading = { fill: "2E75B6", type: ShadingType.CLEAR };
const headerText = { bold: true, color: "FFFFFF", size: 22 };

// Content width for US Letter: 12240 - 2880 = 9360 DXA
const contentWidth = 9360;
const col1Width = 4680;
const col2Width = 4680;

function createTable(headers, rows, colWidths = null) {
  const actualColWidths = colWidths || Array(headers.length).fill(contentWidth / headers.length);

  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: actualColWidths[i], type: WidthType.DXA },
      shading: headerShading,
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: h, ...headerText })]
      })]
    }))
  });

  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders,
      width: { size: actualColWidths[i], type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun(typeof cell === 'string' ? cell : cell.toString())]
      })]
    }))
  }));

  return new Table({
    width: { size: contentWidth, type: WidthType.DXA },
    columnWidths: actualColWidths,
    rows: [headerRow, ...dataRows]
  });
}

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 22 } // 11pt default
      }
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 }
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "404040" },
        paragraph: { spacing: { before: 120, after: 80 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: {
          width: 12240,   // US Letter
          height: 15840
        },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Title Page
      new Paragraph({
        spacing: { before: 480, after: 240 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "SYNTH-GPR", bold: true, size: 48, color: "2E75B6" })]
      }),
      new Paragraph({
        spacing: { after: 480 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Synthetic Ground Penetrating Radar Dataset & ML Pipeline", bold: true, size: 28 })]
      }),
      new Paragraph({
        spacing: { before: 240, after: 240 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Project Overview & Architecture Documentation", size: 24, italics: true })]
      }),
      new Paragraph({
        spacing: { before: 600, after: 120 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Author: Álvaro Jería", size: 22 })]
      }),
      new Paragraph({
        spacing: { after: 480 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "June 2024", size: 22 })]
      }),

      // Divider
      new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 1 } },
        spacing: { before: 240, after: 240 },
        children: [new TextRun("")]
      }),

      new Paragraph({ children: [new TextRun("")] }),
      new Paragraph({ children: [new PageBreak()] }),

      // Table of Contents
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Table of Contents")]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("1. Project Overview")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("2. Problem & Solution")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("3. Technical Architecture")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("4. Data Pipeline")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("5. Core Components")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("6. Key Features")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("7. Getting Started")] }),
      new Paragraph({ spacing: { after: 400 }, children: [new TextRun("8. Project Statistics")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 1: Project Overview
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("1. Project Overview")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("What is Synth-GPR?")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("Synth-GPR is a comprehensive framework for generating synthetic Ground Penetrating Radar (GPR) datasets and training machine learning classifiers to assess railway ballast fouling conditions.")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Core Innovation")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("The key innovation is predicting fouling class from GPR waveform features alone—without relying on metadata (material composition, density, moisture). This is critical because metadata is unavailable in real-world GPR field deployments.")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Baseline Performance")]
      }),
      createTable(["Metric", "Value"], [
        ["Dataset Size", "30,000+ samples"],
        ["Feature Dimension", "572 (waveform only)"],
        ["Model Type", "Random Forest"],
        ["Balanced Accuracy", "70.83%"],
        ["Training Time", "~30 minutes"]
      ]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 2: Problem & Solution
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("2. Problem & Solution")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("The Problem")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Traditional ballast fouling assessment relies on:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Lab measurements—expensive, limited samples")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Metadata-based models—require lab inputs (permittivity, density, moisture)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Hand-engineered features—no generalization to field data")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("The Solution")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Synth-GPR solves this by:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Generating synthetic data at scale (10k+ samples with full geometric control)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Extracting waveform-only features (572 features from A-scan alone)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Training production models with baseline 70.83% balanced accuracy")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Enabling field deployment (only Ez waveform needed, no metadata)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 3: Technical Architecture
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("3. Technical Architecture")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("High-Level Overview")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("Synth-GPR is organized into three main layers:")]
      }),

      createTable(["Layer", "Purpose", "Key Modules"], [
        ["Data Generation", "Create synthetic GPR geometries and run FDTD simulations", "rock_packing, gpr_commands, scene_generator"],
        ["Feature Extraction", "Extract 572-dimensional features from raw A-scan waveforms", "signal_processing, feature_extraction"],
        ["ML Pipeline", "Train and evaluate classifiers for fouling prediction", "train_rf, train_xgboost, evaluation"]
      ], [3120, 3120, 3120]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Modular Design")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("The codebase is organized into reusable components:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Domain Models (value_objects, coordinates, scene_parameters)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Data Access Layer (repositories, filesystem_repository)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Core Algorithms (signal_processing, rock_packing, fouling calculation)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• I/O Utilities (file_reader, file_writer, dataset_io)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Visualization (render, panels, publication_figures)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 4: Data Pipeline
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("4. Data Pipeline")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("End-to-End Workflow")]
      }),

      createTable(["Stage", "Input", "Process", "Output"], [
        ["1. Generation", "Parameters (fouling level, antenna, material)", "Rock packing algorithm + geometry creation", ".in files"],
        ["2. Simulation", ".in geometry files", "gprMax FDTD electromagnetic simulation (400 MHz Ricker)", ".out HDF5 files with Ez waveform"],
        ["3. Extraction", ".out files", "Feature extraction from A-scan signals", "572-dimensional feature vectors"],
        ["4. ML Training", "Feature vectors + labels", "Random Forest / XGBoost training", "Fouling classifier model"]
      ], [1404, 2340, 2808, 2808]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Feature Extraction Details")]
      }),

      createTable(["Feature Group", "Count", "Description"], [
        ["Time-domain statistics", "~25", "Mean, RMS, std, skewness, kurtosis, peak values, area"],
        ["Hilbert envelope", "~25", "Energy envelope metrics capturing pulse shape"],
        ["FFT features", "8", "Frequency domain analysis (peak, bandwidth, entropy, flatness)"],
        ["STFT features", "7", "Time-frequency energy in depth bands"],
        ["Slice statistics", "28", "14 temporal segments × 2 metrics"],
        ["Grid features", "480", "16×10 spatial-temporal grid × 3 channels"],
        ["TOTAL WAVEFORM", "572", "All extracted from raw A-scan signal"]
      ], [2340, 1170, 5850]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 5: Core Components
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("5. Core Components")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Rock Packing Algorithms")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("12 configurable algorithms with different speed/quality tradeoffs:")]
      }),

      createTable(["Algorithm", "Speed", "Quality", "Use Case"], [
        ["RSA (Random Sequential)", "< 1s", "Low", "Fast prototyping"],
        ["Grid", "< 1s", "Low", "Regular patterns"],
        ["Circlify", "1-5s", "Medium", "Testing"],
        ["Simulated Annealing", "5-10s", "Medium", "Balanced"],
        ["ShangChu (Recommended)", "15-20s", "High", "Production datasets"],
        ["HybridShang", "15-20s", "High+", "Enhanced quality"]
      ], [1872, 1404, 1404, 3680]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Fouling Classification")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Five fouling classes defined by Fouling Index (FI) and Percentage Void Contamination (PVC):")]
      }),

      createTable(["Class", "Label", "FI Range", "Description"], [
        ["C", "Clean", "0.0–0.2", "No fouling material in voids"],
        ["MC", "Moderately Clean", "0.2–0.4", "Minimal fouling"],
        ["MF", "Mixed Fouling", "0.4–0.6", "Partial void contamination"],
        ["F", "Fouled", "0.6–0.8", "Significant fouling"],
        ["HF", "Highly Fouled", "0.8–1.0", "Voids mostly filled with fines"]
      ], [1872, 1872, 1872, 3744]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Electromagnetic Simulation")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Configuration:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Antenna: 400 MHz Ricker wavelet (production standard)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Time window: 20 ns")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• PML boundary: 10 cells")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Output: Ez time-domain waveforms (A-scans)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 6: Key Features
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("6. Key Features")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Synthetic Data Generation")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Generates realistic GPR geometries with configurable:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Fouling levels (5 classes: Clean → Highly Fouled)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Rock packing algorithms (12 variants)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Antenna configurations (bistatic, frequency-selectable)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Material properties (permittivity, conductivity, moisture)")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Visualization")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Comprehensive visualization tools:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• High-resolution blueprint diagrams of simulated geometries")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• A-scan visualization with physical GPR interpretation")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• 6-panel analysis plots (raw signal, Hilbert envelope, FFT, STFT, grid, physics)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• 3D scene animations and publication-quality figures")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Machine Learning Pipeline")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Production-ready ML capabilities:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Random Forest and XGBoost classifiers")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Class balancing and hyperparameter tuning")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Cross-validation and rigorous model evaluation")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• Feature importance analysis and confusion matrices")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 7: Getting Started
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("7. Getting Started")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Installation")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Prerequisites: Python 3.8+, gprMax, pip")]
      }),
      new Paragraph({
        spacing: { before: 120, after: 120 },
        children: [new TextRun("1. Clone repository and navigate to directory")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [new TextRun("2. Create virtual environment: python -m venv venv")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [new TextRun("3. Install dependencies: pip install -r requirements.txt")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("4. Verify setup: pytest tests/ -v")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Quick Start Pipeline")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Step 1: Generate Synthetic Geometries")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("python scripts/pipeline/generate_in_files.py output/ --mode batch --labels CL MC MF F HF -n 50 --angular")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Step 2: Run Electromagnetic Simulations")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("python scripts/pipeline/run_simulations.py output/ -j 4")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Step 3: Extract Features")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("python scripts/pipeline/extract_features.py output/ --output features.csv")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Step 4: Train ML Classifier")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("python scripts/pipeline/train_rf_waveform_only.py")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 8: Project Statistics
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("8. Project Statistics")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Codebase Overview")]
      }),

      createTable(["Component", "Count/Details"], [
        ["Python Modules", "60+ files in src/"],
        ["Scripts", "30+ executable scripts"],
        ["Test Files", "25+ test modules"],
        ["Documentation Files", "80+ markdown files"],
        ["Packing Algorithms", "12 variants"],
        ["Feature Groups", "7 categories (572 total features)"],
        ["Fouling Classes", "5 (Clean to Highly Fouled)"]
      ], [4680, 4680]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Directory Structure")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("src/ — Core library modules")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • domain/ — Domain models and value objects")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • repositories/ — Data access layer")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • visualization/ — Plotting and rendering")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [new TextRun("  • [60+ modules] — Core algorithms and utilities")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("scripts/ — Executable scripts")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • pipeline/ — Main generation and ML workflow")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • analysis/ — Validation and research analyses")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • experiments/ — Research experiments")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [new TextRun("  • visualization/ — Plotting and rendering scripts")]
      }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("docs/ — Comprehensive documentation")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • setup/ — Installation and configuration")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • architecture/ — Technical architecture")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("  • algorithms/ — Algorithm documentation")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 120 },
        children: [new TextRun("  • research/ — Research papers and analyses")]
      }),

      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("tests/ — Test suite (pytest)")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Dependencies")]
      }),

      createTable(["Category", "Key Libraries"], [
        ["Scientific Computing", "numpy, scipy, pandas"],
        ["Machine Learning", "scikit-learn, xgboost"],
        ["Visualization", "matplotlib, plotly, pillow"],
        ["Data I/O", "h5py (HDF5), pyarrow (Parquet)"],
        ["Testing", "pytest, hypothesis"],
        ["Configuration", "pyyaml, python-dotenv"]
      ], [3120, 6240]),

      new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Development Standards")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("The project follows professional development practices:")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Code style: Black formatter, type hints, docstrings")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Testing: Comprehensive pytest suite with unit and integration tests")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Documentation: Markdown files in docs/, inline docstrings")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("• Version control: Git with clear commit history")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("• CI/CD ready: Configuration for automated testing and validation")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Final Summary
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Summary")]
      }),

      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun("Synth-GPR is a mature, well-engineered framework for synthetic GPR dataset generation and machine learning-based fouling classification. Key strengths include:")]
      }),

      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("✓ Waveform-only feature approach enables field deployment")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("✓ Modular architecture with 12 packing algorithms and 7 feature groups")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("✓ Production-ready ML pipeline with baseline 70.83% accuracy")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("✓ Comprehensive documentation (80+ markdown files)")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 60 },
        children: [new TextRun("✓ Rigorous testing and professional development standards")]
      }),
      new Paragraph({
        spacing: { before: 60, after: 200 },
        children: [new TextRun("✓ Scalable infrastructure for generating 10k+ synthetic samples")]
      }),

      new Paragraph({ spacing: { before: 200, after: 200 }, children: [new TextRun("")] }),

      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 1 } },
        spacing: { before: 240, after: 120 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun("For questions, issues, or collaboration: alvaro.jeria.m@gmail.com")]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const path = "/sessions/busy-inspiring-hopper/mnt/Synth-GPR/CODEBASE_PRESENTATION.docx";
  fs.writeFileSync(path, buffer);
  console.log("✓ Document created: CODEBASE_PRESENTATION.docx");
});
