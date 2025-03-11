/**
 * Internationalization configuration for the 3X-UI Management System.
 * 
 * This module configures i18next for internationalization support.
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import moment from 'moment-jalaali';

// English translations
const enTranslations = {
  common: {
    dashboard: 'Dashboard',
    users: 'Users',
    roles: 'Roles',
    servers: 'Servers',
    locations: 'Locations',
    services: 'Services',
    clients: 'Clients',
    orders: 'Orders',
    reports: 'Reports',
    settings: 'Settings',
    logout: 'Logout',
    profile: 'Profile',
    language: 'Language',
    darkMode: 'Dark Mode',
    search: 'Search',
    notifications: 'Notifications',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    confirm: 'Confirm',
    cancel: 'Cancel',
    save: 'Save',
    add: 'Add',
    edit: 'Edit',
    delete: 'Delete',
    view: 'View',
    actions: 'Actions',
    status: 'Status',
    refresh: 'Refresh',
    noData: 'No data available',
    welcomeBack: 'Welcome back',
    back: 'Back',
    noResults: 'No results found',
    required: 'This field is required',
  },
  auth: {
    login: {
      title: 'Login',
      submit: 'Login',
      success: 'Successfully logged in',
      error: 'Invalid username or password',
      forgotPassword: 'Forgot password?',
      noAccount: 'Don\'t have an account?',
      register: 'Register',
    },
    register: {
      title: 'Register',
      submit: 'Register',
      success: 'Successfully registered',
      error: 'Registration failed',
      haveAccount: 'Already have an account?',
    },
    forgotPassword: {
      title: 'Forgot Password',
      submit: 'Send Reset Link',
      success: 'Password reset link sent to your email',
      error: 'Failed to send reset link',
      description: 'Enter your email and we\'ll send you a link to reset your password',
      backToLogin: 'Back to login',
    },
    resetPassword: {
      title: 'Reset Password',
      submit: 'Reset Password',
      success: 'Password successfully reset',
      error: 'Failed to reset password',
      invalidToken: 'Invalid reset link',
      backToLogin: 'Back to login',
    },
    fields: {
      username: 'Username',
      email: 'Email',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      newPassword: 'New Password',
    },
  },
  dashboard: {
    totalUsers: 'Total Users',
    activeUsers: 'Active Users',
    totalServers: 'Total Servers',
    activeServers: 'Active Servers',
    totalServices: 'Total Services',
    totalClients: 'Total Clients',
    activeClients: 'Active Clients',
    totalIncome: 'Total Income',
    todayIncome: 'Today\'s Income',
    thisMonth: 'This Month',
    lastMonth: 'Last Month',
    trafficUsage: 'Traffic Usage',
    recentActivities: 'Recent Activities',
    systemStatus: 'System Status',
    activeConnections: 'Active Connections',
    cpuUsage: 'CPU Usage',
    memoryUsage: 'Memory Usage',
    diskUsage: 'Disk Usage',
    title: 'Dashboard',
    welcome: 'Welcome',
    stats: {
      total: 'Total',
      active: 'Active',
      inactive: 'Inactive',
    },
  },
  user: {
    fullName: 'Full Name',
    email: 'Email',
    username: 'Username',
    roles: 'Roles',
    phone: 'Phone',
    telegramId: 'Telegram ID',
    wallet: 'Wallet Balance',
    lastLogin: 'Last Login',
    createdAt: 'Created At',
    active: 'Active',
    inactive: 'Inactive',
    status: 'Status',
    superuser: 'Superuser',
    isActive: 'Is Active',
    isSuperuser: 'Is Superuser',
    userDetails: 'User Details',
    createUser: 'Create User',
    updateUser: 'Update User',
    deleteUser: 'Delete User',
    deleteUserConfirm: 'Are you sure you want to delete this user? This action cannot be undone.',
    userCreated: 'User created successfully.',
    userUpdated: 'User updated successfully.',
    userDeleted: 'User deleted successfully.',
  },
  validation: {
    username: {
      required: 'Username is required',
      min: 'Username must be at least 3 characters',
      max: 'Username must be at most 20 characters',
    },
    email: {
      required: 'Email is required',
      valid: 'Invalid email address',
    },
    password: {
      required: 'Password is required',
      min: 'Password must be at least 8 characters',
    },
    confirmPassword: {
      required: 'Confirm password is required',
      match: 'Passwords do not match',
    },
  },
  profile: {
    title: 'Profile',
    edit: 'Edit Profile',
    changePassword: 'Change Password',
    logout: 'Logout',
  },
  settings: {
    title: 'Settings',
    theme: {
      title: 'Theme',
      light: 'Light',
      dark: 'Dark',
      system: 'System',
    },
    language: {
      title: 'Language',
      fa: 'Persian',
      en: 'English',
    },
  },
};

// Persian translations
const faTranslations = {
  common: {
    dashboard: 'داشبورد',
    users: 'کاربران',
    roles: 'نقش‌ها',
    servers: 'سرورها',
    locations: 'مکان‌ها',
    services: 'سرویس‌ها',
    clients: 'مشتریان',
    orders: 'سفارشات',
    reports: 'گزارشات',
    settings: 'تنظیمات',
    logout: 'خروج',
    profile: 'پروفایل',
    language: 'زبان',
    darkMode: 'حالت تاریک',
    search: 'جستجو',
    notifications: 'اعلان‌ها',
    loading: 'در حال بارگذاری...',
    error: 'خطا',
    success: 'موفقیت',
    confirm: 'تایید',
    cancel: 'انصراف',
    save: 'ذخیره',
    add: 'افزودن',
    edit: 'ویرایش',
    delete: 'حذف',
    view: 'مشاهده',
    actions: 'عملیات',
    status: 'وضعیت',
    refresh: 'بازنشانی',
    noData: 'اطلاعاتی موجود نیست',
    welcomeBack: 'خوش آمدید',
    back: 'بازگشت',
    noResults: 'نتیجه‌ای یافت نشد',
    required: 'این فیلد الزامی است',
  },
  auth: {
    login: {
      title: 'ورود به سیستم',
      submit: 'ورود',
      success: 'با موفقیت وارد شدید',
      error: 'نام کاربری یا رمز عبور اشتباه است',
      forgotPassword: 'رمز عبور خود را فراموش کرده‌اید؟',
      noAccount: 'حساب کاربری ندارید؟',
      register: 'ثبت نام',
    },
    register: {
      title: 'ثبت نام',
      submit: 'ثبت نام',
      success: 'ثبت نام با موفقیت انجام شد',
      error: 'خطا در ثبت نام',
      haveAccount: 'قبلاً ثبت نام کرده‌اید؟',
    },
    forgotPassword: {
      title: 'بازیابی رمز عبور',
      submit: 'ارسال لینک بازیابی',
      success: 'لینک بازیابی رمز عبور به ایمیل شما ارسال شد',
      error: 'خطا در ارسال لینک بازیابی',
      description: 'ایمیل خود را وارد کنید تا لینک بازیابی رمز عبور برای شما ارسال شود',
      backToLogin: 'بازگشت به صفحه ورود',
    },
    resetPassword: {
      title: 'تغییر رمز عبور',
      submit: 'تغییر رمز عبور',
      success: 'رمز عبور با موفقیت تغییر کرد',
      error: 'خطا در تغییر رمز عبور',
      invalidToken: 'لینک بازیابی نامعتبر است',
      backToLogin: 'بازگشت به صفحه ورود',
    },
    fields: {
      username: 'نام کاربری',
      email: 'ایمیل',
      password: 'رمز عبور',
      confirmPassword: 'تکرار رمز عبور',
      newPassword: 'رمز عبور جدید',
    },
  },
  dashboard: {
    totalUsers: 'کل کاربران',
    activeUsers: 'کاربران فعال',
    totalServers: 'کل سرورها',
    activeServers: 'سرورهای فعال',
    totalServices: 'کل سرویس‌ها',
    totalClients: 'کل مشتریان',
    activeClients: 'مشتریان فعال',
    totalIncome: 'کل درآمد',
    todayIncome: 'درآمد امروز',
    thisMonth: 'این ماه',
    lastMonth: 'ماه گذشته',
    trafficUsage: 'مصرف ترافیک',
    recentActivities: 'فعالیت‌های اخیر',
    systemStatus: 'وضعیت سیستم',
    activeConnections: 'اتصالات فعال',
    cpuUsage: 'مصرف CPU',
    memoryUsage: 'مصرف حافظه',
    diskUsage: 'مصرف دیسک',
    title: 'داشبورد',
    welcome: 'خوش آمدید',
    stats: {
      total: 'کل',
      active: 'فعال',
      inactive: 'غیرفعال',
    },
  },
  user: {
    fullName: 'نام کامل',
    email: 'ایمیل',
    username: 'نام کاربری',
    roles: 'نقش‌ها',
    phone: 'تلفن',
    telegramId: 'شناسه تلگرام',
    wallet: 'موجودی کیف پول',
    lastLogin: 'آخرین ورود',
    createdAt: 'تاریخ ایجاد',
    active: 'فعال',
    inactive: 'غیرفعال',
    status: 'وضعیت',
    superuser: 'کاربر ارشد',
    isActive: 'فعال است',
    isSuperuser: 'کاربر ارشد است',
    userDetails: 'جزئیات کاربر',
    createUser: 'ایجاد کاربر',
    updateUser: 'بروزرسانی کاربر',
    deleteUser: 'حذف کاربر',
    deleteUserConfirm: 'آیا از حذف این کاربر اطمینان دارید؟ این عمل قابل بازگشت نیست.',
    userCreated: 'کاربر با موفقیت ایجاد شد.',
    userUpdated: 'کاربر با موفقیت بروزرسانی شد.',
    userDeleted: 'کاربر با موفقیت حذف شد.',
  },
  validation: {
    username: {
      required: 'نام کاربری الزامی است',
      min: 'نام کاربری باید حداقل ۳ کاراکتر باشد',
      max: 'نام کاربری باید حداکثر ۲۰ کاراکتر باشد',
    },
    email: {
      required: 'ایمیل الزامی است',
      valid: 'ایمیل معتبر نیست',
    },
    password: {
      required: 'رمز عبور الزامی است',
      min: 'رمز عبور باید حداقل ۸ کاراکتر باشد',
    },
    confirmPassword: {
      required: 'تکرار رمز عبور الزامی است',
      match: 'رمز عبور و تکرار آن یکسان نیستند',
    },
  },
  profile: {
    title: 'پروفایل',
    edit: 'ویرایش پروفایل',
    changePassword: 'تغییر رمز عبور',
    logout: 'خروج',
  },
  settings: {
    title: 'تنظیمات',
    theme: {
      title: 'تم',
      light: 'روشن',
      dark: 'تیره',
      system: 'سیستم',
    },
    language: {
      title: 'زبان',
      fa: 'فارسی',
      en: 'English',
    },
  },
};

// Translations
const resources = {
  fa: {
    translation: faTranslations,
  },
  en: {
    translation: enTranslations,
  },
};

// Configure i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'fa',
    supportedLngs: ['fa', 'en'],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

// Configure moment-jalaali
moment.loadPersian({ dialect: 'persian-modern', usePersianDigits: true });

export default i18n; 