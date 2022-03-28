import { Navbar, Nav, Container } from 'react-bootstrap';
import React from 'react';
import PropTypes from 'prop-types';
import './Navigation.css';
import { Link } from "react-router-dom";


const Navigation = () => (
  <Navbar bg="dark" variant="dark" className='navi'>
    <Container>
    <Navbar.Brand href="#home">
      <Link to="/">QueryTime Leaderboard</Link>
    </Navbar.Brand>
    <Nav className="nav">
      <Link to="/challenges">Challenges  |</Link> 
      <Link to="/challengeOne">Challenge One  |</Link> 
      <Link to="/controlCenter">Control Center</Link>
    </Nav>
    </Container>
  </Navbar>
);

Navigation.propTypes = {};

Navigation.defaultProps = {};

export default Navigation;
