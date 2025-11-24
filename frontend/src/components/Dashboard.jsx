import { useState, useEffect } from 'react';
import { fetchDashboardData } from '../api/dashboardapi';


const Dashboard =  () => {
    const [dashboardData, setDashboardData] = useState({ });

    useEffect(() => {
        (async () => {
          try {
            const data = await fetchDashboardData();
            setDashboardData(data);
          } catch (err) {
            console.error(err);
          }
    })();
    },[]);
    

    return (
        <div>
            <p>  {JSON.stringify(dashboardData)} </p>
        </div>
    );
};

export default Dashboard;