# Sahayak API Reference Directory

This document provides technical documentation for all RESTful and WebSocket API endpoints in the Sahayak platform.

---

## 1. Authentication Portals

### Register User
* **Method**: `POST`
* **Endpoint**: `/api/v1/auth/register`
* **Authentication**: None
* **Request Body**:
  ```json
  {
    "email": "water_officer@sahayak.gov.in",
    "password": "password123",
    "full_name": "Municipal Water Head",
    "role": "officer",
    "phone_number": "+919999999903"
  }
  ```
* **Response**:
  ```json
  {
    "id": "c1a6b094-1a3b-4c28-9844-3c6fde83ac58",
    "email": "water_officer@sahayak.gov.in",
    "full_name": "Municipal Water Head",
    "role": "officer",
    "phone_number": "+919999999903",
    "created_at": "2026-07-08T10:14:02.124Z"
  }
  ```

### Login User
* **Method**: `POST`
* **Endpoint**: `/api/v1/auth/login`
* **Authentication**: None
* **Request Body**:
  ```json
  {
    "email": "mp_vijayawada@sahayak.gov.in",
    "password": "password123"
  }
  ```
* **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "mp",
    "name": "Honorable MP (Vijayawada)",
    "email": "mp_vijayawada@sahayak.gov.in",
    "user_id": "8ad14966-6e93-410d-939c-70cbe4213131"
  }
  ```

---

## 2. Grievance Management APIs

### File Grievance (Web Citizen Intake)
* **Method**: `POST`
* **Endpoint**: `/api/v1/grievances/`
* **Authentication**: Bearer JWT (Citizen)
* **Request Body**:
  ```json
  {
    "title": "Water Pipe Burst Vasant Nagar",
    "description": "Clean drinking water is leaking onto main street from broken pipeline.",
    "latitude": 16.5062,
    "longitude": 80.6480,
    "source": "WEB",
    "language": "en",
    "evidence_url": "https://example.com/intake.jpg"
  }
  ```
* **Response**:
  ```json
  {
    "id": "e45f9a6e-41a9-4672-913a-cc894fe9b0f6",
    "title": "Water Pipe Burst Vasant Nagar",
    "status": "SUBMITTED",
    "priority": "MEDIUM",
    "priority_score": 0.5,
    "citizen_id": "da61e5b4-4b1a-47eb-835e-a8175087fe4a"
  }
  ```

### List Grievances
* **Method**: `GET`
* **Endpoint**: `/api/v1/grievances/`
* **Query Parameters**:
  * `status_filter` (Optional, e.g. `ROUTED`, `ASSIGNED`, `RESOLVED`, `CLOSED`)
  * `dept_filter` (Optional, UUID of department)
* **Authentication**: Bearer JWT (Role-Based Access Control)
  * *Citizen*: Returns only their own complaints.
  * *Officer*: Returns complaints routed to or resolved by their department.
  * *MP/Admin*: Returns all constituency complaints.

### Get Grievance Detail
* **Method**: `GET`
* **Endpoint**: `/api/v1/grievances/{id}`
* **Authentication**: Bearer JWT
* **Response**: Includes full grievance details, AI category decision explanation, uploaded evidence before/after URLs, and the complete **explainable multi-agent audit timeline**.

### Resolve Grievance (Vision verification)
* **Method**: `POST`
* **Endpoint**: `/api/v1/grievances/{id}/resolve`
* **Authentication**: Bearer JWT (Officer)
* **Request Body**:
  ```json
  {
    "evidence_url": "https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg",
    "notes": "Replaced PVC pipe section and tightened clamp."
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "message": "AI Verification passed. Status updated to RESOLVED. Notification dispatched to citizen.",
    "report": {
      "is_verified": true,
      "match_confidence": 0.92,
      "remarks": "Before image showed a defect. After image shows repairs complete.",
      "verification_checklist": [
        "Defect is no longer visible",
        "New repair materials match surrounding structure"
      ]
    }
  }
  ```

---

## 3. Conversational Bot Gateway

### Conversational WhatsApp Simulator
* **Method**: `POST`
* **Endpoint**: `/api/v1/grievances/whatsapp`
* **Authentication**: Bearer JWT (Citizen)
* **Request Body**:
  ```json
  {
    "message": "Water pipe leak in street 4 Vasant Nagar",
    "media_url": null,
    "content_type": null
  }
  ```
* **Response (Conversational AI dynamic turn)**:
  ```json
  {
    "reply": "Thank you. Since when has this water leak been happening? Is it affecting nearby traffic?"
  }
  ```

---

## 4. Real-Time WebSockets
Clients open WebSockets to receive live JSON events:
* **Citizen Feed**: `ws://localhost:8000/ws/citizen`
* **Officer Feed**: `ws://localhost:8000/ws/officer`
* **MP Dashboard Feed**: `ws://localhost:8000/ws/mp`
* **Format**:
  ```json
  {
    "event": "GRIEVANCE_UPDATED",
    "grievance_id": "e45f9a6e-41a9-4672-913a-cc894fe9b0f6",
    "status": "ASSIGNED",
    "message": "Officer Municipal Water Head accepted task."
  }
  ```
