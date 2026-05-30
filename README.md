<div align="center">
  <h1>⚡ FlashSaleRag</h1>
  <p><strong>Ultra-Concurrent Flash Market & High-Performance Asynchronous Inventory Management</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react)](https://react.dev/)
  [![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg?logo=vite)](https://vitejs.dev/)
  [![LangChain](https://img.shields.io/badge/LangChain-Enabled-lightgrey.svg)](https://www.langchain.com/)
</div>

<hr/>

An enterprise-grade, cloud-native microservice architecture designed to handle unpredictable traffic bursts (100x traffic spikes) during e-commerce flash sales. The system integrates advanced rate-limiting, dynamic algorithmic surge pricing, event-driven AI workflow automation, and a resilient GenAI customer concierge with RAG-based graceful fallback execution.

## 🌟 Live Demo & API

*   **Frontend (Chaos Engineering Command Center)**: [Live Dashboard](https://flashsale-frontend.onrender.com)
*   **Backend (Core API & AI Engine)**: [Live Swagger API](https://flashsale-backend-mubx.onrender.com/docs)

> [!NOTE]
> **Note for Judges**: This project strictly follows a **Decoupled Microservice Architecture**. 
> * The **Backend API** handles the actual real-time processing (Redis Token-Bucket Rate Limiter, Atomic Lua Scripts for Inventory, FAISS Vector DB, and LangChain AI Agents). You can test the endpoints live via the Swagger UI.
> * The **Frontend Dashboard** acts as an interactive "Chaos Engineering Visualization Center". Because browsers cannot naturally simulate 10,000+ RPS without being blocked, the frontend visually simulates a massive traffic spike (Chaos Engineering) to demonstrate how the backend architecture (Load Balancer -> Bot Mitigation -> Auto-Scaling) reacts to extreme load.

## 🚀 Key Features

*   **⚡ Ultra-Concurrent Processing**: Engineered to handle massive traffic spikes typical in flash sales without degrading performance.
*   **🛡️ Token-Bucket Rate Limiter**: Built-in DDoS protection and spam prevention using dynamic 429 interceptors.
*   **📈 Algorithmic Surge Pricing**: Automatically adjusts pricing dynamically based on real-time inventory depletion.
*   **🤖 AI-Powered Workflows**:
    *   **Fraud Detection**: Flags anomalous burst patterns for audit.
    *   **Auto-Restock Pipeline**: Connects with supply chain systems when stock dips below critical levels.
*   **💬 RAG-Based Customer Concierge**: An intelligent conversational agent that helps users with their queries using Retrieval-Augmented Generation.
*   **✨ Modern Dashboard**: A beautifully animated, real-time responsive dashboard built with React 19, TailwindCSS, and Framer Motion.

## 🛠️ Tech Stack

### Backend Layer
*   **Framework**: FastAPI
*   **AI/LLM Engine**: OpenAI, LangChain
*   **Vector Database**: FAISS (for RAG)
*   **Server**: Uvicorn

### Frontend Layer
*   **Framework**: React 19 + Vite
*   **Styling**: TailwindCSS
*   **Animations**: Framer Motion
*   **Charts/Visualization**: Chart.js, react-chartjs-2
*   **Icons**: Lucide React

## 🏗️ System Architecture Blueprint

Below is the conceptual event-driven flow of transactions, security filters, and AI automation triggers mapped across the system pipeline:

```text
[ Incoming Web Traffic Burst (100x Spike) ]
                   │
                   ▼
     ┌───────────────────────────┐
     │   X-Admin-Token Guard     │  <── Auth Layer Security Check
     └─────────────┬─────────────┘
                   │
                   ▼
     ┌───────────────────────────┐
     │ Token-Bucket Rate Limiter │  <── Dynamic 429 Interceptor (DDoS Protection)
     └─────────────┬─────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  [ Approved Request ]   [ Rejected Burst (Spam) ]
         │                   │
         ▼                   ▼
┌──────────────────┐   ┌──────────────────────────────┐
│ Atomic Inventory │   │    🛡️ AI Fraud Trigger       │
│ Deduction State  │   │ "Flag Anomalous Burst Audit" │
└────────┬─────────┘   └──────────────────────────────┘
         │
         ├───► Stock < 20% ──► [ 📈 Algorithmic Surge Pricing: Auto +10% ]
         │
         ├───► Stock < 10% ──► [ 🤖 Supply Chain Auto-Restock Pipeline ]
         │
         └───► Success ──────► [ 💌 Smart Shipping & Order Confirmation Agent ]
```

## 📁 Project Structure

```text
FlashSaleRag/
├── app/                  # FastAPI Backend Source Code
│   ├── ai/               # LangChain & AI agents logic
│   ├── core/             # Core settings & configurations
│   ├── database/         # DB models & FAISS vector store
│   └── main.py           # Application Entry Point
├── frontend/             # React + Vite Frontend App
│   ├── src/              # React components & pages
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── requirements.txt      # Python dependencies
├── rate_limiter.py       # Custom Rate Limiter logic
├── test_scale.py         # Scaling test scripts
├── Dockerfile            # Backend containerization
└── deployment.yaml       # K8s/Deployment configuration
```

## ⚙️ Getting Started

Follow these steps to get the project up and running locally.

### Prerequisites
*   [Python 3.11+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)
*   An OpenAI API Key

### 1. Backend Setup

1. **Navigate to the root directory**:
   ```bash
   cd FlashSaleRag
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and add your OpenAI Key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. API documentation can be found at `http://localhost:8000/docs`.

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd FlashSaleRag/frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

## 🐳 Deployment

*   **Docker**: A `Dockerfile` is provided for containerizing the backend service.
*   **Kubernetes**: Refer to `deployment.yaml` for deploying the microservice in a K8s cluster.
*   **Vercel**: Configuration (`vercel.json`) is included for seamless edge deployments.

---
<div align="center">
  <i>Built for the next generation of high-velocity commerce.</i>
</div>
