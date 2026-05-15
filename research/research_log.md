
# Research Log: Cross-Subject Music-Emotion Prediction

**Project Title:** A Comparative Analysis of Machine Learning Models for Cross-Subject Music-Emotion Prediction

**Author:** Ishan Siddhartha

**Institutional Context:** Summer Research Project (2026)

## 1. Problem Statement & Motivation

Existing literature (Daly et al., 2015; Krish, 2021) has established that EEG signals combined with acoustic features can predict emotional states (Valence/Arousal). However, these studies primarily utilized **within-subject** validation (k-fold), which often captures individual physiological "fingerprints" rather than universal emotional biomarkers.

**The Goal:** To bridge the gap between "lab-accurate" models and "real-world" applications by evaluating model performance on **unseen subjects**. This is critical for neuro-technological systems (like the NeuroSync proposal) where zero-calibration for new users is the primary deployment hurdle.

## 2. Proposed Methodology

### 2.1 Validation Strategy: Leave-One-Subject-Out (LOSO)

To ensure **Generalizability**, we implement LOSO cross-validation.

* **The Process:** For $N$ subjects, the model is trained on $N-1$ subjects and tested on the $N^{th}$ subject. This is repeated $N$ times.
* **The Necessity:** EEG data violates the I.I.D. (Independent and Identically Distributed) assumption if split randomly. LOSO prevents **Data Leakage** where the model memorizes a specific subject’s baseline brain activity rather than the emotional response.

### 2.2 Model Selection & Justification

We compare three distinct algorithmic architectures to establish a performance benchmark:

1. **Lasso Regression (L1-Regularized Linear Model):**
* *Role:* Interpretable Baseline (used in Krish, 2021).
* *Math:* Minimizes $\text{RSS} + \lambda \sum |w_j|$. It performs automatic feature selection by forcing the coefficients of non-contributory EEG features to zero.


2. **Random Forest (Ensemble Bagging):**
* *Role:* Robustness to Artifacts.
* *Math:* Utilizes orthogonal feature splitting. It is mathematically invariant to outliers (like eye-blink spikes) because it relies on thresholding $\mathbb{I}(x_i > \tau)$ rather than scalar magnitude.


3. **XGBoost (Gradient Boosting):**
* *Role:* State-of-the-Art Predictive Power.
* *Math:* Sequentially minimizes a regularized objective function using second-order Taylor expansion (Hessian). It is optimized for the tabular, high-dimensional nature of extracted EEG/audio features.



---

## 3. Project Roadmap (4-Week Sprint)

| Phase | Focus | Key Deliverable |
| --- | --- | --- |
| **Week 1** | Data Acquisition & EDA | Visualized EEG epochs & Audio clips from `ds002721`. |
| **Week 2** | Feature Engineering | CSV containing extracted Band Power, Hjorth params, & MFCCs. |
| **Week 3** | Model Training (LOSO) | Performance metrics (RMSE/R²) for Lasso, RF, and XGBoost. |
| **Week 4** | Analysis & Writing | Final Paper/Presentation drafting. |

---

## 4. Progress Log

### Day 1: [May 10, 2026] - Setup & Data Ingestion

* **Status:** Initializing Project.
* **Tasks Completed:**
* [x] Defined research gap and methodology.
* [x] Set up Python virtual environment on Fedora.
* [x] Identified target dataset: **OpenNeuro ds002721** (Daly et al., 2015).


* **Notes:**
* Environment requires `mne` for EEG processing and `librosa` for audio.
* Need to ensure the `ds002721` BIDS structure is preserved during download for easier parsing.


* **Next Steps:** Download full raw EEG data (~31 subjects) and begin first-pass visualization of subject-01.

---

### Tips for your Mentor:

When you show them this, emphasize that you aren't just "running code." You are **validating an assumption** (that LOSO is harder but more realistic than k-fold). Professors love it when a student acknowledges the flaws in previous papers (like the data leakage/random split issue) and tries to fix them.

Since you're on **Fedora**, are you planning to use a specific IDE or notebook setup (like VS Code or Jupyter) for the visualization phase tomorrow?

### Day 2: [May 10, 2026] - Dataset Exploration & Literature Review

* **Status:** Deep-diving into dataset structure and reference papers.
* **Tasks Completed:**
  * [x] Located audio stimulus files: All 360 MP3s confirmed in `data/music/Set1/Set1/` (Eerola & Vuoskoski, 2010, Set 1).
  * [x] Confirmed event-to-audio mapping: EEG event codes 301–360 → subtract 300 → `NNN.mp3` (e.g., event `362` → `062.mp3`).
  * [x] Located emotion ratings: `data/music/mean_ratings_set1.csv` (8 Likert scales + TARGET label per clip).
  * [x] Located tracklist metadata: `data/music/set1_tracklist.csv` (album, track name, timestamp per clip).
  * [x] Traced a full example: Event `362` → `062.mp3` → Valence=3.83, Energy=5.33, Tension=5.50 (SAD) → "The English Patient" Track 12.
  * [x] Completed deep-read of **Daly et al. (2015)** — extracted methodology.
  * [x] Completed deep-read of **Krish (2021)** — extracted methodology.
  * [x] Designed project folder structure and 5-notebook pipeline (see `research/plan.md`).

* **Key Findings from Literature:**

  **Daly et al. (2015) — "Music-induced emotions can be predicted from a combination of brain activity and acoustic features"**
  * *Stimuli:* 40 clips from Eerola & Vuoskoski Set 1 (12–15s film soundtracks).
  * *Participants:* 31 (same as our dataset).
  * *EEG Features:* 400 total — 20 frequency bands (4 Hz width, 0–80 Hz) × 19 channels + prefrontal asymmetry (F3−F4 per band).
  * *Acoustic Features:* 135 (Mel-cepstral coefficients, Chroma, etc.).
  * *Feature Selection:* PCA-based participation index (top 5th percentile).
  * *Model:* Linear regression with stepwise training, 10×10 cross-fold (within-subject).
  * *Results (Combined EEG + Acoustic):*
    * PC1 (Valence): r = 0.243 ± 0.005
    * PC2 (Energy-arousal): r = 0.158 ± 0.006
    * PC3 (Tension-arousal): r = 0.102 ± 0.005
  * *Key Insight:* EEG features alone significantly outperform acoustic features alone. Combined features are best. Valence predicted by delta + beta over right frontal cortex; Energy-arousal by beta + gamma over left motor cortex; Tension-arousal by delta + beta + gamma over right motor/parietal cortex.
  * *Artifact Rejection:* 31.03% of trials removed (EMG + amplitude > ±100 µV).

  **Krish (2021) — "Using a Combination of Electroencephalographic and Acoustic Features to Predict Music-Induced Emotions"**
  * *Stimuli:* Same dataset (40 clips from Set 1).
  * *EEG Features:* 285 total — DWT decomposition into 5 bands (δ 0–6, θ 6–12, α 12–24, β 24–48, γ 48–80 Hz), extracting: energy, mean, std, entropy, Hjorth mobility, power spectrum.
  * *Acoustic Features:* 352 total — Chroma (84), BPM, ZCR (7), Key, MFCC (140), Tonnetz, Spectral Centroid/Rolloff/Flatness/Bandwidth/Contrast.
  * *Feature Selection:* Recursive Feature Elimination (RFE).
  * *Model:* Lasso regression (α = 10), 5-fold cross-validation (within-subject).
  * *Results (Combined EEG + Acoustic):*
    * PC1 (Valence-arousal): r = 0.774
    * PC2 (Tension-arousal): r = 0.791
    * PC3 (Energy-arousal): r = 0.798
  * *Key Insight:* ~370% improvement over Daly et al. (2015). RFE ranked Key and BPM as most important acoustic features; Hjorth Mobility as most important EEG feature. Females 24.2% more emotionally expressive than males (p < 0.001). Model tested on pop songs for valence prediction — "Dancing Queen" (ABBA) ranked highest.
  * *Note on PC naming:* Krish's PC1 = Valence-arousal, PC2 = Tension-arousal, PC3 = Energy-arousal (slightly different axis labeling from Daly, but same Schimmack & Grob 3D model).

  **Critical Methodological Difference (The Gap We're Addressing):**
  * Both papers use **within-subject** k-fold CV. This means the model sees data from the same subject in both train and test splits — it can learn individual EEG "fingerprints" (alpha rhythm baseline, skull conductivity, etc.) rather than true emotion biomarkers.
  * Our **LOSO (Leave-One-Subject-Out)** approach tests whether these features generalize to a completely unseen subject — a much harder but more realistic benchmark for real-world BCI/music-therapy deployment.

* **Project Structure Designed:**
daly-comp-analysis/
├── env/                        # Python venv (git-ignored)
├── notebooks/                  # All .ipynb notebooks
│   ├── 01_eda_raw_data.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_lasso.ipynb
│   ├── 04_model_random_forest.ipynb
│   └── 05_model_xgboost.ipynb
├── src/                        # Reusable Python modules
│   ├── __init__.py
│   ├── eeg_utils.py            # MNE-based EEG loading, filtering, epoching
│   ├── audio_utils.py          # Librosa-based MFCC/spectral extraction
│   ├── features.py             # Feature engineering pipeline
│   ├── models.py               # Lasso, RF, XGBoost + LOSO logic
│   └── viz.py                  # Plotting helpers
├── data/                       # Processed outputs (git-ignored)
│   ├── features/               # Extracted feature CSVs
│   ├── models/                 # Saved model artifacts
│   └── results/                # Metrics CSVs, figures
├── requirements.txt
├── .gitignore
├── research/
├── sub-01/ ... sub-31/         # Raw BIDS data (keep as-is)
└── code/


* **Notes:**
* The 8 Likert questions map to the Schimmack & Grob 3D model via PCA — need to derive the exact PCA loading matrix from the papers or compute it from the raw ratings.
* Audio files are confirmed present — no external download needed for MFCC extraction.
* Resting-state runs (1 & 6, 300s each) could serve as baseline normalization for band power features.
* Krish's DWT + Hjorth approach appears superior to Daly's pure band-power approach — we should implement both and compare.

* **Next Steps:** Set up Python venv, install dependencies, create `src/` module stubs, and begin Notebook 01 (raw EEG visualization for sub-01).

---

### Day 3: [May 13, 2026] - Data Download & Notebook Setup

* **Status:** Data acquisition complete. Notebook pipeline initialized.
* **Tasks Completed:**
  * [x] Cloned original OpenNeuro repository (`https://github.com/OpenNeuroDatasets/ds002721.git`) to `/tmp/ds002721-clone/`.
  * [x] Initialized git-annex and configured s3-PUBLIC remote for OpenNeuro S3 backend access.
  * [x] Downloaded all 31 subjects × 6 runs = 185 EDF files (~3.6 GB total) using `git annex get` with loop iteration.
  * [x] Resolved permission issues: Removed broken symlinks and re-copied files with `sudo` to populate `/home/trainerblue/Documents/daly-comp-analysis/data/sub-{01..31}/eeg/`.
  * [x] Verified all 185 EDF files are real files (not symlinks) and accessible.
  * [x] Created 5-cell Notebook 01 (`01_eda_raw_data.ipynb`) with path resolution, EDF loading (mne), event parsing, and raw signal visualization.
  * [x] Visualised sub-01 run-2 raw EEG data with MNE's `raw.plot()` — confirmed 19 channels, 500 Hz sampling, and expected event markers.

* **Technical Notes:**
  * Initial brace expansion command `git annex get sub-{01..31}/eeg/*_eeg.edf -J 4` got stuck mid-execution (exit 130).
  * Solution: Switched to loop-based iteration `for i in {01..31}; do git annex get sub-$i/eeg/*_eeg.edf -J 4; done` — completed successfully.
  * Data files from git-annex are stored as symlinks pointing to `.git/annex/objects/` — dereferenced with `cp -L` flag during copy.
  * All files are read-only (`-r--r--r--`) from annex; used `sudo` to override for clean integration into project structure.

* **Environment Status:**
  * Python 3.14 venv fully configured with 11 packages (mne, pandas, numpy, scikit-learn, xgboost, matplotlib, seaborn, jupyterlab, librosa, scipy, tqdm).
  * All packages import-verified; no dependency issues.

* **Notebook 01 Capabilities:**
  * Cell 1–2: Title and objectives.
  * Cell 3: Smart path resolution (handles notebook run from any directory in the project).
  * Cell 4: Loads EDF for sub-01 run-2; displays MNE raw object and channel info.
  * Cell 5: Loads event markers from TSV; displays first 10 rows and unique trial codes; plots raw 19-channel EEG with 10-second window and auto-scaling.

* **Next Steps:** Execute Notebook 01 cells to confirm data loading pipeline works end-to-end. Then design and implement Notebook 02 (Feature Engineering: Band Power, Hjorth Parameters, MFCCs).

---

### Day 4: [May 15, 2026] - Goal Refinement & Feature Strategy

* **Status:** Solidified feature engineering strategy based on Daly (2015) vs Krish (2021) methodologies.
* **Tasks Completed:**
  * [x] Reviewed literature feature selections: Identified that Krish's massive performance boost (from r=0.24 to r=0.77) relied heavily on **Hjorth Mobility** and **Entropy** rather than standard band-powers.
  * [x] Analyzed label distribution (`mean_ratings_set1.csv`): Discovered items 001–060 distinctly capture valence extremes (1-30 = HAPPY, 31-60 = SAD). While this enables binary classification, significant within-class variability in continuous `valence`, `energy`, and `tension` ratings exists. This validates our choice to use continuous regression (predicting the PCs) over simple binary labels, allowing us to exploit the full signal variation.
  * [x] Formalized our Feature Superset: We will extract both Daly's asymmetry/band-powers and Krish's Wavelet-based Hjorth/Entropy features.
  * [x] Finalized Targets: We will regress onto the 3 Principal Components (Valence, Energy, Tension) instead of binary classification to maintain a direct mathematical comparison with the literature.
  * [x] Reaffirmed LOSO necessity: The primary aim is to test if Krish's high correlation metrics collapse under strict Leave-One-Subject-Out (LOSO) cross-validation (i.e., proving within-subject testing was overfitting).

* **Next Pipeline Goals:**
  1. Map the event TSV files specifically to the correct 15-second EEG epochs post-stimulus.
  2. Implement an artifact rejection pipeline (dropping trials with > ±100 µV amplitude to match Daly).
  3. Write the MNE-based feature extraction script (Notebook 02) calculating Hjorth params, band powers, and extracting audio MFCC/Chroma.