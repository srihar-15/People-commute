# Sahayak Tech Stack Directory

This document details every technology used in the Sahayak platform, where it is used, its purpose, and the rationale for its choice for a production-aligned GovTech platform.

---

## 1. Frontend Client
* **Framework**: Next.js 15 (React 19)
  * *Purpose*: Main user interface routing, static generation, server rendering, and hydration.
  * *Where Used*: Entire `frontend/` directory (Citizen, Officer, and MP Dashboards).
  * *Why Chosen*: App Router supports fast compilation (Turbopack) and easy server-side capabilities, facilitating high-performance load times essential for government services.
* **Styling**: TailwindCSS
  * *Purpose*: Utility-first styling for responsive layout design.
  * *Where Used*: Throughout Next.js components.
  * *Why Chosen*: Fast styling iteration without maintaining large separate stylesheets, conforming closely to structured responsive grid parameters.
* **Icons**: Lucide React
  * *Purpose*: Consistent, clean SVG iconography.
  * *Where Used*: Sidebar, headers, buttons, and status timelines.
  * *Why Chosen*: Modern and light footprint with strict matching UI layouts.

---

## 2. Backend Server
* **Framework**: FastAPI (Python 3.11)
  * *Purpose*: High-performance RESTful API endpoints and WebSocket servers.
  * *Where Used*: Entire `backend/` directory.
  * *Why Chosen*: Extremely fast execution times (on par with Go/NodeJS), native asynchronous support, automatic OpenAPI/Swagger generation, and seamless integration with Python-based AI libraries.
* **Database ORM**: SQLAlchemy 2.0
  * *Purpose*: Object-Relational Mapping for database queries.
  * *Where Used*: `backend/app/core/database.py` and model declarations in `backend/app/models/`.
  * *Why Chosen*: Enterprise-ready database abstraction layer. Facilitates swapping SQLite development engines with PostgreSQL production targets.

---

## 3. Database
* **Development**: SQLite
  * *Purpose*: Zero-config local development database.
  * *Where Used*: `backend/` local file storage.
  * *Why Chosen*: High speed, portable database testing for local MVP execution.
* **Production**: PostgreSQL (with pgvector)
  * *Purpose*: Production relational database storing grievances, users, audits, and vector embeddings.
  * *Where Used*: Target deployment database.
  * *Why Chosen*: Support for complex schemas, strict transaction isolation, and pgvector for native cosine vector similarity search.

---

## 4. AI & Conversational Agents
* **Agent Framework**: LangGraph
  * *Purpose*: Stateful, conversational, and multi-agent coordination.
  * *Where Used*: `backend/app/agents/` (Citizen Intake Chat StateGraph and Grievance Routing graph).
  * *Why Chosen*: Offers cyclic graphs, checkpoints, memory states, and resume capabilities, which are essential for multi-turn conversations and human-in-the-loop validation.
* **API SDK**: Google Generative AI Python SDK (`google-generativeai`)
  * *Purpose*: Official SDK to communicate with Google Gemini models.
  * *Where Used*: `backend/app/services/ai/shared_ai.py`
  * *Why Chosen*: Native access to state-of-the-art Google AI Studio models (Gemini 2.5 Flash / Pro).
* **Models Used**:
  * **Gemini 2.5 Flash**: Conversational reasoning, translation, and structured JSON extraction in citizen intake. Also drives before-and-after image verification (multimodal analysis).
  * **Gemini Embeddings (`text-embedding-004`)**: Generates vector representations of grievance texts for duplicate detection and RAG retrieval.
