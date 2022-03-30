import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
import ChallengeTable from "../components/Table/ChallengeTable";
import axios from "axios";
import "./ChallengeOne.css";

const ChallengeOnePage = (props) => {
  const { state } = useLocation();
  console.log(state);

  const saveEntryDataHandler = (inpEntryData) => {
    const entryData = {
      ...inpEntryData,
      challenge_id: state.challenge_id,
    };
    console.log(entryData);
    sendRequestToServer(entryData);
  };

  const sendRequestToServer = async (data) => {
    const res = await axios.post('http://127.0.0.1:5000/submissions', data);
    console.log(res)
  }

    return (
        <div>
            <div className="text-center">
                <p />
                <h1>Challenge {state.challenge_name} - {state.challenge_type_description}</h1>
                <div className="challenge-text">
                    <span>{state.challenge_description}</span>
                </div>
            </div>
            <ChallengeTable challengeId={1}/>
            <div className="text-center">
              <h2>Make A New Submission</h2>
            </div>
            <QueryForm onSaveQueryData = {saveEntryDataHandler} />
        </div>
  );
};

export default ChallengeOnePage;
