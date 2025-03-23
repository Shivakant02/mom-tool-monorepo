// src/components/tasks/Pagination.jsx
export default function Pagination({
  currentPage,
  totalPages,
  setCurrentPage,
}) {
  return (
    <div className="flex justify-center mt-4 space-x-2">
      <button
        className="btn btn-sm"
        disabled={currentPage === 1}
        onClick={() => setCurrentPage((prev) => prev - 1)}
      >
        Prev
      </button>
      <span className="btn btn-sm btn-ghost cursor-default">
        Page {currentPage} of {totalPages}
      </span>
      <button
        className="btn btn-sm"
        disabled={currentPage === totalPages}
        onClick={() => setCurrentPage((prev) => prev + 1)}
      >
        Next
      </button>
    </div>
  );
}
