import React, { useState } from 'react';


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

function PrescriptionAnalyzer() {
  const [prescriptionText, setPrescriptionText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzePrescription = async () => {
    if (!prescriptionText.trim()) {
      setError('Please enter prescription text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/health/analyze-prescription?prescriptionText=${encodeURIComponent(prescriptionText)}`,
        { method: 'POST' }
      );

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError('Failed to analyze prescription. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ 
            fontSize: '42px', 
            color: 'white', 
            margin: '0 0 10px 0',
            fontWeight: '700',
            textShadow: '0 2px 10px rgba(0,0,0,0.2)'
          }}>
            🏥 Prescription Analyzer
          </h1>
          <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.9)', margin: 0 }}>
            AI-powered prescription analysis for personalized meal recommendations
          </p>
        </div>

        {/* Input Card */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '32px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          marginBottom: '30px'
        }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '12px', 
            fontWeight: '700',
            fontSize: '16px',
            color: '#333'
          }}>
            📋 Enter Your Prescription
          </label>

          {/* OCR Image Upload */}
          <div style={{ marginBottom: '16px' }}>
             <label style={{
                display: 'inline-block',
                padding: '8px 16px',
                background: '#f0f0f0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                border: '1px solid #ccc',
                marginBottom: '8px'
             }}>
                📷 Scan Image (Python OCR + Preprocessing)
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;

                    setLoading(true);
                    setError(null);
                    try {
                      // FIX: Call Java middleware, NOT Python directly!
                      // React → Java → Python (3-tier architecture)
                      const formData = new FormData();
                      formData.append('file', file);
                      
                      const response = await fetch(`${API_BASE_URL}/api/health/ocr/extract-text`, {
                        method: 'POST',
                        body: formData
                      });
                      
                      const data = await response.json();
                      
                      if (data.success) {
                        setPrescriptionText(data.text);
                        // Show confidence if available
                        if (data.confidence) {
                          console.log(`OCR Confidence: ${data.confidence}`);
                        }
                      } else {
                        throw new Error(data.error || 'OCR extraction failed');
                      }
                    } catch (err) {
                      console.error("OCR Error:", err);
                      setError("Failed to read image. Please type manually or try a clearer photo.");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  style={{ display: 'none' }}
                />
             </label>
             {loading && !prescriptionText && <span style={{ marginLeft: '10px', color: '#666' }}>🔍 Scanning image...</span>}
          </div>

          <textarea
    value={prescriptionText}
            onChange={(e) => setPrescriptionText(e.target.value)}
            placeholder="Paste your prescription here...&#10;&#10;Example:&#10;Patient: John Doe&#10;Diagnosis: Type 2 Diabetes Mellitus&#10;HbA1c: 8.5%&#10;Medications: Metformin 500mg BD"
            rows={10}
            style={{
              width: '100%',
              padding: '16px',
              border: '2px solid #e8e8e8',
              borderRadius: '12px',
              fontSize: '15px',
              fontFamily: 'monospace',
              resize: 'vertical',
              transition: 'all 0.3s',
              outline: 'none'
            }}
            onFocus={(e) => e.target.style.borderColor = '#667eea'}
            onBlur={(e) => e.target.style.borderColor = '#e8e8e8'}
          />

          {error && (
            <div style={{
              marginTop: '16px',
              padding: '14px 18px',
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
              color: 'white',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              animation: 'shake 0.5s'
            }}>
              <span style={{ fontSize: '20px' }}>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <button
            onClick={analyzePrescription}
            disabled={loading || !prescriptionText.trim()}
            style={{
              marginTop: '20px',
              padding: '16px 0',
              background: loading || !prescriptionText.trim() 
                ? '#ccc' 
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '18px',
              fontWeight: '700',
              cursor: loading || !prescriptionText.trim() ? 'not-allowed' : 'pointer',
              width: '100%',
              boxShadow: loading || !prescriptionText.trim() ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)',
              transition: 'all 0.3s',
              transform: 'scale(1)'
            }}
            onMouseEnter={(e) => {
              if (!loading && prescriptionText.trim()) {
                e.target.style.transform = 'scale(1.02)';
                e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'scale(1)';
              e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
            }}
          >
            {loading ? (
              <span>🔄 Analyzing...</span>
            ) : (
              <span>🔍 Analyze Prescription</span>
            )}
          </button>
        </div>

        {/* Results Card */}
        {analysis && (
          <div style={{
            background: 'white',
            borderRadius: '20px',
            padding: '32px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            animation: 'slideUp 0.5s ease-out'
          }}>
            <h2 style={{ marginTop: 0, color: '#333', fontSize: '28px' }}>📊 Analysis Results</h2>

            {/* Conditions */}
            <div style={{ marginBottom: '28px' }}>
              <h3 style={{ color: '#667eea', marginBottom: '16px', fontSize: '20px' }}>
                Detected Conditions
              </h3>
              <div style={{ display: 'grid', gap: '12px' }}>
                {analysis.condition_details?.map((cond, idx) => (
                  <div key={idx} style={{
                    padding: '16px 20px',
                    background: 'linear-gradient(135deg, #f5f7ff 0%, #e8ecff 100%)',
                    borderLeft: '5px solid #667eea',
                    borderRadius: '10px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'transform 0.2s',
                    cursor: 'default'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateX(5px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateX(0)'}
                  >
                    <strong style={{ fontSize: '16px', color: '#333' }}>{cond.display_name}</strong>
                    <span style={{
                      padding: '4px 12px',
                      background: cond.type === 'chronic' 
                        ? 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)' 
                        : 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: '600',
                      color: '#333'
                    }}>
                      {cond.type}
                    </span>
                  </div>
                )) || <p style={{ color: '#999', fontStyle: 'italic' }}>No conditions detected</p>}
              </div>
            </div>

            {/* Medications */}
            {analysis.medications?.length > 0 && (
              <div style={{ marginBottom: '28px' }}>
                <h3 style={{ color: '#667eea', marginBottom: '16px', fontSize: '20px' }}>
                  💊 Medications
                </h3>
                {analysis.medications.map((med, idx) => (
                  <div key={idx} style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #fffaf0 0%, #fff5e6 100%)',
                    marginBottom: '12px',
                    borderRadius: '12px',
                    border: '1px solid #ffe0b2'
                  }}>
                    <strong style={{ fontSize: '17px', color: '#e67e22' }}>{med.name}</strong>
                    {med.timing && (
                      <p style={{ margin: '8px 0 0 0', fontSize: '14px', color: '#555' }}>
                        ⏰ {med.timing}
                      </p>
                    )}
                    {med.alert && (
                      <p style={{ 
                        margin: '8px 0 0 0', 
                        fontSize: '14px', 
                        color: '#c0392b',
                        padding: '8px 12px',
                        background: '#ffe6e6',
                        borderRadius: '6px',
                        marginTop: '8px'
                      }}>
                        ⚠️ {med.alert}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Plan Summary */}
            <div style={{
              padding: '24px',
              background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
              borderRadius: '12px',
              marginBottom: '20px'
            }}>
              <h3 style={{ marginTop: 0, color: '#2e7d32', fontSize: '20px' }}>
                📅 Plan Summary
              </h3>
              <p style={{ margin: '0 0 12px 0', lineHeight: '1.6', color: '#333' }}>
                {analysis.analysis_summary}
              </p>
              <div style={{ 
                display: 'inline-block',
                padding: '8px 16px',
                background: 'white',
                borderRadius: '8px',
                fontWeight: '600',
                color: '#2e7d32'
              }}>
                Duration: {analysis.plan_duration_days} days
              </div>
            </div>

            {/* Disclaimer */}
            <div style={{
              background: '#fff3cd',
              padding: '18px',
              borderRadius: '10px',
              border: '1px solid #ffc107'
            }}>
              <p style={{ margin: 0, fontSize: '14px', color: '#856404', lineHeight: '1.5' }}>
                ⚕️ <strong>Medical Disclaimer:</strong> This analysis is for informational purposes only. 
                Always consult your doctor before making dietary changes.
              </p>
            </div>
          </div>
        )}

        <style>{`
          @keyframes slideUp {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
          }
        `}</style>
      </div>
    </div>
  );
}

export default PrescriptionAnalyzer;
