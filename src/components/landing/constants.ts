// Company logos configuration
export const companyLogos = [
  { id: 1, src: '/companies_logos/google-logo.png', alt: 'Google Logo' },
  { id: 2, src: '/companies_logos/microsoft-logo.png', alt: 'Microsoft Logo' },
  { id: 3, src: '/companies_logos/meta-logo.png', alt: 'Meta Logo' },
  { id: 4, src: '/companies_logos/amazon-logo.png', alt: 'Amazon Logo' },
  { id: 5, src: '/companies_logos/apple-logo.png', alt: 'Apple Logo' },
  { id: 6, src: '/companies_logos/nvidia-logo.png', alt: 'Nvidia Logo' },
];

// Animation constants
export const CIRCLE_OFFSET = 60;
export const MOVEMENT_AMPLITUDE = 10;
export const ANIMATION_DURATION = '30s';
export const LASER_DURATION_MS = 400;
export const LASER_MIN_INTERVAL_MS = 1000;
export const LASER_MAX_INTERVAL_MS = 3000;

// Re-export language configuration from shared constants
export { availableLanguages } from '@/constants/languages';