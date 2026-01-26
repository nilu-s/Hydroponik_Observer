import { useState } from "react";

import HomePage from "./pages/HomePage";
import SettingsPage from "./pages/SettingsPage";

type Page = "home" | "settings";

const App = () => {
  const [page, setPage] = useState<Page>("home");

  if (page === "settings") {
    return <SettingsPage onBack={() => setPage("home")} />;
  }

  return <HomePage onOpenSettings={() => setPage("settings")} />;
};

export default App;
