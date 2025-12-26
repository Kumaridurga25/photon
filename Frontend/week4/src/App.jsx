import { useEffect, useRef, useState } from "react";
import StockCard from "./components/StockCard";
import "./index.css";

const WS_URL = "ws://127.0.0.1:8000/ws";
const SYMBOLS = ["AAPL", "GOOGL", "AMZN", "MSFT"];

export default function App() {
  const [status, setStatus] = useState("Connecting...");
  const [stocks, setStocks] = useState({});
  const socketRef = useRef(null);

  useEffect(() => {
    connectSocket();
    return () => socketRef.current?.close();
  }, []);

  const connectSocket = () => {
    const socket = new WebSocket(WS_URL);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
      setStatus("Connected");

      SYMBOLS.forEach(symbol => {
        socket.send(JSON.stringify({ action: "subscribe", symbol }));
      });
    };

    socket.onmessage = (event) => {
      console.log("Incoming:", event.data);
      const { ticker, price, change } = JSON.parse(event.data);

      setStocks(prev => {
        const prevPrice = prev[ticker]?.price ?? null;
        let trend = "";
        if (prevPrice !== null) {
          trend = price > prevPrice ? "up" : price < prevPrice ? "down" : "";
        }
        return { ...prev, [ticker]: { price, change, trend } };
      });
    };

    socket.onclose = () => {
      console.log("Disconnected. Reconnecting...");
      setStatus("Disconnected. Reconnecting...");

      setTimeout(connectSocket, 3000);
    };

    socket.onerror = (err) => {
      console.error("WebSocket error", err);
      setStatus("Error");
      socket.close();
    };
  };

  return (
    <div className="app">
      <p className={`status ${status.toLowerCase()}`}>
          {status}
      </p>

      <h1>Photon ⚡ Live Stocks</h1>
      <div className="grid">
        {Object.entries(stocks).map(([ticker, data]) => (
          <StockCard key={ticker} ticker={ticker} {...data} />
        ))}
      </div>
    </div>
  );
}
