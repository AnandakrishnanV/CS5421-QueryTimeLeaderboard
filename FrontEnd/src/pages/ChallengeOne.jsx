import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
import ChallengeTable from "../components/Table/ChallengeTable";
import PageModal from "./PageModal";
import axios from "axios";
import "./ChallengeOne.css";
import { Card } from "react-bootstrap";

const ChallengeOnePage = (props) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [ifError, setIfError] = useState(false);
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
      //login
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
        console.log(response);
      })
      .catch((err) => {
        setIfError(true);
        console.log(err.response.data.message);
        setErrorMsg(err.response.data.message);
      });
  };

  const checkLogin = () => {
    let current_time = Date.now() / 1000;

    if (current_time - state.token_timestamp >= 600) {
      setIsLoggedIn(false);
    } else {
      setIsLoggedIn(true);
    }
  };

  const renderWarningMessage = (msg) => {
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
    } else {
      return <div></div>;
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
    </div>
  );
};

export default ChallengeOnePage;
