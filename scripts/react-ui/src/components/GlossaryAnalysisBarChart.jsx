import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Victoria 3', terms: 4000 },
  { name: 'Stellaris', terms: 3000 },
  { name: 'Hearts of Iron 4', terms: 2000 },
  { name: 'Crusader Kings 3', terms: 2780 },
  { name: 'Europa Universalis 4', terms: 1890 },
];

const GlossaryAnalysisBarChart = () => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        margin={{
          top: 5, right: 30, left: 20, bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="terms" fill="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default GlossaryAnalysisBarChart;
