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

export async function queryStats(fetch, runId) {
    const runIdQueryStr = (runId) ? (`?run_id=${runId}`) : ('')
    const [monthlyRes, dailyRes] = await Promise.all([
      fetch(`${PUBLIC_API_URL}/runs/stats/monthly${runIdQueryStr}`, {mode:"no-cors"}),
      fetch(`${PUBLIC_API_URL}/runs/stats/daily${runIdQueryStr}`, {mode:"no-cors"}),
    ])
    const monthly = await monthlyRes.json();
    const daily = await dailyRes.json();

    return {
        monthly: monthly.monthly,
        daily: daily.daily
    }
}
