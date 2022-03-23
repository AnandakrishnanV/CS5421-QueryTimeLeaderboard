import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";

import "./QueryForm.css";

const QueryForm = (props) => {
  const [inpSID, setInpSID] = useState("");
  const [inpName, setName] = useState("");
  const [inpQuery, setInpQuery] = useState("");
  const [ifDangerKeyword, setDangerKeyword] = useState(false);
  const dangerArray = [
    "create ",
    "alter ",
    "add column ",
    "drop ",
    "truncate ",
    "insert ",
    "update ",
    "delete ",
  ];

  const submitHandler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    var ifFKey = checkForbiddenKeywords()

    const submitData = {
      sid: inpSID,
      name: inpName,
      query: inpQuery,
      timestamp: Math.floor(Date.now() / 1000),
    };

    if(!ifFKey) {
      props.onSaveQueryData(submitData); //passing data UP
      setInpSID("");
      setName("");
      setInpQuery("");
    }
  };

  const checkForbiddenKeywords = () => {
    var qr = inpQuery;
    var fkey = false

    dangerArray.every((item) => {
      if (qr.includes(item)) {
        fkey = true
        setDangerKeyword(true)
        return false;
      }
      return true;
    });

    return fkey
  }

  const renderWarningMessage = () => {
    if(ifDangerKeyword) {
      return <h3>Please avoid using forbidden keywords and resubmit your query</h3>
    }
    else {
      return <div></div>
    }
  };

  const sidChangeHandler = (event) => {
    setInpSID(event.target.value);
  };

  const nameChangeHandler = (event) => {
    setName(event.target.value);
  };

  const queryChangeHandler = (event) => {    

      setInpQuery(event.target.value);
      setDangerKeyword(false)
  };

  return (
    <Form className="query-form" onSubmit={submitHandler}>
      <Form.Group className="mb-3">
        <Form.Label>Student ID</Form.Label>
        <Form.Control
          type="text"
          value={inpSID}
          placeholder="Enter Student ID"
          onChange={sidChangeHandler}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Name</Form.Label>
        <Form.Control
          type="text"
          value={inpName}
          placeholder="Name"
          onChange={nameChangeHandler}
        />
      </Form.Group>
      <Form.Group className="mb-3">
        <Form.Label>Query</Form.Label>
        <Form.Control as="textarea" rows={4} value={inpQuery} onChange={queryChangeHandler} />
      </Form.Group>
      <Button variant="primary" type="submit">
        Submit
      </Button>
      {renderWarningMessage()}
    </Form>
  );
};

export default QueryForm;
