import { Link } from "react-router-dom";
import {useEffect, useState, useMemo} from 'react'
import axios from "axios";
import { useTable, useSortBy, useGlobalFilter, useFilters} from "react-table/dist/react-table.development";
import { COLUMNS } from './components/ladderColumns'
import './components/ladderColumns.css'
import { GlobalFilter } from "./components/globalLadderFilter";

import Navigation from "./components/Navigation/Navigation";

export default function App() {
  const [sqlLadder, setSqlLadder] = useState([])
  const fetchLadder = async () => {
    const res = await axios.get("http://localhost:3001/query").catch(err => console.log(err))

    if(res){
      const queries = res.data
      setSqlLadder(queries.map(query =>({
        ...query,
        total_time: query.execution_time + query.planning_time
      })))
    }
    
  }
  useEffect(()=> {
    fetchLadder()
  }, [])
  
  const columns = useMemo(() => COLUMNS, [])

  const ladderData = useMemo(() => [...sqlLadder], [sqlLadder])
  
  console.log(...ladderData)

  const tableInstance = useTable({
    columns,
    data: ladderData
  },
  useFilters,
  useGlobalFilter,
  useSortBy
  )
  
  const{
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state,
    setGlobalFilter
  } = tableInstance
  
  

  const {globalFilter} = state

  return (
    <div>
      <h1>SQL ladder</h1>
      <nav
        style={{
          borderBottom: "solid 1px",
          paddingBottom: "1rem",
        }}
      >
        <Link to="/db">Our DB</Link> |{" "}
        <Link to="/submission">SQL Submission</Link>|{" "}
        <Link to="/tasks">SQL Tasks</Link>
      </nav>
      <>
      <Navigation/>      
      <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter}/>
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                {column.render('Header')}
                <span>
                  {column.isSorted ? (column.isSortedDesc ? '⬇️' : '⬆️') : '↕'}
                </span>
                <div>{column.canFilter ? column.render('Filter'): null}</div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row)
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => {
                  return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
      </>
    </div>
  );
}

