"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export interface SetInfo {
  timestamp: string;
  set_info: string;
}

export interface Prediction {
  timestamp: string;
  predicted_win: number;
}

interface PredictedWinChartProps {
  sets: SetInfo[];
  predictions: Prediction[];
}

export function PredictedWinChart({ sets, predictions }: PredictedWinChartProps) {
  if (!sets || sets.length === 0) {
    return <div className="text-center text-sm text-gray-500 mt-6">Nessun dato disponibile</div>;
  }

  const chartData = sets.map((s, idx) => ({
    setInfo: s.set_info,
    win: +(predictions[idx]?.predicted_win * 100).toFixed(1) || 0,
  }));

  return (
    <div className="mt-6">
      <div className="w-full h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 5, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="setInfo"
              axisLine={false}
              tickLine={false}
              tick={false}
              label={{ value: 'Andamento del WinScore', position: 'insideBottom', dy: 0, style: { fontSize: '15px', fontWeight: 300 } }}
            />
            <YAxis axisLine={false} tickLine={false} domain={[0, 100]} unit="%" />
            <Tooltip formatter={(value: number) => `${value}%`} />
            <Line type="monotone" dataKey="win" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}