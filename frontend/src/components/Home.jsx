import { useEffect, useState } from 'react';
import { fetchSalesByDate, simulateSalesForDate, fetchWeather } from '../api/chatgpt';

const Home = () => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const showSuccess = useAutoClearMessage(successMessage, setSuccessMessage);
  const showError = useAutoClearMessage(errorMessage, setErrorMessage);
  const [salesDate, setSalesDate] = useState('');
  const [salesLoading, setSalesLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isSimulation, setIsSimulation] = useState(false);
  const [sales, setSales] = useState([]);
  const [agentConversation, setAgentConversation] = useState([]);
  const [weather, setWeather] = useState(null);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');

  const [conversationLoading, setConversationLoading] = useState(false);

  function useAutoClearMessage(message, setMessage, delay = 5000) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
      if (message) {
        setVisible(true);
        const timer = setTimeout(() => {
          setVisible(false);
          setTimeout(() => setMessage(''), 1000);
        }, delay);
        return () => clearTimeout(timer);
      }
    }, [message, setMessage, delay]);

    return visible;
  }

  const isFutureDate = (date) => {
    const today = new Date().toISOString().split('T')[0];
    return date > today;
  };

  const formatDateForDisplay = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const fetchSales = async () => {
    const futureDate = isFutureDate(selectedDate);
    setIsSimulation(futureDate);
    setSalesLoading(true);
    setConversationLoading(futureDate);
    setAgentConversation([]);

    try {
      let data;
      if (futureDate) {
        data = await simulateSalesForDate({ date: selectedDate });

        if (data.conversation && Array.isArray(data.conversation)) {
          setAgentConversation(data.conversation);
        }
      } else {
        data = await fetchSalesByDate({ date: selectedDate });
      }
      const groupedSales = data.sales.reduce((acc, sale) => {
        if (!acc[sale.transaction_id]) {
          acc[sale.transaction_id] = {
            transaction_id: sale.transaction_id,
            timestamp: sale.timestamp,
            items: [],
            total: 0,
          };
        }
        acc[sale.transaction_id].items.push({
          name: sale.item_name,
          quantity: sale.quantity,
          amount: sale.amount,
        });
        acc[sale.transaction_id].total += sale.amount;
        return acc;
      }, {});

      const salesArray = Object.values(groupedSales);
      setSales(salesArray);
      setSalesDate(selectedDate);

      if (salesArray.length > 0) {
        setSuccessMessage(
          futureDate
            ? `Sales simulation completed for ${formatDateForDisplay(selectedDate)}!`
            : `Sales data loaded for ${formatDateForDisplay(selectedDate)}!`,
        );
      } else {
        setSuccessMessage(
          futureDate
            ? `No sales simulated for ${formatDateForDisplay(selectedDate)}`
            : `No sales found for ${formatDateForDisplay(selectedDate)}`,
        );
      }
    } catch (err) {
      console.error('Error fetching sales:', err);
      setErrorMessage(
        futureDate
          ? `Failed to simulate sales for ${formatDateForDisplay(selectedDate)}.`
          : `Failed to fetch sales for ${formatDateForDisplay(selectedDate)}.`,
      );
    } finally {
      setSalesLoading(false);
      setConversationLoading(false);
    }
  };

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
    setSales([]);
    setAgentConversation([]);
    setSalesDate('');
  };

  const clearResults = () => {
    setSales([]);
    setAgentConversation([]);
    setSalesDate('');
    setIsSimulation(false);
  };

  console.log(agentConversation);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setWeather(null);
    try {
      const data = await fetchWeather({ lat: parseFloat(lat), lon: parseFloat(lon) });
      setWeather(data);
    } catch (e) {
      setErrorMessage(e?.response?.data?.message || e.message || "Virhe haussa");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-start bg-gray-100 p-4 pt-8">
      <div className="w-full max-w-4xl">
        <h1 className="mb-8 text-center text-3xl font-bold">Sales Analysis & Simulation</h1>

        <div className="mb-6 rounded-xl bg-white p-6 shadow-md">
          <div className="flex flex-col items-end gap-4 sm:flex-row">
            <div className="flex-1">
              <label htmlFor="salesDate" className="mb-2 block text-sm font-medium">
                Select Date
              </label>
              <input
                id="salesDate"
                type="date"
                value={selectedDate}
                onChange={handleDateChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => fetchSales()}
                disabled={salesLoading || conversationLoading}
                className="rounded-lg bg-black px-6 py-2 font-semibold text-white shadow transition-colors duration-200 hover:cursor-pointer hover:bg-blue-700 disabled:bg-gray-400"
              >
                {salesLoading
                  ? 'Loading...'
                  : isFutureDate(selectedDate)
                    ? 'Simulate Sales'
                    : 'Fetch Sales'}
              </button>

              {(sales.length > 0 || agentConversation.length > 0) && (
                <button
                  onClick={clearResults}
                  className="rounded-lg bg-gray-500 px-4 py-2 font-semibold text-white shadow transition-colors duration-200 hover:cursor-pointer hover:bg-gray-600"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        {conversationLoading && (
          <div className="mb-6 rounded-lg bg-white p-4 shadow">
            <div className="flex items-center space-x-2">
              <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-blue-600"></div>
              <p>Simulating sales...</p>
            </div>
          </div>
        )}

        {agentConversation.length > 0 && (
          <div className="mb-6 rounded-lg bg-white p-6 shadow">
            <h3 className="mb-4 flex items-center text-lg font-semibold text-gray-800">
              Agent Conversation Log
            </h3>
            <div className="max-h-96 space-y-3 overflow-y-auto">
              {agentConversation.map((message, index) => (
                <div
                  key={index}
                  className={`rounded-lg p-3 ${
                    message.type === 'user'
                      ? 'border-l-4 border-blue-400 bg-blue-50'
                      : message.type === 'assistant'
                        ? 'border-l-4 border-green-400 bg-green-50'
                        : 'border-l-4 border-gray-400 bg-gray-50'
                  }`}
                >
                  <div className="mb-1 flex items-center space-x-2">
                    <span className="text-sm font-medium">
                      {message.agent || message.type || 'Agent'}
                    </span>
                    {message.timestamp && (
                      <span className="text-xs text-gray-400">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <p className="text-sm leading-relaxed text-gray-700">
                    {message.content || message.message}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        <form onSubmit={onSubmit} className="mt-6 space-y-3 rounded-lg bg-white p-4 shadow">
          <div>
            <label className="block text-sm font-medium">Lat</label>
            <input
              type="number"
              step="any"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              required
              className="mt-1 w-full rounded border px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Lon</label>
            <input
              type="number"
              step="any"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              required
              className="mt-1 w-full rounded border px-3 py-2"
            />
          </div>
          <div className="pt-2">
            <button type="submit" disabled={loading} className="rounded bg-black px-4 py-2 font-semibold text-white disabled:bg-gray-400">
              {loading ? "Haetaan..." : "Hae sää"}
            </button>
          </div>
        </form> 
        {weather && (
          <>
            <div
              className={`mt-3 rounded-lg p-3 font-medium ${
                weather.is_raining ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"
              }`}
            >
              {weather.is_raining ? "It’s raining today" : "It’s not raining today"}
            </div>

            <pre className="mt-3 max-w-4xl overflow-auto rounded-lg bg-gray-900 p-4 text-sm text-gray-100">
              {JSON.stringify(weather, null, 2)}
            </pre>
          </>
        )}
        {sales.length > 0 && (
          <div className="mb-6 rounded-lg bg-white p-6 shadow">
            <h3 className="mb-4 flex items-center text-xl font-semibold text-gray-800">
              {isSimulation ? (
                <>Simulated Sales for {formatDateForDisplay(salesDate)}</>
              ) : (
                <>Sales for {formatDateForDisplay(salesDate)}</>
              )}
            </h3>

            <div className="grid gap-4">
              {sales.map((transaction) => (
                <div
                  key={transaction.transaction_id}
                  className="rounded-lg border border-gray-200 bg-gray-50 p-4"
                >
                  <div className="mb-2 flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-800">
                        Transaction ID: {transaction.transaction_id}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(transaction.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <p className="text-lg font-bold text-green-600">
                      €{transaction.total.toFixed(2)}
                    </p>
                  </div>

                  <div className="space-y-1">
                    {transaction.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span>
                          {item.quantity} × {item.name}
                        </span>
                        <span className="text-gray-600">€{item.amount.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 border-t border-gray-200 pt-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium text-gray-700">
                  Total {isSimulation ? 'Simulated' : ''} Revenue:
                </span>
                <span className="text-2xl font-bold text-green-600">
                  €{sales.reduce((sum, t) => sum + t.total, 0).toFixed(2)}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {sales.length} transaction{sales.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="mt-4 w-full max-w-md rounded-lg border border-blue-300 bg-blue-100 p-4 text-blue-800 shadow">
          <p className="font-medium">Loading answer...</p>
        </div>
      )}

      {successMessage && !loading && !errorMessage && (
        <div
          className={`mt-4 w-full max-w-md rounded-lg border border-green-300 bg-green-100 p-4 text-green-800 shadow transition-opacity duration-1000 ${
            showSuccess ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <p className="font-medium">{successMessage}</p>
        </div>
      )}

      {errorMessage && !loading && (
        <div
          className={`mt-4 w-full max-w-md rounded-lg border border-red-300 bg-red-100 p-4 text-red-800 shadow transition-opacity duration-1000 ${
            showError ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <p className="font-medium">{errorMessage}</p>
        </div>
      )}
    </div>
  );
};

export default Home;
