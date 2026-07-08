"use client";

import React, { useState, useEffect, useRef } from "react";
import { MessageSquare, Send, Paperclip, Camera, Shield, CheckCircle2, ChevronLeft, Phone, Video } from "lucide-react";
import { api } from "@/lib/api";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  time: string;
  image?: string;
  status?: "sent" | "delivered" | "read";
}

interface Grievance {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  resolution_notes?: string;
}

export default function CitizenPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", sender: "bot", text: "Namaskar 🙏 Welcome to Sahayak, your official Govt of AP grievance portal. Please describe your issue clearly.", time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [myGrievances, setMyGrievances] = useState<Grievance[]>([]);
  const [authenticated, setAuthenticated] = useState(false);
  const [selectedGrievance, setSelectedGrievance] = useState<any>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    async function initSession() {
      try {
        // Authenticate automatically as Ramesh Kumar
        const authData = await api.login("ramesh@citizen.in", "password123");
        localStorage.setItem("token", authData.access_token);
        setAuthenticated(true);
        
        // Fetch initially
        const list = await api.listGrievances();
        setMyGrievances(list);
      } catch (err) {
        console.error("Auto login failed:", err);
      }
    }
    
    initSession();
  }, []);

  useEffect(() => {
    if (!authenticated) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/citizen`);
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "GRIEVANCE_UPDATED") {
        fetchGrievances();
        try {
          const resG = await api.getGrievanceDetail(data.grievance_id);
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            sender: "bot",
            text: `Update on your grievance: Status changed to ${resG.status}.\n${resG.resolution_notes || ""}`,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
          }]);
        } catch (e) {
          console.error(e);
        }
      }
    };
    return () => ws.close();
  }, [authenticated]);

  const fetchGrievances = async () => {
    try {
      const data = await api.listGrievances();
      setMyGrievances(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent, isImage: boolean = false) => {
    e.preventDefault();
    if (!inputValue.trim() && !isImage) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: isImage ? "Uploaded Evidence Image" : inputValue,
      image: isImage ? "https://sahayak-demo-evidence.s3.amazonaws.com/pothole_intake.jpg" : undefined,
      time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      status: "sent"
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue("");
    setIsTyping(true);

    try {
      let payload = {};
      if (isImage) {
        payload = { media_url: "https://sahayak-demo-evidence.s3.amazonaws.com/pothole_intake.jpg", content_type: "image/jpeg" };
      } else {
        payload = { message: userMsg.text };
      }

      // Call API using global fetchAPI client via endpoint
      const response = await fetch("http://localhost:8000/api/v1/grievances/whatsapp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(payload)
      });
      const res = await response.json();
      
      setMessages(prev => prev.map(m => m.id === userMsg.id ? {...m, status: "read"} : m));

      setTimeout(() => {
        setIsTyping(false);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: "bot",
          text: res.reply,
          time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        }]);
        fetchGrievances();
      }, 800);

    } catch (err: any) {
      setIsTyping(false);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: "bot",
        text: "Sorry, the server is unreachable right now.",
        time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      }]);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 flex justify-center items-center p-4 sm:p-8 font-sans">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Mock WhatsApp Interface */}
        <div className="lg:col-span-1 bg-white rounded-[2.5rem] shadow-2xl border-[12px] border-slate-800 overflow-hidden flex flex-col h-[800px] relative">
          
          {/* Top Header */}
          <div className="bg-[#075E54] text-white px-4 py-4 flex items-center gap-3 shadow-md z-10 relative">
            <ChevronLeft className="w-7 h-7 cursor-pointer" />
            <div className="relative">
              <div className="w-11 h-11 bg-white rounded-full flex justify-center items-center shadow-inner overflow-hidden border-2 border-white">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" alt="Gov" className="w-6 h-auto opacity-90"/>
              </div>
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-[#075E54] rounded-full"></div>
            </div>
            <div className="flex-1">
              <h2 className="font-bold text-lg leading-tight">Govt of AP Sahayak</h2>
              <p className="text-xs text-green-100 font-medium">Official Grievance Bot • Online</p>
            </div>
            <div className="flex gap-4">
              <Video className="w-5 h-5 text-green-100" />
              <Phone className="w-5 h-5 text-green-100" />
            </div>
          </div>
          
          {/* Chat Background */}
          <div className="absolute inset-0 bg-[#E5DDD5] z-0 opacity-40 mix-blend-multiply" 
               style={{backgroundImage: `url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')`}}></div>

          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 z-10 relative">
            <div className="text-center mb-6">
              <span className="bg-[#E1F3FB] text-slate-600 text-xs font-bold px-3 py-1.5 rounded-lg shadow-sm border border-slate-200">
                Official Business Account
              </span>
            </div>
            
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} mb-2`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 relative shadow-sm text-[15px] font-medium leading-relaxed ${
                  msg.sender === "user" 
                    ? "bg-[#DCF8C6] text-slate-800 rounded-tr-none border border-green-200" 
                    : "bg-white text-slate-800 rounded-tl-none border border-slate-200"
                }`}>
                  {msg.image && (
                    <img src={msg.image} alt="Upload" className="w-full max-h-56 object-cover rounded-xl mb-2 border border-slate-300 shadow-sm" />
                  )}
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                  <div className={`text-[11px] font-bold mt-1.5 flex justify-end items-center gap-1 opacity-70`}>
                    {msg.time}
                    {msg.sender === "user" && msg.status && (
                      <CheckCircle2 className={`w-3.5 h-3.5 ${msg.status === "read" ? "text-blue-500" : "text-slate-400"}`} />
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none shadow-sm flex gap-1.5 items-center border border-slate-200">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: "0.2s"}}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: "0.4s"}}></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-[#F0F0F0] px-3 py-3 flex items-end gap-2 z-10 relative">
            <button className="p-2 text-slate-500 hover:text-slate-700 bg-transparent rounded-full transition">
              <Camera className="w-6 h-6" />
            </button>
            <form onSubmit={handleSendMessage} className="flex-1 flex bg-white rounded-full shadow-sm items-center border border-slate-300 pl-4 pr-1 relative overflow-hidden focus-within:ring-2 focus-within:ring-[#075E54]">
              <input
                type="text"
                placeholder="Type a message..."
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                className="flex-1 py-3 text-base font-medium text-slate-800 focus:outline-none bg-transparent"
              />
              <button 
                type="button" 
                onClick={(e) => handleSendMessage(e, true)}
                title="Send Demo Photo"
                className="p-2 text-slate-400 hover:text-[#075E54] transition"
              >
                <Paperclip className="w-5 h-5" />
              </button>
            </form>
            <button 
              onClick={handleSendMessage}
              className="p-3.5 bg-[#00A884] text-white rounded-full hover:bg-[#008f6f] transition shadow-md flex items-center justify-center cursor-pointer transform hover:scale-105"
            >
              <Send className="w-5 h-5 ml-0.5" />
            </button>
          </div>
        </div>

        {/* Right Side: Citizen Portal Status Tracker */}
        <div className="lg:col-span-2 flex flex-col h-[800px]">
          <div className="bg-blue-900 rounded-t-3xl p-8 flex items-center gap-5 shadow-lg border-b border-blue-800 z-10">
            <div className="w-16 h-16 bg-white/10 rounded-2xl flex justify-center items-center border-2 border-white/20 shadow-inner">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white tracking-tight">Citizen Dashboard</h1>
              <p className="text-blue-200 font-semibold mt-1">Track your official grievance reports live</p>
            </div>
          </div>
          
          <div className="flex-1 bg-white rounded-b-3xl shadow-xl overflow-y-auto p-8 border border-slate-200">
            <div className="flex justify-between items-center mb-8 border-b border-slate-200 pb-4">
              <h2 className="text-xl font-black text-slate-800 flex items-center gap-2">
                <MessageSquare className="w-6 h-6 text-blue-700"/> My Active Reports
              </h2>
              <span className="bg-blue-100 text-blue-800 px-4 py-1.5 rounded-lg text-sm font-black border border-blue-200 shadow-sm">
                Total: {myGrievances.length}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {myGrievances.map(g => (
                <div
                  key={g.id}
                  onClick={async () => {
                    try {
                      const detail = await api.getGrievanceDetail(g.id);
                      setSelectedGrievance(detail);
                    } catch (e) {
                      console.error(e);
                    }
                  }}
                  className="bg-slate-50 border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition cursor-pointer hover:border-blue-400"
                >
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-black text-lg text-slate-900 truncate max-w-[70%]">{g.title}</h3>
                    <span className={`text-xs font-black uppercase px-3 py-1.5 rounded-lg border shadow-sm ${
                      g.status === "CLOSED" ? "bg-green-100 text-green-700 border-green-200" :
                      g.status === "RESOLVED" ? "bg-blue-100 text-blue-700 border-blue-200" :
                      "bg-orange-100 text-orange-700 border-orange-200"
                    }`}>
                      {g.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 font-medium line-clamp-3 leading-relaxed">
                    {g.description}
                  </p>
                  
                  {g.resolution_notes && (
                    <div className="mt-4 pt-4 border-t border-slate-200">
                      <p className="text-xs font-black uppercase text-green-700 mb-1">Resolution Provided:</p>
                      <p className="text-sm font-semibold text-slate-700 italic border-l-4 border-green-400 pl-3 py-1 bg-white rounded-r-lg">
                        {g.resolution_notes}
                      </p>
                    </div>
                  )}

                  <div className="mt-5 pt-4 border-t border-slate-200 flex justify-between items-center text-xs text-slate-500 font-bold">
                    <span>ID: {g.id.substring(0,8)}</span>
                    <span>Reported: {new Date(g.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
              
              {myGrievances.length === 0 && (
                <div className="col-span-1 md:col-span-2 py-16 text-center text-slate-500">
                  <div className="w-20 h-20 bg-slate-100 rounded-full flex justify-center items-center mx-auto mb-4 border-4 border-white shadow-sm">
                    <CheckCircle2 className="w-10 h-10 text-slate-300" />
                  </div>
                  <p className="text-lg font-bold">No grievances reported yet.</p>
                  <p className="text-sm mt-2 font-medium">Use the WhatsApp assistant to report an issue.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Selected Grievance Details & Timeline Modal */}
      {selectedGrievance && (
        <div className="fixed inset-0 bg-black/55 backdrop-blur-sm flex justify-center items-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-8 shadow-2xl border border-slate-200 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedGrievance(null)}
              className="absolute top-6 right-6 p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>

            <div className="border-b border-slate-200 pb-5 pr-8">
              <span className={`inline-block text-xs font-black uppercase px-3 py-1 rounded-md border mb-3 ${
                selectedGrievance.status === "CLOSED" ? "bg-green-100 text-green-700 border-green-200" :
                selectedGrievance.status === "RESOLVED" ? "bg-blue-100 text-blue-700 border-blue-200" :
                "bg-orange-100 text-orange-700 border-orange-200"
              }`}>
                {selectedGrievance.status}
              </span>
              <h2 className="text-2xl font-black text-slate-900 leading-snug">{selectedGrievance.title}</h2>
              <p className="text-xs font-bold text-slate-400 mt-1">Grievance Reference: {selectedGrievance.id}</p>
            </div>

            <div className="py-6 space-y-6 text-base">
              <div>
                <span className="font-black block text-sm uppercase tracking-wider text-slate-500 mb-2">Description</span>
                <p className="bg-slate-50 p-5 rounded-2xl border border-slate-200 text-slate-700 leading-relaxed font-semibold">
                  {selectedGrievance.description}
                </p>
              </div>

              {selectedGrievance.status === "RESOLVED" && (
                <div className="flex gap-4">
                  <button
                    onClick={async () => {
                      try {
                        await api.confirmGrievance(selectedGrievance.id);
                        setSelectedGrievance(null);
                        const list = await api.listGrievances();
                        setMyGrievances(list);
                      } catch (e) {
                        console.error(e);
                      }
                    }}
                    className="flex-1 py-3.5 rounded-xl bg-green-700 hover:bg-green-600 text-white font-black text-sm tracking-wide shadow-md transition cursor-pointer text-center"
                  >
                    Confirm & Close Ticket
                  </button>
                  <button
                    onClick={async () => {
                      const notes = prompt("Please describe why the repair is unsatisfactory:");
                      if (!notes) return;
                      try {
                        await api.rejectGrievance(selectedGrievance.id, notes);
                        setSelectedGrievance(null);
                        const list = await api.listGrievances();
                        setMyGrievances(list);
                      } catch (e) {
                        console.error(e);
                      }
                    }}
                    className="flex-1 py-3.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-black text-sm tracking-wide shadow-md transition cursor-pointer text-center"
                  >
                    Reject & Reopen Ticket
                  </button>
                </div>
              )}

              {/* Explainable AI Timeline */}
              {selectedGrievance.audit_logs && selectedGrievance.audit_logs.length > 0 && (
                <div className="pt-6 border-t border-slate-200 space-y-4">
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
        </div>
      )}
    </main>
  );
}
