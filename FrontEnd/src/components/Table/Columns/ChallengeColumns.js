import { ColumnFilter } from "./ladderColumnFilter";

export const COLUMNS = [
  {
    Header: "Rank #",
    accessor: "rank",
    Filter: ColumnFilter,
    disableFilters: true,
  },
  {
    Header: "User Name",
    accessor: "user_name",
    Filter: ColumnFilter,
  },
  {
    Header: "Planning Time",
    accessor: "planning_time",
    Filter: ColumnFilter,
    disableFilters: true,
  },
  {
    Header: "Execution Time",
    accessor: "execution_time",
    Filter: ColumnFilter,
    disableFilters: true,
  },

  {
    Header: "Total Time",
    accessor: "total_time",
    Filter: ColumnFilter,
    disableFilters: true,
  },
  {
    Header: "Submission time",
    accessor: "timestamp",
    Filter: ColumnFilter,
    disableFilters: true,
  },
];
