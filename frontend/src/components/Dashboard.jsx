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
    
    const ytd_sales_growth = dashboardData?.sales?.ytd?.growth ?? "N/A";

    return (
        <div>
            <p>  {ytd_sales_growth} </p>
        </div>
    );
};

export default Dashboard;