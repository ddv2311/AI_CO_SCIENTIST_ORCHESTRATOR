# 🏆 AI Co-Scientist Lab Orchestrator (Hackathon Submission)

## 💡 Novel Idea: Autonomous Scientific Discovery

This project implements a multi-agent system designed to automate the initial, iterative phase of scientific research: **Hypothesis Generation, Parallel Prior Art Review, and Experimental Protocol Drafting.** It simulates a **collaborative scientific team** to accelerate discovery from weeks to minutes, making complex research accessible.

The core innovation is orchestrating **multi-tool execution** over **large, unstructured data** payloads, a classic challenge in production AI.

## ✨ Technical Showcase (Composio Meta-Tools)

This solution is engineered to maximize technical points by forcing the use of critical Composio features in a sequential, high-stakes workflow.

| Composio Feature | Agent & Action | Why It Wins |
| :--- | :--- | :--- |
| **`COMPOSIO_CREATE_PLAN`** | **Hypothesis Agent** uses this first to decompose the research goal into auditable, sequential steps. | Guarantees reliable, structured workflow execution and control. |
| **`COMPOSIO_MULTI_EXECUTE_TOOL`** | **Literature Agent** runs concurrent searches across **Arxiv** (research papers) and **PubChem** (chemical data). | Demonstrates high-speed parallel data collection from distinct, external sources. |
| **`COMPOSIO_REMOTE_WORKBENCH`** | Used immediately after multi-execute to **store the raw, large text** of scientific papers (simulated payload). | **CRITICAL:** Prevents LLM context overflow, showcasing a production-ready solution for big data. |
| **`COMPOSIO_REMOTE_BASH_TOOL`** | **Analysis Agent** executes a simulated Python/Pandas script to clean and analyze the Workbench data. | Enables the agent to perform **computation and analysis**, going beyond simple text summarization. |

## 🛠️ Project Setup and Execution

### Prerequisites

1.  Python 3.10+
2.  **Free LLM Key:** A **Groq API Key** (for fast, free LLM inference).
3.  **Tool Router Key:** Your **Composio API Key**.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR-REPO-LINK]
    cd ai-co-scientist-orchestrator
    ```
2.  **Setup Virtual Environment:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration (`.env` file)

Copy the example file and fill in your keys.

```powershell
Copy-Item .env.example .env
# Edit the .env file with your GROQ_API_KEY and COMPOSIO_API_KEY.