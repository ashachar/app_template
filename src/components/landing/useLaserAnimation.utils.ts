import { companyLogos } from './constants';

export const getLaserOriginX = (
  targetIndex: number,
  defaultX: number,
  containerRefElement: HTMLDivElement | null,
  heroVideoRef: React.RefObject<HTMLVideoElement>
) => {
  if (!containerRefElement) return defaultX;
  const numLogos = companyLogos.length;
  const logosPerSide = Math.ceil(numLogos / 2);
  if (targetIndex < logosPerSide) {
    const heroWrapper = heroVideoRef.current?.closest('.hero-container');
    if (!heroWrapper) return defaultX;
    const heroRect = heroWrapper.getBoundingClientRect();
    const containerRect = containerRefElement.getBoundingClientRect();
    return (heroRect.left - containerRect.left) + (heroRect.width * 0.59);
  }
  return defaultX;
};

export const generateLightningPath = (
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  seed = 0
) => {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const segments = Math.min(7, Math.max(5, Math.floor(distance / 50)));
  const points = [`${x1},${y1}`];
  for (let i = 1; i < segments; i++) {
    const progress = i / segments;
    const baseX = x1 + dx * progress;
    const baseY = y1 + dy * progress;
    const offsetMultiplier = Math.sin(progress * Math.PI) * 1.5;
    const perpX = -dy / distance;
    const perpY = dx / distance;
    const offset = (Math.sin(i * seed * 10) * 0.5 + Math.random() - 0.5) * 12 * offsetMultiplier;
    points.push(`${baseX + perpX * offset},${baseY + perpY * offset}`);
  }
  points.push(`${x2},${y2}`);
  return points.join(' ');
};

export const calculateBeamLength = (
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number => {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy) * 1.2;
};