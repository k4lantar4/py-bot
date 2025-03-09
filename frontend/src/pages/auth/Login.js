/**
 * Login page for the 3X-UI Management System.
 * 
 * This component provides a login form for authenticating users.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Checkbox,
  Container,
  FormControlLabel,
  TextField,
  Typography,
  Paper,
  Grid,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useAuth } from '../../contexts/AuthContext';
import { authAPI } from '../../services/api';

// Validation schema for login form
const validationSchema = Yup.object({
  usernameOrEmail: Yup.string().required('Username or email is required'),
  password: Yup.string().required('Password is required'),
});

/**
 * Login component for user authentication.
 */
const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  /**
   * Handle form submission.
   * 
   * @param {Object} values - Form values
   */
  const handleSubmit = async (values) => {
    setLoading(true);
    setError('');
    
    try {
      // Call API to login
      const data = await authAPI.login(
        values.usernameOrEmail,
        values.password
      );
      
      // Update auth context
      await login(data.user, data.tokens);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      
      // Handle different error cases
      if (error.response) {
        if (error.response.status === 401) {
          setError(t('auth.loginFailed'));
        } else if (error.response.data?.detail) {
          setError(error.response.data.detail);
        } else {
          setError(t('common.error'));
        }
      } else {
        setError(t('common.error'));
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Form handling with Formik
  const formik = useFormik({
    initialValues: {
      usernameOrEmail: '',
      password: '',
      rememberMe: false,
    },
    validationSchema,
    onSubmit: handleSubmit,
  });
  
  /**
   * Toggle password visibility.
   */
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <Paper 
        elevation={3} 
        sx={{
          mt: 8,
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <IconButton
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              mb: 2,
            }}
            disabled
          >
            <LockOutlinedIcon />
          </IconButton>
          <Typography component="h1" variant="h5">
            {t('auth.login')}
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={formik.handleSubmit} noValidate sx={{ mt: 1, width: '100%' }}>
          <TextField
            margin="normal"
            fullWidth
            id="usernameOrEmail"
            label={t('auth.emailAddress')}
            name="usernameOrEmail"
            autoComplete="email"
            autoFocus
            value={formik.values.usernameOrEmail}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.usernameOrEmail && Boolean(formik.errors.usernameOrEmail)}
            helperText={formik.touched.usernameOrEmail && formik.errors.usernameOrEmail}
            disabled={loading}
          />
          
          <TextField
            margin="normal"
            fullWidth
            name="password"
            label={t('auth.password')}
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password && Boolean(formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          <FormControlLabel
            control={
              <Checkbox 
                color="primary" 
                name="rememberMe" 
                checked={formik.values.rememberMe}
                onChange={formik.handleChange}
                disabled={loading}
              />
            }
            label={t('auth.rememberMe')}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.2 }}
            disabled={loading}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              t('auth.signIn')
            )}
          </Button>
          
          <Grid container>
            <Grid item xs>
              <Link to="/auth/forgot-password" style={{ textDecoration: 'none' }}>
                <Typography variant="body2" color="primary">
                  {t('auth.forgotPassword')}
                </Typography>
              </Link>
            </Grid>
            <Grid item>
              <Link to="/auth/register" style={{ textDecoration: 'none' }}>
                <Typography variant="body2" color="primary">
                  {t('auth.dontHaveAccount')} {t('auth.signUp')}
                </Typography>
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login; 