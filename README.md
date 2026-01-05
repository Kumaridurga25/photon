**📈 Real-Time Stock Price Streaming Application**

This repository contains a full-stack real-time stock price streaming application, developed as part of an internship project.

The application streams stock price updates in real time using WebSockets.
My primary responsibility and contribution for this internship was the backend implementation.

**📁 Project Structure**

Photon-Stock\_project/
├── backend/
│   └── servermain.py        # FastAPI backend (internship contribution)
├── frontend/
│   └── ...            # Frontend files
├── README.md
└── .env

**🚀 Features**

* Real-time stock price updates using WebSockets
* Supports multiple stock symbols (AAPL, GOOGL, AMZN, MSFT)
* Demo mode with simulated price changes
* Live mode using Finnhub Stock API
* Multiple client subscriptions
* Asynchronous and scalable backend architecture

**🛠️ Tech Stack**

**Backend**
* Python
* FastAPI
* WebSockets
* AsyncIO
* httpx
* Uvicorn

**Frontend**
Implemented separately

**⚙️ Environment Variables**

Create a .env file in the project root:
FINNHUB_API_KEY=your_finnhub_api_key
DEMO_MODE=true

* DEMO_MODE=true → Simulated stock prices
* DEMO_MODE=false → Live prices from Finnhub

**▶️ How to Run the Backend**

1.Install dependencies:

pip install fastapi uvicorn httpx python-dotenv

2.Start the backend server:

python backend/servermain.py

3.Backend will run at:

http://localhost:8000

4.WebSocket endpoint:

ws://localhost:8000/ws

**🔌 WebSocket Usage**

**Subscribe to a stock**

{
     "action": "subscribe",

     "symbol": "AAPL"
}

**Sample response**

{
     "ticker": "AAPL",

     "price": 151.42,

     "change": 0.38,

     "mode": "demo"
}

**👨‍💻 My Internship Contribution**

* Designed and implemented the FastAPI backend
* Implemented real-time WebSocket communication
* Integrated live stock data API and demo mode
* Managed client subscriptions and async data streaming
* Focused on scalability, error handling, and clean architecture

**📝 Note**

* This repository contains both frontend and backend components developed collaboratively.  
* My internship contribution and evaluation focus on the backend implementation.







