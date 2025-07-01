# AI for HR Commute Automation

An intelligent, AI-powered web application designed to automate the process of verifying and approving employee commute allowances. This tool streamlines HR workflows by validating addresses against official documents, checking policy eligibility, verifying vehicle ownership for private vehicle claims, and calculating allowances based on the employee's mode of transport.

![Untitled diagram _ Mermaid Chart-2025-07-01-150853](https://github.com/user-attachments/assets/a9795aaa-0a37-445d-9569-9d8e18f517b2)

---

## 🚀 Features

*   **Automated Address Verification**: Uses a multi-modal AI to read and extract addresses from uploaded documents (like utility bills) and validates them against user input.
*   **AI-Powered Policy Engine**: Intelligently determines employee eligibility by comparing their commute distance and job role against a flexible, external company policy file.
*   **Secure Document Validation**: For private vehicle claims, the system requires and validates the employee's Driving License and Vehicle Ownership proof.
*   **Dynamic Distance Calculation**: Integrates with the Google Maps API to accurately calculate the commute distance between the employee's home and the office.
*   **Interactive Chat Interface**: Engages with the employee through a conversational UI to determine their mode of transport and provide specific allowance details.
*   **Modular & Maintainable**: Built with a modular architecture using LangGraph, making it easy to modify the workflow, prompts, or external services.

## ⚙️ Tech Stack

*   **Application Framework**: [Streamlit](https://streamlit.io/)
*   **AI Workflow Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
*   **Large Language Models (LLM)**: [Groq](https://groq.com/) API with Llama & Llava models.
*   **Mapping Service**: [Google Maps Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix)
---

## 🛠️ Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

*   [Python 3.9+](https://www.python.org/downloads/)
*   [Docker](https://www.docker.com/products/docker-desktop/) and Docker Desktop running.
*   A [Docker Hub](https://hub.docker.com/) account (for pushing/pulling images).
*   API keys for:
    *   Groq
    *   Google Maps Platform (with Distance Matrix API enabled)

### Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/DyingRusher/HR_commute_ai.git
    cd HR_commute_ai
    ```

2.  **Create the Environment File**
    Create a file named `.env` in the root of the project directory and add your API keys:
    ```env
    # .env
    GROQ_API_KEY="gsk_YourGroqApiKey"
    GOOGLE_MAPS_API_KEY="YourGoogleMapsApiKey"
    ```
    > **Note:** This `.env` file is listed in `.gitignore` and will not be committed to the repository for security reasons.

3.  **Build the Docker Image**
    From the root directory, run the following command to build the Docker image. This will install all dependencies and package the application.
    ```sh
    docker build -t hr-commute-app .
    ```

4.  **Run the Docker Container**
    Once the image is built, run the application in a container. This command maps the port and securely passes your API keys from the `.env` file into the container.
    ```sh
    docker run --rm -p 8501:8501 --env-file .env hr-commute-app
    ```

5.  **Access the Application**
    Open your web browser and navigate to:
    **[http://localhost:8501](http://localhost:8501)**

    You should now see the HR Commute Automation app running!

---

## 📝 Application Workflow

The application follows a robust, multi-step validation process to ensure compliance and accuracy:

1.  **Initial Data Submission**: The user (HR personnel or an employee) enters their full name, address, and job role, and uploads a proof of address document.
2.  **Address Validation**: The AI extracts the address from the uploaded document and compares it to the typed address. The process halts if there is a mismatch.
3.  **Policy Eligibility Check**: If the address is valid, the system calculates the commute distance and checks the company policy (`policy.txt`) to determine if the employee's role and distance make them eligible for an allowance.
4.  **Transport Mode Inquiry**: For eligible employees, the application asks for their primary mode of transport.
5.  **Conditional Document Request**:
    *   If the user chooses **Walking, Bicycle, or Public Transport**, the system provides the relevant allowance details immediately.
    *   If the user chooses **Private Vehicle**, the system requires them to upload a **Driving License** and **Vehicle Ownership Proof**.
6.  **Vehicle Document Validation**: The AI validates that the names on the uploaded vehicle documents match the employee's name. The process halts if the documents are invalid.
7.  **Final Approval**: Upon successful validation of all required documents, the final allowance details are provided to the user.

### Customizing the Policy

The core eligibility rules can be easily modified without changing any code. Simply edit the `policy.txt` file with your company's specific rules for job roles and distance requirements.
