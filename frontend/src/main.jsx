import React from "react";
import ReactDOM from "react-dom/client";
import MapView from "./MapView";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <div style={{ fontFamily: "sans-serif" }}>
      <header style={{
        position: "absolute", top: 0, left: 0, right: 0,
        zIndex: 1000, padding: "12px 20px",
        background: "rgba(13,17,23,0.85)",
        backdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", gap: 12,
        borderBottom: "1px solid rgba(255,255,255,0.08)"
      }}>
        <span style={{ fontSize: 20 }}>🌍</span>
        <span style={{ color: "#fff", fontWeight: 500, fontSize: 15 }}>
          UN AI Situation Room
        </span>
        <span style={{
          marginLeft: "auto", fontSize: 11, padding: "3px 8px",
          background: "rgba(224,75,74,0.2)", color: "#f09595",
          borderRadius: 20, border: "0.5px solid #f09595"
        }}>
          Day 1 · Stub data
        </span>
      </header>
      <MapView />
    </div>
  </React.StrictMode>
);