import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Button,
  Container,
  Link,
  TextField,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { useSnackbar } from 'notistack';

const ForgotPassword = () => {
  const { t } = useTranslation();
  const { forgotPassword } = useAuth();
  const { enqueueSnackbar } = useSnackbar();

  const formik = useFormik({
    initialValues: {
      email: '',
    },
    validationSchema: Yup.object({
      email: Yup.string()
        .email(t('validation.email.valid'))
        .required(t('validation.email.required')),
    }),
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await forgotPassword(values.email);
        enqueueSnackbar(t('auth.forgotPassword.success'), { variant: 'success' });
      } catch (error) {
        enqueueSnackbar(
          error.response?.data?.message || t('auth.forgotPassword.error'),
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
        <Typography component="h1" variant="h5">
          {t('auth.forgotPassword.title')}
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1, mb: 3 }}>
          {t('auth.forgotPassword.description')}
        </Typography>
        <Box
          component="form"
          onSubmit={formik.handleSubmit}
          noValidate
          sx={{ mt: 1 }}
        >
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label={t('auth.fields.email')}
            name="email"
            autoComplete="email"
            autoFocus
            value={formik.values.email}
            onChange={formik.handleChange}
            error={formik.touched.email && Boolean(formik.errors.email)}
            helperText={formik.touched.email && formik.errors.email}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={formik.isSubmitting}
          >
            {t('auth.forgotPassword.submit')}
          </Button>
          <Box sx={{ textAlign: 'center' }}>
            <Link component={RouterLink} to="/auth/login" variant="body2">
              {t('auth.forgotPassword.backToLogin')}
            </Link>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default ForgotPassword; 