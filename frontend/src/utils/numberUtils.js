import { useSettings } from '../contexts/SettingsContext';

// Persian digits
const PERSIAN_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
const ENGLISH_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

/**
 * Convert English digits to Persian
 * 
 * @param {string|number} value - Value to convert
 * @returns {string} Value with Persian digits
 */
export const toPersianDigits = (value) => {
  if (!value) return '';
  return value.toString().replace(/[0-9]/g, (d) => PERSIAN_DIGITS[d]);
};

/**
 * Convert Persian digits to English
 * 
 * @param {string} value - Value to convert
 * @returns {string} Value with English digits
 */
export const toEnglishDigits = (value) => {
  if (!value) return '';
  return value.toString().replace(/[۰-۹]/g, (d) => ENGLISH_DIGITS[PERSIAN_DIGITS.indexOf(d)]);
};

/**
 * Format number with thousands separator
 * 
 * @param {number} value - Number to format
 * @param {boolean} usePersianDigits - Whether to use Persian digits
 * @returns {string} Formatted number
 */
export const formatNumber = (value, usePersianDigits = true) => {
  if (!value && value !== 0) return '';
  
  const formatted = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return usePersianDigits ? toPersianDigits(formatted) : formatted;
};

/**
 * Format currency based on user settings
 * 
 * @param {number} value - Amount to format
 * @param {boolean} showCurrency - Whether to show currency symbol/name
 * @returns {string} Formatted amount
 */
export const formatCurrency = (value, showCurrency = true) => {
  const { currency } = useSettings();
  const formatted = formatNumber(value);

  if (!showCurrency) return formatted;

  switch (currency) {
    case 'IRR':
      return `${formatted} ریال`;
    case 'IRT':
      return `${formatted} تومان`;
    case 'USD':
      return `$${formatted}`;
    case 'EUR':
      return `€${formatted}`;
    default:
      return formatted;
  }
};

/**
 * Convert numbers to Persian words
 * 
 * @param {number} value - Number to convert
 * @returns {string} Number in Persian words
 */
export const numberToWords = (value) => {
  const units = ['', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه'];
  const tens = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود'];
  const teens = ['ده', 'یازده', 'دوازده', 'سیزده', 'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده'];
  const hundreds = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد'];
  const thousands = ['', 'هزار', 'میلیون', 'میلیارد', 'تریلیون'];

  if (value === 0) return 'صفر';
  if (!value) return '';

  const convertGroup = (num) => {
    const h = Math.floor(num / 100);
    const t = Math.floor((num % 100) / 10);
    const u = num % 10;
    let result = '';

    if (h > 0) {
      result += hundreds[h] + ' و ';
    }

    if (t === 1) {
      result += teens[u];
    } else {
      if (t > 1) {
        result += tens[t];
        if (u > 0) result += ' و ';
      }
      if (u > 0 || (t === 0 && h === 0)) {
        result += units[u];
      }
    }

    return result.trim();
  };

  const groups = [];
  let num = Math.abs(Math.floor(value));
  
  while (num > 0) {
    groups.push(num % 1000);
    num = Math.floor(num / 1000);
  }

  let result = '';
  for (let i = groups.length - 1; i >= 0; i--) {
    if (groups[i] === 0) continue;
    
    const groupText = convertGroup(groups[i]);
    if (groupText) {
      if (result) result += ' و ';
      result += groupText;
      if (i > 0) result += ' ' + thousands[i];
    }
  }

  return result;
};

/**
 * Format file size in Persian
 * 
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return 'صفر بایت';

  const k = 1024;
  const sizes = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت', 'ترابایت'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${formatNumber(parseFloat((bytes / Math.pow(k, i)).toFixed(2)))} ${sizes[i]}`;
};

/**
 * Format percentage in Persian
 * 
 * @param {number} value - Percentage value
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value, decimals = 0) => {
  if (!value && value !== 0) return '';
  
  const formatted = value.toFixed(decimals);
  return `${toPersianDigits(formatted)}٪`;
};

/**
 * Format phone number in Persian style
 * 
 * @param {string} value - Phone number
 * @returns {string} Formatted phone number
 */
export const formatPhoneNumber = (value) => {
  if (!value) return '';

  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length === 11 && cleaned.startsWith('09')) {
    return toPersianDigits(
      cleaned.replace(/(\d{4})(\d{3})(\d{4})/, '$1 $2 $3')
    );
  }
  return toPersianDigits(value);
};

/**
 * Format national code in Persian style
 * 
 * @param {string} value - National code
 * @returns {string} Formatted national code
 */
export const formatNationalCode = (value) => {
  if (!value) return '';

  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return toPersianDigits(
      cleaned.replace(/(\d{3})(\d{6})(\d{1})/, '$1-$2-$3')
    );
  }
  return toPersianDigits(value);
};

/**
 * Format postal code in Persian style
 * 
 * @param {string} value - Postal code
 * @returns {string} Formatted postal code
 */
export const formatPostalCode = (value) => {
  if (!value) return '';

  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return toPersianDigits(
      cleaned.replace(/(\d{5})(\d{5})/, '$1-$2')
    );
  }
  return toPersianDigits(value);
}; 