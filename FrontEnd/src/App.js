import { Link } from "react-router-dom";
import LadderTable from "./components/Table/LadderTable";


import Navigation from "./components/Navigation/Navigation";

export default function App() {
  

  return (
    <div>
      <Navigation/>      
      <LadderTable/>
    </div>
  );
}

