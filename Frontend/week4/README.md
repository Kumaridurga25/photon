# Photon – Week 4: Live Stock Dashboard

This week focuses on building a **real-time stock price dashboard** using **React + WebSockets**.

---

## Features

- Real-time stock updates using WebSocket
- Supports multiple stocks:
  - AAPL
  - GOOGL
  - AMZN
  - MSFT
- Price movement indicators:
  - ↑ Green for price increase
  - ↓ Red for price decrease
- Auto-reconnect on WebSocket disconnect
- Clean component-based architecture

---

##  Tech Stack

- React (Vite)
- WebSocket API
- JavaScript (ES6+)
- CSS

---

## Folder Structure

#  Photon – Week 4: Live Stock Dashboard

This week focuses on building a **real-time stock price dashboard** using **React + WebSockets**.

---

## Features

- Real-time stock updates using WebSocket
- Supports multiple stocks:
  - AAPL
  - GOOGL
  - AMZN
  - MSFT
- Price movement indicators:
  - ↑ Green for price increase
  - ↓ Red for price decrease
- Auto-reconnect on WebSocket disconnect
- Clean component-based architecture

---

## Tech Stack

- React (Vite)
- WebSocket API
- JavaScript (ES6+)
- CSS

---

## Folder Structure

week4/
├── src/
│ ├── components/
│ │ └── StockCard.jsx
│ ├── App.jsx
│ ├── main.jsx
│ ├── index.css
│ └── App.css
├── public/
├── index.html
├── package.json
└── vite.config.js


---

## WebSocket Flow

1. Frontend connects to backend WebSocket
2. Subscribes to stock symbols
3. Receives live price updates
4. UI updates with trend indicators

---

## Run Locally

```bash
cd Frontend/week4
npm install
npm run dev
