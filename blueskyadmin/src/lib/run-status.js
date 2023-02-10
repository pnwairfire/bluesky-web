
export const statuses = {
    "Enqueued": "enqueued",
    "Dequeued": "dequeued",
    "Running": "running",
    "StartingModule": 'starting_module',
    'RunningModule': 'running_module',
    'CompletedModule': 'completed_module',
    'FailedModule': 'failed_module',
    "ProcessingOutput": "processing_output",
    "Completed": "completed",
    "Failed": "failed"
}

export const reverseRunStatusMappings = Object.keys(statuses).reduce((r,k) => {
    r[statuses[k]] = k
    return r
}, {})
