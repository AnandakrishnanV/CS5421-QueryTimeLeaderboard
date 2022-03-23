import React, { useState } from "react";
import Navigation from "../components/Navigation/Navigation";
import { Form, Button } from "react-bootstrap";

import "./ControlCentre.css";

const ControlCentre = (props) => {
  const challenge1Text =
    "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.";

  const challenge2Text =
    "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.";


  const actualPassHash = "teachteampass";
  const [inpC1Challenge, setC1IinpChallenge] = useState("");
  const [inpC2Challenge, setC2IinpChallenge] = useState("");
  const [inpPass, setPass] = useState("");
  const [ifPassCorrect, setIfPass] = useState("");

  const submitC1Handler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      challengeID: 1,
      challengeText: inpC1Challenge,
      timestamp:Math.floor(Date.now()/1000)
    };
    //props.onSaveChallengeData(submitData); //passing data UP
    setC1IinpChallenge("");
  };

  const c1ChangeHandler = (event) => {
    setC1IinpChallenge(event.target.value);
  };

  const submitC2Handler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      challengeID: 2,
      challengeText: inpC2Challenge,
      timestamp:Math.floor(Date.now()/1000)
    };
    //props.onSaveChallengeData(submitData); //passing data UP
    setC2IinpChallenge("");
  };

  const c2ChangeHandler = (event) => {
    setC2IinpChallenge(event.target.value);
  };

  const submitPassHandler = (event) => {
    event.preventDefault();

    if (inpPass === actualPassHash) {
      setIfPass(true);
    }
    setPass("");
  };

  const passChangeHandler = (event) => {
    setPass(event.target.value);
  };

  if (!ifPassCorrect) {
    return (
      <div>
        <Navigation />
        <Form className="cc-pass-form login-form" onSubmit={submitPassHandler}>
          <Form.Group className="mb-3" controlId="formBasicPassword">
            <Form.Label>Teaching Team</Form.Label>
            <Form.Control
              type="password"
              placeholder="Password"
              onChange={passChangeHandler}
            />
          </Form.Group>
          <div className="">
            <Button type="submit">Login</Button>
          </div>
        </Form>
      </div>
    );
  } else {
    return (
      <div>
        <Navigation />
        <div className="challenge-forms">
          <Form className="cc-pass-form challenge-form" onSubmit={submitC1Handler} id="Form1">
            <Form.Group className="mb-3">
              <h3>Current Challenge - Fastest Time</h3>
              <Form.Label>{challenge1Text}</Form.Label>
              <Form.Control as="textarea" rows={4} onChange={c1ChangeHandler} />
            </Form.Group>
            <div className="">
              <Button type="submit">Submit</Button>
            </div>
          </Form>
          <Form className="cc-pass-form challenge-form" onSubmit={submitC2Handler} id="Form2">
            <Form.Group className="mb-3">
              <h3>Current Challenge - Slowest Time</h3>
              <Form.Label>{challenge2Text}</Form.Label>
              <Form.Control as="textarea" rows={4} onChange={c2ChangeHandler} />
            </Form.Group>
            <div className="">
              <Button type="submit">Submit</Button>
            </div>
          </Form>
        </div>
      </div>
    );
  }
};

export default ControlCentre;
