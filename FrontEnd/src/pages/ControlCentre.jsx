import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";
import Challenges from "./Challenges";
import axios from "axios";


import "./ControlCentre.css";

const ControlCentre = (props) => {

  const actualPassHash = "teachteampass";
  const [inpChallenge, setInpChallenge] = useState("");
  const [inpChallengeName, setInpChallengeName] = useState("");
  const [inpChallengeRes, setInpChallengeRes] = useState("");
  const [inpChallengeType, setInpChallengeType] = useState("1");
  const [inpPass, setPass] = useState("");
  const [ifPassCorrect, setIfPass] = useState("");

  const submitCHandler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      challenge_name: inpChallengeName,
      challenge_description: inpChallenge,
      user_name: "ta",
      query:  inpChallengeRes,
      challenge_type: inpChallengeType,
                          //-->change later
    };

    sendRequestToServer(submitData);

    setInpChallenge("");
    setInpChallengeRes("");
    setInpChallengeType("");
  };

  const sendRequestToServer = async (data) => {
    const res = await axios.post('http://127.0.0.1:5000/challenges', data);
    console.log(res)
  }

  const chalTypeChangeHandler = (event) => {
    setInpChallengeType(event.target.value);
  };

  const chalChangeHandler = (event) => {
    setInpChallenge(event.target.value);
  };

  const chalNameChangeHandler = (event) => {
    setInpChallengeName(event.target.value);
  };

  const chalResultChangeHandler = (event) => {
    setInpChallengeRes(event.target.value);
  };

  const submitPassHandler = (event) => {
    event.preventDefault();
    setIfPass(true)
    if (inpPass === actualPassHash) {
      //  setIfPass(true);   ---> changing for dev
    }
    setPass("");
  };

  const passChangeHandler = (event) => {
    setPass(event.target.value);
  };

  if (!ifPassCorrect) {
    return (
      <div>
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
        <Challenges></Challenges>
        <div className="challenge-forms">
          <Form
            className="cc-pass-form challenge-form"
            onSubmit={submitCHandler}
            id="Form1"
          >
            <Form.Group className="mb-3">
              <h3>Add New Challenge</h3>
              <Form.Label>Select Challenge Type</Form.Label>
              <Form.Select onChange={chalTypeChangeHandler}>
                <option value="1">Slowest Query</option>
                <option value="2">Fastest Query</option>
              </Form.Select>
              <Form.Label>Enter New Challenge Name</Form.Label>
              <Form.Control
                as="input"
                value={inpChallengeName}
                onChange={chalNameChangeHandler}
              />
              <Form.Label>Enter New Challenge Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={inpChallenge}
                onChange={chalChangeHandler}
              />
              <Form.Label>Enter Challenge Result Query</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={inpChallengeRes}
                onChange={chalResultChangeHandler}
              />
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
