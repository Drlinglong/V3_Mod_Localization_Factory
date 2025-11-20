import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const GlossaryAnalysisBarChart = () => {
  const { t } = useTranslation();

  const data = [
    { name: t('game_name_vic3'), terms: 4000 },
    { name: t('game_name_stellaris'), terms: 3000 },
    { name: t('game_name_hoi4'), terms: 2000 },
    { name: t('game_name_ck3'), terms: 2780 },
    { name: t('game_name_eu4'), terms: 1890 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        margin={{
          top: 5, right: 30, left: 20, bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#373A40" vertical={false} />
        <XAxis dataKey="name" stroke="#909296" tick={{ fill: '#909296' }} />
        <YAxis stroke="#909296" tick={{ fill: '#909296' }} />
        <Tooltip
          cursor={{ fill: '#373A40', opacity: 0.4 }}
          contentStyle={{ backgroundColor: '#2C2E33', borderColor: '#373A40', color: '#C1C2C5' }}
          itemStyle={{ color: '#C1C2C5' }}
        />
        <Legend wrapperStyle={{ paddingTop: '20px' }} />
        <Bar dataKey="terms" name={t('homepage_bar_chart_terms')} fill="#339af0" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default GlossaryAnalysisBarChart;
