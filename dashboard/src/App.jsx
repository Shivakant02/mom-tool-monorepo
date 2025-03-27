import { Navigate, Route, Router, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import TaskList from "./pages/TaskList";
import Charts from "./pages/Charts";
import ProjectDetails from "./pages/ProjectDetails";
import MomPage from "./pages/MomPage";
import MissingFieldsPage from "./components/tables/NoAssigneeTable";
import MissingTable from "./pages/MissingTable";
import UpdateMissingFieldsPage from "./pages/UpdateMissingFieldsPage";
import ScheduleMeeting from "./pages/ScheduleMeeting";
import UpcomingEvents from "./pages/UpcomingEvents";
import PastMeeting from "./pages/PastMeeting";

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
          <Route path="/missing-field-table" element={<MissingTable />} />
          <Route path="/meetings" element={<ScheduleMeeting />} />
          <Route path="/upcoming-events" element={<UpcomingEvents />} />
          <Route path="/past-events" element={<PastMeeting />} />
          <Route
            path="/update-missing-fields/:issueKey"
            element={<UpdateMissingFieldsPage />}
          />
        </Routes>
      </div>
    </>
  );
}

export default App;
