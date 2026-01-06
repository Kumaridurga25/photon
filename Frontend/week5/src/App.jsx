import { useEffect, useRef, useState } from "react";
import StockCard from "./components/StockCard";
import Header from "./components/Header";
import "./index.css";

const WS_URL = "ws://127.0.0.1:8000/ws";
const SYMBOLS = ["AAPL", "GOOGL", "AMZN", "MSFT"];

export default function App() {
  const [status, setStatus] = useState("Connecting...");
  const [stocks, setStocks] = useState({});
  const socketRef = useRef(null);
  const manualClose = useRef(false);

  useEffect(() => {
    connect();
    return () => {
      manualClose.current = true;
      socketRef.current?.close();
    };
  }, []);

  const connect = () => {
    manualClose.current = false;
    const ws = new WebSocket(WS_URL);
    socketRef.current = ws;

    ws.onopen = () => {
      setStatus("Connected");
      SYMBOLS.forEach(symbol =>
        ws.send(JSON.stringify({ action: "subscribe", symbol }))
      );
    };

    ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (!data.ticker) return;

  const price = Number(data.price);
  const change = Number(data.change);

  let trend = "flat";
  if (change > 0) trend = "up";
  else if (change < 0) trend = "down";

  setStocks(prev => ({
    ...prev,
    [data.ticker]: {
      price,
      change,
      trend,
      mode: data.mode
    }
  }));
};

    ws.onclose = () => {
      if (manualClose.current) return;
      setStatus("Disconnected. Reconnecting...");
      setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      setStatus("Error");
      ws.close();
    };
  };

  return (
    <div className="app">
      <Header status={status} />
      <div className="grid">
        {Object.entries(stocks)
          .sort((a, b) => b[1].price - a[1].price)
          .map(([ticker, data]) => (
            <StockCard key={ticker} ticker={ticker} {...data} />
          ))}
      </div>
    </div>
  );
}
