Photon – Week 5 Frontend

Real-time Stock Ticker Dashboard (React + WebSockets)

Overview

Week 5 focuses on building a production-ready frontend for the Photon project.
The application displays real-time stock price updates using WebSockets and a clean, scalable React architecture.

The frontend connects to a FastAPI WebSocket backend and updates stock prices without page refresh.

 Features (Week-5)

 Real-time stock price updates via WebSockets

 Auto reconnect if WebSocket connection drops

 Component-based React architecture

 Price trend indicators (up/down arrows & colors)

 Dark / ☀ Light theme toggle

 Sorting stocks by price

 Clean and responsive UI using CSS Grid

 Tech Stack

Frontend: React (Vite)

State Management: React Hooks

Real-time Communication: WebSocket API

Styling: CSS

Build Tool: Vite

📂 Project Structure
week5/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── StockCard.jsx
│   │   └── ThemeToggle.jsx

🔌 WebSocket Flow

Browser loads index.html

main.jsx initializes React

App.jsx opens WebSocket connection

Client subscribes to stock symbols

Backend streams live price updates

UI updates automatically in real time

▶️ How to Run (Frontend)
npm install
npm run dev


App runs at:

http://localhost:5173


⚠️ Make sure the FastAPI backend is running on:

ws://127.0.0.1:8000/ws

Key Learnings (Week-5)

Handling real-time data streams in React

Building reconnect-safe WebSocket clients

Structuring scalable React components

Improving UX with visual indicators and themes

Preparing frontend code for production readiness

 Notes

Week-5 frontend uses demo or backend-streamed data

Live financial APIs are handled safely on the backend

node_modules is excluded using .gitignore

Conclusion

Week-5 transforms the Photon project from a functional prototype into a polished, scalable, and production-style frontend suitable for real-world real-time applications.