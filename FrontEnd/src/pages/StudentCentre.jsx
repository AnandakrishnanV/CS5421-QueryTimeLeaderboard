import React, { useState } from "react";
import { Form, Button } from "react-bootstrap";
import axios from "axios";

import { Link, Navigate, useNavigate } from "react-router-dom";

import "./StudentCentre.css";

const StudentCentre = () => {
  const [inpUserName, setInpUserName] = useState("stu1");
  const [inpPassword, setInpPassword] = useState("jw8s0F4");
  const [ifUserNameWrong, setIfUserNameWrong] = useState(false);
  const [token, setToken] = useState("");

  const userNameChangeHandler = (event) => {
    setInpUserName(event.target.value);
    setIfUserNameWrong(false);
  };

  const passwordChangeHandler = (event) => {
    setInpPassword(event.target.value);
  };

  let nav = useNavigate();

  const handleRowClick = (event) => {
    // console.log(event.target.parentElement.firstChild.textContent);
    // let clickId = event.target.parentElement.firstChild.textContent;
    // var challenge = null;
    // // challengeData.filter((obj) => {
    // //   return obj.challenge_id === clickId;
    // // });
    // console.log(challenge);
    // let path = "/studentsubmissions";
    // nav(path, { state: challenge[0] });
  };

  const submitHandler = (event) => {
    event.preventDefault(); //to stop req sent to anywhere, prompting refresh

    const submitData = {
      user_name: inpUserName,
      password: inpPassword,
    };

    fetchToken(submitData);

    setInpUserName("");
    setInpPassword("");
  };

  const fetchToken = async (data) => {
    console.log(data);
    const res = await axios
      .post("http://127.0.0.1:5000/login", {
        user_name: data.user_name,
        password: inpPassword,
      })
      .catch((err) => console.log(err));

    if (res) {
      const token = res.data.token;
      console.log(token);
      setToken(token);
      localStorage.setItem("user", inpUserName);
      localStorage.setItem("token", token);
      localStorage.setItem("token_timestamp", Date.now()/1000)

      fetchSubmissionData(data);
    }
  };

  const fetchSubmissionData = async (data) => {
    console.log(data);

    // let config = {
    //   headers: {
    //     user: localStorage.getItem("user"),
    //     token: localStorage.getItem("token"),
    //   },
    //   user_name: localStorage.getItem("user"),
    // };

    const res = await axios
      .get("http://127.0.0.1:5000/submissions", {
        params: { user_name: data.user_name },
      })
      .catch((err) => console.log(err));

    if (res) {
      const data = res.data;
      console.log(data);
      if (!data.length) {
        setIfUserNameWrong(true);
      } else {
        let path = "/studentsubmissions";
        nav(path, { state: data });
      }
    }
  };

  //   const checkForbiddenKeywords = () => {
  //     var qr = inpQuery;
  //     var fkey = false;

  //     dangerArray.every((item) => {
  //       if (qr.includes(item)) {
  //         fkey = true;
  //         setDangerKeyword(true);
  //         return false;
  //       }
  //       return true;
  //     });

  //     return fkey;
  //   };

  const renderWrongMessage = () => {
    if (ifUserNameWrong) {
      return <h3>Please enter the correct Username</h3>;
    } else {
      return <div></div>;
    }
  };

  return (
    <Form className="query-form" onSubmit={submitHandler}>
      <Form.Group className="mb-3">
        <Form.Label>Student User Name</Form.Label>
        <Form.Control
          type="text"
          value={inpUserName}
          placeholder="Enter Student UserName"
          onChange={userNameChangeHandler}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Student Password</Form.Label>
        <Form.Control
          type="password"
          value={inpPassword}
          placeholder="Enter Student Password"
          onChange={passwordChangeHandler}
        />
      </Form.Group>

      <Button variant="primary" type="submit">
        Submit
      </Button>
      {renderWrongMessage()}
    </Form>
  );
};

export default StudentCentre;
