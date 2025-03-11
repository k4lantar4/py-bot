/**
 * Login page for the 3X-UI Management System.
 * 
 * This component provides a login form for authenticating users.
 */

import React from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Container,
  Link,
  TextField,
  Typography,
  InputAdornment,
  IconButton,
  Paper,
  Divider,
} from '@mui/material';
import { Visibility, VisibilityOff, Login as LoginIcon } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useSnackbar } from 'notistack';
import LoadingButton from '@mui/lab/LoadingButton';

/**
 * Login component for user authentication.
 */
const Login = () => {
  const { t } = useTranslation();
  const { login } = useAuth();
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = React.useState(false);

  const formik = useFormik({
    initialValues: {
      usernameOrEmail: '',
      password: '',
    },
    validationSchema: Yup.object({
      usernameOrEmail: Yup.string()
        .required(t('validation.email.required')),
      password: Yup.string()
        .required(t('validation.password.required')),
    }),
    onSubmit: async (values, { setSubmitting }) => {
      try {
        const response = await login(values.usernameOrEmail, values.password);
        if (response) {
          enqueueSnackbar(t('auth.login.success'), { variant: 'success' });
          navigate('/dashboard');
        }
      } catch (error) {
        enqueueSnackbar(
          error.response?.data?.message || t('auth.login.error'),
          { variant: 'error' }
        );
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
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
            <LoginIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
            <Typography component="h1" variant="h5">
              {t('auth.login.title')}
            </Typography>
          </Box>

          <Box
            component="form"
            onSubmit={formik.handleSubmit}
            noValidate
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="usernameOrEmail"
              label={t('auth.fields.email')}
              name="usernameOrEmail"
              autoComplete="email"
              autoFocus
              value={formik.values.usernameOrEmail}
              onChange={formik.handleChange}
              error={formik.touched.usernameOrEmail && Boolean(formik.errors.usernameOrEmail)}
              helperText={formik.touched.usernameOrEmail && formik.errors.usernameOrEmail}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label={t('auth.fields.password')}
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formik.values.password}
              onChange={formik.handleChange}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
            />

            <LoadingButton
              type="submit"
              fullWidth
              variant="contained"
              loading={formik.isSubmitting}
              loadingPosition="start"
              startIcon={<LoginIcon />}
              sx={{ mb: 2 }}
            >
              {t('auth.login.submit')}
            </LoadingButton>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Link component={RouterLink} to="/auth/forgot-password" variant="body2">
                {t('auth.login.forgotPassword')}
              </Link>
              <Link component={RouterLink} to="/auth/register" variant="body2">
                {t('auth.login.noAccount')}
              </Link>
            </Box>

            <Divider sx={{ my: 2 }}>
              <Typography variant="body2" color="text.secondary">
                یا
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              color="primary"
              onClick={() => {/* Add social login handler */}}
              sx={{ mt: 1 }}
            >
              ورود با گوگل
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login; 