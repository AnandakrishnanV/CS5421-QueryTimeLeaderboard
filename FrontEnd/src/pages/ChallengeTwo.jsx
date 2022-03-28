import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import QueryForm from "../components/QueryForm/QueryForm";
import ChallengeTable from "../components/Table/ChallengeTable";
import "./Challenges.css";
import Navigation from "../components/Navigation/Navigation";

const ChallengeTwoPage = (props) => {
  const { state } = useLocation();
  console.log(state);

  const saveEntryDataHandler = (inpEntryData) => {
    const entryData = {
      ...inpEntryData,
      challenge_id: state.challenge_id,
    };
    console.log(entryData);
  };

    const challengeText = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."

    return (
        <div>
            <div className="text-center">
                <p />
                <h1>Challenge Two - Slowest Query</h1>
                <div className="challenge-text">
                    <span>{challengeText}</span>
                </div>
            </div>
            <ChallengeTable challengeId={2}/>
            <QueryForm onSaveQueryData = {saveEntryDataHandler} />
        </div>
  );
};

export default ChallengeTwoPage;
