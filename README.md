# Codex_Intership Suite

This repository hosts the **Codex_Intership Suite**, a comprehensive dashboard featuring four advanced AI modules developed during the internship. The application leverages Google's **Gemini 2.5 Flash** model for multimodal capabilities, React 18 for the UI, and Tailwind CSS for styling.

## 🚀 Modules

### 1. AI Career Counsellor
An NLP-driven chat interface that assesses user interests, education, and skills to provide tailored career roadmaps.

### 2. AI Writer & Summarizer
A productivity tool that condenses extensive documents into structured summaries.

### 3. Stock Trend Predictor
A hybrid financial tool combining quantitative data with qualitative analysis.

### 4. Smart Resume Optimizer (Flagship)
An advanced document engineering tool that parses existing resumes and tailors them to specific Job Descriptions.

## 🛠️ Tech Stack

*   **Frontend**: React 18, TypeScript
*   **AI Model**: Google Gemini 2.5 Flash (`@google/genai`)
*   **Styling**: Tailwind CSS, Lucide React (Icons)
*   **Visualization**: Recharts

## ⚙️ How to Run Locally (Remove AI Studio Traces)

To run this application as a standalone local project (removing the "Emerged by Google AI Studio" traces), follow these steps:

1.  **Download & Extract**: Clone or download this repository to your local machine.

2.  **Clean Up `index.html`**:
    *   Open `index.html`.
    *   **Delete** the entire `<script type="importmap">...</script>` block.
    *   Ensure the script tag points to the source: `<script type="module" src="/index.tsx"></script>`.

3.  **Install Dependencies**:
    *   Open your terminal in the project folder.
    *   Run:
    ```bash
    npm install
    ```

4.  **Configure Environment**:
    *   Create a `.env` file in the root directory.
    *   Add your API Key:
    ```env
    VITE_API_KEY=your_google_gemini_api_key_here
    ```

5.  **Run the App**:
    *   Start the local development server:
    ```bash
    npm run dev
    ```
    *   Open the link (usually `http://localhost:5173`) in your browser.

## 📦 Deployment / Push to GitHub

To erect (deploy) this code to your specific repository `https://github.com/Eswar-Naidus`, follow these exact steps:

1.  **Create the Repository on GitHub**: Name it `Codex_Intership`.
2.  **Push Code**:

    ```bash
    git init
    git add .
    git commit -m "Initial Release: Codex_Intership Suite"
    git branch -M main
    git remote add origin https://github.com/Eswar-Naidus/Codex_Intership.git
    git push -u origin main
    ```

## 📄 License
Developed for the Codex_Intership program.