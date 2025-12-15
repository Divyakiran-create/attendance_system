# 📸 AI-Based Classroom Surveillance & Attendance System

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)

An automated, biometric attendance system designed for classroom surveillance. Unlike traditional "punch-in" systems, this microservice uses **Computer Vision** to analyze group photos taken at the **Start**, **Mid**, and **End** of a lecture.

The system utilizes a **3-Point Verification Logic**: A student is marked "Present" in the final daily report *only* if their face is successfully identified in all three temporal checkpoints.

---

## 🏗️ System Architecture

The application follows a **Containerized Microservice Architecture**.

1.  **Client Layer:** Users interact via the FastAPI Swagger UI (or future mobile apps) to upload high-resolution group photos.
2.  **API Gateway:** FastAPI receives the payload, validates the session type (Start/Mid/End), and routes the request.
3.  **AI Engine:** The core service uses `dlib` (HOG/CNN models) to detect faces, generate 128-dimensional biometric embeddings, and perform Euclidean distance matching against enrolled users.
4.  **Data Persistence:**
    * **Enrolled Faces:** Stored as vector arrays.
    * **Sightings:** Raw logs of every identification event.
    * **Attendance:** Final consolidated records based on business logic.

```mermaid
graph TD
    subgraph Docker_Host [Docker Container Environment]
        subgraph Services
            API["API Gateway (FastAPI)"]
            AI["AI Processing Engine"]
        end

        subgraph Data_Layer
            DB[("PostgreSQL")]
        end
    end

    Client["Client / Camera Feed"] -->|POST Group Photo| API
    API -->|Async Processing| AI
    AI -->|Fetch Known Encodings| DB
    AI -->|Match Faces & Log Sighting| DB
    
    subgraph Logic_Check [End of Day Process]
        Batch["Finalize Attendance"] -->|Query Sightings| DB
        DB -->|Verify Start+Mid+End| Batch
        Batch -->|Write Final Status| DB
    end
````

-----

## 📂 Project Structure

The codebase is organized following modern Python backend standards, separating concerns between Routers (Controllers), Models (ORM), and Services (Logic).

```txt
attendance_system/
├── app/
│   ├── core/
│   │   └── database.py       # DB Connection & Session management
│   ├── models/
│   │   ├── user.py           # User table definition
│   │   ├── face.py           # Biometric vector storage
│   │   ├── sighting.py       # Raw sighting logs (Start/Mid/End)
│   │   ├── attendance.py     # Final consolidated attendance
│   │   └── __init__.py       # Model registry
│   ├── routers/
│   │   ├── auth.py           # System health & face checks
│   │   ├── user.py           # User enrollment endpoints
│   │   └── classroom.py      # Surveillance & Logic endpoints
│   ├── services/
│   │   └── face.py           # Core AI logic (face_recognition lib wrapper)
│   └── main.py               # Application Entrypoint
├── alembic/                  # Database Migrations
├── docker-compose.yml        # Infrastructure orchestration
├── Dockerfile                # Environment definition
└── requirements.txt          # Python dependencies
```

-----

## 🚀 Installation & Setup

This project is fully Dockerized. You do not need to install Python, PostgreSQL, or AI libraries manually on your host machine.

### Prerequisites

  * **Docker Desktop** (Running)
  * **Git**

### 1\. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/attendance_system.git](https://github.com/YOUR_USERNAME/attendance_system.git)
cd attendance_system
```

### 2\. Build and Start Services

This command pulls the Postgres image, builds the Python AI container, and networks them together.
*(Note: First build may take \~5-10 minutes to compile `dlib`).*

```bash
docker compose up -d --build
```

### 3\. Initialize the Database

The database starts empty. Run the migration scripts to generate the schema.

```bash
docker compose exec web alembic upgrade head
```

### 4\. Verify Deployment

Access the interactive API documentation at:
👉 **http://localhost:8000/docs**

-----

## 🧪 Usage Workflow

### Step 1: User Enrollment

  * **Endpoint:** `POST /users/`
  * **Action:** Provide `full_name`, `email`, and a clear **Face Photo**.
  * **Result:** The system extracts and stores the 128-d face encoding.

### Step 2: Surveillance (The "3-Check" Process)

Simulate a class session by uploading group photos at three intervals.

1.  **Start of Class:**
      * `POST /classroom/upload-group-photo` -\> `check_type="start"`
2.  **Middle of Class:**
      * `POST /classroom/upload-group-photo` -\> `check_type="mid"`
3.  **End of Class:**
      * `POST /classroom/upload-group-photo` -\> `check_type="end"`

> **Note:** The AI will scan the entire group photo, find all enrolled students, and log their specific sightings.

### Step 3: Finalize Attendance

  * **Endpoint:** `POST /classroom/finalize-day`
  * **Logic:** The system queries the daily logs. A student is marked **Present** only if `count(distinct session_type) == 3`.

-----

## 🛠️ Troubleshooting

**Issue: `ModuleNotFoundError` or Container crash**

  * Check logs: `docker compose logs -f web`
  * Rebuild container: `docker compose up -d --build`

**Issue: Database connection failed**

  * Ensure the DB container is healthy: `docker compose ps`
  * Restart services: `docker compose restart`

-----

## 📜 Tech Stack

  * **Language:** Python 3.9
  * **Framework:** FastAPI
  * **Computer Vision:** OpenCV, dlib, face\_recognition
  * **Database:** PostgreSQL 15
  * **ORM:** SQLAlchemy
  * **Infrastructure:** Docker & Docker Compose

<!-- end list -->
