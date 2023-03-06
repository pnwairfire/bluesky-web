/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */
import { PUBLIC_API_URL } from '$env/static/public';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
    try {
        const [monthlyRes, dailyRes] = await Promise.all([
          fetch(`${PUBLIC_API_URL}/runs/stats/monthly`, {mode:"no-cors"}),
          fetch(`${PUBLIC_API_URL}/runs/stats/daily`, {mode:"no-cors"}),
        ])
        const monthly = await monthlyRes.json();
        const daily = await dailyRes.json();
        const stats = {
            monthly: monthly.monthly,
            daily: daily.daily
        }
        return { stats }
    } catch(error) {
        console.error(`Error in load loading stats information: ${error}`);
        return {error}
    }
}
