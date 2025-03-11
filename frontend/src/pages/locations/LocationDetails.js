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
  Link
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';

const LocationDetails = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();
  const isNew = id === 'new';

  // State
  const [location, setLocation] = useState({
    name: '',
    country: '',
    country_code: '',
    flag_emoji: '',
    is_active: true
  });
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Fetch location details if editing
  useEffect(() => {
    if (!isNew) {
      fetchLocation();
    }
  }, [id]);

  const fetchLocation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/locations/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchFailed'));
      }
      
      const data = await response.json();
      setLocation(data);
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Handle form changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocation(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle switch change
  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setLocation(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Handle save
  const handleSave = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);

      const response = await fetch(
        isNew ? '/api/locations' : `/api/locations/${id}`,
        {
          method: isNew ? 'POST' : 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(location),
        }
      );

      if (!response.ok) {
        throw new Error(t('errors.saveFailed'));
      }

      enqueueSnackbar(
        t(isNew ? 'locations.createSuccess' : 'locations.updateSuccess'),
        { variant: 'success' }
      );
      navigate('/locations');
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
          onClick={() => navigate('/locations')}
          sx={{ textDecoration: 'none' }}
        >
          {t('locations.title')}
        </Link>
        <Typography color="text.primary">
          {isNew ? t('locations.new') : t('locations.edit')}
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          {isNew ? t('locations.new') : t('locations.edit')}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/locations')}
        >
          {t('common.back')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Form */}
      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSave}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="name"
                label={t('locations.name')}
                value={location.name}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="country"
                label={t('locations.country')}
                value={location.country}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="country_code"
                label={t('locations.countryCode')}
                value={location.country_code}
                onChange={handleChange}
                fullWidth
                required
                inputProps={{
                  maxLength: 2,
                  style: { textTransform: 'uppercase' }
                }}
                helperText={t('locations.countryCodeHelp')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="flag_emoji"
                label={t('locations.flagEmoji')}
                value={location.flag_emoji}
                onChange={handleChange}
                fullWidth
                helperText={t('locations.flagEmojiHelp')}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    name="is_active"
                    checked={location.is_active}
                    onChange={handleSwitchChange}
                    color="primary"
                  />
                }
                label={t('locations.isActive')}
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/locations')}
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
    </Container>
  );
};

export default LocationDetails; 