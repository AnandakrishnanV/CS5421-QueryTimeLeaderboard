import React, { useEffect, useMemo, useState } from "react";
import { Table } from "react-bootstrap";
import "./Challenges.css";
import axios from "axios";
import { C_COL } from "../components/challengeColumns";
import {
  useTable,
  useSortBy,
  useGlobalFilter,
  useFilters,
} from "react-table/dist/react-table.development";

import { Link, Navigate, useNavigate } from "react-router-dom";

const Challenges = () => {
  let nav = useNavigate();
  const handleRowClick = (event) => {
    console.log(event.target.parentElement.firstChild.textContent);
    let clickId = event.target.parentElement.firstChild.textContent;
    var challenge = challengeData.filter((obj) => {
      return obj.challenge_id === clickId;
    });
    console.log(challenge);

    let path = "/challengeOne";
    nav(path, { state: challenge[0] });
  };

  const [chalData, setChalData] = useState([]);
  const fetchChalData = async () => {
    const res = await axios
      .get(" http://127.0.0.1:5000/challenges")
      .catch((err) => console.log(err));

    if (res) {
      const data = res.data;
      console.log(data);
      setChalData(
        data.map((item) => ({
          ...item,
        }))
      );
    }
  };
  useEffect(() => {
    fetchChalData();
  }, []);

  const columns = useMemo(() => C_COL, []);
  const challengeData = useMemo(() => [...chalData], [chalData]);
  console.log(challengeData);

  const tableInstance = useTable(
    {
      columns,
      data: challengeData,
    },
    useFilters,
    useGlobalFilter,
    useSortBy
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state,
  } = tableInstance;

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

export default Challenges;
