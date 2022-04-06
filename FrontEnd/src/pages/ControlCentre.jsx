import React, { useEffect, useState } from "react";
import { Form, Button } from "react-bootstrap";
import Challenges from "./Challenges";
import axios from "axios";
import { Link, Navigate, useNavigate } from "react-router-dom";

import "./ControlCentre.css";

const ControlCentre = (props) => {
  let nav = useNavigate();

  const [inpChallenge, setInpChallenge] = useState("");
  const [inpChallengeName, setInpChallengeName] = useState("");
  const [inpChallengeRes, setInpChallengeRes] = useState("");
  const [inpChallengeType, setInpChallengeType] = useState("1");
  const [inpUserName, setInpUserName] = useState("");
  const [inpPass, setPass] = useState("");
  const [ifPassCorrect, setIfPass] = useState("");

  const submitCHandler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      challenge_name: inpChallengeName,
      challenge_description: inpChallenge,
      user_name: localStorage.getItem("tt_user"),
      query: inpChallengeRes,
      challenge_type: inpChallengeType,
      //-->change later
    };

    sendRequestToServer(submitData);

    setInpChallenge("");
    setInpChallengeRes("");
    setInpChallengeType("");
  };

  const sendRequestToServer = async (data) => {
    let config = {
      headers: {
        user: localStorage.getItem("tt_user"),
        token: localStorage.getItem("tt_token"),
      },
    };

    //console.log(data);
    //console.log(config);

    const res = await axios
      .post("http://127.0.0.1:5000/challenges", data, config)
      .then((response) => {
       if(response.statusText === 'CREATED') {
         window.location.reload(false);
       }
      });
    //console.log(res);
  };

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

  const submitPassHandler = async (event) => {
    event.preventDefault();

    //console.log("here");

    const req = await axios
      .post("http://127.0.0.1:5000/login", {
        user_name: inpUserName,
        password: inpPass,
      })
      .then((response) => {
        //console.log(response.data);

        if (response.data.is_admin) {
          localStorage.setItem("tt_user", inpUserName);
          localStorage.setItem("tt_token", response.data.token);
          localStorage.setItem("tt_token_timestamp", Date.now());

          setIfPass(true);
        }
      });

    setInpUserName("");
    setPass("");
  };

  const checkLogin = () => {
    if (
      Date.now() / 1000 - localStorage.getItem("tt_token_timestamp") <= 1200 &&
      localStorage.getItem("tt_token") &&
      localStorage.getItem("tt_token") !== null
    ) {
      setIfPass(true);
    } else {
      setIfPass(false);
    }
  };

  const passChangeHandler = (event) => {
    setPass(event.target.value);
  };

  const userNameChangeHandler = (event) => {
    setInpUserName(event.target.value);
  };

  useEffect(() => {
    checkLogin();
  });

  if (!ifPassCorrect) {
    return (
      <div>
        <Form className="cc-pass-form login-form" onSubmit={submitPassHandler}>
          <Form.Group className="mb-3" controlId="formUserName">
            <Form.Label>User Name</Form.Label>
            <Form.Control
              type="input"
              placeholder="User Name"
              value={inpUserName}
              onChange={userNameChangeHandler}
            />
          </Form.Group>
          <Form.Group className="mb-3" controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Password"
              value={inpPass}
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
        <Challenges from="control-centre"></Challenges>
        <div className="challenge-forms">
          <Form
            className="cc-pass-form challenge-form"
            onSubmit={submitCHandler}
            id="Form1"
          >
            <Form.Group className="mb-3">
              <h3>Add New Challenge</h3>
              <Form.Label>Select Challenge Type</Form.Label>
              <Form.Select onChange={chalTypeChangeHandler} value={inpChallengeType}>
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
