import { t } from 'i18next';

/**
 * Error codes and their corresponding messages
 */
const ERROR_MESSAGES = {
  // Auth errors
  'auth/invalid-credentials': 'auth.errors.invalidCredentials',
  'auth/user-not-found': 'auth.errors.userNotFound',
  'auth/email-already-in-use': 'auth.errors.emailInUse',
  'auth/weak-password': 'auth.errors.weakPassword',
  'auth/invalid-email': 'auth.errors.invalidEmail',
  'auth/operation-not-allowed': 'auth.errors.operationNotAllowed',
  'auth/requires-recent-login': 'auth.errors.requiresRecentLogin',
  'auth/too-many-requests': 'auth.errors.tooManyRequests',
  'auth/user-disabled': 'auth.errors.userDisabled',
  'auth/invalid-verification-code': 'auth.errors.invalidVerificationCode',
  'auth/invalid-verification-id': 'auth.errors.invalidVerificationId',
  'auth/invalid-phone-number': 'auth.errors.invalidPhoneNumber',
  'auth/missing-phone-number': 'auth.errors.missingPhoneNumber',
  'auth/quota-exceeded': 'auth.errors.quotaExceeded',

  // Network errors
  'network/no-internet': 'network.errors.noInternet',
  'network/timeout': 'network.errors.timeout',
  'network/server-error': 'network.errors.serverError',
  'network/unknown': 'network.errors.unknown',

  // API errors
  'api/bad-request': 'api.errors.badRequest',
  'api/unauthorized': 'api.errors.unauthorized',
  'api/forbidden': 'api.errors.forbidden',
  'api/not-found': 'api.errors.notFound',
  'api/method-not-allowed': 'api.errors.methodNotAllowed',
  'api/conflict': 'api.errors.conflict',
  'api/internal-server-error': 'api.errors.internalServerError',
  'api/service-unavailable': 'api.errors.serviceUnavailable',

  // Validation errors
  'validation/required': 'validation.errors.required',
  'validation/min-length': 'validation.errors.minLength',
  'validation/max-length': 'validation.errors.maxLength',
  'validation/email': 'validation.errors.email',
  'validation/password-match': 'validation.errors.passwordMatch',
  'validation/phone': 'validation.errors.phone',
  'validation/national-code': 'validation.errors.nationalCode',
  'validation/postal-code': 'validation.errors.postalCode',
  'validation/card-number': 'validation.errors.cardNumber',
  'validation/sheba': 'validation.errors.sheba',

  // Default error
  default: 'common.errors.unknown',
};

/**
 * Get error message for a given error code
 * 
 * @param {string} code - Error code
 * @param {Object} params - Parameters for translation
 * @returns {string} Translated error message
 */
export const getErrorMessage = (code, params = {}) => {
  const messageKey = ERROR_MESSAGES[code] || ERROR_MESSAGES.default;
  return t(messageKey, params);
};

/**
 * Handle API error response
 * 
 * @param {Object} error - Axios error object
 * @returns {Object} Error details
 */
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return {
          code: 'api/bad-request',
          message: data.message || getErrorMessage('api/bad-request'),
          details: data.errors,
        };
      case 401:
        return {
          code: 'api/unauthorized',
          message: data.message || getErrorMessage('api/unauthorized'),
        };
      case 403:
        return {
          code: 'api/forbidden',
          message: data.message || getErrorMessage('api/forbidden'),
        };
      case 404:
        return {
          code: 'api/not-found',
          message: data.message || getErrorMessage('api/not-found'),
        };
      case 405:
        return {
          code: 'api/method-not-allowed',
          message: data.message || getErrorMessage('api/method-not-allowed'),
        };
      case 409:
        return {
          code: 'api/conflict',
          message: data.message || getErrorMessage('api/conflict'),
        };
      case 500:
        return {
          code: 'api/internal-server-error',
          message: getErrorMessage('api/internal-server-error'),
        };
      case 503:
        return {
          code: 'api/service-unavailable',
          message: getErrorMessage('api/service-unavailable'),
        };
      default:
        return {
          code: 'api/unknown',
          message: getErrorMessage('default'),
        };
    }
  } else if (error.request) {
    // Request made but no response
    if (!navigator.onLine) {
      return {
        code: 'network/no-internet',
        message: getErrorMessage('network/no-internet'),
      };
    }
    if (error.code === 'ECONNABORTED') {
      return {
        code: 'network/timeout',
        message: getErrorMessage('network/timeout'),
      };
    }
    return {
      code: 'network/unknown',
      message: getErrorMessage('network/unknown'),
    };
  }
  
  // Something else happened
  return {
    code: 'default',
    message: getErrorMessage('default'),
  };
};

/**
 * Handle validation errors
 * 
 * @param {Object} errors - Validation errors object
 * @returns {Object} Formatted validation errors
 */
export const handleValidationErrors = (errors) => {
  const formattedErrors = {};

  Object.keys(errors).forEach((field) => {
    const error = errors[field];
    if (typeof error === 'string') {
      formattedErrors[field] = getErrorMessage(`validation/${error}`);
    } else if (Array.isArray(error)) {
      formattedErrors[field] = error.map((err) => 
        getErrorMessage(`validation/${err}`)
      ).join(', ');
    }
  });

  return formattedErrors;
};

/**
 * Handle auth errors
 * 
 * @param {Object} error - Auth error object
 * @returns {Object} Error details
 */
export const handleAuthError = (error) => {
  const code = error.code || 'default';
  return {
    code,
    message: getErrorMessage(code),
  };
};

/**
 * Format validation error message
 * 
 * @param {string} field - Field name
 * @param {string} type - Error type
 * @param {Object} params - Additional parameters
 * @returns {string} Formatted error message
 */
export const formatValidationError = (field, type, params = {}) => {
  return getErrorMessage(`validation/${type}`, {
    field: t(`fields.${field}`),
    ...params,
  });
}; 