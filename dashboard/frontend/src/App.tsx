import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface Metrics {
  timestamp: string;
  acceleration: {
    typing_speed: number;
    error_recovery: number;
    context_switching: number;
    problem_solving: number;
  };
  patterns: {
    recognition_speed: number;
    integration_speed: number;
    pattern_complexity: number;
  };
  growth: {
    acceleration_trend: number;
    learning_efficiency: number;
    adaptability: number;
  };
  meta_patterns: {
    learning_acceleration: number;
    pattern_recognition_evolution: number;
    integration_speed_changes: number;
    adaptability_growth: number;
  };
}

function App() {
  const [metrics, setMetrics] = useState<Metrics[]>([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000/ws');

    ws.onmessage = (event) => {
      const newMetric = JSON.parse(event.data);
      setMetrics((prevMetrics) => [...prevMetrics.slice(-20), newMetric]);
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Cognitive Metrics Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="border p-4 rounded">
          <h2 className="text-xl mb-2">Acceleration Metrics</h2>
          <LineChart width={500} height={300} data={metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="acceleration.typing_speed" stroke="#8884d8" />
            <Line type="monotone" dataKey="acceleration.error_recovery" stroke="#82ca9d" />
            <Line type="monotone" dataKey="acceleration.context_switching" stroke="#ffc658" />
          </LineChart>
        </div>
        <div className="border p-4 rounded">
          <h2 className="text-xl mb-2">Pattern Recognition</h2>
          <LineChart width={500} height={300} data={metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="patterns.recognition_speed" stroke="#8884d8" />
            <Line type="monotone" dataKey="patterns.integration_speed" stroke="#82ca9d" />
          </LineChart>
        </div>
      </div>
    </div>
  );
}

export default App;
