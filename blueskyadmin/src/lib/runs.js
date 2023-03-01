import { PUBLIC_API_URL } from '$env/static/public';

export const limit = 20

export async function queryRuns(fetch, page, offset, runStatus, runId) {
    let apiUrl = `${PUBLIC_API_URL}/runs/${runStatus || ''}?limit=${limit}&offset=${offset}`
    if (runId)
        apiUrl += `&run_id=${runId}`
    console.log(`Fetching from ${apiUrl}`)
    const res = await fetch(apiUrl, {mode:"no-cors"});
    const runsData = await res.json();
    return runsData
}
