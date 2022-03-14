import { Link } from "react-router-dom";
import {useEffect, useState} from 'react'
import axios from "axios";
import { useTable } from "react-table/dist/react-table.development";

export default function App() {
  const [sqlQueries, setSqlQueries] = useState()
  const fetchQueries = async () => {
    const res = await axios.get("http://localhost:3001/query").catch(err => console.log(err))

    if(res){
      const queries = res.data
      console.log(queries)
      setSqlQueries(queries)
    }
  }

  useEffect(()=> {
    fetchQueries()
  }, [])

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
      <h2>Task: To extract so and so from the db</h2>

    </div>
  );
}

