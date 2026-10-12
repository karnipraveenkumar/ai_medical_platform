import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const visits = [
  { month: 'Jan', patients: 680, appointments: 520 }, { month: 'Feb', patients: 720, appointments: 565 },
  { month: 'Mar', patients: 690, appointments: 550 }, { month: 'Apr', patients: 840, appointments: 660 },
  { month: 'May', patients: 790, appointments: 620 }, { month: 'Jun', patients: 940, appointments: 735 },
  { month: 'Jul', patients: 890, appointments: 710 }, { month: 'Aug', patients: 1030, appointments: 815 },
  { month: 'Sep', patients: 970, appointments: 780 }, { month: 'Oct', patients: 1110, appointments: 875 },
  { month: 'Nov', patients: 1050, appointments: 850 }, { month: 'Dec', patients: 1210, appointments: 940 },
]
const departments = [{ name: 'Cardiology', value: 32, color: '#4c6fff' }, { name: 'Neurology', value: 24, color: '#26b7a5' }, { name: 'Orthopedics', value: 21, color: '#f5b84b' }, { name: 'General', value: 23, color: '#a3aef8' }]
const money = (n: number) => `₹${n}k`

export function VisitsChart() {
  return <ResponsiveContainer width="100%" height="100%"><AreaChart data={visits} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}><defs><linearGradient id="patientFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#4c6fff" stopOpacity={0.2}/><stop offset="100%" stopColor="#4c6fff" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#edf0f6" vertical={false} strokeDasharray="3 4"/><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 11 }}/><YAxis axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 11 }}/><Tooltip contentStyle={{ border: '1px solid #e8ebf2', borderRadius: 12, boxShadow: '0 8px 24px #1d2a4412' }}/><Area type="monotone" dataKey="patients" name="Patient visits" stroke="#4c6fff" strokeWidth={2.5} fill="url(#patientFill)"/><Area type="monotone" dataKey="appointments" name="Appointments" stroke="#22b8a7" strokeWidth={2.5} fill="none"/></AreaChart></ResponsiveContainer>
}
export function RevenueChart() {
  const data = [{ month: 'Jan', revenue: 320 }, { month: 'Feb', revenue: 370 }, { month: 'Mar', revenue: 345 }, { month: 'Apr', revenue: 420 }, { month: 'May', revenue: 395 }, { month: 'Jun', revenue: 480 }, { month: 'Jul', revenue: 460 }, { month: 'Aug', revenue: 520 }]
  return <ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}><CartesianGrid stroke="#edf0f6" vertical={false} strokeDasharray="3 4"/><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 11 }}/><YAxis tickFormatter={money} axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 10 }}/><Tooltip formatter={(v) => [`₹${v}k`, 'Revenue']} contentStyle={{ border: '1px solid #e8ebf2', borderRadius: 12 }}/><Bar dataKey="revenue" fill="#4c6fff" radius={[5, 5, 0, 0]} barSize={22}/></BarChart></ResponsiveContainer>
}
export function DepartmentChart() {
  return <div className="department-chart"><div className="donut"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={departments} dataKey="value" nameKey="name" innerRadius="66%" outerRadius="94%" paddingAngle={4} stroke="none">{departments.map((d) => <Cell key={d.name} fill={d.color}/>)}</Pie><Tooltip formatter={(v) => [`${v}%`, 'Share']}/></PieChart></ResponsiveContainer><div className="donut-center"><strong>100%</strong><span>visits</span></div></div><div className="legend-list">{departments.map(d => <div key={d.name} className="legend-row"><span className="legend-dot" style={{ background: d.color }}/><span>{d.name}</span><strong>{d.value}%</strong></div>)}</div></div>
}
