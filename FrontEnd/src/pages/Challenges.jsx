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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [chalData, setChalData] = useState([]);

  let nav = useNavigate();
  const handleRowClick = (event) => {
    checkLogin();

    if (isLoggedIn) {
      console.log(event.target.parentElement.firstChild.textContent);
      let clickId = event.target.parentElement.firstChild.textContent;
      console.log(chalData)
      var challenge = chalData.filter((obj) => {
        return obj.challenge_no == clickId;
      });
      console.log(challenge);

      fetchLadder(challenge[0]);
    } else {
      let path = "/studentcentre";
      nav(path, {});
      console.log("hi");
    }
  };

  const fetchLadder = async (challenge) => {
    let config = {
      headers: {
        user: localStorage.getItem("user"),
        token: localStorage.getItem("token"),
      },
      params: { challenge_id: challenge.challenge_id },
    };

    const req = await axios
      .get("http://127.0.0.1:5000/submissions", config)
      .then((response) => {
        let queries = response.data;
        console.log(queries);

        queries.map((item) => {
          //setting rank and rounding time
          item.rank = item.rank + 1;
          item.total_time = item.total_time.toFixed(4);
        });

        queries = queries.filter((item) => {
          return item.is_correct != false;
        });

        let send_data = {
          challenge: challenge,
          chal_list: queries,
          user: localStorage.getItem("user"),
          token: localStorage.getItem("token"),
          token_timestamp: localStorage.getItem("token_timestamp"),
        };

        let path = "/challengeOne";
        nav(path, { state: send_data });
      });
  };

  const checkLogin = () => {
    if (localStorage.getItem("token_timestamp")) {
      let token_time = localStorage.getItem("token_timestamp");
      let current_time = Date.now() / 1000;

      if (current_time - token_time >= 600) {
        setIsLoggedIn(false);
      } else {
        setIsLoggedIn(true);
      }
    }
  };

 
  const fetchChalData = async () => {
    const res = await axios
      .get(" http://127.0.0.1:5000/challenges")
      .catch((err) => console.log(err));

    if (res) {
      const data = res.data;
      console.log(data);
      data.forEach((item, index) => (item.challenge_no = index + 1));

      setChalData(
        data.map((item) => ({
          ...item,
        }))
      );
      console.log(chalData);
    }
  };
  useEffect(() => {
    fetchChalData();
    checkLogin();
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
