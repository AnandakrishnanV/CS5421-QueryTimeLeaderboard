import React, { useState } from "react";
import Navigation from "../components/Navigation/Navigation";
import QueryForm from "../components/QueryForm/QueryForm";
import { Table } from "react-bootstrap";
import "./Challenges.css";

import { Link, Navigate, useNavigate } from "react-router-dom";

const Challenges = () => {
  // let nav = useNavigate();

  // const handleRowClick = () => {
  //   console.log("click");

  //   let path = "/challengeOne";
  //   nav(path, {state:{id:1,name:'sabaoon'}});
  // };

  return (
    <div>
      <div>
        <Table className="chal-table zui-table-rounded">
          <thead className="chal-thead">
            <tr>
              <th>#</th>
              <th>Challenge Name</th>
              <th>Challenge Type</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td >Mark</td>
              <td>Otto</td>
              <td>@mdo</td>
            </tr>
            <tr>
              <td>2</td>
              <td>Jacob</td>
              <td>Thornton</td>
              <td>@fat</td>
            </tr>
          </tbody>
        </Table>
      </div>
    </div>
  );
};

export default Challenges;
