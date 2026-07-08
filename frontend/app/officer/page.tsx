"use client";

import React, { useState, useEffect } from "react";
import { Clipboard, ShieldAlert, Award, FileText, CheckCircle, HelpCircle, ArrowRight, Upload, AlertCircle, Info, RefreshCw, Shield } from "lucide-react";
import { api } from "@/lib/api";

interface Grievance {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  sla_deadline?: string;
}

export default function OfficerDashboard() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [selectedGrievance, setSelectedGrievance] = useState<any>(null);
  const [assistantData, setAssistantData] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [proofUrl, setProofUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [password, setPassword] = useState("password123");

  const [selectedPersona, setSelectedPersona] = useState("water_officer@sahayak.gov.in");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const authData = await api.login(selectedPersona, password);
      localStorage.setItem("token", authData.access_token);
      setUser(authData);
      const list = await api.listGrievances();
      setGrievances(list);
    } catch (err: any) {
      setLoginError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/officer`);
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "GRIEVANCE_SUBMITTED" || data.event === "GRIEVANCE_UPDATED") {
        const list = await api.listGrievances();
        setGrievances(list);
      }
    };
    return () => ws.close();
  }, [user]);

  const handleSelectGrievance = async (g: Grievance) => {
    setLoading(false);
    setVerificationResult(null);
    setProofUrl("");
    setNotes("");
    
    try {
      const details = await api.getGrievanceDetail(g.id);
      setSelectedGrievance(details);
      
      setAssistantLoading(true);
      const assistant = await api.getOfficerAssistant(g.id);
      setAssistantData(assistant);
    } catch (err: any) {
      alert(`Error loading details: ${err.message}`);
    } finally {
      setAssistantLoading(false);
    }
  };

  const handleAcceptGrievance = async () => {
    if (!selectedGrievance) return;
    try {
      const updated = await api.acceptGrievance(selectedGrievance.id);
      setSelectedGrievance((prev: any) => ({ ...prev, status: updated.status, assigned_officer_id: updated.assigned_officer_id }));
      const list = await api.listGrievances();
      setGrievances(list);
    } catch (err: any) {
      alert(`Error accepting task: ${err.message}`);
    }
  };

  const handleResolveGrievance = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGrievance || !proofUrl.trim()) return;

    setLoading(true);
    setVerificationResult(null);
    
    try {
      const res = await api.resolveGrievance(selectedGrievance.id, {
        evidence_url: proofUrl,
        notes: notes
      });
      
      setVerificationResult(res);
      if (res.success) {
        setSelectedGrievance((prev: any) => ({ ...prev, status: "RESOLVED" }));
        setProofUrl("");
        setNotes("");
      }
      
      const list = await api.listGrievances();
      setGrievances(list);
    } catch (err: any) {
      setVerificationResult({
        success: false,
        message: `Network/Server Error: ${err.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const queueGrievances = grievances.filter(g => g.status === "ROUTED");
  const myGrievances = grievances.filter(g => g.status === "ASSIGNED");
  const resolvedGrievances = grievances.filter(g => g.status === "RESOLVED" || g.status === "CLOSED");

  if (!user) {
    return (
      <main className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans text-slate-900">
        <div className="bg-white p-10 rounded-2xl shadow-xl border border-slate-200 max-w-md w-full">
          <div className="flex flex-col items-center mb-8 text-center">
            <div className="p-4 rounded-full bg-blue-900 text-white mb-4 shadow-md">
              <Clipboard className="w-10 h-10" />
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900">Department Portal</h1>
            <p className="text-base text-slate-500 mt-2">Officer Action & Verification Hub</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Select Department Role</label>
              <select
                value={selectedPersona}
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-blue-800"
              >
                <option value="water_officer@sahayak.gov.in">Water Dept Officer</option>
                <option value="roads_officer@sahayak.gov.in">Roads Dept Officer</option>
                <option value="sanitation_officer@sahayak.gov.in">Sanitation Officer</option>
                <option value="electricity_officer@sahayak.gov.in">Electricity Officer</option>
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
            <Clipboard className="w-7 h-7" />
          </div>
          <div>
            <h1 className="font-extrabold text-2xl tracking-tight">Department Officer Dashboard</h1>
            <p className="text-sm text-blue-200 font-medium mt-0.5">Manage queues and resolve issues with AI Officer Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <select
            value={selectedPersona}
            onChange={(e) => setSelectedPersona(e.target.value)}
            className="bg-white/10 border border-white/20 text-sm text-white rounded-lg px-4 py-2 focus:outline-none font-semibold cursor-pointer"
          >
            <option className="text-black" value="water_officer@sahayak.gov.in">Water Dept Officer</option>
            <option className="text-black" value="roads_officer@sahayak.gov.in">Roads Dept Officer</option>
            <option className="text-black" value="sanitation_officer@sahayak.gov.in">Sanitation Officer</option>
            <option className="text-black" value="electricity_officer@sahayak.gov.in">Electricity Officer</option>
          </select>
          <div className="text-sm text-blue-200 font-bold border-l border-white/20 pl-6 flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white text-blue-900 flex justify-center items-center font-black">
              {user.name.charAt(0)}
            </div>
            {user.name}
          </div>
        </div>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden h-[calc(100vh-85px)]">
        
        {/* Left Column: Queues */}
        <div className="lg:col-span-3 border-r border-slate-300 bg-slate-100 overflow-y-auto p-6 space-y-8 shadow-inner">
          <div className="space-y-4">
            <div className="flex justify-between items-center px-1">
              <h3 className="text-sm font-black tracking-widest uppercase text-blue-800 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse shadow-sm" /> Unassigned Queue ({queueGrievances.length})
              </h3>
            </div>
            
            {queueGrievances.length === 0 ? (
              <div className="p-6 rounded-xl border-2 border-dashed border-slate-300 bg-white text-center text-sm font-semibold text-slate-500">
                No new unassigned tasks.
              </div>
            ) : (
              <div className="space-y-3">
                {queueGrievances.map(g => (
                  <div
                    key={g.id}
                    onClick={() => handleSelectGrievance(g)}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all shadow-sm ${
                      selectedGrievance?.id === g.id
                        ? "bg-blue-50 border-blue-500 ring-2 ring-blue-200"
                        : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-md"
                    }`}
                  >
                    <h4 className="font-bold text-sm text-slate-900 truncate">{g.title}</h4>
                    <p className="text-xs text-slate-600 font-medium truncate mt-1">{g.description}</p>
                    <div className="flex justify-between items-center text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
                      <span className="text-red-700 font-black">{g.priority}</span>
                      <span className="font-semibold">{new Date(g.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-black tracking-widest uppercase text-green-700 px-1 border-b border-slate-200 pb-2">
              My Active Tasks ({myGrievances.length})
            </h3>
            
            {myGrievances.length === 0 ? (
              <div className="p-6 rounded-xl border-2 border-dashed border-slate-300 bg-white text-center text-sm font-semibold text-slate-500">
                You have no active accepted tasks.
              </div>
            ) : (
              <div className="space-y-3">
                {myGrievances.map(g => (
                  <div
                    key={g.id}
                    onClick={() => handleSelectGrievance(g)}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all shadow-sm ${
                      selectedGrievance?.id === g.id
                        ? "bg-green-50 border-green-500 ring-2 ring-green-200"
                        : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-md"
                    }`}
                  >
                    <h4 className="font-bold text-sm text-slate-900 truncate">{g.title}</h4>
                    <p className="text-xs text-slate-600 font-medium truncate mt-1">{g.description}</p>
                    <div className="flex justify-between items-center text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
                      <span className="text-red-700 font-black">{g.priority}</span>
                      <span className="font-semibold">SLA: {g.sla_deadline ? new Date(g.sla_deadline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "None"}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-4 opacity-75">
            <h3 className="text-sm font-black tracking-widest uppercase text-slate-500 px-1 border-b border-slate-200 pb-2">
              Resolved / Audited ({resolvedGrievances.length})
            </h3>
            
            <div className="space-y-3">
              {resolvedGrievances.map(g => (
                <div
                  key={g.id}
                  onClick={() => handleSelectGrievance(g)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all shadow-sm ${
                    selectedGrievance?.id === g.id
                      ? "bg-slate-100 border-slate-400"
                      : "bg-white border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <h4 className="font-bold text-sm text-slate-700 truncate">{g.title}</h4>
                  <div className="flex justify-between items-center text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
                    <span className="text-green-700 font-black">{g.status}</span>
                    <span className="font-semibold">{new Date(g.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center column: Form */}
        <div className="lg:col-span-5 border-r border-slate-300 flex flex-col bg-white overflow-y-auto p-8 shadow-sm z-10">
          {selectedGrievance ? (
            <div className="space-y-8">
              <div className="border-b border-slate-200 pb-6">
                <div className="flex justify-between items-start">
                  <h2 className="text-2xl font-black text-slate-900 leading-snug">{selectedGrievance.title}</h2>
                  <span className="text-xs font-black tracking-wider uppercase px-3 py-1.5 rounded-lg border border-slate-300 bg-slate-100 text-slate-700 shadow-sm">
                    {selectedGrievance.status}
                  </span>
                </div>
                <p className="text-sm font-bold text-slate-400 mt-2">ID: {selectedGrievance.id}</p>
              </div>

              <div className="space-y-6 text-base">
                <div>
                  <h4 className="font-black text-slate-800 mb-2">Citizen Description:</h4>
                  <p className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-slate-700 leading-relaxed font-medium shadow-inner">
                    {selectedGrievance.description}
                  </p>
                </div>

                {selectedGrievance.evidence && selectedGrievance.evidence.some((e: any) => e.type === "intake_evidence") && (
                  <div>
                    <h4 className="font-black text-slate-800 mb-2">Intake Photo (Before):</h4>
                    <img
                      src={selectedGrievance.evidence.find((e: any) => e.type === "intake_evidence").media_url}
                      alt="Intake Evidence"
                      className="w-full h-56 rounded-2xl object-cover border-4 border-slate-100 shadow-md"
                    />
                  </div>
                )}

                {selectedGrievance.status === "ROUTED" && (
                  <button
                    onClick={handleAcceptGrievance}
                    className="w-full py-4 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-black text-lg tracking-wide shadow-lg transition cursor-pointer"
                  >
                    Accept Task & Lock to Queue
                  </button>
                )}

                {selectedGrievance.status === "ASSIGNED" && (
                  <form onSubmit={handleResolveGrievance} className="space-y-6 pt-6 border-t border-slate-200">
                    <h3 className="font-black text-lg text-green-700 flex items-center gap-2"><CheckCircle className="w-5 h-5"/> Resolve Task</h3>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-bold text-slate-700">Evidence Proof Image URL:</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg"
                        value={proofUrl}
                        onChange={e => setProofUrl(e.target.value)}
                        className="w-full bg-slate-50 border-2 border-slate-300 rounded-xl px-4 py-3 text-base font-medium focus:outline-none focus:border-green-600 focus:ring-4 focus:ring-green-100 text-slate-900 transition"
                      />
                      <button
                        type="button"
                        onClick={() => setProofUrl("https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg")}
                        className="text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-300 shadow-sm transition"
                      >
                        Use Demo Proof Image
                      </button>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-bold text-slate-700">Work Resolution Notes:</label>
                      <textarea
                        required
                        rows={4}
                        placeholder="Detail the exact work carried out to solve this issue..."
                        value={notes}
                        onChange={e => setNotes(e.target.value)}
                        className="w-full bg-slate-50 border-2 border-slate-300 rounded-xl p-4 text-base font-medium focus:outline-none focus:border-green-600 focus:ring-4 focus:ring-green-100 text-slate-900 resize-none transition shadow-sm"
                      />
                    </div>

                    {verificationResult && (
                      <div className={`p-6 rounded-xl border-2 shadow-sm text-base space-y-3 font-medium ${
                        verificationResult.success
                          ? "bg-green-50 border-green-300 text-green-900"
                          : "bg-red-50 border-red-300 text-red-900"
                      }`}>
                        <div className="flex items-center gap-2 font-black text-lg">
                          {verificationResult.success ? <CheckCircle className="w-6 h-6 text-green-600" /> : <AlertCircle className="w-6 h-6 text-red-600" />}
                          {verificationResult.success ? "AI Verification Success" : "AI Verification Rejected"}
                        </div>
                        <p className="leading-relaxed">
                          {verificationResult.message}
                        </p>
                        
                        {verificationResult.report?.verification_checklist && (
                          <div className="pt-4 mt-2 border-t border-black/10">
                            <span className="font-black block mb-2 text-sm uppercase tracking-wider opacity-80">Vision Checklist Results:</span>
                            <ul className="list-disc pl-5 space-y-1 text-sm font-semibold">
                              {verificationResult.report.verification_checklist.map((item: string, i: number) => (
                                <li key={i}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-4 rounded-xl bg-green-700 hover:bg-green-600 disabled:bg-slate-400 text-white font-black text-lg tracking-wide shadow-lg transition cursor-pointer"
                    >
                      {loading ? "Running AI Verification..." : "Submit Proof & Trigger AI Verification"}
                    </button>
                  </form>
                )}

                {/* Explainable AI Timeline */}
                {selectedGrievance.audit_logs && selectedGrievance.audit_logs.length > 0 && (
                  <div className="mt-8 pt-6 border-t border-slate-200 space-y-4">
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
            </div>
          ) : (
            <div className="h-full flex flex-col justify-center items-center text-center text-slate-400 p-8">
              <Clipboard className="w-16 h-16 text-slate-300 mb-4" />
              <p className="text-xl font-bold max-w-sm text-slate-500">Select a grievance task from the queue to begin inspection and resolution.</p>
            </div>
          )}
        </div>

        {/* Right column: Assistant */}
        <div className="lg:col-span-4 flex flex-col overflow-y-auto p-8 bg-blue-50/50">
          <h3 className="font-black text-lg text-blue-900 flex items-center gap-2 border-b border-blue-200 pb-4 shadow-sm bg-white -mx-8 px-8 -mt-8 pt-8 mb-6">
            <HelpCircle className="w-6 h-6 text-blue-700" /> Officer Assistant Agent
          </h3>

          {selectedGrievance ? (
            assistantLoading ? (
              <div className="py-12 text-center text-sm font-bold text-blue-700 animate-pulse bg-white rounded-xl shadow-sm border border-blue-100">
                Querying versioned SOP references and historical index...
              </div>
            ) : assistantData ? (
              <div className="space-y-8 text-base">
                
                <div className="space-y-3">
                  <h4 className="font-black text-blue-800 uppercase tracking-wider text-sm flex items-center gap-2"><FileText className="w-4 h-4"/> Applicable Government SOPs</h4>
                  {assistantData.suggested_sops && assistantData.suggested_sops.map((sop: any, i: number) => (
                    <div key={i} className="p-5 rounded-xl bg-white border border-slate-200 shadow-md space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="font-black text-slate-900">{sop.title}</span>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2.5 py-1 rounded-lg font-mono font-bold border border-blue-200">v{sop.version}</span>
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed font-medium italic border-l-4 border-blue-400 pl-3">
                        "{sop.content}"
                      </p>
                      <div className="text-xs font-bold text-slate-400 flex justify-between pt-2 border-t border-slate-100">
                        <span>Source: {sop.source.split("/").pop()}</span>
                        <span>Date: {sop.date}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="space-y-3">
                  <h4 className="font-black text-purple-800 uppercase tracking-wider text-sm flex items-center gap-2"><CheckCircle className="w-4 h-4"/> Similar Solved Grievances</h4>
                  {assistantData.similar_cases && assistantData.similar_cases.length > 0 ? (
                    assistantData.similar_cases.map((sc: any, i: number) => (
                      <div key={i} className="p-5 rounded-xl bg-white border border-slate-200 shadow-md space-y-2">
                        <div className="flex justify-between items-center text-sm font-black">
                          <span className="text-slate-900 truncate max-w-[75%]">{sc.title}</span>
                          <span className="text-xs text-purple-700 font-mono bg-purple-50 px-2 py-1 rounded-lg border border-purple-200">{Math.round(sc.similarity * 100)}% match</span>
                        </div>
                        <p className="text-sm text-slate-600 leading-relaxed mt-2 font-medium">
                          <strong className="text-slate-800">Fix details:</strong> {sc.resolution_notes}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 font-medium italic p-2">No similar closed cases found in the database.</p>
                  )}
                </div>

                <div className="space-y-3">
                  <h4 className="font-black text-green-700 uppercase tracking-wider text-sm flex items-center gap-2"><AlertCircle className="w-4 h-4"/> Recommended Action Steps</h4>
                  <ul className="bg-white border border-slate-200 shadow-md rounded-xl p-6 space-y-3 text-slate-800 text-sm leading-relaxed font-semibold">
                    {assistantData.likely_steps && assistantData.likely_steps.map((step: string, i: number) => (
                      <li key={i} className="flex gap-2 items-start"><span className="text-green-600 mt-0.5">•</span> {step}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-slate-500 font-bold bg-white rounded-xl shadow-sm border border-slate-200">
                No assistant data loaded.
              </div>
            )
          ) : (
            <div className="h-full flex flex-col justify-center items-center text-center text-slate-400 p-6 bg-white rounded-2xl shadow-sm border border-blue-100">
              <Info className="w-12 h-12 text-blue-200 mb-4" />
              <p className="text-base font-bold text-slate-500 max-w-[250px]">Select a grievance task to load proactive AI recommendations.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
