import { useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);

  const toggle = () => {
    document.body.classList.toggle("light");
    setDark(!dark);
  };

  return (
    <button className="theme-btn" onClick={toggle}>
      {dark ? "🌙 Dark" : "☀ Light"}
    </button>
  );
}
