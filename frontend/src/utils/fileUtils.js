import { formatFileSize } from './numberUtils';

/**
 * Get file extension
 * 
 * @param {string} filename - File name
 * @returns {string} File extension
 */
export const getFileExtension = (filename) => {
  if (!filename) return '';
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
};

/**
 * Get file name without extension
 * 
 * @param {string} filename - File name
 * @returns {string} File name without extension
 */
export const getFileNameWithoutExtension = (filename) => {
  if (!filename) return '';
  const lastDotIndex = filename.lastIndexOf('.');
  return lastDotIndex === -1 ? filename : filename.slice(0, lastDotIndex);
};

/**
 * Get file type icon name based on extension
 * 
 * @param {string} filename - File name
 * @returns {string} Icon name
 */
export const getFileTypeIcon = (filename) => {
  const extension = getFileExtension(filename).toLowerCase();

  // Images
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension)) {
    return 'image';
  }

  // Documents
  if (['doc', 'docx'].includes(extension)) {
    return 'word';
  }
  if (['xls', 'xlsx'].includes(extension)) {
    return 'excel';
  }
  if (['ppt', 'pptx'].includes(extension)) {
    return 'powerpoint';
  }
  if (extension === 'pdf') {
    return 'pdf';
  }
  if (['txt', 'rtf'].includes(extension)) {
    return 'text';
  }

  // Archives
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
    return 'archive';
  }

  // Audio
  if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension)) {
    return 'audio';
  }

  // Video
  if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'].includes(extension)) {
    return 'video';
  }

  // Code
  if (['js', 'jsx', 'ts', 'tsx', 'html', 'css', 'php', 'py', 'java'].includes(extension)) {
    return 'code';
  }

  return 'file';
};

/**
 * Get file type label based on extension
 * 
 * @param {string} filename - File name
 * @returns {string} File type label in Persian
 */
export const getFileTypeLabel = (filename) => {
  const extension = getFileExtension(filename).toLowerCase();

  // Images
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension)) {
    return 'تصویر';
  }

  // Documents
  if (['doc', 'docx'].includes(extension)) {
    return 'سند Word';
  }
  if (['xls', 'xlsx'].includes(extension)) {
    return 'صفحه گسترده Excel';
  }
  if (['ppt', 'pptx'].includes(extension)) {
    return 'ارائه PowerPoint';
  }
  if (extension === 'pdf') {
    return 'سند PDF';
  }
  if (['txt', 'rtf'].includes(extension)) {
    return 'متن ساده';
  }

  // Archives
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
    return 'فایل فشرده';
  }

  // Audio
  if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension)) {
    return 'فایل صوتی';
  }

  // Video
  if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'].includes(extension)) {
    return 'فایل ویدیویی';
  }

  // Code
  if (['js', 'jsx', 'ts', 'tsx', 'html', 'css', 'php', 'py', 'java'].includes(extension)) {
    return 'کد برنامه';
  }

  return 'فایل';
};

/**
 * Format file info for display
 * 
 * @param {File} file - File object
 * @returns {Object} Formatted file info
 */
export const formatFileInfo = (file) => {
  return {
    name: file.name,
    nameWithoutExtension: getFileNameWithoutExtension(file.name),
    extension: getFileExtension(file.name),
    size: formatFileSize(file.size),
    type: getFileTypeLabel(file.name),
    icon: getFileTypeIcon(file.name),
    lastModified: new Date(file.lastModified),
  };
};

/**
 * Check if file type is allowed
 * 
 * @param {File} file - File object
 * @param {string[]} allowedTypes - Array of allowed MIME types
 * @returns {boolean} True if file type is allowed
 */
export const isFileTypeAllowed = (file, allowedTypes) => {
  if (!allowedTypes || !allowedTypes.length) return true;
  return allowedTypes.includes(file.type);
};

/**
 * Check if file size is within limit
 * 
 * @param {File} file - File object
 * @param {number} maxSize - Maximum size in bytes
 * @returns {boolean} True if file size is within limit
 */
export const isFileSizeValid = (file, maxSize) => {
  if (!maxSize) return true;
  return file.size <= maxSize;
};

/**
 * Convert file to base64
 * 
 * @param {File} file - File object
 * @returns {Promise<string>} Base64 string
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

/**
 * Convert base64 to file
 * 
 * @param {string} base64 - Base64 string
 * @param {string} filename - File name
 * @returns {File} File object
 */
export const base64ToFile = (base64, filename) => {
  const arr = base64.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  
  return new File([u8arr], filename, { type: mime });
};

/**
 * Download file from URL
 * 
 * @param {string} url - File URL
 * @param {string} filename - File name
 */
export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Create object URL for file
 * 
 * @param {File} file - File object
 * @returns {string} Object URL
 */
export const createObjectURL = (file) => {
  return URL.createObjectURL(file);
};

/**
 * Revoke object URL
 * 
 * @param {string} url - Object URL
 */
export const revokeObjectURL = (url) => {
  URL.revokeObjectURL(url);
}; 