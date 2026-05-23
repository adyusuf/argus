import { NavLink, Outlet } from "react-router-dom";
import { Camera, Activity, AlertTriangle } from "lucide-react";

const NAV = [
  { to: "/", label: "Dashboard", icon: Activity },
  { to: "/cameras", label: "Cameras", icon: Camera },
  { to: "/events", label: "Events", icon: AlertTriangle },
] as const;

export default function Layout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "system-ui, sans-serif" }}>
      <aside
        style={{
          width: 220,
          background: "#0f172a",
          color: "#e2e8f0",
          padding: "1.5rem 0",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, padding: "0 1.25rem", marginBottom: "2rem" }}>
          Argus
        </h1>
        <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "0.625rem 1.25rem",
                color: isActive ? "#38bdf8" : "#94a3b8",
                background: isActive ? "#1e293b" : "transparent",
                textDecoration: "none",
                fontSize: "0.9rem",
                borderLeft: isActive ? "3px solid #38bdf8" : "3px solid transparent",
              })}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, background: "#f1f5f9", padding: "2rem" }}>
        <Outlet />
      </main>
    </div>
  );
}
