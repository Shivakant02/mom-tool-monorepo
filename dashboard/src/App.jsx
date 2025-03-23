import { Navigate, Route, Router, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import TaskList from "./pages/TaskList";
import Charts from "./pages/Charts";
import ProjectDetails from "./pages/ProjectDetails";
import MomPage from "./pages/MomPage";

function App() {
  return (
    <>
      <div className="min-h-screen bg-base-200 p-6">
        <Navbar />
        <Routes>
          <Route path="/" element={<Navigate to="/charts" />} />
          <Route path="/charts" element={<Charts />} />
          <Route path="/tasks-list" element={<TaskList />} />
          <Route path="/project" element={<ProjectDetails />} />
          <Route path="/mom" element={<MomPage />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
