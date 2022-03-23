import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";

import './QueryForm.css'

const QueryForm = (props) => {
  const [inpSID, setInpSID] = useState("");
  const [inpName, setName] = useState("");
  const [inpQuery, setInpQuery] = useState("");

  const submitHandler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      sid: inpSID,
      name: inpName,
      query: inpQuery,
      timestamp:Math.floor(Date.now()/1000)

    };

    props.onSaveQueryData(submitData); //passing data UP
    setInpSID("");
    setName("");
    setInpQuery("");
  };

  const sidChangeHandler = (event) => {
    setInpSID(event.target.value);
  };

  const nameChangeHandler = (event) => {
    setName(event.target.value);
  };

  const queryChangeHandler = (event) => {
    setInpQuery(event.target.value);
  };

  return (
    <Form className = "query-form" onSubmit={submitHandler}>
      <Form.Group className="mb-3" >
        <Form.Label>Student ID</Form.Label>
        <Form.Control type="text" placeholder="Enter Student ID" onChange={sidChangeHandler}/>        
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Name</Form.Label>
        <Form.Control type="text" placeholder="Name" onChange={nameChangeHandler}/>
      </Form.Group>
      <Form.Group className="mb-3">
        <Form.Label>Query</Form.Label>
        <Form.Control as="textarea" rows={4} onChange={queryChangeHandler}/>
      </Form.Group>
      <Button variant="primary" type="submit">
        Submit
      </Button>
    </Form>
  );
};

export default QueryForm;
