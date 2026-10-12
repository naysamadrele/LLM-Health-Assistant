import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Activity, Users, Clipboard, FileText, Search, Settings, Sun, Moon, 
  Plus, LogOut, ChevronRight, AlertTriangle, ShieldCheck, Download, 
  BookOpen, HelpCircle, Check, Info, FileSpreadsheet, RefreshCw
} from 'lucide-react';

// Setup API URL mapping
const DEFAULT_API_URL = 'http://localhost:8000/api/v1';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [backendUrl, setBackendUrl] = useState(localStorage.getItem('backend_url') || DEFAULT_API_URL);
  
  // Theme state
  const [darkMode, setDarkMode] = useState(localStorage.getItem('theme') === 'dark');

  // Navigation
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Auth state
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // App data state
  const [patients, setPatients] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [symptoms, setSymptoms] = useState([]);
  
  // Selection states
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [kbQuery, setKbQuery] = useState('');
  const [kbResults, setKbResults] = useState([]);
  const [kbLoading, setKbLoading] = useState(false);

  // New Patient Form
  const [newPatient, setNewPatient] = useState({ name: '', age: 40, gender: 'Male', height: 170, weight: 70 });
  const [patientSearch, setPatientSearch] = useState('');
  
  // New Assessment Wizard
  const [wizardStep, setWizardStep] = useState(1);
  const [wizardVitals, setWizardVitals] = useState({
    systolic: 120, diastolic: 80, heartRate: 72, temp: 36.6, respRate: 16, spo2: 98, bloodSugar: ''
  });
  const [selectedSymptomCodes, setSelectedSymptomCodes] = useState([]);
  const [symptomSearch, setSymptomSearch] = useState('');
  const [wizardLifestyle, setWizardLifestyle] = useState({
    smoking: 'never', alcohol: 'none', exercise: 'moderate', diet: 'balanced', sleep: '7-8 hours', stress: 'low'
  });
  const [wizardHistory, setWizardHistory] = useState({
    diabetes: false, hypertension: false, asthma: false, heart_disease: false, kidney_disease: false, liver_disease: false, allergies: '', medications: ''
  });
  const [assessmentLoading, setAssessmentLoading] = useState(false);

  // Axios Client with default configurations
  const api = axios.create({
    baseURL: backendUrl,
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });

  // Dark mode trigger
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Fetch initial profile
  useEffect(() => {
    if (token) {
      api.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(err => {
          console.error("Auth me error", err);
          handleLogout();
        });
    }
  }, [token]);

  // Fetch global lists
  useEffect(() => {
    if (token) {
      fetchDashboardData();
    }
  }, [token, activeTab]);

  const fetchDashboardData = async () => {
    try {
      const [patientsRes, assessmentsRes, symptomsRes] = await Promise.all([
        api.get('/patients/'),
        api.get('/assessments/'),
        api.get('/symptoms/')
      ]);
      setPatients(patientsRes.data);
      setAssessments(assessmentsRes.data);
      setSymptoms(symptomsRes.data);
    } catch (err) {
      console.error("Error loading dashboard data", err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      const res = await axios.post(`${backendUrl}/auth/login`, {
        email: authEmail,
        password: authPassword
      });
      const receivedToken = res.data.access_token;
      localStorage.setItem('token', receivedToken);
      setToken(receivedToken);
      setActiveTab('dashboard');
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      await axios.post(`${backendUrl}/auth/register`, {
        email: authEmail,
        password: authPassword,
        full_name: authName,
        role: 'doctor'
      });
      setIsRegistering(false);
      setAuthError('Account registered successfully. Please log in.');
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Registration failed. Try again.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setUser(null);
    setAssessments([]);
    setPatients([]);
  };

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/patients/', {
        name: newPatient.name,
        age: parseInt(newPatient.age),
        gender: newPatient.gender,
        height: parseFloat(newPatient.height),
        weight: parseFloat(newPatient.weight)
      });
      setPatients([res.data, ...patients]);
      setSelectedPatientId(res.data.id);
      setNewPatient({ name: '', age: 40, gender: 'Male', height: 170, weight: 70 });
      setWizardStep(2); // advance wizard
    } catch (err) {
      alert("Error creating patient profile");
    }
  };

  const handleRunAssessment = async () => {
    if (!selectedPatientId) return alert("Please select or create a patient first.");
    setAssessmentLoading(true);
    try {
      const payload = {
        patient_id: selectedPatientId,
        blood_pressure_systolic: parseInt(wizardVitals.systolic),
        blood_pressure_diastolic: parseInt(wizardVitals.diastolic),
        heart_rate: parseInt(wizardVitals.heartRate),
        temperature: parseFloat(wizardVitals.temp),
        respiratory_rate: parseInt(wizardVitals.respRate),
        oxygen_saturation: parseInt(wizardVitals.spo2),
        blood_sugar: wizardVitals.bloodSugar !== '' ? parseInt(wizardVitals.bloodSugar) : null,
        symptoms: selectedSymptomCodes,
        lifestyle: wizardLifestyle,
        medical_history: wizardHistory
      };
      
      const res = await api.post('/assessments/', payload);
      setAssessments([res.data, ...assessments]);
      setSelectedAssessment(res.data);
      // Reset wizard
      setWizardStep(1);
      setSelectedSymptomCodes([]);
      setWizardVitals({ systolic: 120, diastolic: 80, heartRate: 72, temp: 36.6, respRate: 16, spo2: 98, bloodSugar: '' });
      
      // Go to report detail
      setActiveTab('reports');
    } catch (err) {
      console.error(err);
      alert("Failed to submit health assessment.");
    } finally {
      setAssessmentLoading(false);
    }
  };

  const downloadReportPdf = async (assessmentId) => {
    try {
      const res = await api.get(`/assessments/${assessmentId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assessment_report_${assessmentId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Error generating PDF download.");
    }
  };

  const handleKbSearch = async (e) => {
    e.preventDefault();
    if (!kbQuery.trim()) return;
    setKbLoading(true);
    try {
      // Direct post to semantic guidelines
      const res = await api.get(`/symptoms/?search=${kbQuery}`);
      // Fallback display
      setKbResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setKbLoading(false);
    }
  };

  const updateSettingUrl = (url) => {
    setBackendUrl(url);
    localStorage.setItem('backend_url', url);
    alert("Backend URL updated successfully.");
  };

  // Helper values
  const urgentCount = (assessments || []).filter(a => a.priority === 'EMERGENCY' || a.priority === 'HIGH').length;
  if (!token) {
    // Authenticate overlay
    return (
      <div className={`min-h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-950 px-4 transition-colors duration-200 ${darkMode ? 'dark' : ''}`}>
        <div className="w-full max-w-md bg-white dark:bg-slate-900 shadow-xl rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 p-8 glass">
          <div className="text-center mb-6">
            <div className="inline-flex p-3 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-400 mb-2">
              <Activity className="h-8 w-8 animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">Explainable CDSS</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              General Health Assessment & Clinical Support Framework
            </p>
          </div>

          <form onSubmit={isRegistering ? handleRegister : handleLogin} className="space-y-4">
            {isRegistering && (
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">Full Name</label>
                <input 
                  type="text" 
                  value={authName}
                  onChange={(e) => setAuthName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                  placeholder="Dr. Alexander Fleming"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">Email Address</label>
              <input 
                type="email" 
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                placeholder="clinician@hospital.org"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">Password</label>
              <input 
                type="password" 
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                placeholder="••••••••"
                required
              />
            </div>

            {authError && (
              <div className="p-3 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200 dark:border-red-900/50 flex gap-2">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{authError}</span>
              </div>
            )}

            <button 
              type="submit" 
              disabled={authLoading}
              className="w-full py-3 px-4 bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2 shadow"
            >
              {authLoading && <RefreshCw className="h-4 w-4 animate-spin" />}
              {isRegistering ? 'Register Clinician Profile' : 'Access Clinical Dashboard'}
            </button>
          </form>

          <div className="mt-6 text-center text-xs">
            <button 
              type="button"
              onClick={() => { setIsRegistering(!isRegistering); setAuthError(''); }}
              className="text-brand-600 dark:text-brand-400 font-semibold hover:underline"
            >
              {isRegistering ? 'Already have an account? Sign In' : 'Create new clinical profile'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Filtered patients list
  const filteredPatients = patients.filter(p => 
    p.name.toLowerCase().includes(patientSearch.toLowerCase())
  );

  return (
    <div className={`min-h-screen flex bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200 ${darkMode ? 'dark' : ''}`}>
      
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col shrink-0">
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center gap-3">
          <Activity className="h-7 w-7 text-brand-600 dark:text-brand-400 animate-pulse" />
          <div>
            <h2 className="text-md font-bold tracking-tight">CDSS Suite</h2>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest font-semibold">Assessment v1.0</span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          <button 
            onClick={() => { setActiveTab('dashboard'); setSelectedAssessment(null); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'dashboard' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <Activity className="h-4 w-4" />
            <span>Dashboard</span>
          </button>

          <button 
            onClick={() => { setActiveTab('new-assessment'); setSelectedAssessment(null); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'new-assessment' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <Plus className="h-4 w-4" />
            <span>New Assessment</span>
          </button>

          <button 
            onClick={() => { setActiveTab('patients'); setSelectedAssessment(null); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'patients' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <Users className="h-4 w-4" />
            <span>Patient Profiles</span>
          </button>

          <button 
            onClick={() => { setActiveTab('reports'); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'reports' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <Clipboard className="h-4 w-4" />
            <span>Reports & Timeline</span>
          </button>

          <button 
            onClick={() => { setActiveTab('knowledge-base'); setSelectedAssessment(null); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'knowledge-base' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <BookOpen className="h-4 w-4" />
            <span>Knowledge Base</span>
          </button>

          <button 
            onClick={() => { setActiveTab('settings'); setSelectedAssessment(null); }}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'settings' ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border-l-4 border-brand-600' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'}`}
          >
            <Settings className="h-4 w-4" />
            <span>System Settings</span>
          </button>
        </nav>

        {/* BOTTOM USER PANEL */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 flex flex-col gap-2">
          {user && (
            <div className="flex items-center gap-2 px-2 py-1">
              <div className="h-8 w-8 rounded-full bg-brand-500 flex items-center justify-center font-bold text-white text-xs">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold truncate">{user.full_name}</p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate uppercase font-semibold">{user.role}</p>
              </div>
            </div>
          )}
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-xs font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 transition"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Logout Session</span>
          </button>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-bold tracking-tight text-slate-800 dark:text-white capitalize">
              {activeTab.replace('-', ' ')}
            </h1>
            {activeTab === 'dashboard' && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-400 flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping"></span>
                Services Active
              </span>
            )}
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <div className="text-right">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Clinical Workspace</p>
              <p className="text-xs font-semibold text-slate-500">{new Date().toDateString()}</p>
            </div>
          </div>
        </header>

        {/* TAB VIEWS RENDER */}
        <div className="flex-1 p-8 space-y-8">
          
          {/* TAB 1: CLINICAL DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* TOP ROW STATS */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Assessments Run</span>
                    <h3 className="text-3xl font-extrabold mt-1">{assessments.length}</h3>
                  </div>
                  <div className="p-3 bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 rounded-xl">
                    <Clipboard className="h-6 w-6" />
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Critical Overrides</span>
                    <h3 className="text-3xl font-extrabold mt-1 text-red-600 dark:text-red-400">{urgentCount}</h3>
                  </div>
                  <div className="p-3 bg-red-100 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded-xl">
                    <AlertTriangle className="h-6 w-6" />
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Active Patients</span>
                    <h3 className="text-3xl font-extrabold mt-1">{patients.length}</h3>
                  </div>
                  <div className="p-3 bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 rounded-xl">
                    <Users className="h-6 w-6" />
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Symptoms Catalog</span>
                    <h3 className="text-3xl font-extrabold mt-1">{symptoms.length}</h3>
                  </div>
                  <div className="p-3 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-xl">
                    <Activity className="h-6 w-6" />
                  </div>
                </div>
              </div>

              {/* QUICK DISMISS DISCLAIMER */}
              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-900/50 rounded-xl text-xs flex gap-3">
                <Info className="h-5 w-5 shrink-0 text-blue-500" />
                <div>
                  <p className="font-bold uppercase tracking-wider mb-0.5">Clinical Decision Support Tool Notice</p>
                  <p>
                    This workspace combines Machine Learning risk models (XGBoost/Sklearn) and Local LLM (Llama 3) vector search pipelines to assist general diagnosis. It serves as clinical workflow support only and does not declare confirmed diagnosis.
                  </p>
                </div>
              </div>

              {/* CLINICAL METRICS GRID */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* LATEST LOGS TIMELINE */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 lg:col-span-2">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Recent Health Assessments</h3>
                    <button onClick={() => setActiveTab('reports')} className="text-xs text-brand-600 dark:text-brand-400 font-semibold hover:underline">View All</button>
                  </div>
                  
                  {assessments.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">
                      <Clipboard className="h-10 w-10 mx-auto mb-2 opacity-40" />
                      <p className="text-sm">No clinical evaluations logged yet.</p>
                      <button onClick={() => setActiveTab('new-assessment')} className="mt-3 text-xs bg-brand-600 text-white px-3 py-1.5 rounded-lg">Run Initial Screen</button>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-medium">
                            <th className="py-3">Patient</th>
                            <th className="py-3">Vitals Check</th>
                            <th className="py-3">Priority Override</th>
                            <th className="py-3">Date</th>
                            <th className="py-3 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-y-slate-100 dark:divide-slate-800">
                          {assessments.slice(0, 5).map(evalRec => (
                            <tr key={evalRec.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                              <td className="py-3 font-semibold text-slate-800 dark:text-white">
                                {patients.find(p => p.id === evalRec.patient_id)?.name || 'Unknown Patient'}
                              </td>
                              <td className="py-3 text-xs">
                                BP: {evalRec.blood_pressure_systolic}/{evalRec.blood_pressure_diastolic} | SpO2: {evalRec.oxygen_saturation}%
                              </td>
                              <td className="py-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  evalRec.priority === 'EMERGENCY' ? 'bg-red-100 text-red-800 dark:bg-red-950/40 dark:text-red-400' :
                                  evalRec.priority === 'HIGH' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400' :
                                  'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
                                }`}>
                                  {evalRec.priority}
                                </span>
                              </td>
                              <td className="py-3 text-xs text-slate-500">
                                {new Date(evalRec.created_at).toLocaleDateString()}
                              </td>
                              <td className="py-3 text-right">
                                <button 
                                  onClick={() => { setSelectedAssessment(evalRec); setActiveTab('reports'); }}
                                  className="p-1 text-brand-600 dark:text-brand-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                                >
                                  <ChevronRight className="h-4 w-4" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* PATIENT DEMOGRAPHICS OVERVIEW */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Patient Registrations</h3>
                  
                  {patients.length === 0 ? (
                    <p className="text-sm text-slate-400 text-center py-12">No patient files on record.</p>
                  ) : (
                    <div className="space-y-4 overflow-y-auto max-h-[300px] pr-1">
                      {patients.slice(0, 5).map(pat => (
                        <div key={pat.id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl">
                          <div>
                            <p className="text-sm font-semibold">{pat.name}</p>
                            <p className="text-xs text-slate-400">{pat.age} yrs • {pat.gender} • {pat.weight} kg</p>
                          </div>
                          <button 
                            onClick={() => { setSelectedPatientId(pat.id); setWizardStep(2); setActiveTab('new-assessment'); }}
                            className="text-xs text-brand-600 dark:text-brand-400 font-bold flex items-center gap-1 hover:underline"
                          >
                            New Screen <Plus className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: NEW ASSESSMENT WIZARD */}
          {activeTab === 'new-assessment' && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-8 glass max-w-4xl mx-auto">
              
              {/* STAGE HEADER BAR */}
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-6 mb-8">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-brand-100 dark:bg-brand-900/40 text-brand-600 dark:text-brand-400 rounded-xl">
                    <Activity className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">Evaluation Wizard</h3>
                    <p className="text-xs text-slate-400">Step {wizardStep} of 4: Setup input variables</p>
                  </div>
                </div>

                <div className="flex gap-1.5">
                  {[1, 2, 3, 4].map(stepNum => (
                    <div 
                      key={stepNum} 
                      className={`h-1.5 w-10 rounded-full transition-all ${
                        wizardStep >= stepNum ? 'bg-brand-600 dark:bg-brand-500' : 'bg-slate-200 dark:bg-slate-800'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* STEP 1: PATIENT PROFILE SELECTION OR CREATION */}
              {wizardStep === 1 && (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-md font-semibold mb-2">Select Existing Patient Profile</h4>
                    <div className="relative mb-3">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                      <input 
                        type="text"
                        value={patientSearch}
                        onChange={(e) => setPatientSearch(e.target.value)}
                        placeholder="Search patient profiles..."
                        className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[180px] overflow-y-auto pr-1">
                      {filteredPatients.map(p => (
                        <div 
                          key={p.id}
                          onClick={() => setSelectedPatientId(p.id)}
                          className={`p-3 border rounded-xl cursor-pointer transition flex items-center justify-between ${
                            selectedPatientId === p.id 
                              ? 'border-brand-500 bg-brand-50/20 dark:bg-brand-950/20' 
                              : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                          }`}
                        >
                          <div>
                            <p className="text-sm font-semibold">{p.name}</p>
                            <p className="text-xs text-slate-400">{p.age} yrs • {p.gender} • {p.height} cm • {p.weight} kg</p>
                          </div>
                          {selectedPatientId === p.id && <Check className="h-4 w-4 text-brand-600 dark:text-brand-400" />}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="relative border-t border-slate-200 dark:border-slate-800 pt-6">
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-white dark:bg-slate-900 px-3 text-xs text-slate-400 uppercase font-semibold">Or Create Profile</span>
                    
                    <form onSubmit={handleCreatePatient} className="grid grid-cols-1 md:grid-cols-5 gap-4">
                      <div className="md:col-span-2">
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Full Name</label>
                        <input 
                          type="text" 
                          required
                          value={newPatient.name}
                          onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                          placeholder="John Doe"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Age</label>
                        <input 
                          type="number" 
                          required
                          value={newPatient.age}
                          onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Gender</label>
                        <select 
                          value={newPatient.gender}
                          onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
                        >
                          <option>Male</option>
                          <option>Female</option>
                          <option>Other</option>
                        </select>
                      </div>
                      <div className="flex items-end">
                        <button 
                          type="submit"
                          className="w-full py-2 bg-brand-600 text-white rounded-lg text-xs font-semibold hover:bg-brand-700 transition"
                        >
                          Save Profile
                        </button>
                      </div>
                    </form>
                  </div>

                  <div className="flex justify-end pt-4 border-t border-slate-200 dark:border-slate-800">
                    <button 
                      disabled={!selectedPatientId}
                      onClick={() => setWizardStep(2)}
                      className="px-6 py-2 bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold rounded-lg hover:bg-brand-700"
                    >
                      Next: Enter Vitals
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2: VITALS ENTRY */}
              {wizardStep === 2 && (
                <div className="space-y-6">
                  <h4 className="text-md font-semibold">Log Vital Signs</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Systolic BP (mmHg)</label>
                      <input 
                        type="number"
                        value={wizardVitals.systolic}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, systolic: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Diastolic BP (mmHg)</label>
                      <input 
                        type="number"
                        value={wizardVitals.diastolic}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, diastolic: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Heart Rate (bpm)</label>
                      <input 
                        type="number"
                        value={wizardVitals.heartRate}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, heartRate: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Temperature (°C)</label>
                      <input 
                        type="number"
                        step="0.1"
                        value={wizardVitals.temp}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, temp: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Oxygen Saturation (%)</label>
                      <input 
                        type="number"
                        value={wizardVitals.spo2}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, spo2: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Respiration Rate (/min)</label>
                      <input 
                        type="number"
                        value={wizardVitals.respRate}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, respRate: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Blood Sugar (mg/dL - Optional)</label>
                      <input 
                        type="number"
                        value={wizardVitals.bloodSugar}
                        onChange={(e) => setWizardVitals({ ...wizardVitals, bloodSugar: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                        placeholder="Fast/Random blood glucose"
                      />
                    </div>
                  </div>

                  <div className="flex justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
                    <button 
                      onClick={() => setWizardStep(1)}
                      className="px-6 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-500 hover:bg-slate-50"
                    >
                      Back
                    </button>
                    <button 
                      onClick={() => setWizardStep(3)}
                      className="px-6 py-2 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700"
                    >
                      Next: Choose Symptoms
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 3: SYMPTOMS SEARCH AND SELECTION (100+ CATALOG) */}
              {wizardStep === 3 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h4 className="text-md font-semibold">Select Patient Symptoms</h4>
                    <span className="text-xs bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-full font-bold text-brand-600 dark:text-brand-400">
                      {selectedSymptomCodes.length} Selected
                    </span>
                  </div>

                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <input 
                      type="text"
                      value={symptomSearch}
                      onChange={(e) => setSymptomSearch(e.target.value)}
                      placeholder="Search symptom index (e.g. fever, chest pain, numbness)..."
                      className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent"
                    />
                  </div>

                  {/* SEARCH RESULTS SYMPTOMS */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-[300px] overflow-y-auto pr-1">
                    {symptoms.filter(sym => 
                      sym.name.toLowerCase().includes(symptomSearch.toLowerCase()) ||
                      sym.category.toLowerCase().includes(symptomSearch.toLowerCase())
                    ).map(sym => {
                      const isSelected = selectedSymptomCodes.includes(sym.code);
                      return (
                        <div 
                          key={sym.id}
                          onClick={() => {
                            if (isSelected) {
                              setSelectedSymptomCodes(selectedSymptomCodes.filter(c => c !== sym.code));
                            } else {
                              setSelectedSymptomCodes([...selectedSymptomCodes, sym.code]);
                            }
                          }}
                          className={`p-3 border rounded-xl cursor-pointer transition flex items-start gap-2.5 ${
                            isSelected 
                              ? 'border-brand-500 bg-brand-50/20 dark:bg-brand-950/20' 
                              : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                          }`}
                        >
                          <div className={`mt-0.5 h-4 w-4 shrink-0 rounded border flex items-center justify-center ${
                            isSelected ? 'bg-brand-600 border-brand-600 text-white' : 'border-slate-300'
                          }`}>
                            {isSelected && <Check className="h-3 w-3" />}
                          </div>
                          <div>
                            <p className="text-xs font-semibold leading-none mb-1 flex items-center gap-1.5">
                              {sym.name}
                              {sym.is_red_flag && (
                                <span className="h-1.5 w-1.5 rounded-full bg-red-500" title="Emergency Red Flag" />
                              )}
                            </p>
                            <span className="text-[9px] text-slate-400 uppercase font-bold">{sym.category}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
                    <button 
                      onClick={() => setWizardStep(2)}
                      className="px-6 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-500 hover:bg-slate-50"
                    >
                      Back
                    </button>
                    <button 
                      onClick={() => setWizardStep(4)}
                      className="px-6 py-2 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700"
                    >
                      Next: Patient History
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 4: LIFESTYLE & MEDICAL HISTORY */}
              {wizardStep === 4 && (
                <div className="space-y-6">
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Lifestyle column */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Lifestyle Metrics</h4>
                      
                      <div>
                        <label className="block text-xs font-semibold mb-1">Smoking status</label>
                        <select 
                          value={wizardLifestyle.smoking}
                          onChange={(e) => setWizardLifestyle({ ...wizardLifestyle, smoking: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
                        >
                          <option value="never">Never smoked</option>
                          <option value="former">Former smoker</option>
                          <option value="active">Active smoker (moderate)</option>
                          <option value="heavy">Active smoker (heavy)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold mb-1">Alcohol Consumption</label>
                        <select 
                          value={wizardLifestyle.alcohol}
                          onChange={(e) => setWizardLifestyle({ ...wizardLifestyle, alcohol: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
                        >
                          <option value="none">None / Non-drinker</option>
                          <option value="moderate">Moderate consumption</option>
                          <option value="heavy">Frequent / Heavy drinker</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold mb-1">Weekly Physical Exercise</label>
                        <select 
                          value={wizardLifestyle.exercise}
                          onChange={(e) => setWizardLifestyle({ ...wizardLifestyle, exercise: e.target.value })}
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
                        >
                          <option value="none">Sedentary (no active exercise)</option>
                          <option value="moderate">Moderate (1-3 days/week)</option>
                          <option value="active">Active (4-7 days/week)</option>
                        </select>
                      </div>
                    </div>

                    {/* Medical history column */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Clinical Medical History</h4>
                      
                      <div className="grid grid-cols-2 gap-3 pt-2">
                        {Object.keys(wizardHistory).filter(k => typeof wizardHistory[k] === 'boolean').map(keyName => (
                          <div 
                            key={keyName}
                            onClick={() => setWizardHistory({ ...wizardHistory, [keyName]: !wizardHistory[keyName] })}
                            className={`p-2.5 border rounded-lg cursor-pointer transition flex items-center justify-between ${
                              wizardHistory[keyName] 
                                ? 'border-brand-500 bg-brand-50/20 dark:bg-brand-950/20' 
                                : 'border-slate-200 dark:border-slate-800'
                            }`}
                          >
                            <span className="text-xs font-semibold capitalize">{keyName.replace('_', ' ')}</span>
                            <div className={`h-4 w-4 rounded-full border flex items-center justify-center ${
                              wizardHistory[keyName] ? 'bg-brand-600 border-brand-600 text-white' : 'border-slate-300'
                            }`}>
                              {wizardHistory[keyName] && <Check className="h-2.5 w-2.5" />}
                            </div>
                          </div>
                        ))}
                      </div>

                      <div>
                        <label className="block text-xs font-semibold mb-1">Medications or Allergies</label>
                        <textarea 
                          value={wizardHistory.allergies}
                          onChange={(e) => setWizardHistory({ ...wizardHistory, allergies: e.target.value })}
                          rows="2"
                          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                          placeholder="List current medications and allergies (e.g. penicillin)"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between pt-6 border-t border-slate-200 dark:border-slate-800">
                    <button 
                      onClick={() => setWizardStep(3)}
                      className="px-6 py-2 border border-slate-300 dark:border-slate-700 rounded-lg text-sm text-slate-500 hover:bg-slate-50"
                    >
                      Back
                    </button>
                    
                    <button 
                      onClick={handleRunAssessment}
                      disabled={assessmentLoading}
                      className="px-8 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg flex items-center gap-2 shadow"
                    >
                      {assessmentLoading && <RefreshCw className="h-4 w-4 animate-spin" />}
                      Run Clinical Assessment Engine
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: PATIENT PROFILES LIST */}
          {activeTab === 'patients' && (
            <div className="space-y-6 max-w-5xl mx-auto">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Database Patient Directory</h3>
                <button 
                  onClick={() => { setSelectedPatientId(''); setWizardStep(1); setActiveTab('new-assessment'); }}
                  className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center gap-1 shadow"
                >
                  <Plus className="h-4 w-4" /> Add Patient Profile
                </button>
              </div>

              <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-medium">
                        <th className="py-3">Name</th>
                        <th className="py-3">Age</th>
                        <th className="py-3">Gender</th>
                        <th className="py-3">Height / Weight</th>
                        <th className="py-3">Register Date</th>
                        <th className="py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {patients.map(p => (
                        <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                          <td className="py-3 font-semibold text-slate-800 dark:text-white">{p.name}</td>
                          <td className="py-3">{p.age} years</td>
                          <td className="py-3">{p.gender}</td>
                          <td className="py-3">{p.height} cm / {p.weight} kg</td>
                          <td className="py-3 text-slate-500">{new Date(p.created_at).toLocaleDateString()}</td>
                          <td className="py-3 text-right space-x-2">
                            <button 
                              onClick={() => { setSelectedPatientId(p.id); setWizardStep(2); setActiveTab('new-assessment'); }}
                              className="text-xs bg-brand-50 dark:bg-brand-950/20 text-brand-600 dark:text-brand-400 font-bold px-2 py-1 rounded"
                            >
                              Assess Patient
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: REPORTS & TIMELINE */}
          {activeTab === 'reports' && (
            <div className="space-y-6 max-w-6xl mx-auto">
              {!selectedAssessment ? (
                <div className="space-y-4">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Clinical Evaluation Records</h3>
                  <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm text-left">
                        <thead>
                          <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-medium">
                            <th className="py-3">Patient Profile</th>
                            <th className="py-3">Systolic/Diastolic</th>
                            <th className="py-3">Blood Sugar</th>
                            <th className="py-3">Emergency Override</th>
                            <th className="py-3">Evaluation Date</th>
                            <th className="py-3 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                          {assessments.map(item => {
                            const patient = patients.find(p => p.id === item.patient_id);
                            return (
                              <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30">
                                <td className="py-3">
                                  <p className="font-semibold text-slate-800 dark:text-white">{patient?.name || 'Unknown'}</p>
                                  <p className="text-[10px] text-slate-400">{patient?.age} yrs • {patient?.gender}</p>
                                </td>
                                <td className="py-3">{item.blood_pressure_systolic}/{item.blood_pressure_diastolic} mmHg</td>
                                <td className="py-3">{item.blood_sugar ? `${item.blood_sugar} mg/dL` : 'Not tested'}</td>
                                <td className="py-3">
                                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                                    item.priority === 'EMERGENCY' ? 'bg-red-100 text-red-800 dark:bg-red-950/40 dark:text-red-400' :
                                    item.priority === 'HIGH' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400' :
                                    'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
                                  }`}>
                                    {item.priority}
                                  </span>
                                </td>
                                <td className="py-3 text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
                                <td className="py-3 text-right space-x-2">
                                  <button 
                                    onClick={() => setSelectedAssessment(item)}
                                    className="text-xs bg-brand-600 hover:bg-brand-700 text-white px-2.5 py-1 rounded"
                                  >
                                    Inspect report
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                // REPORT DETAILED SCREEN
                <div className="space-y-6">
                  <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                    <button 
                      onClick={() => setSelectedAssessment(null)}
                      className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-white font-bold"
                    >
                      ← Back to evaluation records
                    </button>
                    
                    <button 
                      onClick={() => downloadReportPdf(selectedAssessment.id)}
                      className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center gap-1 shadow"
                    >
                      <Download className="h-4 w-4" /> Download PDF Report
                    </button>
                  </div>

                  {/* TWO COLUMN INSPECT LAYOUT */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    {/* LEFT COLUMN: PATIENT AND SHAP MODEL PROBABILITIES */}
                    <div className="space-y-6">
                      {/* Vitals overview box */}
                      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Patient Vitals Profile</h4>
                        <div className="space-y-3 text-sm">
                          <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="text-slate-400">Assessed Patient:</span>
                            <span className="font-semibold">{selectedAssessment.patient?.name}</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="text-slate-400">Age / Gender:</span>
                            <span>{selectedAssessment.patient?.age} yrs / {selectedAssessment.patient?.gender}</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="text-slate-400">Blood Pressure:</span>
                            <span>{selectedAssessment.blood_pressure_systolic}/{selectedAssessment.blood_pressure_diastolic} mmHg</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="text-slate-400">Oxygen Saturation (SpO2):</span>
                            <span className={selectedAssessment.oxygen_saturation < 92 ? 'text-red-500 font-bold' : ''}>
                              {selectedAssessment.oxygen_saturation}%
                            </span>
                          </div>
                          <div className="flex justify-between pb-2">
                            <span className="text-slate-400">Blood Glucose:</span>
                            <span>{selectedAssessment.blood_sugar ? `${selectedAssessment.blood_sugar} mg/dL` : 'N/A'}</span>
                          </div>
                        </div>
                      </div>

                      {/* ML Classifier results and SHAP attributions */}
                      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 space-y-4">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Disease Risk Estimates</h4>
                        
                        <div className="space-y-4">
                          {selectedAssessment.predictions?.map(p => (
                            <div key={p.id} className="space-y-1">
                              <div className="flex justify-between text-xs">
                                <span className="font-semibold">{p.disease}</span>
                                <span className={`font-bold ${
                                  p.risk_level === 'HIGH' ? 'text-red-600 dark:text-red-400' :
                                  p.risk_level === 'MEDIUM' ? 'text-amber-600 dark:text-amber-400' :
                                  'text-emerald-600 dark:text-emerald-400'
                                }`}>
                                  {(p.probability * 100).toFixed(1)}% ({p.risk_level})
                                </span>
                              </div>
                              <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${
                                    p.risk_level === 'HIGH' ? 'bg-red-500' :
                                    p.risk_level === 'MEDIUM' ? 'bg-amber-500' :
                                    'bg-emerald-500'
                                  }`} 
                                  style={{ width: `${p.probability * 100}%` }}
                                />
                              </div>
                              
                              {/* SHAP explanation snippet */}
                              {p.shap_data?.natural_language_explanation && (
                                <p className="text-[10px] text-slate-500 leading-tight italic bg-slate-50 dark:bg-slate-800/40 p-2 rounded mt-1 border border-slate-100 dark:border-slate-800">
                                  {p.shap_data.natural_language_explanation}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* RIGHT COLUMN: RAG SUMMARY AND RETRIEVED TEXT EVIDENCE */}
                    <div className="lg:col-span-2 space-y-6">
                      
                      {/* LLM Synthesis panel */}
                      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3 mb-4">
                          <Activity className="h-5 w-5 text-brand-600 dark:text-brand-400" />
                          <h4 className="text-sm font-bold uppercase tracking-wider">Clinical Evidence Synthesizer</h4>
                        </div>
                        
                        <div className="text-sm leading-relaxed whitespace-pre-line text-slate-800 dark:text-slate-200 space-y-4">
                          {selectedAssessment.reports?.[0]?.llm_diagnosis || 'Synthesis summary generation pending.'}
                        </div>
                      </div>

                      {/* Vector Search Grounding */}
                      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">ChromaDB Grounded Sources</h4>
                        
                        <div className="space-y-3">
                          {selectedAssessment.reports?.[0]?.retrieved_evidence?.map((ev, index) => (
                            <div key={index} className="p-3.5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/50 dark:border-slate-800/50">
                              <p className="text-xs font-bold text-brand-600 dark:text-brand-400 mb-1">{ev.metadata?.source || 'NHS Guidelines'}</p>
                              <p className="text-xs text-slate-600 dark:text-slate-300 leading-normal">{ev.text}</p>
                            </div>
                          ))}
                          {(!selectedAssessment.reports?.[0]?.retrieved_evidence || selectedAssessment.reports[0].retrieved_evidence.length === 0) && (
                            <p className="text-xs text-slate-400">No medical references were retrieved for this assessment.</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: KNOWLEDGE BASE EXPLORER */}
          {activeTab === 'knowledge-base' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="text-center max-w-xl mx-auto mb-6">
                <BookOpen className="h-10 w-10 text-brand-600 dark:text-brand-400 mx-auto mb-2" />
                <h3 className="text-lg font-bold">Medical Knowledge Base Directory</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Query the local vector index directly to review clinical staging guidelines, diagnostic criteria, or preventive interventions.
                </p>
              </div>

              <form onSubmit={handleKbSearch} className="flex gap-2">
                <input 
                  type="text" 
                  value={kbQuery}
                  onChange={(e) => setKbQuery(e.target.value)}
                  placeholder="Enter medical terms (e.g., stroke tpa window, diabetes staging, hypertensive crisis)..."
                  className="flex-1 px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                  required
                />
                <button 
                  type="submit"
                  disabled={kbLoading}
                  className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-6 py-2.5 rounded-lg text-sm flex items-center gap-1 shadow"
                >
                  {kbLoading && <RefreshCw className="h-4 w-4 animate-spin" />}
                  Search Index
                </button>
              </form>

              <div className="space-y-4 mt-6">
                {kbResults.length > 0 ? (
                  kbResults.map((item, idx) => (
                    <div key={idx} className="bg-white dark:bg-slate-900 p-5 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
                      <span className="text-[10px] bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-400 px-2 py-0.5 rounded font-bold uppercase">
                        Symptom Database: {item.category}
                      </span>
                      <h4 className="text-md font-bold mt-2 text-slate-800 dark:text-white">{item.name}</h4>
                      <p className="text-sm text-slate-600 dark:text-slate-300 mt-1.5 leading-relaxed">{item.description || 'No description available.'}</p>
                      {item.is_red_flag && (
                        <div className="mt-3 inline-flex items-center gap-1.5 text-xs text-red-600 bg-red-50 dark:bg-red-950/20 px-2 py-0.5 rounded font-semibold border border-red-200 dark:border-red-900/50">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          <span>Emergency Red Flag Modifier</span>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 bg-white dark:bg-slate-900 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-slate-400">
                    <Search className="h-8 w-8 mx-auto mb-2 opacity-40" />
                    <p className="text-sm">Search symptom definitions above.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 6: SYSTEM SETTINGS */}
          {activeTab === 'settings' && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-8 glass max-w-2xl mx-auto space-y-8">
              
              <div className="space-y-4">
                <h4 className="text-md font-semibold border-b border-slate-100 dark:border-slate-800 pb-2">Environment Configuration</h4>
                
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">FastAPI Backend Endpoint</label>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      defaultValue={backendUrl}
                      id="backendUrlInput"
                      className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-transparent text-sm"
                    />
                    <button 
                      onClick={() => updateSettingUrl(document.getElementById('backendUrlInput').value)}
                      className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-4 py-2 rounded-lg"
                    >
                      Update
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Local Ollama LLM Connection</label>
                  <input 
                    type="text" 
                    value="http://localhost:11434"
                    disabled
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 text-sm text-slate-400"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">Managed automatically by local server instance environments.</p>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-md font-semibold border-b border-slate-100 dark:border-slate-800 pb-2">Interface Preferences</h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold">Workspace Dark Mode</p>
                    <p className="text-xs text-slate-400">Toggle dark style sheets for medical workspace screens.</p>
                  </div>
                  <button 
                    onClick={() => setDarkMode(!darkMode)}
                    className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold rounded-lg transition"
                  >
                    {darkMode ? 'Switch to Light' : 'Switch to Dark'}
                  </button>
                </div>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl text-xs space-y-2 border border-slate-200 dark:border-slate-800">
                <p className="font-bold uppercase tracking-wider">System Specifications</p>
                <div className="grid grid-cols-2 gap-2 text-slate-500">
                  <span>ML Classifiers:</span> <span className="text-slate-800 dark:text-slate-200 font-semibold">XGBoost & Random Forest</span>
                  <span>Explainability Layer:</span> <span className="text-slate-800 dark:text-slate-200 font-semibold">SHAP (TreeExplainer)</span>
                  <span>Vector Database:</span> <span className="text-slate-800 dark:text-slate-200 font-semibold">ChromaDB Persistant</span>
                  <span>LLM Core:</span> <span className="text-slate-800 dark:text-slate-200 font-semibold">Ollama / Llama 3 (8B Instruct Q4)</span>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
