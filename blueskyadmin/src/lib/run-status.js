
export const runStatuses = {
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

export const reverseRunStatusMappings = Object.keys(runStatuses).reduce((r,k) => {
    r[runStatuses[k]] = k
    return r
}, {})


export function translateRunStatus(s) {
    if (runStatuses[s])
        return runStatuses[s]

    else if (reverseRunStatusMappings[s])
        return s

    return null
}
