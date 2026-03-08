# 🏥 Cardionova — Cardiovascular Risk Prediction System

A production-grade, full-stack machine learning system that predicts 
a patient's **10-year cardiovascular disease (CVD) risk** using the 
Framingham Heart Study dataset.

Built as a B.Tech Minor Project at **Medicaps University, Indore (2026)**.

---

## 👩‍💻 Developer
- **Pranjali Dangi** — EN23CS301768
- B.Tech CSE, Medicaps University
- Supervisor: Dr. Manoranjan Kumar Sinha
- Co-Guide: Prof. Digendra Singh Rathore

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| ML Models | Scikit-learn, XGBoost |
| Explainability | SHAP |
| Backend API | FastAPI + Python |
| Database | MongoDB Atlas |
| Frontend | React.js |
| Deployment | Docker + Render + Vercel |

---

## 📊 Model Performance

| Metric | Value |
|---|---|
| Champion Model | Logistic Regression (L1, C=0.175) |
| CV AUC-ROC | 0.7309 ✅ |
| Clinical Recall | 0.83 (catches 83% of CVD cases) |
| Tuning Method | Grid → Random → Bayesian Optimization |

---

## 🗂️ Project Structure

Cardionova/
├── data/
│ ├── notebooks/ # Jupyter notebooks (Modules 1-3)
│ ├── src/ # preprocessing.py
│ ├── models/ # Saved .pkl files (git-ignored)
│ └── reports/ # Generated plots and CSVs
├── backend/ # FastAPI application (Module 4)
├── frontend/ # React dashboard (Module 5)
├── requirements.txt
└── README.md


---

## 🚀 Modules

| Module | Status | Description |
|---|---|---|
| Module 1 | ✅ Complete | EDA, KNN Imputation, Feature Engineering |
| Module 2 | ✅ Complete | Model Training, 3-Stage Hyperparameter Tuning |
| Module 3 | ✅ Complete | SHAP Explainability — Global + Local |
| Module 4 | 🔜 Upcoming | FastAPI Backend |
| Module 5 | 🔜 Upcoming | React Frontend + Docker |

---

## ⚙️ Setup Instructions

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/cardionova.git
cd cardionova

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your own framingham.csv to data/
# Then run notebooks in order:
# 01_eda_preprocessing.ipynb → 02_model_selection.ipynb → 02b_advanced_tuning.ipynb
