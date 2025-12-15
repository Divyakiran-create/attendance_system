# 📸 AI-Based Classroom Surveillance & Attendance System

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)

An automated, biometric attendance system designed for classroom surveillance. Unlike traditional punch-in systems, this platform leverages **Computer Vision** to analyze group photographs captured at the **Start**, **Mid**, and **End** of a lecture.

The system enforces a **3-Point Verification Logic**: a student is marked **Present** in the final attendance report *only if* their face is successfully identified in **all three** temporal checkpoints.

---

## 🏗️ System Architecture

The application is built using a **Containerized Microservice Architecture**, optimized for scalability, isolation, and production deployment.

### Architectural Flow

1. **Client Layer**  
   Users interact through the FastAPI Swagger UI (or future web/mobile clients) to upload high-resolution classroom images.

2. **API Gateway**  
   FastAPI validates incoming requests, identifies the session type (`start`, `mid`, `end`), and forwards them for processing.

3. **AI Processing Engine**  
   Uses `dlib` (HOG/CNN models) to:
   - Detect faces
   - Generate 128-dimensional facial embeddings
   - Perform Euclidean distance matching against enrolled users

4. **Data Persistence Layer**
   - **Enrolled Faces:** Stored as vector embeddings
   - **Sightings:** Raw logs of every detected face per session
   - **Attendance:** Final consolidated daily records

```mermaid
graph TD
    subgraph Docker_Host [Docker Container Environment]
        subgraph Services
            API[API Gateway (FastAPI)]
            AI[AI Processing Engine]
        end

        subgraph Data_Layer
            DB[(PostgreSQL)]
        end
    end

    Client[Client / Camera Feed] -->|POST Group Photo| API
    API -->|Async Processing| AI
    AI -->|Fetch Known Encodings| DB
    AI -->|Match Faces & Log Sighting| DB

    subgraph Logic_Check [End of Day Process]
        Batch[Finalize Attendance] -->|Query Sightings| DB
        DB -->|Verify Start + Mid + End| Batch
        Batch -->|Write Final Status| DB
    end

attendance_system/
├── app/
│   ├── core/
│   │   └── database.py       # DB connection & session management
│   ├── models/
│   │   ├── user.py           # User table definition
│   │   ├── face.py           # Biometric vector storage
│   │   ├── sighting.py       # Raw sighting logs (Start/Mid/End)
│   │   ├── attendance.py     # Final consolidated attendance
│   │   └── __init__.py       # Model registry
│   ├── routers/
│   │   ├── auth.py           # System health & validation endpoints
│   │   ├── user.py           # User enrollment APIs
│   │   └── classroom.py      # Surveillance & attendance logic
│   ├── services/
│   │   └── face.py           # Core AI logic (face_recognition wrapper)
│   └── main.py               # Application entrypoint
├── alembic/                  # Database migrations
├── docker-compose.yml        # Infrastructure orchestration
├── Dockerfile                # Container environment definition
└── requirements.txt          # Python dependencies
