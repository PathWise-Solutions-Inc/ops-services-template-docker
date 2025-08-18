import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

interface DashboardProps {
  systemStatus: {
    lightrag: boolean;
    supabase: boolean;
    n8n: boolean;
    redis: boolean;
  };
}

interface Stats {
  documentsCount: number;
  entitiesCount: number;
  relationshipsCount: number;
  queriesCount: number;
  avgResponseTime: number;
  storageUsed: string;
}

interface RecentActivity {
  id: string;
  type: 'upload' | 'query' | 'chat';
  description: string;
  timestamp: string;
}

const Dashboard: React.FC<DashboardProps> = ({ systemStatus }) => {
  const [stats, setStats] = useState<Stats>({
    documentsCount: 0,
    entitiesCount: 0,
    relationshipsCount: 0,
    queriesCount: 0,
    avgResponseTime: 0,
    storageUsed: '0 MB',
  });

  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchRecentActivity();
  }, []);

  const fetchStats = async () => {
    try {
      // In production, fetch from actual API
      // const response = await fetch('/api/stats');
      // const data = await response.json();
      
      // Mock data for demonstration
      setStats({
        documentsCount: 42,
        entitiesCount: 256,
        relationshipsCount: 189,
        queriesCount: 1024,
        avgResponseTime: 235,
        storageUsed: '124.5 MB',
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentActivity = async () => {
    // Mock recent activity
    setRecentActivity([
      {
        id: '1',
        type: 'upload',
        description: 'Uploaded: AI Healthcare Report.pdf',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      },
      {
        id: '2',
        type: 'query',
        description: 'Query: "What are the latest AI trends?"',
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      },
      {
        id: '3',
        type: 'chat',
        description: 'Chat session started with 5 exchanges',
        timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      },
    ]);
  };

  // Data for charts
  const pieData = [
    { name: 'Documents', value: stats.documentsCount, color: '#0088FE' },
    { name: 'Entities', value: stats.entitiesCount, color: '#00C49F' },
    { name: 'Relationships', value: stats.relationshipsCount, color: '#FFBB28' },
  ];

  const barData = [
    { name: 'Mon', queries: 120, avgTime: 210 },
    { name: 'Tue', queries: 145, avgTime: 225 },
    { name: 'Wed', queries: 180, avgTime: 235 },
    { name: 'Thu', queries: 165, avgTime: 220 },
    { name: 'Fri', queries: 190, avgTime: 245 },
    { name: 'Sat', queries: 90, avgTime: 200 },
    { name: 'Sun', queries: 85, avgTime: 195 },
  ];

  const lineData = [
    { time: '00:00', cpu: 20, memory: 45 },
    { time: '04:00', cpu: 15, memory: 42 },
    { time: '08:00', cpu: 35, memory: 55 },
    { time: '12:00', cpu: 45, memory: 65 },
    { time: '16:00', cpu: 40, memory: 60 },
    { time: '20:00', cpu: 30, memory: 50 },
    { time: '24:00', cpu: 25, memory: 48 },
  ];

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 60) return `${minutes} minutes ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)} hours ago`;
    return `${Math.floor(minutes / 1440)} days ago`;
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* System Status Cards */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Documents
                  </Typography>
                  <Typography variant="h4">
                    {stats.documentsCount}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Entities
                  </Typography>
                  <Typography variant="h4">
                    {stats.entitiesCount}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Relations
                  </Typography>
                  <Typography variant="h4">
                    {stats.relationshipsCount}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Queries
                  </Typography>
                  <Typography variant="h4">
                    {stats.queriesCount}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Service Status */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Service Status
            </Typography>
            <List dense>
              {Object.entries(systemStatus).map(([service, status]) => (
                <ListItem key={service}>
                  <ListItemText primary={service.toUpperCase()} />
                  <Chip
                    label={status ? 'Online' : 'Offline'}
                    color={status ? 'success' : 'error'}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Knowledge Base Composition */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Knowledge Base Composition
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Query Performance */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Weekly Query Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="queries" fill="#8884d8" name="Queries" />
                <Bar yAxisId="right" dataKey="avgTime" fill="#82ca9d" name="Avg Time (ms)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Resource Usage */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Resource Usage (24h)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#8884d8" name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#82ca9d" name="Memory %" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%', maxHeight: 350, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {recentActivity.map((activity) => (
                <ListItem key={activity.id}>
                  <ListItemText
                    primary={activity.description}
                    secondary={formatTimestamp(activity.timestamp)}
                  />
                  <Chip
                    label={activity.type}
                    size="small"
                    color={
                      activity.type === 'upload'
                        ? 'primary'
                        : activity.type === 'query'
                        ? 'secondary'
                        : 'default'
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* System Info */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Average Response Time
                </Typography>
                <Typography variant="h6">{stats.avgResponseTime} ms</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Storage Used
                </Typography>
                <Typography variant="h6">{stats.storageUsed}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary">
                  API Version
                </Typography>
                <Typography variant="h6">v1.0.0</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary">
                  Last Updated
                </Typography>
                <Typography variant="h6">{new Date().toLocaleDateString()}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;