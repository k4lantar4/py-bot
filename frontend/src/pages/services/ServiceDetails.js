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
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
  Autocomplete
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
  Layers as LayersIcon,
  Computer as ComputerIcon,
  Description as DescriptionIcon,
  Language as LanguageIcon,
  LocalOffer as LocalOfferIcon,
  Storage as StorageIcon,
  Schedule as ScheduleIcon,
  AttachMoney as AttachMoneyIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';

const ServiceDetails = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();
  const isNew = id === 'new';

  // State
  const [service, setService] = useState({
    name: '',
    description: '',
    type: 'vpn',
    protocol: 'v2ray',
    price: 0,
    traffic_gb: 0,
    duration_days: 30,
    is_active: true,
    server_id: '',
    features: []
  });
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [servers, setServers] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  
  // Service types and protocols
  const serviceTypes = ['vpn', 'vps', 'proxy', 'hosting'];
  const protocolOptions = ['v2ray', 'trojan', 'shadowsocks', 'wireguard', 'openvpn', 'ssh'];

  // Fetch service details if editing
  useEffect(() => {
    fetchServers();
    
    if (!isNew) {
      fetchService();
    }
  }, [id]);

  const fetchService = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/services/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchFailed'));
      }
      
      const data = await response.json();
      setService(data);
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchServers = async () => {
    try {
      const response = await fetch('/api/servers', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchServersFailed'));
      }
      
      const data = await response.json();
      setServers(data);
    } catch (err) {
      enqueueSnackbar(err.message, { variant: 'error' });
    }
  };

  // Handle form changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setService(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle number changes
  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    setService(prev => ({
      ...prev,
      [name]: value === '' ? '' : Number(value)
    }));
  };

  // Handle switch change
  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setService(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle features change
  const handleFeaturesChange = (event, newValue) => {
    setService(prev => ({
      ...prev,
      features: newValue
    }));
  };

  // Handle save
  const handleSave = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);

      const response = await fetch(
        isNew ? '/api/services' : `/api/services/${id}`,
        {
          method: isNew ? 'POST' : 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(service),
        }
      );

      if (!response.ok) {
        throw new Error(t('errors.saveFailed'));
      }

      enqueueSnackbar(
        t(isNew ? 'services.createSuccess' : 'services.updateSuccess'),
        { variant: 'success' }
      );
      navigate('/services');
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
          onClick={() => navigate('/services')}
          sx={{ textDecoration: 'none' }}
        >
          {t('services.title')}
        </Link>
        <Typography color="text.primary">
          {isNew ? t('services.new') : t('services.edit')}
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          {isNew ? t('services.new') : service.name}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/services')}
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
          aria-label="service details tabs"
        >
          <Tab 
            icon={<LayersIcon />} 
            iconPosition="start" 
            label={t('services.tabs.general')} 
            id="service-tab-0" 
          />
          {!isNew && (
            <Tab 
              icon={<DescriptionIcon />} 
              iconPosition="start" 
              label={t('services.tabs.features')} 
              id="service-tab-1" 
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
                  {t('services.basicInfo')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  name="name"
                  label={t('services.name')}
                  value={service.name}
                  onChange={handleChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LayersIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="type-select-label">{t('services.type')}</InputLabel>
                  <Select
                    labelId="type-select-label"
                    name="type"
                    value={service.type}
                    onChange={handleChange}
                    label={t('services.type')}
                  >
                    {serviceTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {t(`services.types.${type}`, type)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  name="description"
                  label={t('services.description')}
                  value={service.description}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={3}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <DescriptionIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              
              {/* Protocol and Server */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t('services.technicalDetails')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="protocol-select-label">{t('services.protocol')}</InputLabel>
                  <Select
                    labelId="protocol-select-label"
                    name="protocol"
                    value={service.protocol}
                    onChange={handleChange}
                    label={t('services.protocol')}
                    startAdornment={
                      <InputAdornment position="start">
                        <LanguageIcon fontSize="small" />
                      </InputAdornment>
                    }
                  >
                    {protocolOptions.map((protocol) => (
                      <MenuItem key={protocol} value={protocol}>
                        {protocol.toUpperCase()}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="server-select-label">{t('services.server')}</InputLabel>
                  <Select
                    labelId="server-select-label"
                    name="server_id"
                    value={service.server_id}
                    onChange={handleChange}
                    label={t('services.server')}
                    startAdornment={
                      <InputAdornment position="start">
                        <ComputerIcon fontSize="small" />
                      </InputAdornment>
                    }
                  >
                    <MenuItem value="">
                      <em>{t('common.none')}</em>
                    </MenuItem>
                    {servers.map((server) => (
                      <MenuItem key={server.id} value={server.id}>
                        {server.name} ({server.ip})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              {/* Pricing and Limits */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t('services.pricingAndLimits')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  name="price"
                  label={t('services.price')}
                  type="number"
                  value={service.price}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <AttachMoneyIcon fontSize="small" />
                      </InputAdornment>
                    ),
                    inputProps: { min: 0, step: 0.01 }
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  name="traffic_gb"
                  label={t('services.trafficGB')}
                  type="number"
                  value={service.traffic_gb}
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
                    inputProps: { min: 0 }
                  }}
                  helperText={t('services.trafficHelp')}
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  name="duration_days"
                  label={t('services.durationDays')}
                  type="number"
                  value={service.duration_days}
                  onChange={handleNumberChange}
                  fullWidth
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <ScheduleIcon fontSize="small" />
                      </InputAdornment>
                    ),
                    endAdornment: <InputAdornment position="end">{t('services.days')}</InputAdornment>,
                    inputProps: { min: 1 }
                  }}
                />
              </Grid>
              
              {/* Status */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="is_active"
                      checked={service.is_active}
                      onChange={handleSwitchChange}
                      color="primary"
                    />
                  }
                  label={t('services.isActive')}
                />
              </Grid>
              
              {/* Actions */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/services')}
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

      {/* Features Tab */}
      {tabValue === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            {t('services.features')}
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Autocomplete
              multiple
              freeSolo
              options={[]}
              value={service.features || []}
              onChange={handleFeaturesChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('services.features')}
                  helperText={t('services.featuresHelp')}
                  fullWidth
                />
              )}
            />
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default ServiceDetails; 