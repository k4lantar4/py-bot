import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Chip,
  Tooltip,
  Alert
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Layers as LayersIcon,
  ShoppingCart as ShoppingCartIcon,
  ViewQuilt as ViewQuiltIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

const ServicesList = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  
  // State
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch services
  const fetchServices = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/services', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchFailed'));
      }
      
      const data = await response.json();
      setServices(data);
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Load services on mount
  useEffect(() => {
    fetchServices();
  }, []);

  // Handle refresh
  const handleRefresh = () => {
    fetchServices();
  };

  // Handle add new service
  const handleAdd = () => {
    navigate('/services/new');
  };

  // Handle edit service
  const handleEdit = (id) => {
    navigate(`/services/${id}`);
  };

  // Handle delete service
  const handleDelete = async (id) => {
    if (window.confirm(t('services.deleteConfirm'))) {
      try {
        const response = await fetch(`/api/services/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error(t('errors.deleteFailed'));
        }

        enqueueSnackbar(t('services.deleteSuccess'), { variant: 'success' });
        fetchServices();
      } catch (err) {
        enqueueSnackbar(err.message, { variant: 'error' });
      }
    }
  };

  // Format price
  const formatPrice = (price) => {
    return `$${price.toFixed(2)}`;
  };

  // Get service type color
  const getServiceTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'vpn':
        return 'primary';
      case 'vps':
        return 'secondary';
      case 'proxy':
        return 'info';
      case 'hosting':
        return 'success';
      default:
        return 'default';
    }
  };

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
        >
          {t('common.retry')}
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          {t('services.title')}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            sx={{ mr: 2 }}
            disabled={loading}
          >
            {t('common.refresh')}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAdd}
          >
            {t('services.add')}
          </Button>
        </Box>
      </Box>

      {/* Services Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('services.name')}</TableCell>
              <TableCell>{t('services.type')}</TableCell>
              <TableCell align="center">{t('services.price')}</TableCell>
              <TableCell align="center">{t('services.traffic')}</TableCell>
              <TableCell align="center">{t('services.duration')}</TableCell>
              <TableCell align="right">{t('common.actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : services.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                  <Typography variant="body1" color="textSecondary">
                    {t('services.noServices')}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              services.map((service) => (
                <TableRow key={service.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LayersIcon sx={{ mr: 1 }} />
                      {service.name}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={service.type}
                      color={getServiceTypeColor(service.type)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    {formatPrice(service.price)}
                  </TableCell>
                  <TableCell align="center">
                    {service.traffic_gb ? `${service.traffic_gb} GB` : t('services.unlimited')}
                  </TableCell>
                  <TableCell align="center">
                    {service.duration_days} {t('services.days')}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title={t('common.edit')}>
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(service.id)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.delete')}>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(service.id)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default ServicesList; 