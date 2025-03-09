/**
 * Dashboard page for the 3X-UI Management System.
 * 
 * This component displays system statistics and activity information.
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  CardHeader,
  Avatar,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Person as PersonIcon,
  Computer as ServerIcon,
  Layers as ServiceIcon,
  ShoppingCart as OrderIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  PersonOutline as PersonOutlineIcon,
  Storage as StorageIcon,
  Router as RouterIcon,
  Devices as DevicesIcon,
  ImportExport as ImportExportIcon,
  Timeline as TimelineIcon,
  Public as PublicIcon,
  Dns as DnsIcon,
  Memory as MemoryIcon,
  SdStorage as SdStorageIcon,
  NetworkCheck as NetworkCheckIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { format } from 'date-fns';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Demo data for charts
const serverStatusData = [
  { name: 'Online', value: 18 },
  { name: 'Offline', value: 2 },
];

const trafficData = [
  { name: 'Jan', traffic: 400 },
  { name: 'Feb', traffic: 300 },
  { name: 'Mar', traffic: 600 },
  { name: 'Apr', traffic: 800 },
  { name: 'May', traffic: 700 },
  { name: 'Jun', traffic: 900 },
  { name: 'Jul', traffic: 1000 },
];

const revenueData = [
  { name: 'Jan', revenue: 4000 },
  { name: 'Feb', revenue: 3000 },
  { name: 'Mar', revenue: 5000 },
  { name: 'Apr', revenue: 7000 },
  { name: 'May', revenue: 6000 },
  { name: 'Jun', revenue: 8000 },
  { name: 'Jul', revenue: 9500 },
];

const usersData = [
  { name: 'Jan', active: 40, total: 60 },
  { name: 'Feb', active: 45, total: 70 },
  { name: 'Mar', active: 55, total: 85 },
  { name: 'Apr', active: 65, total: 100 },
  { name: 'May', active: 80, total: 120 },
  { name: 'Jun', active: 95, total: 140 },
  { name: 'Jul', active: 110, total: 160 },
];

// COLORS for pie chart
const COLORS = ['#0088FE', '#FF8042'];

/**
 * Dashboard component displaying system metrics and activities.
 */
const Dashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const theme = useTheme();
  const { user } = useAuth();
  
  // State for dashboard data
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Line chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: theme.palette.text.primary,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        ticks: {
          color: theme.palette.text.secondary,
        },
        grid: {
          color: theme.palette.divider,
        },
      },
      x: {
        ticks: {
          color: theme.palette.text.secondary,
        },
        grid: {
          color: theme.palette.divider,
        },
      },
    },
    elements: {
      line: {
        tension: 0.4,
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };
  
  // Traffic data for chart
  const trafficData = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [
      {
        fill: true,
        label: t('dashboard.thisMonth'),
        data: [65, 59, 80, 81, 56, 55, 40],
        borderColor: theme.palette.primary.main,
        backgroundColor: `${theme.palette.primary.main}20`,
      },
      {
        fill: true,
        label: t('dashboard.lastMonth'),
        data: [28, 48, 40, 19, 86, 27, 90],
        borderColor: theme.palette.secondary.main,
        backgroundColor: `${theme.palette.secondary.main}20`,
      },
    ],
  };
  
  /**
   * Fetch dashboard data from API.
   */
  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a production environment, we would use real API calls
      // For now, simulate API response with mock data
      // const statsResponse = await dashboardAPI.getStats();
      // const activitiesResponse = await dashboardAPI.getRecentActivities(10);
      
      // Mock data for demonstration
      const statsData = {
        totalUsers: 156,
        activeUsers: 124,
        totalServers: 32,
        activeServers: 28,
        totalServices: 15,
        totalClients: 532,
        activeClients: 486,
        totalIncome: 14520,
        todayIncome: 650,
        cpuUsage: 42,
        memoryUsage: 67,
        diskUsage: 52,
        activeConnections: 183,
      };
      
      const activitiesData = Array(10)
        .fill(null)
        .map((_, index) => ({
          id: index + 1,
          type: ['user_login', 'server_add', 'client_create', 'order_complete', 'server_update'][
            Math.floor(Math.random() * 5)
          ],
          user: {
            id: Math.floor(Math.random() * 100) + 1,
            name: `User ${Math.floor(Math.random() * 100) + 1}`,
          },
          description: `Activity ${index + 1} description`,
          timestamp: new Date(Date.now() - Math.floor(Math.random() * 1000000000)),
        }));
      
      setStats(statsData);
      setActivities(activitiesData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch data on component mount
  useEffect(() => {
    fetchDashboardData();
  }, []);
  
  /**
   * Handle refresh button click.
   */
  const handleRefresh = () => {
    fetchDashboardData();
  };
  
  /**
   * Status card component.
   * 
   * @param {Object} props - Component props
   * @param {string} props.title - Card title
   * @param {any} props.value - Card value
   * @param {string} props.subtitle - Card subtitle
   * @param {React.ReactNode} props.icon - Card icon
   * @param {string} props.color - Card color
   */
  const StatusCard = ({ title, value, subtitle, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Avatar
              sx={{
                backgroundColor: `${color}.light`,
                color: `${color}.dark`,
                width: 48,
                height: 48,
              }}
            >
              {icon}
            </Avatar>
          </Grid>
          <Grid item xs>
            <Typography variant="h5" fontWeight="bold">
              {value}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {title}
            </Typography>
          </Grid>
          {subtitle && (
            <Grid item xs={12}>
              <Typography variant="caption" color="textSecondary">
                {subtitle}
              </Typography>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
  
  if (loading && !stats) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '80vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
          >
            {t('common.refresh')}
          </Button>
        </Paper>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('common.dashboard')}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : t('common.refresh')}
          </Button>
        </Box>
      </Box>
      
      {user && (
        <Typography variant="h6" sx={{ mb: 4 }}>
          {t('common.welcomeBack')}, {user.full_name || user.username}!
        </Typography>
      )}
      
      <Grid container spacing={3}>
        {/* User Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.totalUsers')}
            value={stats?.totalUsers}
            icon={<PeopleIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.activeUsers')}
            value={stats?.activeUsers}
            icon={<PersonOutlineIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.totalServers')}
            value={stats?.totalServers}
            icon={<StorageIcon />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.activeServers')}
            value={stats?.activeServers}
            icon={<RouterIcon />}
            color="info"
          />
        </Grid>
        
        {/* Client Stats */}
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.totalClients')}
            value={stats?.totalClients}
            icon={<DevicesIcon />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.activeClients')}
            value={stats?.activeClients}
            icon={<NetworkCheckIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.totalIncome')}
            value={`$${stats?.totalIncome}`}
            icon={<ImportExportIcon />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <StatusCard
            title={t('dashboard.todayIncome')}
            value={`$${stats?.todayIncome}`}
            icon={<TimelineIcon />}
            color="warning"
          />
        </Grid>
        
        {/* Traffic Chart */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title={t('dashboard.trafficUsage')} />
            <CardContent sx={{ height: 300 }}>
              <Line options={chartOptions} data={trafficData} />
            </CardContent>
          </Card>
        </Grid>
        
        {/* System Status */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title={t('dashboard.systemStatus')} />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <DnsIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="body1">
                      {t('dashboard.activeConnections')}: {stats?.activeConnections}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                      <MemoryIcon color="warning" sx={{ mr: 1 }} />
                      {t('dashboard.cpuUsage')}: {stats?.cpuUsage}%
                    </Typography>
                    <Box sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Box
                        sx={{
                          width: `${stats?.cpuUsage}%`,
                          bgcolor: 'warning.main',
                          height: 8,
                          borderRadius: 1,
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                      <SdStorageIcon color="primary" sx={{ mr: 1 }} />
                      {t('dashboard.memoryUsage')}: {stats?.memoryUsage}%
                    </Typography>
                    <Box sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Box
                        sx={{
                          width: `${stats?.memoryUsage}%`,
                          bgcolor: 'primary.main',
                          height: 8,
                          borderRadius: 1,
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                      <PublicIcon color="secondary" sx={{ mr: 1 }} />
                      {t('dashboard.diskUsage')}: {stats?.diskUsage}%
                    </Typography>
                    <Box sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Box
                        sx={{
                          width: `${stats?.diskUsage}%`,
                          bgcolor: 'secondary.main',
                          height: 8,
                          borderRadius: 1,
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Activities */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title={t('dashboard.recentActivities')}
              action={
                <IconButton onClick={handleRefresh} disabled={loading}>
                  {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                </IconButton>
              }
            />
            <CardContent>
              <List>
                {activities.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    {index > 0 && <Divider variant="inset" component="li" />}
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar>
                          {activity.type.includes('user') ? (
                            <PersonOutlineIcon />
                          ) : activity.type.includes('server') ? (
                            <StorageIcon />
                          ) : activity.type.includes('client') ? (
                            <DevicesIcon />
                          ) : (
                            <ImportExportIcon />
                          )}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.description}
                        secondary={`${activity.user.name} • ${format(new Date(activity.timestamp), 'MMM d, yyyy h:mm a')}`}
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 