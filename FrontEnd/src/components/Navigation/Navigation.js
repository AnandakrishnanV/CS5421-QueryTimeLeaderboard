import { Navbar, Nav, Container } from "react-bootstrap";
import React from "react";
import PropTypes from "prop-types";
import "./Navigation.css";
import { Link } from "react-router-dom";

const Navigation = () => (
  <Navbar bg="dark" variant="dark" className="navi">
    <Container>
    <Navbar.Brand href="/">QueryTime Leaderboard</Navbar.Brand>
    <Nav className="nav">
      <Link className="nav-link" to="/challenges">Challenges</Link> 
      <Link className="nav-link" to="/studentCentre">Student Center</Link>
      <Link className="nav-link" to="/controlCentre">Control Center</Link>
    </Nav>
    </Container>
  </Navbar>
);

Navigation.propTypes = {};

Navigation.defaultProps = {};

export default Navigation;
