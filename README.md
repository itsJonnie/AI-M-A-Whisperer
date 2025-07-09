# 🤖 AI M&A Whisperer

**AI M&A Whisperer** is a GPT-powered M&A strategy tool that analyzes startups and generates acquisition insights using real corporate development logic.

🔗 **Live Preview**: [ai-ma-whisperer.preview.emergentagent.com](https://ai-ma-whisperer.preview.emergentagent.com)

---

## 💡 What It Does

Input a startup name, short description, and optionally upload pitch deck slides.  
You’ll get:

- 🏢 **Top 2–3 Potential Acquirers** with synergy fit scores
- 📊 **Strategic Fit Summary** (product, market, tech, team)
- 💰 **Estimated Valuation Range** with logic & comps

Built to mimic how MBB (McKinsey, BCG, Bain) or Big Tech corp dev teams evaluate startups.

---

## ⚙️ Tech Stack

| Layer        | Tech                      |
|--------------|---------------------------|
| Frontend     | Tailwind CSS + React      |
| LLM Backend  | OpenAI GPT-4 API          |
| Hosting      | Emergent Agent Framework  |
| LLM Logic    | Custom synergy + valuation prompt chaining |

---

## 🔐 Environment Variables

You’ll need a `.env` file in both `/frontend/` and `/backend/`.

Use these templates:

### `/backend/.env.template`
```env
OPENAI_API_KEY=your-openai-key
DEBUG=true
