import * as Yup from 'yup';
import { t } from 'i18next';

// Custom validation methods
Yup.addMethod(Yup.string, 'nationalCode', function () {
  return this.test('nationalCode', t('validation.nationalCode.invalid'), (value) => {
    if (!value) return true;
    if (!/^\d{10}$/.test(value)) return false;

    const check = +value[9];
    const sum = value
      .split('')
      .slice(0, 9)
      .reduce((acc, x, i) => acc + (+x * (10 - i)), 0) % 11;

    return sum < 2 ? check === sum : check + sum === 11;
  });
});

Yup.addMethod(Yup.string, 'mobileNumber', function () {
  return this.test('mobileNumber', t('validation.mobileNumber.invalid'), (value) => {
    if (!value) return true;
    return /^09\d{9}$/.test(value);
  });
});

Yup.addMethod(Yup.string, 'postalCode', function () {
  return this.test('postalCode', t('validation.postalCode.invalid'), (value) => {
    if (!value) return true;
    return /^\d{10}$/.test(value);
  });
});

Yup.addMethod(Yup.string, 'cardNumber', function () {
  return this.test('cardNumber', t('validation.cardNumber.invalid'), (value) => {
    if (!value) return true;
    if (!/^\d{16}$/.test(value)) return false;

    let sum = 0;
    for (let i = 0; i < 16; i++) {
      let d = parseInt(value[i]);
      if (i % 2 === 0) {
        d *= 2;
        if (d > 9) d -= 9;
      }
      sum += d;
    }
    return sum % 10 === 0;
  });
});

Yup.addMethod(Yup.string, 'sheba', function () {
  return this.test('sheba', t('validation.sheba.invalid'), (value) => {
    if (!value) return true;
    if (!/^IR\d{24}$/.test(value)) return false;

    const d1 = value[0].charCodeAt(0) - 65 + 10;
    const d2 = value[1].charCodeAt(0) - 65 + 10;
    const newStr = value.slice(4) + d1.toString() + d2.toString() + value.slice(2, 4);
    let remainder = newStr.split('').reduce((acc, digit) => {
      acc = acc * 10 + parseInt(digit);
      acc %= 97;
      return acc;
    }, 0);

    return remainder === 1;
  });
});

// Common validation schemas
export const loginSchema = Yup.object({
  usernameOrEmail: Yup.string()
    .required(t('validation.required'))
    .min(3, t('validation.minLength', { min: 3 }))
    .max(50, t('validation.maxLength', { max: 50 })),
  password: Yup.string()
    .required(t('validation.required'))
    .min(8, t('validation.minLength', { min: 8 })),
});

export const registerSchema = Yup.object({
  username: Yup.string()
    .required(t('validation.required'))
    .min(3, t('validation.minLength', { min: 3 }))
    .max(20, t('validation.maxLength', { max: 20 }))
    .matches(/^[a-zA-Z0-9_]+$/, t('validation.username.format')),
  email: Yup.string()
    .required(t('validation.required'))
    .email(t('validation.email.format')),
  password: Yup.string()
    .required(t('validation.required'))
    .min(8, t('validation.minLength', { min: 8 }))
    .matches(/[A-Z]/, t('validation.password.uppercase'))
    .matches(/[a-z]/, t('validation.password.lowercase'))
    .matches(/[0-9]/, t('validation.password.number'))
    .matches(/[^A-Za-z0-9]/, t('validation.password.special')),
  confirmPassword: Yup.string()
    .required(t('validation.required'))
    .oneOf([Yup.ref('password'), null], t('validation.password.match')),
});

export const profileSchema = Yup.object({
  firstName: Yup.string()
    .required(t('validation.required'))
    .max(50, t('validation.maxLength', { max: 50 })),
  lastName: Yup.string()
    .required(t('validation.required'))
    .max(50, t('validation.maxLength', { max: 50 })),
  email: Yup.string()
    .required(t('validation.required'))
    .email(t('validation.email.format')),
  mobileNumber: Yup.string()
    .required(t('validation.required'))
    .mobileNumber(),
  nationalCode: Yup.string()
    .required(t('validation.required'))
    .nationalCode(),
  postalCode: Yup.string()
    .nullable()
    .postalCode(),
});

export const changePasswordSchema = Yup.object({
  currentPassword: Yup.string()
    .required(t('validation.required')),
  newPassword: Yup.string()
    .required(t('validation.required'))
    .min(8, t('validation.minLength', { min: 8 }))
    .matches(/[A-Z]/, t('validation.password.uppercase'))
    .matches(/[a-z]/, t('validation.password.lowercase'))
    .matches(/[0-9]/, t('validation.password.number'))
    .matches(/[^A-Za-z0-9]/, t('validation.password.special')),
  confirmNewPassword: Yup.string()
    .required(t('validation.required'))
    .oneOf([Yup.ref('newPassword'), null], t('validation.password.match')),
});

export const bankAccountSchema = Yup.object({
  accountNumber: Yup.string()
    .required(t('validation.required'))
    .matches(/^\d+$/, t('validation.number.format')),
  cardNumber: Yup.string()
    .required(t('validation.required'))
    .cardNumber(),
  sheba: Yup.string()
    .required(t('validation.required'))
    .sheba(),
  bankName: Yup.string()
    .required(t('validation.required')),
});

export const addressSchema = Yup.object({
  province: Yup.string()
    .required(t('validation.required')),
  city: Yup.string()
    .required(t('validation.required')),
  address: Yup.string()
    .required(t('validation.required'))
    .min(10, t('validation.minLength', { min: 10 }))
    .max(200, t('validation.maxLength', { max: 200 })),
  postalCode: Yup.string()
    .required(t('validation.required'))
    .postalCode(),
});

// Helper functions
export const getFieldError = (formik, field) => {
  return formik.touched[field] && formik.errors[field];
};

export const hasError = (formik, field) => {
  return Boolean(getFieldError(formik, field));
};

export const getErrorMessage = (formik, field) => {
  return getFieldError(formik, field) || '';
}; 