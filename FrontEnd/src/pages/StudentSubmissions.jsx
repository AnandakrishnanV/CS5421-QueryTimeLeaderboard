import React, { useEffect, useMemo, useState } from "react";
import { Form, Button } from "react-bootstrap";
import axios from "axios";
import { Sub_Col } from "../components/Table/Columns/SubmissionColumns";
import {
  useTable,
  useSortBy,
  useGlobalFilter,
  useFilters,
} from "react-table/dist/react-table.development";

import { useLocation } from "react-router-dom";

import { Link, Navigate, useNavigate } from "react-router-dom";

import "./StudentSubmissions.css";

//todo: separate page for query viewing, truncate query

const StudentSubmissions = (props) => {
  const { state } = useLocation();
  console.log(state);

  const handleRowClick = () => {};

  //   let nav = useNavigate();
  //   const handleRowClick = (event) => {
  //     console.log(event.target.parentElement.firstChild.textContent);
  //     let clickId = event.target.parentElement.firstChild.textContent;
  //     var challenge = challengeData.filter((obj) => {
  //       return obj.challenge_id === clickId;
  //     });
  //     console.log(challenge);

  //     let path = "/studentPage";
  //     nav(path, { state: challenge[0] });
  //   };

  const [subData, setSubData] = useState([]);

  const checkAndSetQueryCorrectness = (item) => {
      if(item) {
          return "Correct"
      }
      else {
          return "Wrong"
      }
  };

  const fetchSubData = async () => {
    if (state) {
      const data = state.map((obj) => ({
        ...obj,
        correctness: checkAndSetQueryCorrectness(obj.is_correct),
      }));
      setSubData(
        data.map((item) => ({
          ...item,
        }))
      );
      console.log(subData);
    }
  };
  useEffect(() => {
    fetchSubData();
  }, []);

  const columns = useMemo(() => Sub_Col, []);
  const submissionData = useMemo(() => [...subData], [subData]);
  console.log(submissionData);

  const tableInstance = useTable(
    {
      columns,
      data: submissionData,
    },
    useFilters,
    useGlobalFilter,
    useSortBy
  );

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    tableInstance;

  return (
    <div>
      <table className="chal-table zui-table-rounded" {...getTableProps()}>
        <thead className="chal-thead">
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                  {column.render("Header")}
                  <span>
                    {column.isSorted
                      ? column.isSortedDesc
                        ? "⬇️"
                        : "⬆️"
                      : "↕"}
                  </span>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <tr onClick={handleRowClick} {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default StudentSubmissions;
