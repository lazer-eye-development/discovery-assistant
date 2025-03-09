# Agent Assisted Discovery Tool

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Framework">
  <img src="https://img.shields.io/badge/AI-OpenAI-412991.svg" alt="AI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

A streamlined AI assistant that enhances technical discovery conversations with clients through real-time question generation, contextual insights, and automated documentation.






## 🔍 Overview

The Discovery tool transforms client discovery sessions by providing technical professionals with:

- **AI-powered assistance** during live client meetings
- **Intelligent question generation** based on conversation context
- **Automated summary creation** for efficient documentation
- **Strategic next steps** recommendations

This single-page Streamlit application leverages OpenAI's language models (GPT-4o, GPT-4-turbo, or GPT-3.5-turbo) to deliver insights that drive more productive discovery conversations.


## ✨ Features

### 🛠️ Technical Discovery Framework
- Pre-defined technical discovery questions for comprehensive IT infrastructure assessment
- Customizable question framework that adapts to your organization's specific needs
- Structured approach to gather critical system information

### 🤖 Dynamic Question Generation
- AI intelligently generates follow-up questions based on previous answers
- Questions automatically adapt to the client's unique technical environment
- Uncovers deeper insights that might otherwise be missed

### 📝 Real-time Documentation
- Captures meeting notes and client background information in one place
- Context-aware information organization for better knowledge retention
- Eliminates the need for post-meeting transcription

### 🧠 Automated Insights
- Generates concise summaries of technical discussions with key takeaways
- Provides AI-recommended next steps for immediate action
- Transforms raw conversation data into actionable intelligence

### 🔄 Flexible AI Model Selection
- Choose between different OpenAI models based on your specific needs
- Switch models on the fly during your discovery session
- Optimize for speed or depth depending on the conversation

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/lazer-eye-development/discovery-assistant.git
cd agent-assisted-discovery
```

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Run the application:**
```bash
streamlit run app.py
```

## 📊 Usage

1. **Start the application** and enter your client information in the sidebar
2. **Complete the technical questions** in the Technical Discovery tab
3. **Generate dynamic questions** based on the conversation context
4. **Choose your preferred OpenAI model** for different tasks
5. **Create summaries and next steps** for post-meeting follow-up

## 🔒 Security

The application uses OpenAI's API with secure communication. Your API key is stored locally in the `.env` file and is never shared. This application is designed for personal or internal team use.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.


---

<p align="center">
  <small>Made with ❤️ for more effective technical discovery</small>
</p>
