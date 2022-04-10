import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
import ChallengeTable from "../components/Table/ChallengeTable";
import axios from "axios";
import "./ChallengeOne.css";
import { Card, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const ChallengeOnePage = (props) => {
  let nav = useNavigate();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [ifError, setIfError] = useState(false);
  const [ifAdmin, setifAdmin] = useState(false);
  const [ifCreated, setifCreated] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const { state } = useLocation();
  const saveEntryDataHandler = (inpEntryData) => {
    setIfError(false);
    const entryData = {
      ...inpEntryData,
      user_name: state.user,
      challenge_id: state.challenge.challenge_id,
    };

    checkLogin();

    //console.log("loginchecked");

    if (isLoggedIn) {
      sendRequestToServer(entryData);
    } else {
      let path = "/studentcentre";
      nav(path, {});
    }
  };

  const sendRequestToServer = async (data) => {
    //console.log("in post");

    let config = {
      headers: {
        user: localStorage.getItem("user"),
        token: localStorage.getItem("token"),
      },
    };

    const res = await axios
      .post("http://127.0.0.1:5000/submissions", data, config)
      .then((response) => {
        //console.log(response);
        if (response.statusText && response.statusText === "CREATED") {
          setifCreated(true);
          setTimeout(() => {
            setifCreated(false);
          }, 3000);
        }
      })
      .catch((err) => {
        setIfError(true);
        setErrorMsg(err.response.data.message);
      });
  };

  const checkLogin = () => {
    //console.log(state);

    let current_time = Date.now() / 1000;

    if (current_time - state.token_timestamp >= 600) {
      setIsLoggedIn(false);
    } else {
      setIsLoggedIn(true);
    }

    if (state.from && state.from === "control-centre") {
      setifAdmin(true);
    }
  };

  const inactivateChallenge = async () => {
    let config = {
      headers: {
        user: localStorage.getItem("tt_user"),
        token: localStorage.getItem("tt_token"),
      },
    };
    let deleteURL =
      "http://127.0.0.1:5000/challenge/" + state.challenge.challenge_id;
    const res = await axios.delete(deleteURL, config).then((response) => {
      let path = "/controlCentre";
      nav(path, {});
    });
    //console.log(res);
  };

  const renderWarningMessage = () => {
    if (ifError) {
      return (
        <div>
          <Card className="error-card">
            <Card.Header as="h5">Error</Card.Header>
            <Card.Body>
              <Card.Text>{errorMsg}</Card.Text>
            </Card.Body>
          </Card>
        </div>
      );
    } else if (ifCreated) {
      return (
        <div>
          <Card className="error-card">
            <Card.Header as="h5">Created</Card.Header>
            <Card.Body>
              <Card.Text>
                Your entry has been submitted. The entry will upadated one the
                processing is Complete.
              </Card.Text>
            </Card.Body>
          </Card>
        </div>
      );
    }
  };

  const renderDeletionBox = () => {
    if (ifAdmin && !state.challenge.is_deleted) {
      return (
        <div>
          <Card className="error-card text-center">
            <Card.Header as="h5">Deactivate This Challengee</Card.Header>
            <Card.Body>
              <Button onClick={inactivateChallenge}>Deactivate</Button>
            </Card.Body>
          </Card>
        </div>
      );
    } else if (ifAdmin) {
      return (
        <div>
          <Card className="error-card text-center">
            <Card.Body>
              <h5>This challenge is already Deactivated</h5>
            </Card.Body>
          </Card>
        </div>
      );
    }
  };

  useEffect(() => {
    checkLogin();
  }, []);

  return (
    <div>
      <div className="text-center">
        <p />
        <h1>
          Challenge {state.challenge.challenge_name} -{" "}
          {state.challenge.challenge_type_description}
        </h1>
        <div className="challenge-text">
          <span>{state.challenge.challenge_description}</span>
        </div>
      </div>
      <ChallengeTable board_data={state.chal_list} />
      <div className="text-center">
        <h2>Make A New Submission</h2>
      </div>
      <QueryForm onSaveQueryData={saveEntryDataHandler} />
      {renderWarningMessage()}
      {renderDeletionBox()}
    </div>
  );
};

export default ChallengeOnePage;
