import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Users, Activity, AlertTriangle, Clock, TrendingUp, Camera, Wifi } from 'lucide-react'

interface Metrics {
  current_people: number
  total_footfall: number
  avg_dwell_time: number
  queue_length: number
  alerts: string[]
}

interface CameraData {
  [key: string]: Metrics
}

const initialMetrics: CameraData = {
  cam_01: { current_people: 12, total_footfall: 156, avg_dwell_time: 245, queue_length: 3, alerts: [] },
  cam_02: { current_people: 8, total_footfall: 89, avg_dwell_time: 180, queue_length: 0, alerts: [] },
  cam_03: { current_people: 5, total_footfall: 234, avg_dwell_time: 120, queue_length: 4, alerts: ['queue_warning'] },
  cam_04: { current_people: 15, total_footfall: 312, avg_dwell_time: 300, queue_length: 0, alerts: [] }
}

const hourlyData = [
  { hour: '6AM', count: 12 }, { hour: '8AM', count: 28 },
  { hour: '10AM', count: 45 }, { hour: '12PM', count: 67 },
  { hour: '2PM', count: 52 }, { hour: '4PM', count: 78 },
  { hour: '6PM', count: 95 }, { hour: '8PM', count: 43 }
]

function App() {
  const [metrics, setMetrics] = useState<CameraData>(initialMetrics)
  const [connected, setConnected] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState('cam_01')

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8001'
    let ws: WebSocket | null = null
    let reconnectTimer: number

    const connect = () => {
      try {
        ws = new WebSocket(`${wsUrl}/ws/metrics`)

        ws.onopen = () => {
          setConnected(true)
          console.log('Connected to WebSocket')
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'metrics_update' && data.data) {
              setMetrics(data.data)
            }
          } catch (e) {
            console.error('Failed to parse message:', e)
          }
        }

        ws.onclose = () => {
          setConnected(false)
          reconnectTimer = window.setTimeout(connect, 3000)
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
        }
      } catch (e) {
        console.error('Failed to connect:', e)
        setConnected(false)
      }
    }

    connect()

    return () => {
      if (ws) ws.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }
  }, [])

  const totalPeople = Object.values(metrics).reduce((sum, m) => sum + m.current_people, 0)
  const totalFootfall = Object.values(metrics).reduce((sum, m) => sum + m.total_footfall, 0)
  const totalQueue = Object.values(metrics).reduce((sum, m) => sum + m.queue_length, 0)

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Activity size={32} />
            Retail Intelligence Dashboard
          </h1>
          <p style={{ color: '#888', marginTop: '4px' }}>Real-time analytics and monitoring</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: connected ? '#1a3d1a' : '#3d1a1a', borderRadius: '8px' }}>
            <Wifi size={16} />
            <span style={{ fontSize: '14px' }}>{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' }}>
        <MetricCard
          title="Total People"
          value={totalPeople}
          icon={<Users size={24} />}
          color="#4f46e5"
        />
        <MetricCard
          title="Total Footfall"
          value={totalFootfall}
          icon={<TrendingUp size={24} />}
          color="#10b981"
        />
        <MetricCard
          title="Avg Dwell Time"
          value="3m 42s"
          icon={<Clock size={24} />}
          color="#f59e0b"
        />
        <MetricCard
          title="Queue Count"
          value={totalQueue}
          icon={<AlertTriangle size={24} />}
          color={totalQueue > 5 ? '#ef4444' : '#6366f1'}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '30px' }}>
        <div style={{ background: '#1e1e1e', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={20} />
            Hourly Footfall
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="hour" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{ background: '#2a2a2a', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="count" stroke="#4f46e5" strokeWidth={2} dot={{ fill: '#4f46e5' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: '#1e1e1e', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Camera size={20} />
            Camera Status
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {Object.entries(metrics).map(([cameraId, data]) => (
              <div
                key={cameraId}
                onClick={() => setSelectedCamera(cameraId)}
                style={{
                  padding: '12px',
                  background: selectedCamera === cameraId ? '#2a2a2a' : '#252525',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  border: selectedCamera === cameraId ? '2px solid #4f46e5' : '2px solid transparent'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 'bold' }}>{cameraId.toUpperCase()}</span>
                  <span style={{ color: '#10b981', fontSize: '12px' }}>Active</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#888' }}>
                  <span>People: {data.current_people}</span>
                  <span>Queue: {data.queue_length}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ background: '#1e1e1e', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Camera Analytics: {selectedCamera.toUpperCase()}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ background: '#252525', padding: '16px', borderRadius: '8px' }}>
              <div style={{ color: '#888', fontSize: '14px', marginBottom: '4px' }}>Current People</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{metrics[selectedCamera]?.current_people || 0}</div>
            </div>
            <div style={{ background: '#252525', padding: '16px', borderRadius: '8px' }}>
              <div style={{ color: '#888', fontSize: '14px', marginBottom: '4px' }}>Total Footfall</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{metrics[selectedCamera]?.total_footfall || 0}</div>
            </div>
            <div style={{ background: '#252525', padding: '16px', borderRadius: '8px' }}>
              <div style={{ color: '#888', fontSize: '14px', marginBottom: '4px' }}>Avg Dwell Time</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{Math.floor((metrics[selectedCamera]?.avg_dwell_time || 0) / 60)}m {Math.floor((metrics[selectedCamera]?.avg_dwell_time || 0) % 60)}s</div>
            </div>
            <div style={{ background: '#252525', padding: '16px', borderRadius: '8px' }}>
              <div style={{ color: '#888', fontSize: '14px', marginBottom: '4px' }}>Queue Length</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: (metrics[selectedCamera]?.queue_length || 0) > 3 ? '#ef4444' : '#10b981' }}>
                {metrics[selectedCamera]?.queue_length || 0}
              </div>
            </div>
          </div>
        </div>

        <div style={{ background: '#1e1e1e', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} />
            Recent Alerts
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '200px', overflowY: 'auto' }}>
            {metrics[selectedCamera]?.alerts?.length ? (
              metrics[selectedCamera].alerts.map((alert, i) => (
                <div key={i} style={{ padding: '12px', background: '#3d2a1a', borderRadius: '8px', borderLeft: '3px solid #f59e0b' }}>
                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{alert}</div>
                  <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>Queue warning at {selectedCamera}</div>
                </div>
              ))
            ) : (
              <div style={{ color: '#888', textAlign: 'center', padding: '40px' }}>No active alerts</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  color: string
}

function MetricCard({ title, value, icon, color }: MetricCardProps) {
  return (
    <div style={{ background: '#1e1e1e', borderRadius: '12px', padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
      <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: `${color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
        {icon}
      </div>
      <div>
        <div style={{ color: '#888', fontSize: '14px' }}>{title}</div>
        <div style={{ fontSize: '28px', fontWeight: 'bold' }}>{value}</div>
      </div>
    </div>
  )
}

export default App
