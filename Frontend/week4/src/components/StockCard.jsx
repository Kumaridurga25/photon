export default function StockCard({ ticker, price, change, trend }) {
  return (
    <div className="stock-card">
      <h3>{ticker}</h3>

      <p className={`price ${trend}`}>
        ${price}
        <span className="change">
          {change > 0 ? ` (+${change})` : ` (${change})`}
        </span>
        <span className="arrow">
          {trend === "up" ? " ↑" : trend === "down" ? " ↓" : ""}
        </span>
      </p>
    </div>
  );
}
