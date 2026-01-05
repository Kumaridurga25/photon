import ThemeToggle from "./ThemeToggle";

export default function Header({ status }) {
  return (
    <header className="header">
      <h1>⚡ Photon – Live Stocks</h1>
      <p className={`status ${status.toLowerCase()}`}>{status}</p>
      <ThemeToggle />
    </header>
  );
}
