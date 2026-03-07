import { useState } from 'react'
import axios from 'axios'
import { Heart, AlertCircle, CheckCircle } from 'lucide-react'


function App() {
  const [formData, setFormData] = useState({
    male: 1, age: 55, education: 2, currentSmoker: 1, cigsPerDay: 20,
    BPMeds: 0, prevalentStroke: 0, prevalentHyp: 1, diabetes: 0,
    totChol: 250, sysBP: 160, diaBP: 95, BMI: 28, heartRate: 80, glucose: 120
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)


  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
   
    try {
      // ✅ FIXED: Added headers + better error handling
      const response = await axios.post('http://localhost:8000/api/predict', formData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })
      setResult(response.data)
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message)
      setResult({
        error: error.response?.status === 404
          ? 'API endpoint not found. Check http://localhost:8000/docs'
          : 'Prediction failed. Backend logs: ' + (error.message || 'Unknown error')
      })
    }
    setLoading(false)
  }


  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* HEADER */}
        <div className="text-center mb-12">
          <Heart className="w-24 h-24 mx-auto mb-6 text-red-500 animate-pulse" />
          <h1 className="text-6xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-4">
            🫀 Cardionova
          </h1>
          <p className="text-2xl text-gray-600 max-w-2xl mx-auto">
            AI-Powered Cardiovascular Risk Assessment (0.726 AUC)
          </p>
        </div>


        <div className="grid lg:grid-cols-2 gap-12">
          {/* FORM */}
          <div className="card bg-base-100 shadow-2xl p-10 rounded-3xl">
            <h2 className="card-title text-4xl mb-8">🩺 Patient Data</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Male</span>
                </label>
                <input type="checkbox" checked={formData.male}
                  onChange={e => setFormData({...formData, male: e.target.checked ? 1 : 0})}
                  className="checkbox checkbox-lg checkbox-primary"
                />
              </div>
             
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Age</span>
                </label>
                <input type="range" min="30" max="80" value={formData.age}
                  onChange={e => setFormData({...formData, age: +e.target.value})}
                  className="range range-primary"
                />
                <label className="label">{formData.age} years</label>
              </div>


              <div className="form-control">
                <label className="label">
                  <span className="label-text">Smoker</span>
                </label>
                <input type="checkbox" checked={formData.currentSmoker}
                  onChange={e => setFormData({...formData, currentSmoker: e.target.checked ? 1 : 0})}
                  className="checkbox checkbox-lg checkbox-warning"
                />
              </div>


              <div className="form-control">
                <label className="label">
                  <span className="label-text">Cigs/Day</span>
                </label>
                <input type="number" min="0" max="60" value={formData.cigsPerDay}
                  onChange={e => setFormData({...formData, cigsPerDay: +e.target.value})}
                  className="input input-bordered input-lg w-full"
                />
              </div>


              <div className="form-control">
                <label className="label">
                  <span className="label-text">Systolic BP</span>
                </label>
                <input type="number" min="90" max="250" value={formData.sysBP}
                  onChange={e => setFormData({...formData, sysBP: +e.target.value})}
                  className="input input-bordered input-lg input-error w-full"
                />
              </div>


              <div className="form-control">
                <label className="label">
                  <span className="label-text">Cholesterol</span>
                </label>
                <input type="number" min="100" max="500" value={formData.totChol}
                  onChange={e => setFormData({...formData, totChol: +e.target.value})}
                  className="input input-bordered input-lg input-warning w-full"
                />
              </div>


              <div className="md:col-span-2">
                <button type="submit" disabled={loading}
                  className="btn btn-primary btn-lg w-full text-xl shadow-2xl hover:shadow-3xl"
                >
                  {loading ? (
                    <>
                      <span className="loading loading-spinner loading-lg"></span>
                      <span>Analyzing Risk Profile...</span>
                    </>
                  ) : (
                    <>
                      <Heart className="w-6 h-6" />
                      <span>🩺 Assess CVD Risk</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>


          {/* RESULTS */}
          <div className="card bg-base-100 shadow-2xl p-10 rounded-3xl">
            <h2 className="card-title text-4xl mb-8">📊 Results</h2>
           
            {result && !result.error ? (
              <>
                <div className={`text-center p-12 rounded-3xl shadow-2xl text-white text-5xl font-bold mb-8 ${
                  result.risk_category === 'HIGH' ?
                  'bg-gradient-to-r from-red-500 to-red-700' :
                  'bg-gradient-to-r from-emerald-500 to-emerald-700'
                }`}>
                  {result.risk_category}
                  <div className="text-4xl mt-4">{result.risk_percentage}</div>
                </div>


                <div className="card bg-base-200 p-8 mb-8">
                  <h3 className="text-2xl font-bold mb-6">🎯 Clinical Recommendations</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    {result.recommendations.map((rec, i) => (
                      <div key={i} className="alert alert-info shadow-lg">
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>


                <div className="grid md:grid-cols-2 gap-6 text-center">
                  <div className="stats shadow">
                    <div className="stat">
                      <div className="stat-title">Raw Probability</div>
                      <div className="stat-value text-primary">{result.risk_probability?.toFixed(3)}</div>
                    </div>
                  </div>
                  <div className="stats shadow">
                    <div className="stat">
                      <div className="stat-title">Model AUC</div>
                      <div className="stat-value text-success">0.726</div>
                    </div>
                  </div>
                </div>
              </>
            ) : result?.error ? (
              <div className="alert alert-error shadow-lg">
                <AlertCircle className="w-12 h-12" />
                <span>{result.error}</span>
                <div className="mt-4 text-sm space-y-1">
                  • Backend Terminal 1: uvicorn logs<br/>
                  • Test API: http://localhost:8000/docs<br/>
                  • Curl test: POST /api/predict
                </div>
              </div>
            ) : (
              <div className="hero min-h-96">
                <div className="hero-content text-center">
                  <Heart className="w-32 h-32 text-gray-300 mb-8" />
                  <div className="text-xl font-bold text-gray-500">Enter patient data above</div>
                  <div className="text-lg text-gray-400 mt-2">Click "Assess CVD Risk" for AI prediction</div>
                </div>
              </div>
            )}
          </div>
        </div>


        <div className="text-center mt-20 text-sm text-gray-500 pt-12 border-t border-gray-300">
          <div>Framingham Heart Study • Logistic Regression (0.726 AUC)</div>
          <div>FastAPI + React + DaisyUI • Medicaps University 2026</div>
        </div>
      </div>
    </div>
  )
}


export default App