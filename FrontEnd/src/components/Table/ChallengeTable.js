import { useEffect, useState, useMemo } from "react";
import axios from "axios";
import {
  useTable,
  useSortBy,
  useGlobalFilter,
  useFilters,
} from "react-table/dist/react-table.development";
import { COLUMNS } from "./Columns/ChallengeColumns";
import "./Columns/ladderColumns.css";
import "./ChallengeTable.css";

const ChallengeTable = ({ board_data }) => {
  const [sqlLadder, setSqlLadder] = useState([]);
  const fetchLadder = () => {
    if (board_data) {
      const queries = board_data;
      setSqlLadder(
        queries.map((query) => ({
          ...query,
        }))
      );
    }
  };

  useEffect(() => {
    fetchLadder();
  }, []);

  const columns = useMemo(() => COLUMNS, []);

  const ladderData = useMemo(() => [...sqlLadder], [sqlLadder]);

  const tableInstance = useTable(
    {
      columns,
      data: ladderData,
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
    setGlobalFilter,
  } = tableInstance;

  return (
    <div className="table-container">
      <table className="sticky-column ch-table" {...getTableProps()}>
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <th
                  className="sticky-column"
                  {...column.getHeaderProps(column.getSortByToggleProps())}
                >
                  {column.render("Header")}
                  <span>
                    {column.isSorted
                      ? column.isSortedDesc
                        ? "⬇️"
                        : "⬆️"
                      : "↕"}
                  </span>
                  <div>{column.canFilter ? column.render("Filter") : null}</div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
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

export default ChallengeTable;
