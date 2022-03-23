import React, { useState } from "react";
import Navigation from "../components/Navigation/Navigation";
import QueryForm from "../components/QueryForm/QueryForm";
import './ChallengeTwo.css'

const ChallengeTwoPage = (props) => {

    const saveEntryDataHandler = (inpEntryData) => {
        const entryData = {
            ...inpEntryData,
            challengeID: 2
        };
        console.log(entryData)
    }

    const challengeText = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."

    return (
        <div>
            <Navigation />
            <div className="text-center">
                <p />
                <h1>Challenge One - Slowest Query</h1>
                <div className="challenge-text">
                    <span>{challengeText}</span>
                </div>
            </div>

            <p className="font-italic">Insert Table here</p>
            <QueryForm onSaveQueryData = {saveEntryDataHandler} />
        </div>
    )
}

export default ChallengeTwoPage;