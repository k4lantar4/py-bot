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
  Computer as ComputerIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkCheckIcon,
  CloudCircle as CloudIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

const ServersList = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  
  // State
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch servers
  const fetchServers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/servers', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(t('errors.fetchFailed'));
      }
      
      const data = await response.json();
      setServers(data);
    } catch (err) {
      setError(err.message);
      enqueueSnackbar(err.message, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Load servers on mount
  useEffect(() => {
    fetchServers();
  }, []);

  // Handle refresh
  const handleRefresh = () => {
    fetchServers();
  };

  // Handle add new server
  const handleAdd = () => {
    navigate('/servers/new');
  };

  // Handle edit server
  const handleEdit = (id) => {
    navigate(`/servers/${id}`);
  };

  // Handle delete server
  const handleDelete = async (id) => {
    if (window.confirm(t('servers.deleteConfirm'))) {
      try {
        const response = await fetch(`/api/servers/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error(t('errors.deleteFailed'));
        }

        enqueueSnackbar(t('servers.deleteSuccess'), { variant: 'success' });
        fetchServers();
      } catch (err) {
        enqueueSnackbar(err.message, { variant: 'error' });
      }
    }
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'maintenance':
        return 'warning';
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
          {t('servers.title')}
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
            {t('servers.add')}
          </Button>
        </Box>
      </Box>

      {/* Servers Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('servers.name')}</TableCell>
              <TableCell>{t('servers.ip')}</TableCell>
              <TableCell>{t('servers.location')}</TableCell>
              <TableCell align="center">{t('servers.resources')}</TableCell>
              <TableCell align="center">{t('servers.status')}</TableCell>
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
            ) : servers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                  <Typography variant="body1" color="textSecondary">
                    {t('servers.noServers')}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              servers.map((server) => (
                <TableRow key={server.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ComputerIcon sx={{ mr: 1 }} />
                      {server.name}
                    </Box>
                  </TableCell>
                  <TableCell>{server.ip}</TableCell>
                  <TableCell>
                    {server.location?.name || t('servers.noLocation')}
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                      <Tooltip title={`CPU: ${server.cpu_cores} cores`}>
                        <Chip
                          icon={<MemoryIcon />}
                          label={`${server.cpu_cores || 0}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Tooltip>
                      <Tooltip title={`RAM: ${server.memory_gb} GB`}>
                        <Chip
                          icon={<StorageIcon />}
                          label={`${server.memory_gb || 0} GB`}
                          size="small"
                          color="secondary"
                          variant="outlined"
                        />
                      </Tooltip>
                      <Tooltip title={`Network: ${server.bandwidth_gbps} Gbps`}>
                        <Chip
                          icon={<NetworkCheckIcon />}
                          label={`${server.bandwidth_gbps || 0} Gbps`}
                          size="small"
                          color="info"
                          variant="outlined"
                        />
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={t(`servers.status.${server.status}`, server.status)}
                      color={getStatusColor(server.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title={t('common.edit')}>
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(server.id)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.delete')}>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(server.id)}
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

export default ServersList; 