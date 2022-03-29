import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
import ChallengeTable from "../components/Table/ChallengeTable";
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
  };

    return (
        <div>
            <div className="text-center">
                <p />
                <h1>Challenge {state.challenge_id} - {state.challenge_type}</h1>
                <div className="challenge-text">
                    <span>{state.challenge_text}</span>
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
