import { ColumnFilter } from "./ladderColumnFilter"

export const COLUMNS = [
    {
        Header: "Rank #",
        accessor: 'rank',
        Filter: ColumnFilter,
        disableFilters: true
    },
    {
        Header: "Challenge Id",
        accessor: 'challenge_id',
        Filter: ColumnFilter
    },
    {
        Header: "Name",
        accessor: 'name',
        Filter: ColumnFilter
    },
    {
        Header: "Execution Time",
        accessor: 'execution_time',
        Filter: ColumnFilter,
        disableFilters: true
    },
    {
        Header: "Planning Time",
        accessor: 'planning_time',
        Filter: ColumnFilter,
        disableFilters: true
    },
    {
        Header: "Total Time",
        accessor: 'total_time',
        Filter: ColumnFilter,
        disableFilters: true
    },
    {
        Header: "Last Submission",
        accessor: 'last_submission',
        Filter: ColumnFilter,
        disableFilters: true
    }
]