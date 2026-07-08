import sys
import os
import uuid
import datetime
from sqlalchemy.orm import Session
import bcrypt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models import User, Department, Grievance, Evidence, AuditLog, KnowledgeDocument, ConstituencyHealthIndex, DecisionExplanation

# Direct bcrypt password hashing
def get_hashed_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

hashed_password = get_hashed_password("password123")

def get_mock_embedding(text_keyword):
    # Generates a pseudo-random but deterministic 1536-dimensional vector for mock embedding
    import random
    random.seed(hash(text_keyword) % 123456789)
    vector = [random.uniform(-0.1, 0.1) for _ in range(1536)]
    # L2 normalize
    norm = sum(x*x for x in vector) ** 0.5
    return [x/norm for x in vector]

def seed_database():
    db = SessionLocal()
    try:
        print("Checking if database is already seeded...")
        if db.query(User).filter_by(email="admin@sahayak.gov.in").first():
            print("Database already contains seed data. Skipping.")
            return

        print("Seeding Users...")
        # Users
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="System Administrator",
            role="admin",
            phone_number="+919999999901"
        )
        mp_vijayawada = User(
            id=uuid.uuid4(),
            email="mp_vijayawada@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Honorable MP (Vijayawada)",
            role="mp",
            phone_number="+919999999902"
        )
        mp_guntur = User(
            id=uuid.uuid4(),
            email="mp_guntur@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Honorable MP (Guntur)",
            role="mp",
            phone_number="+919999999907"
        )
        mp_vizag = User(
            id=uuid.uuid4(),
            email="mp_vizag@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Honorable MP (Vizag)",
            role="mp",
            phone_number="+919999999908"
        )
        water_officer = User(
            id=uuid.uuid4(),
            email="water_officer@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Municipal Water Head",
            role="officer",
            phone_number="+919999999903"
        )
        roads_officer = User(
            id=uuid.uuid4(),
            email="roads_officer@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Roads & Traffic Head",
            role="officer",
            phone_number="+919999999904"
        )
        sanitation_officer = User(
            id=uuid.uuid4(),
            email="sanitation_officer@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Sanitation Dept Head",
            role="officer",
            phone_number="+919999999905"
        )
        electricity_officer = User(
            id=uuid.uuid4(),
            email="electricity_officer@sahayak.gov.in",
            password_hash=hashed_password,
            full_name="Electricity Dept Head",
            role="officer",
            phone_number="+919999999906"
        )
        
        citizen_ramesh = User(
            id=uuid.uuid4(),
            email="ramesh@citizen.in",
            password_hash=hashed_password,
            full_name="Ramesh Kumar",
            role="citizen",
            phone_number="+919876543210"
        )
        citizen_sitha = User(
            id=uuid.uuid4(),
            email="sitha@citizen.in",
            password_hash=hashed_password,
            full_name="Sitha Devi",
            role="citizen",
            phone_number="+919876543211"
        )
        citizen_arjun = User(
            id=uuid.uuid4(),
            email="arjun@citizen.in",
            password_hash=hashed_password,
            full_name="Arjun Prasad",
            role="citizen",
            phone_number="+919876543212"
        )

        db.add_all([admin_user, mp_vijayawada, mp_guntur, mp_vizag, water_officer, roads_officer, sanitation_officer, electricity_officer, citizen_ramesh, citizen_sitha, citizen_arjun])
        db.flush() # populated IDs in session

        print("Seeding Departments...")
        # Departments
        water_dept = Department(
            id=uuid.uuid4(),
            name="Municipal Water Supply & Sewerage Board",
            code="WATER",
            head_officer_id=water_officer.id,
            sla_hours=24
        )
        roads_dept = Department(
            id=uuid.uuid4(),
            name="Roads, Traffic & Highway Maintenance",
            code="ROADS",
            head_officer_id=roads_officer.id,
            sla_hours=48
        )
        sanitation_dept = Department(
            id=uuid.uuid4(),
            name="Sanitation, Solid Waste & Environmental Health",
            code="SANITATION",
            head_officer_id=sanitation_officer.id,
            sla_hours=24
        )
        electricity_dept = Department(
            id=uuid.uuid4(),
            name="State Power Transmission & Distribution Corp",
            code="ELECTRICITY",
            head_officer_id=electricity_officer.id,
            sla_hours=12
        )

        db.add_all([water_dept, roads_dept, sanitation_dept, electricity_dept])
        db.flush()

        print("Seeding RAG Knowledge Documents...")
        # Versioned Knowledge Documents
        docs = [
            KnowledgeDocument(
                title="SOP on Water Pipe Leakage Repair",
                content_chunk="Standard Operating Procedure for handling municipal water pipeline leakages. Upon intake classification, water supply must be isolated. Repair team must deploy within 6 hours. High-grade PVC or Cast Iron clamps must be used. Before-and-after photographic evidence is mandatory for billing and closure confirmation.",
                embedding=get_mock_embedding("water leakage pipe clamp repair"),
                source_uri="/docs/sop/water_repair_v1.pdf",
                version="1.2.0",
                publication_date=datetime.date(2025, 4, 15),
                metadata_info={"department": "WATER", "type": "SOP"}
            ),
            KnowledgeDocument(
                title="SOP on Sewage Blockage Clearance",
                content_chunk="Guidelines for clearing sewer blockages in residential wards. Jetting machines are the primary tools. Manual scavenging is strictly prohibited. Work must be scheduled during low-flow periods (10 PM to 5 AM or 11 AM to 4 PM). Verification requires video inspection or local community certificate.",
                embedding=get_mock_embedding("sewer sewage blockage jetting"),
                source_uri="/docs/sop/sewer_clearance_v2.pdf",
                version="2.0.1",
                publication_date=datetime.date(2025, 8, 1),
                metadata_info={"department": "WATER", "type": "SOP"}
            ),
            KnowledgeDocument(
                title="Road Repaving & Pothole Patching Protocol",
                content_chunk="Detailed SOP for patching and repaving municipal roads. Excavation depth must be a minimum of 40mm. Base course aggregate must be compacted to 95% density. Hot-mix asphalt concrete (AC) is required for arterial streets; cold-mix is only allowed as temporary measure. Photo of repair with GPS tag required.",
                embedding=get_mock_embedding("road pothole asphalt paving patch"),
                source_uri="/docs/sop/road_repair_v3.pdf",
                version="3.1.0",
                publication_date=datetime.date(2024, 12, 10),
                metadata_info={"department": "ROADS", "type": "SOP"}
            ),
            KnowledgeDocument(
                title="Sanitation & Garbage Management Guidelines",
                content_chunk="Solid waste collection standards. Ward-level dustbins must be cleared every 24 hours. Segregation at source (dry vs wet waste) is mandatory. Heavy penalty rules apply for illegal open dumping. Cleanliness audits are conducted weekly by the Sanitation Inspector.",
                embedding=get_mock_embedding("garbage waste garbage bin clean sanitation dumping"),
                source_uri="/docs/sop/garbage_mgmt_v1.pdf",
                version="1.0.0",
                publication_date=datetime.date(2025, 1, 20),
                metadata_info={"department": "SANITATION", "type": "SOP"}
            ),
            KnowledgeDocument(
                title="Constituency Development Plan (2026-2030)",
                content_chunk="Key priorities for infrastructure improvement in the constituency. Highlights budget allocation of ₹45 Crores for road expansion, ₹20 Crores for water purification plants, and ₹15 Crores for solar street lighting in high-crime wards (Ward 4 and Ward 5). Aiming for 98% sanitation coverage by 2028.",
                embedding=get_mock_embedding("constituency budget water road infrastructure development"),
                source_uri="/docs/plans/cdp_2026.pdf",
                version="2.6.0",
                publication_date=datetime.date(2026, 1, 5),
                metadata_info={"department": "ALL", "type": "PLAN"}
            ),
            KnowledgeDocument(
                title="Jal Jeevan Mission Guidelines",
                content_chunk="Centrally sponsored scheme. Ensures Functional Household Tap Connection (FHTC) to every rural home. Clean drinking water supply standard is 55 litres per capita per day (lpcd). Quality testing for Fluoride, Arsenic, and Iron must be executed bi-annually.",
                embedding=get_mock_embedding("drinking water tap connection jal jeevan quality testing"),
                source_uri="/docs/schemes/jal_jeevan_guidelines.pdf",
                version="3.2.0",
                publication_date=datetime.date(2024, 5, 22),
                metadata_info={"department": "WATER", "type": "SCHEME"}
            )
        ]
        db.add_all(docs)
        db.flush()

        print("Seeding Constituency Health Index snapshots...")
        # Wards initial metrics (out of 100)
        wards = ["Ward 1 (Vasant Nagar)", "Ward 2 (Ganesh Nagar)", "Ward 3 (Subhash Nagar)", "Ward 4 (Bhimrao Colony)", "Ward 5 (Shastri Nagar)"]
        health_indices = []
        for idx, ward in enumerate(wards):
            # Seed varying metrics so trends look nice
            w_score = 80.0 + (idx * 3.5) % 15.0
            r_score = 75.0 + (idx * 4.2) % 20.0
            e_score = 85.0 - (idx * 2.8) % 15.0
            sa_score = 90.0 - (idx * 5.1) % 10.0
            h_score = 82.0 + (idx * 1.5) % 10.0
            s_score = 70.0 + (idx * 6.5) % 25.0
            safety = 88.0 - (idx * 3.0) % 12.0
            
            avg_health = (w_score + r_score + e_score + sa_score + h_score + s_score + safety) / 7.0
            
            health_indices.append(ConstituencyHealthIndex(
                ward_id=ward,
                water_score=round(w_score, 1),
                roads_score=round(r_score, 1),
                electricity_score=round(e_score, 1),
                education_score=round(e_score, 1),
                healthcare_score=round(h_score, 1),
                sanitation_score=round(s_score, 1),
                safety_score=round(safety, 1),
                overall_health_index=round(avg_health, 1),
                computed_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ))
        db.add_all(health_indices)
        db.flush()

        print("Seeding Grievances & Explanations...")
        
        # 1. Closed Water Complaint
        exp_1 = DecisionExplanation(
            classification_reasoning="The description clearly indicates a pipe burst resulting in water wastage. Identified keywords: leakage, pipe, municipal water.",
            duplicate_similarity_score=0.15,
            priority_factors={"safety": False, "volume": 1, "severity": "medium"},
            routing_explanation="Routed to Municipal Water Supply & Sewerage Board since it belongs to WATER code.",
            confidence_score=0.92,
            extracted_entities={"location": "Ward 1", "infrastructure": "water_pipeline"}
        )
        db.add(exp_1)
        db.flush()
        
        g1 = Grievance(
            id=uuid.uuid4(),
            title="Main water supply pipe leaking",
            description="There is a major leak in the main pipeline near house #45 in Vasant Nagar. Water is logging on the street.",
            description_embedding=get_mock_embedding("main water supply pipe leaking vasant nagar house leak"),
            status="CLOSED",
            priority="MEDIUM",
            priority_score=0.45,
            citizen_id=citizen_ramesh.id,
            department_id=water_dept.id,
            assigned_officer_id=water_officer.id,
            explanation_id=exp_1.id,
            latitude=16.5062, # Centered near Vijayawada (AP representative coords)
            longitude=80.6480,
            source="whatsapp",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            resolved_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
            sla_deadline=datetime.datetime.utcnow() - datetime.timedelta(days=4)
        )
        db.add(g1)
        db.flush()
        
        # Evidence for G1
        ev_1_intake = Evidence(
            grievance_id=g1.id,
            uploader_id=citizen_ramesh.id,
            media_url="https://sahayak-demo-evidence.s3.amazonaws.com/intake_pipe_burst.jpg",
            notes="Water spraying on the road.",
            type="intake_evidence"
        )
        ev_1_closure = Evidence(
            grievance_id=g1.id,
            uploader_id=water_officer.id,
            media_url="https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg",
            notes="Pipe patch completed, clamp installed.",
            type="closure_proof",
            verification_report={"match_confidence": 0.89, "is_verified": True, "remarks": "Before image showed flowing water, after image shows dry asphalt and new metal clamp."}
        )
        db.add_all([ev_1_intake, ev_1_closure])
        
        audit_g1_1 = AuditLog(
            grievance_id=g1.id,
            user_id=citizen_ramesh.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED",
            rationale="Initial complaint filed via WhatsApp."
        )
        audit_g1_2 = AuditLog(
            grievance_id=g1.id,
            user_id=None,
            action="AUTO_ROUTE",
            old_status="SUBMITTED",
            new_status="ROUTED",
            rationale="AI Agent routed to Water Department."
        )
        audit_g1_3 = AuditLog(
            grievance_id=g1.id,
            user_id=water_officer.id,
            action="ACCEPT",
            old_status="ROUTED",
            new_status="ASSIGNED",
            rationale="Accepted by Officer Ramakrishna."
        )
        audit_g1_4 = AuditLog(
            grievance_id=g1.id,
            user_id=water_officer.id,
            action="RESOLVE",
            old_status="ASSIGNED",
            new_status="RESOLVED",
            rationale="Officer completed repair and uploaded proof."
        )
        audit_g1_5 = AuditLog(
            grievance_id=g1.id,
            user_id=citizen_ramesh.id,
            action="CONFIRM_CLOSE",
            old_status="RESOLVED",
            new_status="CLOSED",
            rationale="Citizen confirmed fix on WhatsApp chat."
        )
        db.add_all([audit_g1_1, audit_g1_2, audit_g1_3, audit_g1_4, audit_g1_5])
        
        # 2. Resolved Road Complaint
        exp_2 = DecisionExplanation(
            classification_reasoning="Pothole complaint on main road. Keywords: road, pothole, accident, drive.",
            duplicate_similarity_score=0.12,
            priority_factors={"safety": True, "volume": 1, "severity": "high"},
            routing_explanation="Routed to Roads, Traffic & Highway Maintenance based on ROADS category match.",
            confidence_score=0.95,
            extracted_entities={"location": "Ward 2", "infrastructure": "road_surface"}
        )
        db.add(exp_2)
        db.flush()
        
        g2 = Grievance(
            id=uuid.uuid4(),
            title="Dangerous pothole in Ganesh Nagar",
            description="There is a very deep and wide pothole right at the intersection of Main Road and Lane 3 in Ganesh Nagar. Two-wheelers are slipping daily.",
            description_embedding=get_mock_embedding("dangerous pothole ganesh nagar intersection road two-wheelers slip"),
            status="RESOLVED",
            priority="HIGH",
            priority_score=0.82,
            citizen_id=citizen_sitha.id,
            department_id=roads_dept.id,
            assigned_officer_id=roads_officer.id,
            explanation_id=exp_2.id,
            latitude=16.5120,
            longitude=80.6402,
            source="web",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            resolved_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )
        db.add(g2)
        db.flush()
        
        ev_2_intake = Evidence(
            grievance_id=g2.id,
            uploader_id=citizen_sitha.id,
            media_url="https://sahayak-demo-evidence.s3.amazonaws.com/intake_pothole.jpg",
            notes="Pothole filled with rainwater, hidden danger.",
            type="intake_evidence"
        )
        ev_2_closure = Evidence(
            grievance_id=g2.id,
            uploader_id=roads_officer.id,
            media_url="https://sahayak-demo-evidence.s3.amazonaws.com/closure_pothole_filled.jpg",
            notes="Pothole filled and sealed with hot-mix asphalt.",
            type="closure_proof",
            verification_report={"match_confidence": 0.94, "is_verified": True, "remarks": "Before image showed a water-filled hole in asphalt. After image shows fresh black aggregate patch flush with the road."}
        )
        db.add_all([ev_2_intake, ev_2_closure])
        
        audit_g2_1 = AuditLog(
            grievance_id=g2.id,
            user_id=citizen_sitha.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED",
            rationale="Initial complaint filed via Citizen Web Portal."
        )
        audit_g2_2 = AuditLog(
            grievance_id=g2.id,
            user_id=None,
            action="AUTO_ROUTE",
            old_status="SUBMITTED",
            new_status="ROUTED",
            rationale="AI Agent routed to Roads Department with high priority."
        )
        audit_g2_3 = AuditLog(
            grievance_id=g2.id,
            user_id=roads_officer.id,
            action="ACCEPT",
            old_status="ROUTED",
            new_status="ASSIGNED",
            rationale="Accepted by Officer Srinivasa Rao."
        )
        audit_g2_4 = AuditLog(
            grievance_id=g2.id,
            user_id=roads_officer.id,
            action="RESOLVE",
            old_status="ASSIGNED",
            new_status="RESOLVED",
            rationale="Officer filled the pothole and submitted closure evidence. Awaiting citizen confirmation."
        )
        db.add_all([audit_g2_1, audit_g2_2, audit_g2_3, audit_g2_4])

        # 3. Assigned Garbage Complaint
        exp_3 = DecisionExplanation(
            classification_reasoning="Piles of uncollected household waste. Keywords: garbage, waste, smell, dogs.",
            duplicate_similarity_score=0.08,
            priority_factors={"safety": False, "volume": 2, "severity": "medium"},
            routing_explanation="Routed to Sanitation, Solid Waste & Environmental Health based on SANITATION category match.",
            confidence_score=0.91,
            extracted_entities={"location": "Ward 3", "infrastructure": "garbage_collection"}
        )
        db.add(exp_3)
        db.flush()
        
        g3 = Grievance(
            id=uuid.uuid4(),
            title="Garbage bin overflow in Subhash Nagar",
            description="The public garbage bin at Subhash Nagar near the park has not been cleared for 4 days. It is stinking, and street dogs are scattering the waste.",
            description_embedding=get_mock_embedding("garbage bin overflow subhash nagar park clear days waste dogs"),
            status="ASSIGNED",
            priority="MEDIUM",
            priority_score=0.58,
            citizen_id=citizen_arjun.id,
            department_id=sanitation_dept.id,
            assigned_officer_id=sanitation_officer.id,
            explanation_id=exp_3.id,
            latitude=16.4995,
            longitude=80.6550,
            source="whatsapp",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        )
        db.add(g3)
        db.flush()
        
        ev_3_intake = Evidence(
            grievance_id=g3.id,
            uploader_id=citizen_arjun.id,
            media_url="https://sahayak-demo-evidence.s3.amazonaws.com/intake_garbage.jpg",
            notes="Stuck garbage piled around the bin.",
            type="intake_evidence"
        )
        db.add(ev_3_intake)
        
        audit_g3_1 = AuditLog(
            grievance_id=g3.id,
            user_id=citizen_arjun.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED",
            rationale="Submitted photo and description on WhatsApp."
        )
        audit_g3_2 = AuditLog(
            grievance_id=g3.id,
            user_id=None,
            action="AUTO_ROUTE",
            old_status="SUBMITTED",
            new_status="ROUTED",
            rationale="AI Agent routed to Sanitation Department."
        )
        audit_g3_3 = AuditLog(
            grievance_id=g3.id,
            user_id=sanitation_officer.id,
            action="ACCEPT",
            old_status="ROUTED",
            new_status="ASSIGNED",
            rationale="Accepted by Officer Lakshmi. Sanitation truck queued."
        )
        db.add_all([audit_g3_1, audit_g3_2, audit_g3_3])

        # 4. Routed Electricity Street Light (In Queue)
        exp_4 = DecisionExplanation(
            classification_reasoning="Street light malfunction. Keywords: street lights, dark, unsafe, power.",
            duplicate_similarity_score=0.10,
            priority_factors={"safety": True, "volume": 1, "severity": "medium"},
            routing_explanation="Routed to State Power Transmission & Distribution Corp based on ELECTRICITY category match.",
            confidence_score=0.88,
            extracted_entities={"location": "Ward 4", "infrastructure": "street_lighting"}
        )
        db.add(exp_4)
        db.flush()
        
        g4 = Grievance(
            id=uuid.uuid4(),
            title="Non-functional street lights in Bhimrao Colony",
            description="The entire stretch of street lights on Main Street in Bhimrao Colony is dead. It is pitch dark at night, making it very unsafe for women and children.",
            description_embedding=get_mock_embedding("non-functional street lights bhimrao colony dark unsafe night"),
            status="ROUTED",
            priority="MEDIUM",
            priority_score=0.67,
            citizen_id=citizen_ramesh.id,
            department_id=electricity_dept.id,
            explanation_id=exp_4.id,
            latitude=16.4880,
            longitude=80.6385,
            source="whatsapp",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        )
        db.add(g4)
        db.flush()
        
        audit_g4_1 = AuditLog(
            grievance_id=g4.id,
            user_id=citizen_ramesh.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED",
            rationale="Filed on WhatsApp."
        )
        audit_g4_2 = AuditLog(
            grievance_id=g4.id,
            user_id=None,
            action="AUTO_ROUTE",
            old_status="SUBMITTED",
            new_status="ROUTED",
            rationale="AI Agent classified and routed to Electricity Department Queue."
        )
        db.add_all([audit_g4_1, audit_g4_2])

        # 5. Human Review Water Complaint (low confidence)
        exp_5 = DecisionExplanation(
            classification_reasoning="Grievance mentions dirty smell and muddy water, but also complains about roads getting flooded. Uncertain category split between Water and Sanitation.",
            duplicate_similarity_score=0.22,
            priority_factors={"safety": True, "volume": 1, "severity": "high"},
            routing_explanation="Kept in HUMAN_REVIEW. Confidence score below 75% threshold.",
            confidence_score=0.58,
            extracted_entities={"location": "Ward 5"}
        )
        db.add(exp_5)
        db.flush()
        
        g5 = Grievance(
            id=uuid.uuid4(),
            title="Smelly brown tap water and clogged drains",
            description="The tap water coming to Shastri Nagar area has a very bad chemical smell and looks mud-brown. There is also a clogged open drain that might be leaking into the water pipes.",
            description_embedding=get_mock_embedding("smelly brown tap water clogged drains shastri nagar mud smell leak"),
            status="HUMAN_REVIEW",
            priority="HIGH",
            priority_score=0.74,
            citizen_id=citizen_sitha.id,
            explanation_id=exp_5.id,
            latitude=16.5255,
            longitude=80.6610,
            source="web",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        )
        db.add(g5)
        db.flush()
        
        audit_g5_1 = AuditLog(
            grievance_id=g5.id,
            user_id=citizen_sitha.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED",
            rationale="Filed via portal."
        )
        audit_g5_2 = AuditLog(
            grievance_id=g5.id,
            user_id=None,
            action="PENDING_REVIEW",
            old_status="SUBMITTED",
            new_status="HUMAN_REVIEW",
            rationale="AI classification confidence (58%) is below threshold. Queued for administrator review."
        )
        db.add_all([audit_g5_1, audit_g5_2])

        # 6. Duplicates Clustering Demonstration
        # Master Issue: Water pipe burst in Ward 4
        exp_master = DecisionExplanation(
            classification_reasoning="Water pipe burst causing heavy road flooding.",
            duplicate_similarity_score=0.0,
            priority_factors={"safety": True, "volume": 10, "severity": "high"},
            routing_explanation="Routed to Water Department.",
            confidence_score=0.96,
            extracted_entities={"location": "Ward 4"}
        )
        db.add(exp_master)
        db.flush()
        
        g_master = Grievance(
            id=uuid.uuid4(),
            title="Huge water pipe burst in Bhimrao Colony",
            description="The main water pipeline near the community center has burst. Water is gushing out like a fountain. The entire road is flooded, and houses are getting inundated.",
            description_embedding=get_mock_embedding("huge water pipe burst bhimrao colony road flooded fountain"),
            status="ROUTED",
            priority="EMERGENCY",
            priority_score=0.98,
            citizen_id=citizen_ramesh.id,
            department_id=water_dept.id,
            explanation_id=exp_master.id,
            latitude=16.4892,
            longitude=80.6391,
            source="whatsapp",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            sla_deadline=datetime.datetime.utcnow() + datetime.timedelta(hours=4)
        )
        db.add(g_master)
        db.flush()
        
        audit_m_1 = AuditLog(
            grievance_id=g_master.id,
            user_id=citizen_ramesh.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED"
        )
        audit_m_2 = AuditLog(
            grievance_id=g_master.id,
            user_id=None,
            action="AUTO_ROUTE",
            old_status="SUBMITTED",
            new_status="ROUTED",
            rationale="Classified as Water leakage. Flagged as EMERGENCY due to flood risk."
        )
        db.add_all([audit_m_1, audit_m_2])
        db.flush()
        
        # Duplicate Issue 1 (will be clustered under master)
        exp_dup = DecisionExplanation(
            classification_reasoning="Identified as duplicate of master issue: water pipe burst in Bhimrao Colony.",
            duplicate_similarity_score=0.92,
            priority_factors={"safety": True, "volume": 10, "severity": "high"},
            routing_explanation="Linked to Master Grievance.",
            confidence_score=0.98,
            extracted_entities={"location": "Ward 4"}
        )
        db.add(exp_dup)
        db.flush()
        
        g_dup = Grievance(
            id=uuid.uuid4(),
            title="Road flooded due to pipe leak in Bhimrao Colony",
            description="The road near the community center is completely under water. A drinking water pipeline has broken here. Please fix it immediately.",
            description_embedding=get_mock_embedding("road flooded pipe leak bhimrao colony community center drinking broken"),
            status="DUPLICATE_CLUSTERED",
            priority="HIGH",
            priority_score=0.90,
            citizen_id=citizen_arjun.id,
            department_id=water_dept.id,
            master_issue_id=g_master.id, # LINKED
            explanation_id=exp_dup.id,
            latitude=16.4895,
            longitude=80.6394,
            source="whatsapp",
            language="en",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=45)
        )
        db.add(g_dup)
        db.flush()
        
        audit_d_1 = AuditLog(
            grievance_id=g_dup.id,
            user_id=citizen_arjun.id,
            action="SUBMIT",
            old_status=None,
            new_status="SUBMITTED"
        )
        audit_d_2 = AuditLog(
            grievance_id=g_dup.id,
            user_id=None,
            action="CLUSTER_DUPLICATE",
            old_status="SUBMITTED",
            new_status="DUPLICATE_CLUSTERED",
            rationale=f"AI Duplicate Detection matched this complaint (92% similarity) with active Master Grievance ID: {g_master.id}."
        )
        db.add_all([audit_d_1, audit_d_2])
        
        db.commit()
        print("Database successfully seeded with realistic demo data!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
