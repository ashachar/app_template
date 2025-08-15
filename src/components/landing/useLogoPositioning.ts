import { useState, useEffect, RefObject } from 'react';
import { companyLogos, CIRCLE_OFFSET } from './constants';

interface LogoPosition {
  id: number;
  src: string;
  alt: string;
  x: number;
  y: number;
  delay: number;
}

export const useLogoPositioning = (
  heroContainerRef: RefObject<HTMLDivElement>,
  heroVideoRef: RefObject<HTMLVideoElement>
) => {
  const [logoPositions, setLogoPositions] = useState<LogoPosition[]>([]);
  const [positionsCalculated, setPositionsCalculated] = useState(false);
  const [heroCenter, setHeroCenter] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const placeElements = () => {
      if (!heroContainerRef.current || !heroVideoRef.current) {
        return;
      }

      const containerRect = heroContainerRef.current.getBoundingClientRect();
      const heroWrapper = heroVideoRef.current.closest('.hero-container');
      if (!heroWrapper) return;
      const heroRect = heroWrapper.getBoundingClientRect();

      const heroCenterX = (heroRect.left - containerRect.left) + heroRect.width / 2;
      const heroCenterY = (heroRect.top - containerRect.top) + heroRect.height / 2;
      const laserOriginX = (heroRect.left - containerRect.left) + (heroRect.width * 0.5);
      const laserOriginY = (heroRect.top - containerRect.top) + (heroRect.height * 0.19);

      setHeroCenter({ x: laserOriginX, y: laserOriginY });

      const heroRadius = heroRect.width / 2;
      const circleRadius = heroRadius + CIRCLE_OFFSET;
      const numLogos = companyLogos.length;
      const logosPerSide = Math.ceil(numLogos / 2);

      const newLogoPositions = companyLogos.map((logo, index) => {
        let currentAngle;
        if (index < logosPerSide) {
          const rightQuadrantRange = Math.PI / 2;
          const rightIncrement = rightQuadrantRange / (logosPerSide - 1 || 1);
          currentAngle = -Math.PI / 4 + (index * rightIncrement);
        } else {
          const leftIndex = index - logosPerSide;
          const leftQuadrantRange = Math.PI / 2;
          const leftIncrement = leftQuadrantRange / ((numLogos - logosPerSide) - 1 || 1);
          currentAngle = (Math.PI * 3 / 4) + (leftIndex * leftIncrement);
        }
        const logoX = heroCenterX + circleRadius * Math.cos(currentAngle);
        const logoY = heroCenterY + circleRadius * Math.sin(currentAngle);
        return { ...logo, x: logoX, y: logoY, delay: Math.random() * 5 };
      });

      setLogoPositions(newLogoPositions);
      setPositionsCalculated(true);
    };

    let resizeObserver: ResizeObserver | null = null;
    const containerElement = heroContainerRef.current;
    const heroVideoElement = heroVideoRef.current?.parentElement;

    if (containerElement && heroVideoElement) {
      const placeElementsWithRetry = (retries = 5, delay = 150) => {
        if (heroContainerRef.current && heroVideoElement && heroVideoElement.offsetWidth > 0 && heroVideoElement.offsetHeight > 0) {
          placeElements();
        } else if (retries > 0) {
          setTimeout(() => placeElementsWithRetry(retries - 1, delay), delay);
        } else {
          console.error("LandingPage: Failed to place elements after multiple retries.");
        }
      };

      const initialTimeout = setTimeout(placeElementsWithRetry, 100);
      resizeObserver = new ResizeObserver(placeElements);
      resizeObserver.observe(containerElement);
      if (heroVideoElement) resizeObserver.observe(heroVideoElement);

      return () => {
        clearTimeout(initialTimeout);
        if (resizeObserver) {
          if (containerElement) resizeObserver.unobserve(containerElement);
          if (heroVideoElement) resizeObserver.unobserve(heroVideoElement);
        }
      };
    }
  }, [heroContainerRef, heroVideoRef]);

  return { logoPositions, positionsCalculated, heroCenter };
};