import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Cameras from "./pages/Cameras";
import CameraDetail from "./pages/CameraDetail";
import Events from "./pages/Events";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/cameras" element={<Cameras />} />
        <Route path="/cameras/:id" element={<CameraDetail />} />
        <Route path="/events" element={<Events />} />
      </Route>
    </Routes>
  );
}
