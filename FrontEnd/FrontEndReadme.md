FrontEnd design with React.js

APIs

//Submission API

// Front end send to backend
{
	name: String,
    query: String,
    timeStamp: DateTime,
    challengeId: Number,
}

//  backend to front end
{
	name: String,
    query: String,
    id: String,
    timeStamp: DateTime,
    challengeId: Number,
    planningTime: Number,
    executionTime: Number,
    isCorrect: Boolean,
}

// SQL Challenge
// Front end to backend
{
    challenge: String
}

//Backend to frontend
{
    challenge: String,
    challengeId: Number
}
