import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
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
        <h1>
          Challenge {state.challenge_id} - {state.challenge_type}
        </h1>
        <div className="challenge-text">
          <span>{state.challenge_text}</span>
        </div>
      </div>

      <p className="font-italic">Insert Table here</p>
      <QueryForm onSaveQueryData={saveEntryDataHandler} />
    </div>
  );
};

export default ChallengeOnePage;
