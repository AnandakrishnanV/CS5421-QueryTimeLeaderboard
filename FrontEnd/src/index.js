import 'bootstrap/dist/css/bootstrap.min.css';
import { render } from "react-dom";
import { 
  HashRouter as Router,
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";
import ChallengeOnePage from "./pages/ChallengeOne";
import ControlCentre from './pages/ControlCentre';
import Challenges from './pages/Challenges';
import Navigation from './components/Navigation/Navigation';

import App from "./App";

const rootElement = document.getElementById("root");
render(
  <Router>
    <Navigation />
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/challenges" element={<Challenges />} />
      <Route path="/challengeOne" element={<ChallengeOnePage />} />
      <Route path="/controlCenter" element={<ControlCentre />} />
    </Routes>
  </Router>,
  rootElement
);