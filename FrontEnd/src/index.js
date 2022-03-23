import 'bootstrap/dist/css/bootstrap.min.css';
import { render } from "react-dom";
import { BrowserRouter } from "react-router-dom";
import ChallengeOnePage from "./pages/ChallengeOne";
import ChallengeTwoPage from "./pages/ChallengeOne";
import ControlCentre from './pages/ControlCentre';

import App from "./App";

const rootElement = document.getElementById("root");
render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
  rootElement
);