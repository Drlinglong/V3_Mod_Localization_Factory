import React from 'react';
import { useTranslation } from 'react-i18next';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Modern Dark Theme Colors
const COLORS = ['#4dabf7', '#69db7c', '#ffd43b']; // Mantine Blue 4, Green 4, Yellow 4

const ProjectStatusPieChart = ({ data: dynamicData }) => {
  const { t } = useTranslation();

  const statusMap = {
    'done': t('homepage_pie_chart_translated'),
    'proofreading': t('homepage_pie_chart_proofreading'),
    'todo': t('homepage_pie_chart_untranslated'),
    'Done': t('homepage_pie_chart_translated'),
    'Proofreading': t('homepage_pie_chart_proofreading'),
    'Todo': t('homepage_pie_chart_untranslated')
  };

  const defaultData = [
    { name: t('homepage_pie_chart_translated'), value: 0 },
    { name: t('homepage_pie_chart_proofreading'), value: 0 },
    { name: t('homepage_pie_chart_untranslated'), value: 0 },
  ];

  const data = dynamicData && dynamicData.length > 0
    ? dynamicData.map(d => ({ ...d, name: statusMap[d.name] || d.name }))
    : defaultData;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60} // Donut chart looks more modern
          outerRadius={100}
          paddingAngle={5}
          dataKey="value"
          stroke="none"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ backgroundColor: 'var(--glass-bg)', borderColor: 'var(--glass-border)', color: 'var(--text-main)', backdropFilter: 'blur(10px)' }}
          itemStyle={{ color: 'var(--text-main)' }}
        />
        <Legend wrapperStyle={{ paddingTop: '20px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default ProjectStatusPieChart;
