interface StatsCardProps {
  title: string;
  value: string;
  description: string;
}

export function StatsCard({ title, value, description }: StatsCardProps) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
    </div>
  );
}
