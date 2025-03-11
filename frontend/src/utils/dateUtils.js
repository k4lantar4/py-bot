import moment from 'moment-jalaali';
import { useSettings } from '../contexts/SettingsContext';

// Configure moment-jalaali
moment.loadPersian({ dialect: 'persian-modern', usePersianDigits: true });

/**
 * Format date based on user settings
 * 
 * @param {string|Date} date - Date to format
 * @param {string} format - Format string
 * @returns {string} Formatted date
 */
export const formatDate = (date, format = 'YYYY/MM/DD') => {
  const { dateFormat } = useSettings();
  const momentDate = moment(date);

  if (dateFormat === 'jalali') {
    return momentDate.format(`jYYYY/jMM/jDD${format.slice(10)}`);
  }

  return momentDate.format(format);
};

/**
 * Format date and time
 * 
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date and time
 */
export const formatDateTime = (date) => {
  return formatDate(date, 'YYYY/MM/DD HH:mm');
};

/**
 * Format date in relative format (e.g. "2 days ago")
 * 
 * @param {string|Date} date - Date to format
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (date) => {
  const momentDate = moment(date);
  const now = moment();
  const diffDays = now.diff(momentDate, 'days');
  const diffHours = now.diff(momentDate, 'hours');
  const diffMinutes = now.diff(momentDate, 'minutes');

  if (diffMinutes < 1) {
    return 'همین الان';
  }
  if (diffMinutes < 60) {
    return `${diffMinutes} دقیقه پیش`;
  }
  if (diffHours < 24) {
    return `${diffHours} ساعت پیش`;
  }
  if (diffDays < 7) {
    return `${diffDays} روز پیش`;
  }
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} هفته پیش`;
  }
  if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return `${months} ماه پیش`;
  }
  const years = Math.floor(diffDays / 365);
  return `${years} سال پیش`;
};

/**
 * Convert Gregorian date to Jalali
 * 
 * @param {string|Date} date - Gregorian date
 * @returns {string} Jalali date
 */
export const toJalali = (date) => {
  return moment(date).format('jYYYY/jMM/jDD');
};

/**
 * Convert Jalali date to Gregorian
 * 
 * @param {string} jDate - Jalali date (YYYY/MM/DD)
 * @returns {Date} Gregorian date
 */
export const toGregorian = (jDate) => {
  return moment(jDate, 'jYYYY/jMM/jDD').toDate();
};

/**
 * Get current Jalali year
 * 
 * @returns {number} Current Jalali year
 */
export const getCurrentJalaliYear = () => {
  return moment().jYear();
};

/**
 * Get current Jalali month
 * 
 * @returns {number} Current Jalali month (1-12)
 */
export const getCurrentJalaliMonth = () => {
  return moment().jMonth() + 1;
};

/**
 * Get Jalali month name
 * 
 * @param {number} month - Month number (1-12)
 * @returns {string} Month name in Persian
 */
export const getJalaliMonthName = (month) => {
  const months = [
    'فروردین',
    'اردیبهشت',
    'خرداد',
    'تیر',
    'مرداد',
    'شهریور',
    'مهر',
    'آبان',
    'آذر',
    'دی',
    'بهمن',
    'اسفند',
  ];
  return months[month - 1];
};

/**
 * Get Jalali weekday name
 * 
 * @param {number} weekday - Weekday number (0-6, 0 is Saturday)
 * @returns {string} Weekday name in Persian
 */
export const getJalaliWeekdayName = (weekday) => {
  const weekdays = [
    'شنبه',
    'یکشنبه',
    'دوشنبه',
    'سه‌شنبه',
    'چهارشنبه',
    'پنج‌شنبه',
    'جمعه',
  ];
  return weekdays[weekday];
};

/**
 * Check if a Jalali date is valid
 * 
 * @param {number} year - Jalali year
 * @param {number} month - Jalali month (1-12)
 * @param {number} day - Jalali day
 * @returns {boolean} True if date is valid
 */
export const isValidJalaliDate = (year, month, day) => {
  return moment(`${year}/${month}/${day}`, 'jYYYY/jMM/jDD').isValid();
};

/**
 * Get number of days in a Jalali month
 * 
 * @param {number} year - Jalali year
 * @param {number} month - Jalali month (1-12)
 * @returns {number} Number of days
 */
export const getJalaliMonthLength = (year, month) => {
  return moment.jDaysInMonth(year, month - 1);
};

/**
 * Check if a Jalali year is leap year
 * 
 * @param {number} year - Jalali year
 * @returns {boolean} True if leap year
 */
export const isJalaliLeapYear = (year) => {
  return moment.jIsLeapYear(year);
};

/**
 * Format duration in Persian
 * 
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration
 */
export const formatDuration = (minutes) => {
  if (minutes < 60) {
    return `${minutes} دقیقه`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (remainingMinutes === 0) {
    return `${hours} ساعت`;
  }
  return `${hours} ساعت و ${remainingMinutes} دقیقه`;
};

/**
 * Format date range in Persian
 * 
 * @param {string|Date} startDate - Start date
 * @param {string|Date} endDate - End date
 * @returns {string} Formatted date range
 */
export const formatDateRange = (startDate, endDate) => {
  const start = moment(startDate);
  const end = moment(endDate);

  if (start.isSame(end, 'day')) {
    return formatDate(startDate);
  }

  if (start.isSame(end, 'month')) {
    return `${start.format('jDD')} تا ${end.format('jDD')} ${getJalaliMonthName(start.jMonth() + 1)} ${start.format('jYYYY')}`;
  }

  if (start.isSame(end, 'year')) {
    return `${start.format('jDD')} ${getJalaliMonthName(start.jMonth() + 1)} تا ${end.format('jDD')} ${getJalaliMonthName(end.jMonth() + 1)} ${start.format('jYYYY')}`;
  }

  return `${formatDate(startDate)} تا ${formatDate(endDate)}`;
}; 