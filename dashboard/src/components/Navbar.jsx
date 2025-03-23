// src/components/Navbar.jsx
import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <div className="navbar bg-base-100 rounded-xl shadow mb-6">
      <div className="flex-1">
        <Link to="/" className="btn btn-ghost text-xl">
          Lead Dashboard
        </Link>
      </div>
      <div className="flex-none space-x-2">
        <NavLink to="/charts" className="btn btn-sm btn-outline">
          Charts
        </NavLink>
        <NavLink to="/tasks-list" className="btn btn-sm btn-outline">
          Task List
        </NavLink>
        <NavLink to="/project" className="btn btn-sm btn-outline">
          Project Info
        </NavLink>
      </div>
    </div>
  );
}
