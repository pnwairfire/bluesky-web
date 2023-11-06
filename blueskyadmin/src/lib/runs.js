import { PUBLIC_API_URL, PUBLIC_PGV3_URL } from '$env/static/public';

const publicApiUrlNoSlash = PUBLIC_API_URL.replace(/\/$/, '')
const publicPgv3UrlNoSlash = PUBLIC_PGV3_URL && PUBLIC_PGV3_URL.replace(/\/$/, '')

export const limit = 20

export async function queryRuns(fetch, page, offset, runStatus, runId) {
    let apiUrl = `${publicApiUrlNoSlash}/runs/${runStatus || ''}?limit=${limit}&offset=${offset}`
    if (runId)
        apiUrl += `&run_id=${runId}`
    console.log(`Fetching from ${apiUrl}`)
    const res = await fetch(apiUrl, {mode:"no-cors"});
    const runsData = await res.json();
    if (publicPgv3UrlNoSlash) {
        runsData.runs && runsData.runs.forEach(r => {
            if (r.run_id.endsWith('-dispersion'))
                r.pgv3_url = `${publicPgv3UrlNoSlash}/dispersionresults.php?scenario_id=${r.run_id.replace('-dispersion', '')}`
            else if (r.run_id.endsWith('-plumerise'))
                r.pgv3_url = `${publicPgv3UrlNoSlash}/dispersioninputs.php?scenario_id=${r.run_id.replace('-plumerise', '')}`
        })
    }
    return runsData
}

export async function queryStats(fetch, runId) {
    const runIdQueryStr = (runId) ? (`?run_id=${runId}`) : ('')
    const [monthlyRes, dailyRes] = await Promise.all([
      fetch(`${publicApiUrlNoSlash}/runs/stats/monthly${runIdQueryStr}`, {mode:"no-cors"}),
      fetch(`${publicApiUrlNoSlash}/runs/stats/daily${runIdQueryStr}`, {mode:"no-cors"}),
    ])
    const monthly = await monthlyRes.json();
    const daily = await dailyRes.json();

    return {
        monthly: monthly.monthly,
        daily: daily.daily
    }
}
