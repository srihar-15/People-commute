# Google Build with AI Hackathon: Sahayak Presentation Guide

This document contains slide-by-slide pitch scripts and notes for presenting Sahayak to the hackathon judges.

---

## Slide 1: Title & Vision
* **Headline**: Sahayak: AI-Driven Multi-Agent Municipal Governance Portal
* **Speaker Script**: 
  > "Good morning, judges. Today, we are presenting Sahayak, a revolutionary platform that leverages Google’s state-of-the-art Gemini models and LangGraph to automate, verify, and streamline citizen municipal grievances. It creates absolute transparency between citizens, public officers, and constituency leaders."

## Slide 2: The Problem
* **Bullet Points**:
  * Traditional portals are black holes: Citizens submit tickets but receive no updates.
  * Manual classification and routing lead to massive bureaucratic delays.
  * Lack of resolution verification: Tickets are closed without physical verification of work.
  * Siloed databases: MPs/leaders have no real-time visibility into local ward issues.
* **Speaker Script**:
  > "Public grievance systems in developing nations are broken. Citizens feel unheard, routing is slow, and officers close tickets on paper without actually resolving the issues. There is no automated oversight or quality assurance."

## Slide 3: The Solution (Sahayak)
* **Bullet Points**:
  * Conversational AI Intake: WhatsApp Bot collects structured details dynamically.
  * Automated Multi-Agent Routing: LangGraph StateGraph classifies and schedules SLAs.
  * Vector Duplicate Detection: Cosine similarity on embeddings groups identical issues.
  * AI-Assistant & RAG for Officers: Recommends SOPs and historical fixes.
  * Visual Assurance: Multimodal Vision AI verifies before/after repairs.
  * Leadership Dashboard: Geo-spatial constituency health map for local MPs.
* **Speaker Script**:
  > "Sahayak bridges this gap. We provide a simulated WhatsApp Bot that walks citizens through their reports, automatically translating and structuring inputs. Under the hood, LangGraph coordinates multiple specialized agents. For officers, we provide an AI assistant with SOP context. Most importantly, we use Gemini Vision to visually audit repairs before a ticket is closed."

## Slide 4: Multi-Agent Architecture
* **Diagram Description**: Explain Pipeline A (Conversational memory) and Pipeline B (Asynchronous routing) to show how LangGraph coordinates the workflow.
* **Speaker Script**:
  > "Our system runs on LangGraph. The intake agent pauses and resumes automatically to ask citizens adaptive follow-up questions. Once complete, a background graph routes the ticket, runs duplicate checks using vector embeddings, and assigns appropriate SLAs."

## Slide 5: Actual AI Integrations
* **Key APIs Used**:
  * **Gemini 2.5 Flash**: Orchestrates conversational flow, translates regional inputs, and parses locations.
  * **Gemini 2.5 Multimodal**: Compares intake and closure photos against a checklist to confirm pipe or road repair.
  * **Gemini Embeddings (`text-embedding-004`)**: Powers semantic duplication checks and vector retrieval of SOP policies.
* **Speaker Script**:
  > "We do not use mock wrappers. Sahayak is integrated directly with the official Google Generative AI SDK, using Gemini 2.5 Flash for language tasks, Gemini Vision for before-and-after validation, and Gemini Embeddings for RAG search."

## Slide 6: Demo Walkthrough Flow
1. **Report**: Citizen uploads a photo of a pipe leak to the WhatsApp interface.
2. **Conversation**: The bot asks follow-up questions to identify the location, then files the ticket.
3. **Queue**: The ticket is classified as `WATER`, given a 24h SLA, and routed.
4. **Resolution**: The Water Officer reviews historical cases, uploads the fixed pipe photo, and the Vision AI approves it.
5. **MP Oversight**: The MP views the updated Ward Health Index and geospatial coordinates on the dashboard map.

## Slide 7: Why Sahayak Wins
* **Innovation & Business Impact**:
  * **Visual Proof Audit**: First system to require visual proof checked by Vision AI before closing municipal tasks.
  * **Scalable & Portable**: PostgreSQL/SQLite compatible, ready for public deployment.
  * **Absolute Accountability**: Multi-agent timeline logs are completely transparent, visible on citizen and leader portals alike.
* **Speaker Script**:
  > "Sahayak wins because it shifts governance from administrative paper-pushing to absolute accountability. By utilizing Google's Gemini models, we guarantee that municipal funds are used on actual repairs verified by AI."
