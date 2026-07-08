"use client";

import React, { useState, useEffect } from "react";
import { Award, ShieldAlert, Zap, Map, FileText, Send, AlertTriangle, TrendingUp, RefreshCw, BarChart2, MessageSquare, Clock, ShieldCheck, Check, Shield } from "lucide-react";
import { api } from "@/lib/api";

interface KPI {
  total_grievances: number;
  open_grievances: number;
  resolved_grievances: number;
  closed_grievances: number;
  average_resolution_time_hrs: number;
  constituency_health_index: number;
  ward_health_breakdown: Record<string, number>;
}

interface WardHealth {
  ward_id: string;
  water_score: number;
  roads_score: number;
  electricity_score: number;
  education_score: number;
  healthcare_score: number;
  sanitation_score: number;
  safety_score: number;
  overall_health_index: number;
}

interface Grievance {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  priority_score: number;
  latitude?: number;
  longitude?: number;
  created_at: string;
}

export default function MPDashboard() {
  const [kpis, setKpis] = useState<KPI | null>(null);
  const [wardHealths, setWardHealths] = useState<WardHealth[]>([]);
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [selectedGrievance, setSelectedGrievance] = useState<any>(null);
  
  const [chatQuery, setChatQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState("password123");
  const [loginError, setLoginError] = useState("");
  const [selectedWard, setSelectedWard] = useState<string>("Ward 1 (Vasant Nagar)");

  const [activeTab, setActiveTab] = useState<"dashboard" | "map" | "oversight" | "policy">("dashboard");
  const [selectedPersona, setSelectedPersona] = useState("mp_vijayawada@sahayak.gov.in");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const authData = await api.login(selectedPersona, password);
      localStorage.setItem("token", authData.access_token);
      setUser(authData);
      await fetchData();
    } catch (err: any) {
      setLoginError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/mp`);
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "GRIEVANCE_SUBMITTED" || data.event === "GRIEVANCE_UPDATED") {
        fetchData();
      }
    };
    return () => ws.close();
  }, [user]);

  const fetchData = async () => {
    try {
      const kpiData = await api.getKPIs();
      setKpis(kpiData);
      
      const healthData = await api.getHealthIndices();
      setWardHealths(healthData);
      
      const list = await api.listGrievances();
      setGrievances(list);
    } catch (err) {
      console.error("Error fetching MP data:", err);
    }
  };

  const handleRecalculate = async () => {
    setLoading(true);
    try {
      await api.recalculateHealth();
      await fetchData();
    } catch (err: any) {
      alert(`Error updating: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleEscalate = async (gId: string, priority: string, hours: number) => {
    try {
      await api.mpEscalateGrievance(gId, priority, hours);
      fetchData();
      const updatedDetails = await api.getGrievanceDetail(gId);
      setSelectedGrievance(updatedDetails);
    } catch (err: any) {
      alert(`Error escalating: ${err.message}`);
    }
  };

  const handleInspectGrievance = async (id: string) => {
    try {
      const details = await api.getGrievanceDetail(id);
      setSelectedGrievance(details);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleSendPolicyChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;

    const query = chatQuery;
    setChatQuery("");
    setChatLoading(true);
    
    setChatHistory(prev => [...prev, { role: "user", text: query }]);

    try {
      const res = await api.policyChat(query);
      setChatHistory(prev => [
        ...prev,
        { role: "agent", text: res.answer, sources: res.sources }
      ]);
    } catch (err: any) {
      setChatHistory(prev => [...prev, { role: "system", text: `Error: ${err.message}` }]);
    } finally {
      setChatLoading(false);
    }
  };

  const selectedWardDetails = wardHealths.find(w => w.ward_id === selectedWard);
  const urgentGrievances = grievances.filter(g => g.status !== "CLOSED" && (g.priority === "HIGH" || g.priority === "EMERGENCY"));

  if (!user) {
    return (
      <main className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans text-slate-900">
        <div className="bg-white p-10 rounded-2xl shadow-xl border border-slate-200 max-w-md w-full">
          <div className="flex flex-col items-center mb-8 text-center">
            <div className="p-4 rounded-full bg-blue-900 text-white mb-4 shadow-md">
              <Shield className="w-10 h-10" />
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900">GovPortal Access</h1>
            <p className="text-base text-slate-500 mt-2">MP Constituency Governance Dashboard</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Select Jurisdiction</label>
              <select
                value={selectedPersona}
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-800"
              >
                <option value="mp_vijayawada@sahayak.gov.in">Vijayawada East (MP)</option>
                <option value="mp_guntur@sahayak.gov.in">Guntur West (MP)</option>
                <option value="mp_vizag@sahayak.gov.in">Vizag North (MP)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Security Key</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-800"
                required
              />
            </div>
            
            {loginError && <div className="text-red-600 text-sm font-semibold p-3 bg-red-50 rounded-lg">{loginError}</div>}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-blue-900 hover:bg-blue-800 text-white font-bold text-lg tracking-wide transition shadow-lg flex justify-center items-center gap-2"
            >
              {loading ? "Authenticating..." : "Secure Login"}
            </button>
          </form>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <header className="border-b border-slate-300 bg-blue-900 text-white px-8 py-5 flex justify-between items-center z-20 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="p-2.5 rounded-xl bg-white/10 text-white border border-white/20 shadow-inner">
            <Award className="w-7 h-7" />
          </div>
          <div>
            <h1 className="font-extrabold text-2xl tracking-tight">MP Governance Dashboard</h1>
            <p className="text-sm text-blue-200 font-medium mt-0.5">National Development & Oversight Center</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <select
            value={selectedPersona}
            onChange={(e) => setSelectedPersona(e.target.value)}
            className="bg-white/10 border border-white/20 text-sm text-white rounded-lg px-4 py-2 focus:outline-none font-semibold cursor-pointer"
          >
            <option className="text-black" value="mp_vijayawada@sahayak.gov.in">Vijayawada East (MP)</option>
            <option className="text-black" value="mp_guntur@sahayak.gov.in">Guntur West (MP)</option>
            <option className="text-black" value="mp_vizag@sahayak.gov.in">Vizag North (MP)</option>
          </select>
          
          <button
            onClick={handleRecalculate}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/30 bg-white/10 hover:bg-white/20 text-sm text-white font-bold transition shadow-sm cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Sync Indices
          </button>
          <div className="text-sm text-blue-200 font-bold border-l border-white/20 pl-6 flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white text-blue-900 flex justify-center items-center font-black">
              {user.name.charAt(0)}
            </div>
            {user.name}
          </div>
        </div>
      </header>
      
      <div className="px-8 border-b border-slate-200 bg-white flex gap-8 text-base font-bold shadow-sm z-10">
        <button
          onClick={() => setActiveTab("dashboard")}
          className={`py-4 px-2 border-b-4 transition ${activeTab === "dashboard" ? "border-blue-700 text-blue-800" : "border-transparent text-slate-500 hover:text-slate-800"}`}
        >
          Overview KPIs
        </button>
        <button
          onClick={() => setActiveTab("map")}
          className={`py-4 px-2 border-b-4 transition ${activeTab === "map" ? "border-blue-700 text-blue-800" : "border-transparent text-slate-500 hover:text-slate-800"}`}
        >
          Geo-Spatial Map
        </button>
        <button
          onClick={() => setActiveTab("oversight")}
          className={`py-4 px-2 border-b-4 transition ${activeTab === "oversight" ? "border-blue-700 text-blue-800" : "border-transparent text-slate-500 hover:text-slate-800"}`}
        >
          Oversight & Escalations
        </button>
        <button
          onClick={() => setActiveTab("policy")}
          className={`py-4 px-2 border-b-4 transition ${activeTab === "policy" ? "border-blue-700 text-blue-800" : "border-transparent text-slate-500 hover:text-slate-800"}`}
        >
          Policy Assistant
        </button>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-y-auto p-8 gap-8 max-h-[calc(100vh-140px)]">
        
        {/* KPI Grid */}
        <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="glass-panel p-6 flex flex-col justify-between">
            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Constituency Health</span>
            <div className="flex items-baseline gap-3 mt-4">
              <span className="text-5xl font-black text-blue-900">
                {kpis ? kpis.constituency_health_index : "--"}%
              </span>
              <span className="text-sm text-green-700 font-extrabold flex items-center gap-1 bg-green-50 px-2 py-1 rounded">
                <TrendingUp className="w-4 h-4" /> +1.2%
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Aggregate health across all 7 civic categories</p>
          </div>

          <div className="glass-panel p-6 flex flex-col justify-between">
            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Active Grievances</span>
            <div className="flex items-baseline gap-3 mt-4">
              <span className="text-5xl font-black text-slate-900">
                {kpis ? kpis.open_grievances : "--"}
              </span>
              <span className="text-sm text-slate-500 font-bold">Unresolved</span>
            </div>
            <p className="text-sm text-red-600 mt-3 font-bold flex items-center gap-1.5 bg-red-50 p-2 rounded-lg">
              <ShieldAlert className="w-5 h-5" /> {urgentGrievances.length} require immediate escalation
            </p>
          </div>

          <div className="glass-panel p-6 flex flex-col justify-between">
            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Resolved Complaints</span>
            <div className="flex items-baseline gap-3 mt-4">
              <span className="text-5xl font-black text-slate-900">
                {kpis ? kpis.resolved_grievances + kpis.closed_grievances : "--"}
              </span>
              <span className="text-sm text-green-700 font-bold bg-green-50 px-2 py-1 rounded">
                ({kpis ? kpis.closed_grievances : "--"} audited)
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Closed cases are audited via before-and-after checks</p>
          </div>

          <div className="glass-panel p-6 flex flex-col justify-between">
            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Avg Resolution Speed</span>
            <div className="flex items-baseline gap-3 mt-4">
              <span className="text-5xl font-black text-slate-900">
                {kpis ? kpis.average_resolution_time_hrs : "--"}
              </span>
              <span className="text-base text-slate-500 font-bold">hours</span>
            </div>
            <p className="text-sm text-slate-500 mt-3 font-medium">Target response time: under 24 hours</p>
          </div>
        </div>

        <div className="lg:col-span-12">
          {activeTab === "dashboard" && (
            <div className="flex flex-col items-center justify-center py-24 text-slate-400 h-80 border-2 border-dashed border-slate-300 rounded-2xl bg-white">
              <BarChart2 className="w-16 h-16 mb-6 text-blue-200" />
              <p className="text-lg font-semibold">Top level KPI metrics are shown above. Switch tabs to see detailed breakdown.</p>
            </div>
          )}

          {activeTab === "map" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-panel p-6 flex flex-col">
                <h3 className="text-lg font-black tracking-tight flex items-center gap-2 mb-4 text-slate-800">
                  <Map className="w-6 h-6 text-blue-700" /> Constituency Geographic Map
                </h3>
                
                <div className="h-80 bg-slate-100 rounded-xl relative overflow-hidden border border-slate-300 flex items-center justify-center p-4">
                  <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
                  
                  <div className="w-full h-full relative z-10">
                    {wardHealths.map((w, idx) => {
                      const pos = [
                        { top: "15%", left: "15%", w: "40%", h: "35%", color: "border-green-300 bg-green-50 hover:bg-green-100 text-green-900" },
                        { top: "50%", left: "10%", w: "35%", h: "40%", color: "border-blue-300 bg-blue-50 hover:bg-blue-100 text-blue-900" },
                        { top: "10%", left: "55%", w: "35%", h: "35%", color: "border-orange-300 bg-orange-50 hover:bg-orange-100 text-orange-900" },
                        { top: "45%", left: "48%", w: "45%", h: "25%", color: "border-red-300 bg-red-50 hover:bg-red-100 text-red-900" },
                        { top: "70%", left: "40%", w: "50%", h: "25%", color: "border-purple-300 bg-purple-50 hover:bg-purple-100 text-purple-900" }
                      ][idx];
                      const isSelected = selectedWard === w.ward_id;
                      
                      return (
                        <div
                          key={w.ward_id}
                          onClick={() => setSelectedWard(w.ward_id)}
                          style={{ top: pos.top, left: pos.left, width: pos.w, height: pos.h }}
                          className={`absolute border-2 rounded-xl cursor-pointer flex flex-col justify-center items-center p-3 text-center transition-all shadow-sm ${pos.color} ${
                            isSelected ? "ring-4 ring-blue-500 scale-[1.02] z-20" : ""
                          }`}
                        >
                          <span className="text-sm font-black truncate w-full">{w.ward_id.split(" ")[1]}</span>
                          <span className="text-xs font-bold mt-1 opacity-80">Health: {w.overall_health_index}%</span>
                        </div>
                      );
                    })}

                    {grievances.map((g, i) => {
                      if (g.status === "CLOSED") return null;
                      const pos = [
                        { top: "25%", left: "30%" }, { top: "65%", left: "25%" },
                        { top: "20%", left: "70%" }, { top: "55%", left: "60%" },
                        { top: "80%", left: "75%" }, { top: "50%", left: "55%" }
                      ][i % 6];
                      
                      const isEmergency = g.priority === "EMERGENCY";
                      const color = isEmergency ? "bg-red-600" : "bg-blue-600";
                      
                      return (
                        <div
                          key={g.id}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleInspectGrievance(g.id);
                          }}
                          style={{ top: pos.top, left: pos.left }}
                          className={`absolute w-5 h-5 rounded-full ${color} cursor-pointer z-30 flex items-center justify-center animate-bounce shadow-lg ring-4 ring-white`}
                          title={g.title}
                        >
                          <span className={`absolute w-10 h-10 rounded-full ${color} opacity-30 animate-ping`} />
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div className="flex gap-6 pt-5 text-sm font-bold text-slate-600 justify-center">
                  <span className="flex items-center gap-2"><span className="w-3.5 h-3.5 rounded-full bg-red-600 shadow-sm" /> Emergency</span>
                  <span className="flex items-center gap-2"><span className="w-3.5 h-3.5 rounded-full bg-blue-600 shadow-sm" /> Active Task</span>
                </div>
              </div>

              <div className="glass-panel p-6 flex flex-col gap-6">
                <div className="flex justify-between items-center border-b border-slate-200 pb-4">
                  <h3 className="text-lg font-black flex items-center gap-2 text-slate-800">
                    <BarChart2 className="w-6 h-6 text-green-700" /> Health Metric: {selectedWard.split(" ")[1]}
                  </h3>
                  <span className="text-lg text-green-700 font-black bg-green-50 px-3 py-1 rounded-lg border border-green-200">
                    Overall: {selectedWardDetails?.overall_health_index}%
                  </span>
                </div>

                {selectedWardDetails ? (
                  <div className="space-y-4">
                    {[
                      { name: "Water Supply", score: selectedWardDetails.water_score, color: "bg-blue-500" },
                      { name: "Road Maintenance", score: selectedWardDetails.roads_score, color: "bg-orange-500" },
                      { name: "Power Supply", score: selectedWardDetails.electricity_score, color: "bg-yellow-500" },
                      { name: "Sanitation & Waste", score: selectedWardDetails.sanitation_score, color: "bg-green-600" },
                      { name: "Public Safety", score: selectedWardDetails.safety_score, color: "bg-red-500" }
                    ].map(cat => (
                      <div key={cat.name} className="space-y-1.5">
                        <div className="flex justify-between text-sm text-slate-700 font-bold">
                          <span>{cat.name}</span>
                          <span className="text-slate-900">{cat.score}/100</span>
                        </div>
                        <div className="w-full h-3 rounded-full bg-slate-200 overflow-hidden shadow-inner">
                          <div className={`h-full rounded-full ${cat.color}`} style={{ width: `${cat.score}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-base text-slate-500 text-center py-10 font-medium">
                    Select a ward on the map to view detailed indices.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "oversight" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-panel p-6 flex flex-col flex-1 overflow-hidden h-[600px]">
                <h3 className="text-lg font-black flex items-center gap-2 border-b border-slate-200 pb-4 text-red-700 mb-4 bg-red-50 -mx-6 px-6 -mt-6 pt-6 rounded-t-xl">
                  <ShieldAlert className="w-6 h-6" /> Critical Escalation Queue ({urgentGrievances.length})
                </h3>
                
                <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                  {urgentGrievances.map(g => {
                    const isSelected = selectedGrievance?.id === g.id;
                    return (
                      <div
                        key={g.id}
                        onClick={() => handleInspectGrievance(g.id)}
                        className={`p-5 rounded-xl border-2 cursor-pointer transition-all shadow-sm ${
                          isSelected
                            ? "bg-red-50 border-red-400 ring-2 ring-red-200"
                            : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-md"
                        }`}
                      >
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-bold text-base truncate max-w-[70%] text-slate-900">{g.title}</h4>
                          <span className="text-xs font-black px-2.5 py-1 rounded-md bg-red-100 text-red-700 border border-red-200">
                            {g.priority}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 line-clamp-2 mt-2 leading-relaxed font-medium">
                          {g.description}
                        </p>
                        <div className="flex justify-between items-center text-xs font-bold text-slate-500 pt-4 border-t border-slate-100 mt-4">
                          <span>Status: <strong className="text-slate-800">{g.status}</strong></span>
                          <span>{new Date(g.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    );
                  })}
                  {urgentGrievances.length === 0 && (
                    <div className="text-center text-base text-slate-500 py-12 font-semibold">
                      No active critical escalations.
                    </div>
                  )}
                </div>
              </div>

              <div className="glass-panel p-6 flex flex-col gap-6">
                <h3 className="text-lg font-black flex items-center gap-2 border-b border-slate-200 pb-4 text-slate-800">
                  <Zap className="w-6 h-6 text-orange-500" /> Administrative Action Panel
                </h3>

                {selectedGrievance ? (
                  <div className="space-y-6 text-base">
                    <div className="bg-slate-50 p-5 rounded-xl border border-slate-200">
                      <h4 className="font-black text-slate-900 text-lg mb-2">Inspecting: {selectedGrievance.title}</h4>
                      <p className="text-sm font-bold text-slate-600">Current Status: <strong className="text-blue-700">{selectedGrievance.status}</strong> | Priority: <strong className="text-red-700">{selectedGrievance.priority}</strong></p>
                    </div>
                    
                    {selectedGrievance.status !== "CLOSED" ? (
                      <div className="space-y-4 pt-4 border-t border-slate-200">
                        <span className="font-black block text-sm uppercase tracking-wider text-slate-500">Official Escalation Directives:</span>
                        <div className="grid grid-cols-2 gap-4">
                          <button
                            onClick={() => handleEscalate(selectedGrievance.id, "EMERGENCY", 4)}
                            className="py-4 px-4 rounded-xl bg-red-600 hover:bg-red-700 border border-red-700 text-white font-black text-sm shadow-md transition text-center cursor-pointer flex flex-col items-center justify-center gap-1"
                          >
                            <span>Trigger Emergency Protocol</span>
                            <span className="text-xs font-medium text-red-200">(4 Hour Resolution Limit)</span>
                          </button>
                          <button
                            onClick={() => handleEscalate(selectedGrievance.id, "HIGH", 12)}
                            className="py-4 px-4 rounded-xl bg-orange-500 hover:bg-orange-600 border border-orange-600 text-white font-black text-sm shadow-md transition text-center cursor-pointer flex flex-col items-center justify-center gap-1"
                          >
                            <span>Standard Escalation</span>
                            <span className="text-xs font-medium text-orange-100">(12 Hour Resolution Limit)</span>
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="p-6 bg-green-50 border border-green-200 rounded-xl">
                        <p className="text-green-800 font-black flex items-center gap-2 text-lg"><ShieldCheck className="w-6 h-6" /> Grievance Officially Closed & Audited.</p>
                      </div>
                    )}

                    {/* Explainable AI Timeline */}
                    {selectedGrievance.audit_logs && selectedGrievance.audit_logs.length > 0 && (
                      <div className="mt-6 pt-6 border-t border-slate-200 space-y-4">
                        <span className="font-black block text-sm uppercase tracking-wider text-slate-500">Explainable Multi-Agent Workflow:</span>
                        <div className="relative border-l-2 border-blue-200 ml-3 pl-6 space-y-5">
                          {selectedGrievance.audit_logs.map((log: any) => {
                            const badgeColorMap: Record<string, string> = {
                              CitizenIntakeAgent: "bg-blue-100 text-blue-800 border-blue-200",
                              TranslationAgent: "bg-orange-100 text-orange-800 border-orange-200",
                              ClassificationAgent: "bg-purple-100 text-purple-800 border-purple-200",
                              PriorityScoringAgent: "bg-red-100 text-red-800 border-red-200",
                              DuplicateDetectionAgent: "bg-indigo-100 text-indigo-800 border-indigo-200",
                              RoutingAgent: "bg-teal-100 text-teal-800 border-teal-200",
                              OfficerAssistantAgent: "bg-pink-100 text-pink-800 border-pink-200",
                              ResolutionAssuranceAgent: "bg-green-100 text-green-800 border-green-200",
                              CitizenConfirmationAgent: "bg-slate-100 text-slate-800 border-slate-200",
                              PolicyIntelligenceAgent: "bg-emerald-100 text-emerald-800 border-emerald-200"
                            };
                            const badgeColor = badgeColorMap[log.action] || "bg-gray-100 text-gray-800 border-gray-200";

                            return (
                              <div key={log.id} className="relative">
                                <span className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow-sm" />
                                
                                <div className="flex flex-wrap items-center gap-2 mb-1.5">
                                  <span className={`text-[11px] font-black tracking-wider uppercase px-2 py-0.5 rounded border ${badgeColor}`}>
                                    {log.action}
                                  </span>
                                  <span className="text-[11px] text-slate-400 font-bold">
                                    {new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                                  </span>
                                </div>
                                <p className="text-sm font-semibold text-slate-800 leading-relaxed">
                                  {log.rationale}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-base text-slate-500 text-center py-12 font-medium">
                    Select an escalated grievance from the queue to issue MP directives.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "policy" && (
            <div className="flex flex-col bg-white border border-slate-200 shadow-lg rounded-2xl p-6 max-w-4xl mx-auto h-[650px]">
              <div className="bg-blue-50 -mx-6 -mt-6 p-6 rounded-t-2xl border-b border-blue-100 mb-4">
                <h3 className="font-black text-lg text-blue-900 flex items-center gap-2">
                  <MessageSquare className="w-6 h-6 text-blue-700" /> Government Policy Intelligence Agent
                </h3>
                <p className="text-sm text-blue-700 mt-1 font-medium">Queries verified government schemes, SOP archives, and master development plans.</p>
              </div>

              <div className="flex-1 overflow-y-auto space-y-6 my-4 pr-4">
                {chatHistory.length === 0 ? (
                  <div className="h-full flex flex-col justify-center items-center text-center text-slate-500 px-6 py-10">
                    <FileText className="w-16 h-16 text-slate-300 mb-4" />
                    <p className="text-base font-medium max-w-md">Ask policy questions regarding constituency budgets, scheme requirements, or department SOP rules. Answers are strict and verified.</p>
                  </div>
                ) : (
                  chatHistory.map((msg, i) => {
                    const isUser = msg.role === "user";
                    return (
                      <div key={i} className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                        <div className={`p-4 rounded-2xl max-w-[85%] shadow-sm text-base ${isUser ? "bg-blue-700 text-white rounded-tr-none font-medium" : "bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200 font-medium"}`}>
                          <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                          
                          {!isUser && msg.sources && msg.sources.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-slate-300 text-xs text-slate-600 space-y-2 font-medium">
                              <span className="font-bold text-slate-800 block uppercase tracking-wider">Verified References:</span>
                              {msg.sources.map((src: any, sIdx: number) => (
                                <div key={sIdx} className="bg-white p-2 rounded border border-slate-200 flex items-center gap-2 shadow-sm">
                                  <FileText className="w-4 h-4 text-blue-600" /> {src.title} (v{src.version}, Published: {src.date})
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
                {chatLoading && (
                  <div className="text-blue-600 font-bold italic text-sm animate-pulse p-4 bg-blue-50 rounded-xl inline-block">
                    Governance Agent is retrieving verified context...
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-slate-200">
                <div className="flex flex-wrap gap-2 mb-4">
                  <button
                    type="button"
                    onClick={() => setChatQuery("What is the budget allocation for water infrastructure in Ward 4?")}
                    className="text-xs bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-bold px-3 py-1.5 rounded-lg shadow-sm transition"
                  >
                    💧 Ward 4 Water Budget
                  </button>
                  <button
                    type="button"
                    onClick={() => setChatQuery("What are the recommended base course specifications for patching potholes?")}
                    className="text-xs bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-bold px-3 py-1.5 rounded-lg shadow-sm transition"
                  >
                    🛣️ Pothole Patching SOP
                  </button>
                </div>
                <form onSubmit={handleSendPolicyChat} className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Ask Policy Agent..."
                    value={chatQuery}
                    onChange={e => setChatQuery(e.target.value)}
                    className="flex-1 bg-white border-2 border-slate-300 rounded-xl px-5 py-3.5 text-base font-medium focus:outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-100 text-slate-900 shadow-sm transition"
                  />
                  <button
                    type="submit"
                    className="bg-blue-700 hover:bg-blue-800 text-white px-6 rounded-xl transition flex items-center justify-center cursor-pointer shadow-md"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
