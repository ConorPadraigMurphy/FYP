import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from 'react-router-dom';
//Import icons - FontAwesome
import { FaHome } from "react-icons/fa";

import HomePageContent from "./components/HomePageComponent.js";


function App() {
  return (
    <Router>
      <div className="App" >
        <Navbar bg="dark" variant="dark">
          <Container>
            <Navbar.Brand href="/">Tracking</Navbar.Brand>
            <Nav className="me-auto">
              <Nav.Link href="/"><FaHome/> Home</Nav.Link>
            </Nav>
          </Container>
        </Navbar>
        <Routes>
          <Route path='/' element={<HomePageContent></HomePageContent>}></Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
