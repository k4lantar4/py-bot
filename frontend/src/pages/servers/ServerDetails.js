import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Grid,
  CircularProgress,
  Alert,
  Breadcrumbs,
  Link,
  MenuItem,
  InputAdornment,
  Divider,
  IconButton,
  Card,
  CardHeader,
  CardContent,
  Tab,
  Tabs,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkCheckIcon,
  LocationOn as LocationIcon,
  Devices as DevicesIcon,
  BarChart as BarChartIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';

const ServerDetails = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();
  const isNew = id === 'new';

  // State
  const [server, setServer] = useState({
    name: '',
    ip: '',
    location_id: '',
    cpu_cores: 2,
    memory_gb: 4,
    disk_gb: 50,
    bandwidth_gbps: 1,
    status: 'online',
    is_active: true,
    notes: ''
  });
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [locations, setLocations] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  // Fetch server details if editing
  useEffect(() => {
    fetchLocations();
    
    if (!isNew) {
      fetchServer();
    }
  }, [id]);

  const fetchServer = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/servers/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchFailed'));
      }
      
      const data = await response.json();
      setServer(data);
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await fetch('/api/locations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchLocationsFailed'));
      }
      
      const data = await response.json();
      setLocations(data);
    } catch (err) {
      enqueueSnackbar(err.message, { variant: 'error' });
    }
  };

  // Handle form changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setServer(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle number changes
  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    setServer(prev => ({
      ...prev,
      [name]: value === '' ? '' : Number(value)
    }));
  };

  // Handle switch change
  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setServer(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle save
  const handleSave = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);

      const response = await fetch(
        isNew ? '/api/servers' : `/api/servers/${id}`,
        {
          method: isNew ? 'POST' : 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(server),
        }
      );

      if (!response.ok) {
        throw new Error(t('errors.saveFailed'));
      }

      enqueueSnackbar(
        t(isNew ? 'servers.createSuccess' : 'servers.updateSuccess'),
        { variant: 'success' }
      );
      navigate('/servers');
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 4 }}>
        <Link
          component="button"
          variant="body1"
          onClick={() => navigate('/servers')}
          sx={{ textDecoration: 'none' }}
        >
          {t('servers.title')}
        </Link>
        <Typography color="text.primary">
          {isNew ? t('servers.new') : t('servers.edit')}
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          {isNew ? t('servers.new') : server.name}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/servers')}
        >
          {t('common.back')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          aria-label="server details tabs"
        >
          <Tab 
            icon={<ComputerIcon />} 
            iconPosition="start" 
            label={t('servers.tabs.general')} 
            id="server-tab-0" 
          />
          {!isNew && (
            <Tab 
              icon={<BarChartIcon />} 
              iconPosition="start" 
              label={t('servers.tabs.metrics')} 
              id="server-tab-1" 
            />
          )}
          {!isNew && (
            <Tab 
              icon={<DevicesIcon />} 
              iconPosition="start" 
              label={t('servers.tabs.services')} 
              id="server-tab-2" 
            />
          )}
        </Tabs>
      </Box>

      {/* General Tab */}
      {tabValue === 0 && (
        <Paper sx={{ p: 4 }}>
          <form onSubmit={handleSave}>
            <Grid container spacing={3}>
              {/* Basic Info */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {t('servers.basicInfo')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  name="name"
                  label={t('servers.name')}
                  value={server.name}
                  onChange={handleChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <ComputerIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  name="ip"
                  label={t('servers.ip')}
                  value={server.ip}
                  onChange={handleChange}
                  fullWidth
                  required
                  placeholder="xxx.xxx.xxx.xxx"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NetworkCheckIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="location-select-label">{t('servers.location')}</InputLabel>
                  <Select
                    labelId="location-select-label"
                    name="location_id"
                    value={server.location_id}
                    onChange={handleChange}
                    label={t('servers.location')}
                    startAdornment={
                      <InputAdornment position="start">
                        <LocationIcon fontSize="small" />
                      </InputAdornment>
                    }
                  >
                    <MenuItem value="">
                      <em>{t('common.none')}</em>
                    </MenuItem>
                    {locations.map((location) => (
                      <MenuItem key={location.id} value={location.id}>
                        {location.flag_emoji && <span style={{ marginRight: 8 }}>{location.flag_emoji}</span>}
                        {location.name} ({location.country})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="status-select-label">{t('servers.status')}</InputLabel>
                  <Select
                    labelId="status-select-label"
                    name="status"
                    value={server.status}
                    onChange={handleChange}
                    label={t('servers.status')}
                  >
                    <MenuItem value="online">{t('servers.status.online')}</MenuItem>
                    <MenuItem value="offline">{t('servers.status.offline')}</MenuItem>
                    <MenuItem value="maintenance">{t('servers.status.maintenance')}</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              {/* Hardware Resources */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t('servers.resources')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  name="cpu_cores"
                  label={t('servers.cpuCores')}
                  type="number"
                  value={server.cpu_cores}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <MemoryIcon fontSize="small" />
                      </InputAdornment>
                    ),
                    inputProps: { min: 1 }
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  name="memory_gb"
                  label={t('servers.memoryGB')}
                  type="number"
                  value={server.memory_gb}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <StorageIcon fontSize="small" />
                      </InputAdornment>
                    ),
                    endAdornment: <InputAdornment position="end">GB</InputAdornment>,
                    inputProps: { min: 1 }
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  name="disk_gb"
                  label={t('servers.diskGB')}
                  type="number"
                  value={server.disk_gb}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    endAdornment: <InputAdornment position="end">GB</InputAdornment>,
                    inputProps: { min: 1 }
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  name="bandwidth_gbps"
                  label={t('servers.bandwidthGbps')}
                  type="number"
                  value={server.bandwidth_gbps}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    endAdornment: <InputAdornment position="end">Gbps</InputAdornment>,
                    inputProps: { min: 0.1, step: 0.1 }
                  }}
                />
              </Grid>
              
              {/* Additional Information */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t('servers.additionalInfo')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  name="notes"
                  label={t('servers.notes')}
                  value={server.notes}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={4}
                  helperText={t('servers.notesHelp')}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      name="is_active"
                      checked={server.is_active}
                      onChange={handleSwitchChange}
                      color="primary"
                    />
                  }
                  label={t('servers.isActive')}
                />
              </Grid>
              
              {/* Actions */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/servers')}
                  >
                    {t('common.cancel')}
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SaveIcon />}
                    disabled={saving}
                  >
                    {saving ? t('common.saving') : t('common.save')}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      )}

      {/* Metrics Tab */}
      {tabValue === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            {t('servers.metrics')}
          </Typography>
          <Alert severity="info">
            {t('servers.metricsInfo')}
          </Alert>
        </Paper>
      )}

      {/* Services Tab */}
      {tabValue === 2 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            {t('servers.services')}
          </Typography>
          <Alert severity="info">
            {t('servers.servicesInfo')}
          </Alert>
        </Paper>
      )}
    </Container>
  );
};

export default ServerDetails; 