import { Navbar, Nav, Container } from 'react-bootstrap';
import React from 'react';
import PropTypes from 'prop-types';
import './Navigation.css';

const Navigation = () => (
  <Navbar bg="dark" variant="dark" className='navi'>
    <Container>
    <Navbar.Brand href="#home">QueryTime Leaderboard</Navbar.Brand>
    <Nav className="nav">
      <Nav.Link href="/challengeOne">ChallengeOne</Nav.Link>
      <Nav.Link href="/challengeTwo">ChallengeTwo</Nav.Link>
      <Nav.Link href="/controlcentre">Control Centre</Nav.Link>
    </Nav>
    </Container>
  </Navbar>
);

Navigation.propTypes = {};

Navigation.defaultProps = {};

export default Navigation;
