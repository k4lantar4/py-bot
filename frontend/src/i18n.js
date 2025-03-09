import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Initialize i18next
i18n
  // Load translations from /public/locales
  .use(Backend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    react: {
      useSuspense: true,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    // Default namespaces
    ns: ['common', 'auth', 'dashboard', 'server', 'location', 'service', 'user', 'order', 'discount', 'settings'],
    defaultNS: 'common',
  });

// This is a simple object with translations for quick development
// In production, these would be loaded from JSON files
const resources = {
  en: {
    common: {
      appName: '3X-UI Management System',
      welcome: 'Welcome to 3X-UI Management System',
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      edit: 'Edit',
      delete: 'Delete',
      create: 'Create',
      view: 'View',
      search: 'Search',
      filter: 'Filter',
      yes: 'Yes',
      no: 'No',
      back: 'Back',
      next: 'Next',
      confirm: 'Confirm',
      actions: 'Actions',
      status: 'Status',
      active: 'Active',
      inactive: 'Inactive',
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info',
    },
    auth: {
      login: 'Login',
      logout: 'Logout',
      register: 'Register',
      forgotPassword: 'Forgot Password',
      resetPassword: 'Reset Password',
      email: 'Email',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      username: 'Username',
      fullName: 'Full Name',
      rememberMe: 'Remember Me',
      alreadyHaveAccount: 'Already have an account?',
      dontHaveAccount: 'Don\'t have an account?',
      loginSuccess: 'Login successful!',
      logoutSuccess: 'You have been logged out successfully.',
      registerSuccess: 'Registration successful! Please log in.',
    },
    dashboard: {
      dashboard: 'Dashboard',
      overview: 'Overview',
      serverStatus: 'Server Status',
      totalUsers: 'Total Users',
      activeUsers: 'Active Users',
      totalServers: 'Total Servers',
      activeServers: 'Active Servers',
      totalRevenue: 'Total Revenue',
      monthlyRevenue: 'Monthly Revenue',
      recentOrders: 'Recent Orders',
      recentUsers: 'Recent Users',
    },
  },
  fa: {
    common: {
      appName: 'سیستم مدیریت 3X-UI',
      welcome: 'به سیستم مدیریت 3X-UI خوش آمدید',
      loading: 'در حال بارگذاری...',
      save: 'ذخیره',
      cancel: 'انصراف',
      edit: 'ویرایش',
      delete: 'حذف',
      create: 'ایجاد',
      view: 'مشاهده',
      search: 'جستجو',
      filter: 'فیلتر',
      yes: 'بله',
      no: 'خیر',
      back: 'بازگشت',
      next: 'بعدی',
      confirm: 'تایید',
      actions: 'عملیات',
      status: 'وضعیت',
      active: 'فعال',
      inactive: 'غیرفعال',
      success: 'موفقیت',
      error: 'خطا',
      warning: 'هشدار',
      info: 'اطلاعات',
    },
    auth: {
      login: 'ورود',
      logout: 'خروج',
      register: 'ثبت نام',
      forgotPassword: 'فراموشی رمز عبور',
      resetPassword: 'بازنشانی رمز عبور',
      email: 'ایمیل',
      password: 'رمز عبور',
      confirmPassword: 'تایید رمز عبور',
      username: 'نام کاربری',
      fullName: 'نام کامل',
      rememberMe: 'مرا به خاطر بسپار',
      alreadyHaveAccount: 'قبلا حساب کاربری دارید؟',
      dontHaveAccount: 'حساب کاربری ندارید؟',
      loginSuccess: 'ورود موفقیت آمیز!',
      logoutSuccess: 'با موفقیت خارج شدید.',
      registerSuccess: 'ثبت نام موفقیت آمیز! لطفا وارد شوید.',
    },
    dashboard: {
      dashboard: 'داشبورد',
      overview: 'نمای کلی',
      serverStatus: 'وضعیت سرور',
      totalUsers: 'کل کاربران',
      activeUsers: 'کاربران فعال',
      totalServers: 'کل سرورها',
      activeServers: 'سرورهای فعال',
      totalRevenue: 'درآمد کل',
      monthlyRevenue: 'درآمد ماهانه',
      recentOrders: 'سفارشات اخیر',
      recentUsers: 'کاربران اخیر',
    },
  }
};

// Add resources (for quick development)
// In production, these would be loaded from JSON files via Backend
Object.keys(resources).forEach(lng => {
  Object.keys(resources[lng]).forEach(ns => {
    i18n.addResourceBundle(lng, ns, resources[lng][ns], true, true);
  });
});

export default i18n; 