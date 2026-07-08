# Sahayak: Constituency Intelligence & Support Platform

Sahayak is an enterprise-grade, multi-agent governance decision support platform designed for municipal and constituency administration. It facilitates intelligent, transparent, and verified communications between Citizens, Department Officers, Members of Parliament (MPs), and System Administrators.

---

## 1. System Architecture

Sahayak is engineered as a decoupled, multi-tier system:

```mermaid
graph TD
    A[Citizen WhatsApp Sim / Portal] -->|GraphQL / REST| B[FastAPI Backend Gateway]
    C[Officer Dashboard] -->|REST / WebSockets| B
    D[MP Governance Dashboard] -->|REST / WebSockets| B
    E[Admin Console] -->|REST / WebSockets| B
    
    B -->|Pipeline Trigger| F[Agent State Machine]
    F -->|Nodes| G[Intake / Translate]
    F -->|Nodes| H[Classification]
    F -->|Nodes| I[Duplicate Vector Search]
    F -->|Nodes| J[Routing & SLA Assignment]
    
    B -->|Before/After Evidence| K[Resolution Assurance Agent]
    B -->|SOP Context Query| L[Officer Assistant Agent]
    B -->|Policy Context Query| M[Governance Intelligence RAG]
    
    K -->|Vision Check| N[Shared AI Services]
    L -->|Context Similarity| N
    M -->|Scheme Embeddings| N
    
    B -->|Query / Mutation| O[(PostgreSQL Database)]
```

---

## 2. Database Schema

The database relies on a PostgreSQL schema configured with native JSONB search indices:
* `users`: Stores citizen credentials, department affiliations, and role-based permissions (Citizen, Officer, MP, Admin).
* `departments`: Declares agencies (Water, Roads, Electricity, Sanitation, etc.) and SLA defaults.
* `grievances`: Tracks detailed descriptions, geo-coordinates, languages, priorities, SLA deadlines, and resolution tracking status.
* `evidences`: Contains uploaded intake files and closure proofs paired with AI Vision analysis check records.
* `decision_explanations`: Tracks AI model explanations, confidence metrics, and similarity logs.
* `knowledge_documents`: Houses versioned policy and scheme documents used by the MP RAG Agent.
* `constituency_health_indices`: Contains calculated metric snapshots per ward.
* `audit_logs`: Live record of status changes and administrative overrides.

---

## 3. Installation & Setup

Ensure you have **Python 3.10+**, **Node.js 18+**, and **PostgreSQL** running locally.

### A. Database Initialization
1. Create a database named `sahayak` in your PostgreSQL server.
2. In [backend/app/core/config.py](file:///d:/sahayak/backend/app/core/config.py), update your database credentials:
   ```python
   DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/sahayak"
   ```
3. Initialize the table schemas:
   ```bash
   cd backend
   python init_db_tables.py
   ```
4. Seed the demo dataset (wards, departments, documents, and historical complaints):
   ```bash
   cd backend
   python seed_data.py
   ```

### B. Run the FastAPI Backend Server
1. Navigate to the `backend/` directory.
2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the API server:
   ```bash
   python main.py
   ```
   *The server starts listening on `http://localhost:8000`.*

### C. Run the Next.js Frontend Dashboard
1. Navigate to the `frontend/` directory.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Launch the Next.js development server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:3000` in your web browser.*

---

## 4. Live Demo Walkthrough

### Step 1: Submit Complaint (Citizen Portal)
- Go to `http://localhost:3000/citizen`.
- The interface automatically signs you in as Citizen Ramesh Kumar.
- On the WhatsApp simulator (left), type: 
  > *"Major leakage in municipal pipe near house #10, water spraying everywhere."*
- Click **Send**.
- The backend automatically executes the **Citizen Intake Pipeline**:
  - Translates description if necessary.
  - Classifies the grievance to the **Water Supply Department**.
  - Assigns priority (`MEDIUM`) and sets an SLA deadline.

### Step 2: Accept Task (Officer Dashboard)
- Navigate to `http://localhost:3000/officer` (logged in as Sri K. Ramakrishna, Water Head).
- Select the new complaint in the **Department Queue**.
- Inspect the **Officer Assistant** panel (right) to view:
  - Retrieved Water SOP guidelines.
  - Similar historical resolved blockages.
  - Suggested repair actions.
- Click **Accept Task & Lock to Queue**.

### Step 3: Resolve & Verify (Officer Dashboard)
- Under the accepted task, click **Use Demo Proof Image** to load the resolution proof link:
  `https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg`
- Provide repair notes and click **Submit Proof & Trigger AI Verification**.
- The **Resolution Assurance Agent** compares the intake/repair photos using visual LLM parameters and verifies the repair is complete. Status updates to `RESOLVED`.

### Step 4: Confirm Closure (Citizen Portal)
- Switch back to the Citizen page.
- A live WhatsApp prompt alerts you that the issue is marked `RESOLVED`.
- Click **Confirm Fix** on the card to mark the ticket `CLOSED`.

### Step 5: Governance RAG & Analytics (MP Dashboard)
- Go to `http://localhost:3000/mp` (logged in as Dr. N. Chandrababu, MP).
- View overall Constituency Health index and specific category percentages per ward.
- Use the **Policy Intelligence Agent** chat to ask:
  > *"What are the recommended base course specifications for patching potholes?"*
- Observe the agent retrieving context chunks and citing verified reference documents.

---

## 5. Automated System Tests

You can execute a complete headless simulation of the entire workflow (Steps 1–4) by running our integration script:
```bash
cd backend
python test_integration.py
```
