import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import { Routes, Route, BrowserRouter, Link } from "react-router-dom";
//Import icons - FontAwesome
import HomePageContent from "./components/UploadPage.js";
import TrafficCongestionPage from "./components/TrafficCongestionPage.js";
import BusTimesPage from "./components/BusTimesPage.js";
import UploadPage from "./components/UploadPage.js";
import LoginPage from "./components/LoginPage.js";

import HouseSharpIcon from "@mui/icons-material/HouseSharp";
import TrafficSharpIcon from "@mui/icons-material/TrafficSharp";
import DirectionsCarSharpIcon from "@mui/icons-material/DirectionsCarSharp";
import DirectionsBusSharpIcon from "@mui/icons-material/DirectionsBusSharp";
import UploadSharpIcon from "@mui/icons-material/UploadSharp";
import HomePage from "./components/HomePage.js";
import LoginIcon from "@mui/icons-material/Login";
import SignupPage from "./components/SignupPage.js";

function App() {
  console.log(process.env.REACT_APP_PUBLIC_URL);
  return (
    <BrowserRouter basename={process.env.REACT_APP_PUBLIC_URL}>
      <div className="App">
        <Navbar bg="dark" variant="dark">
          <Container>
            <Navbar.Brand href={process.env.REACT_APP_PUBLIC_URL + "/"}>
              <TrafficSharpIcon fontSize="large" />
              TrafficVision
            </Navbar.Brand>
            <Nav className="me-auto">
              <Nav.Link href={process.env.REACT_APP_PUBLIC_URL + "/"}>
                <HouseSharpIcon />
                Home
              </Nav.Link>
              <Nav.Link
                href={process.env.REACT_APP_PUBLIC_URL + "/trafficcongestion"}
              >
                <DirectionsCarSharpIcon /> Traffic
              </Nav.Link>
              <Nav.Link href={process.env.REACT_APP_PUBLIC_URL + "/bustimes"}>
                <DirectionsBusSharpIcon /> Buses
              </Nav.Link>
              <Nav.Link href={process.env.REACT_APP_PUBLIC_URL + "/upload"}>
                <UploadSharpIcon /> Upload
              </Nav.Link>
            </Nav>
            <Nav>
              <Nav.Link href={process.env.REACT_APP_PUBLIC_URL + "/login"}>
                <LoginIcon /> Login
              </Nav.Link>
            </Nav>
          </Container>
        </Navbar>
        <Routes>
          <Route path="/" element={<HomePage></HomePage>}></Route>
          <Route
            path="/trafficcongestion"
            element={<TrafficCongestionPage></TrafficCongestionPage>}
          ></Route>
          <Route
            path="/bustimes"
            element={<BusTimesPage></BusTimesPage>}
          ></Route>
          <Route path="/upload" element={<UploadPage></UploadPage>}></Route>
          <Route path="/login" element={<LoginPage></LoginPage>}></Route>
          <Route path="/signup" element={<SignupPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
