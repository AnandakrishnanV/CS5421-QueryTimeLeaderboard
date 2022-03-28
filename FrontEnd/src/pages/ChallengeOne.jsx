import React, { useState } from "react";
import Navigation from "../components/Navigation/Navigation";
import QueryForm from "../components/QueryForm/QueryForm";
import "./ChallengeOne.css";

const ChallengeOnePage = (props) => {
  const prop = {
    challengeID: "1",
    challengeText: "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
    challengeRes: "brarfgdgdafsdfasdf",
    challengeType: "inpChallengeType",
    timestamp: Math.floor(Date.now() / 1000),
  };

  const saveEntryDataHandler = (inpEntryData) => {
    console.log(props.id);
    const entryData = {
      ...inpEntryData,
      challengeID: prop.challengeID,
    };
    console.log(entryData);
  };

  return (
    <div>
      <div className="text-center">
        <p />
        <h1>Challenge {prop.challengeID} - {prop.challengeType}</h1>
        <div className="challenge-text">
          <span>{prop.challengeText}</span>
        </div>
      </div>

      <p className="font-italic">Insert Table here</p>
      <QueryForm onSaveQueryData={saveEntryDataHandler} />
    </div>
  );
};

export default ChallengeOnePage;
