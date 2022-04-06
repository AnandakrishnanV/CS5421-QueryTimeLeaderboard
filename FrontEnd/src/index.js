import 'bootstrap/dist/css/bootstrap.min.css';
import { render } from "react-dom";
import { 
  HashRouter as Router,
  Routes,
  Route
} from "react-router-dom";
import ChallengeOnePage from "./pages/ChallengeOne";
import ControlCentre from './pages/ControlCentre';
import Challenges from './pages/Challenges';
import Navigation from './components/Navigation/Navigation';
import StudentCentre from './pages/StudentCentre';
import StudentSubmissions from './pages/StudentSubmissions';

import App from "./App";

const rootElement = document.getElementById("root");
render(
  <Router>
    <Navigation />
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/challenges" element={<Challenges />} />
      <Route path="/challengeOne" element={<ChallengeOnePage />} />
      <Route path="/StudentCentre" element={<StudentCentre />} />
      <Route path="/StudentSubmissions" element={<StudentSubmissions />} />
      <Route path="/controlCentre" element={<ControlCentre />} />
    </Routes>
  </Router>,
  rootElement
);