interface DownloadButtonProps {
  isLoggedIn: boolean;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ isLoggedIn }) => {
  const handleDownload = () => {
    window.open("http://localhost:3000/download_calendar", "_blank");
  };

  return (
    <button
      onClick={handleDownload}
      disabled={!isLoggedIn}
      className={`px-4 py-2 text-sm rounded-md font-medium transition ${
        isLoggedIn
          ? "bg-green-600 text-white hover:bg-green-700"
          : "bg-gray-300 text-gray-600 cursor-not-allowed"
      }`}
    >
      Preuzmi .ICS kalendar
    </button>
  );
};

export default DownloadButton;
