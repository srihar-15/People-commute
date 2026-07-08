"use client";

import Link from "next/link";
import { User, ShieldAlert, Award, Database, ArrowRight } from "lucide-react";

export default function LandingPage() {
  const portals = [
    {
      name: "Citizen Portal",
      desc: "Simulate WhatsApp intake chat, file grievances, upload image evidence, and confirm resolutions.",
      href: "/citizen",
      icon: User,
      color: "from-emerald-500 to-teal-600",
      glow: "glow-emerald",
      badge: "WhatsApp Sim"
    },
    {
      name: "Department Officer",
      desc: "Monitor incoming queue tasks, view AI-retrieved SOPs and historical templates, submit repair proof.",
      href: "/officer",
      icon: ShieldAlert,
      color: "from-blue-500 to-indigo-600",
      glow: "glow-blue",
      badge: "SLA Queue"
    },
    {
      name: "MP Governance Dashboard",
      desc: "Analyze Constituency Health Index, view Leaflet heatmaps, and query the RAG-based Policy intelligence agent.",
      href: "/mp",
      icon: Award,
      color: "from-purple-500 to-pink-600",
      glow: "glow-blue",
      badge: "MP Oversight"
    },
    {
      name: "System Administrator",
      desc: "Manage the Human Review Queue, inspect Explainable AI audit logs, and oversee system status.",
      href: "/admin",
      icon: Database,
      color: "from-amber-500 to-orange-600",
      glow: "glow-emerald",
      badge: "Audit & Review"
    }
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden bg-[#090d16]">
      {/* Background glowing effects */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-blue-900/10 blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-emerald-900/10 blur-[120px]" />

      <div className="max-w-6xl w-full text-center z-10 space-y-12">
        {/* Header */}
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-500/20 bg-blue-500/5 text-blue-400 text-xs font-semibold uppercase tracking-widest animate-pulse">
            Hackathon MVP Presentation
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white">
            SAHAYAK
          </h1>
          <p className="text-xl md:text-2xl font-light text-gradient max-w-3xl mx-auto">
            Constituency Intelligence & Governance Decision Support Platform
          </p>
          <p className="text-sm md:text-base text-gray-400 max-w-2xl mx-auto">
            A state-of-the-art multi-agent workflow platform connecting citizens, department officers, and elected representatives through explainable AI routing, vector de-duplication, and image-based resolution assurance.
          </p>
        </div>

        {/* Portals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {portals.map((portal) => {
            const Icon = portal.icon;
            return (
              <Link key={portal.name} href={portal.href} className="group">
                <div className={`h-full glass-panel glass-panel-hover p-8 flex flex-col justify-between text-left relative overflow-hidden ${portal.glow}`}>
                  <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/5 to-transparent rounded-bl-3xl" />
                  
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <div className={`p-3 rounded-xl bg-gradient-to-br ${portal.color} text-white shadow-lg`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-[10px] font-bold tracking-widest uppercase px-2.5 py-1 rounded-md border border-white/10 bg-white/5 text-gray-300">
                        {portal.badge}
                      </span>
                    </div>

                    <div className="space-y-2">
                      <h2 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                        {portal.name}
                      </h2>
                      <p className="text-sm text-gray-400 leading-relaxed">
                        {portal.desc}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-medium text-blue-400 group-hover:text-emerald-400 transition-colors mt-6">
                    Enter Portal <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Footer */}
        <div className="text-xs text-gray-500 pt-8 border-t border-white/5 max-w-md mx-auto">
          Built with Next.js, FastAPI, PostgreSQL, and LangGraph.
        </div>
      </div>
    </main>
  );
}
