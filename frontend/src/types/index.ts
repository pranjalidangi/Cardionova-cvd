export type RiskLevel = "LOW" | "MODERATE" | "HIGH";

export type ShapFactor = {
  feature: string;
  value: number;
  shap_value: number;
  direction: string;
  magnitude: string;
};

export type PredictionResult = {
  prediction_id: string;
  risk_probability: number;
  risk_level: RiskLevel;
  recommendation: string;
  top_shap_factors: ShapFactor[];
};

export type HealthFormData = {
  name: string;
  age: number;
  male: 0 | 1;
  education: 1 | 2 | 3 | 4;
  currentSmoker: 0 | 1;
  cigsPerDay: number;
  BPMeds: 0 | 1;
  prevalentStroke: 0 | 1;
  prevalentHyp: 0 | 1;
  diabetes: 0 | 1;
  totChol: number;
  sysBP: number;
  diaBP: number;
  BMI: number;
  heartRate: number;
  glucose: number;
};
