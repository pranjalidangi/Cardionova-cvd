import axios from "axios";
import type { HealthFormData, PredictionResult } from "../types";

const BASE = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api`;

export const predict = async (data: HealthFormData): Promise<PredictionResult> => {
  const res = await axios.post(`${BASE}/predict`, data);
  const raw = res.data;

  return {
    prediction_id: raw.prediction_id,
    risk_probability: raw.risk_probability ?? raw.cvd_probability ?? 0,
    risk_level: raw.risk_level,
    recommendation: raw.recommendation,
    top_shap_factors: (raw.top_shap_factors ?? raw.top_risk_factors ?? []).map((f: {
      feature: string;
      value: number;
      shap_value: number;
      direction: string;
      magnitude: string;
    }) => ({
      feature: f.feature,
      value: f.shap_value,
      shap_value: f.shap_value,
      direction: f.direction,
      magnitude: f.magnitude,
    })),
  };
};

export const downloadReport = async (data: HealthFormData): Promise<Blob> => {
  const res = await axios.post(`${BASE}/generate-report`, data, {
    responseType: "blob",
  });
  return res.data;
};

export const sendReport = async (
  data: HealthFormData,
  email: string,
  predictionId: string        // ← add this parameter
): Promise<void> => {
  await axios.post(`${BASE}/send-report`, {
    email: email,
    prediction_id: predictionId,
    input_data: {
      name: data.name, 
      male: data.male,
      age: data.age,
      education: data.education,
      currentSmoker: data.currentSmoker,
      cigsPerDay: data.cigsPerDay,
      BPMeds: data.BPMeds,
      prevalentStroke: data.prevalentStroke,
      prevalentHyp: data.prevalentHyp,
      diabetes: data.diabetes,
      totChol: data.totChol,
      sysBP: data.sysBP,
      diaBP: data.diaBP,
      BMI: data.BMI,
      heartRate: data.heartRate,
      glucose: data.glucose,
    },
  });
};

