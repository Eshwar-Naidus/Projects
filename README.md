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

## ⚙️ How to Run Locally

To run this application as a standalone local project, follow these steps:

1.  **Download & Extract**: Clone or download this repository to your local machine.

2.  **Install Dependencies**:
    *   Open your terminal in the project folder.
    *   Run:
    ```bash
    npm install
    ```

3.  **Configure Environment**:
    *   Create a `.env` file in the root directory.
    *   Add your API Key:
    ```env
    VITE_API_KEY=your_google_gemini_api_key_here
    ```

4.  **Run the App**:
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

## 🔐 Security hardening notes

- The app now uses only locally bundled JavaScript modules (via Vite) instead of runtime CDN import maps, reducing supply-chain/script-injection risk from third-party script hosts.
- `index.html` no longer loads Tailwind via runtime CDN script; styling is served from local static assets.
- A strict referrer policy (`strict-origin-when-cross-origin`) is defined in `index.html` to minimize metadata leakage on cross-origin requests.
- External webfont loading was removed from `index.html` to reduce third-party request surface and passive telemetry exposure.
- Browser-side policy hardening was added in `index.html` via Content Security Policy and Permissions Policy headers to reduce script injection and limit unnecessary hardware/API access.
