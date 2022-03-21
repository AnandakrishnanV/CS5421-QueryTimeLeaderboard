import { Link } from "react-router-dom";
import {useEffect, useState, useMemo} from 'react'
import axios from "axios";
import { useTable } from "react-table/dist/react-table.development";
import {COLUMNS} from './components/ladderColumns'
import './components/ladderColumns.css'
import Navigation from "./components/Navigation/Navigation";

export default function App() {
  const [sqlLadder, setSqlLadder] = useState([])
  const fetchLadder = async () => {
    const res = await axios.get("http://localhost:3001/query").catch(err => console.log(err))

    if(res){
      const queries = res.data
      setSqlLadder(queries)
    }
    
  }

  
  const columns = useMemo(() => COLUMNS, [])

  const ladderData = useMemo(() => [...sqlLadder], [sqlLadder])
  
  console.log(...ladderData)
  const tableInstance = useTable({
    columns,
    data: ladderData
  })
  
  const{
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = tableInstance
  
  useEffect(()=> {
    fetchLadder()
  }, [])

  return (
    <div>
      <Navigation/>      
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
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
        {/* <tfoot>
          {footerGroups.map(footerGroup => (
            <tr {...footerGroup.getFooterGroupProps()}>
              {footerGroup.headers.map(column => (
                <td {...column.getFooterProps()}>{column.render('Footer')}</td>
              ))}
            </tr>
          ))}
        </tfoot> */}
      </table>
    </div>
  );
}

