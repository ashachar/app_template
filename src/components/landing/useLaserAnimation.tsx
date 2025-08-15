import { useState, useEffect, useRef, RefObject } from 'react';
import { LASER_DURATION_MS, LASER_MIN_INTERVAL_MS, LASER_MAX_INTERVAL_MS } from './constants';
import { LogoPosition, ClickLaser } from './useLaserAnimation.types';
import { renderLaser } from './LaserBeam';

export const useLaserAnimation = (
  positionsCalculated: boolean,
  heroCenter: { x: number; y: number } | null,
  logoPositions: LogoPosition[],
  isMobile: boolean,
  heroVideoRef: RefObject<HTMLVideoElement>
) => {
  const [hitLogos, setHitLogos] = useState<Set<number>>(new Set());
  const [laserTargetIndex, setLaserTargetIndex] = useState(0);
  const [showLaser, setShowLaser] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);
  const [clickLaser, setClickLaser] = useState<ClickLaser | null>(null);
  
  const laserTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const clickLaserTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isMobile || !positionsCalculated || !heroCenter || logoPositions.length === 0) {
      setShowLaser(false);
      return;
    }

    const scheduleNextLaser = () => {
      if (hitLogos.size >= logoPositions.length) return null;

      const randomDelay = Math.floor(LASER_MIN_INTERVAL_MS + Math.random() * (LASER_MAX_INTERVAL_MS - LASER_MIN_INTERVAL_MS));
      
      return setTimeout(() => {
        if (isMobile) {
          setShowLaser(false);
          return;
        }
        if (laserTimeoutRef.current) clearTimeout(laserTimeoutRef.current);

        const unhitLogos = logoPositions.filter(logo => !hitLogos.has(logo.id));
        if (unhitLogos.length === 0) {
          setShowLaser(false);
          return;
        }

        const randomUnhitIndex = Math.floor(Math.random() * unhitLogos.length);
        const targetLogo = unhitLogos[randomUnhitIndex];
        const originalIndex = logoPositions.findIndex(logo => logo.id === targetLogo.id);

        setLaserTargetIndex(originalIndex);
        setAnimationKey(prev => prev + 1);
        setShowLaser(true);

        laserTimeoutRef.current = setTimeout(() => {
          setShowLaser(false);
          laserTimeoutRef.current = null;
          setHitLogos(prev => new Set(prev).add(logoPositions[originalIndex].id));
          timerRef.current = scheduleNextLaser();
        }, LASER_DURATION_MS);
      }, randomDelay);
    };

    timerRef.current = scheduleNextLaser();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (laserTimeoutRef.current) clearTimeout(laserTimeoutRef.current);
      setShowLaser(false);
    };
  }, [positionsCalculated, heroCenter, logoPositions, hitLogos, isMobile]);

  useEffect(() => {
    return () => {
      if (clickLaserTimeoutRef.current) {
        clearTimeout(clickLaserTimeoutRef.current);
      }
    };
  }, []);

  const handleLogoClick = (logoIndex: number) => {
    if (isMobile || !positionsCalculated || !heroCenter) return;

    if (clickLaserTimeoutRef.current) {
      clearTimeout(clickLaserTimeoutRef.current);
    }

    setClickLaser({ targetIndex: logoIndex, key: Date.now() });

    clickLaserTimeoutRef.current = setTimeout(() => {
      setClickLaser(null);
      clickLaserTimeoutRef.current = null;
    }, LASER_DURATION_MS);
  };

  const renderLaserWrapper = (targetIndex: number, animationKey: number | string, containerRefElement: HTMLDivElement | null) => {
    return renderLaser({
      targetIndex,
      animationKey,
      containerRefElement,
      heroCenter,
      logoPositions,
      heroVideoRef
    });
  };

  return {
    hitLogos,
    showLaser,
    laserTargetIndex,
    animationKey,
    clickLaser,
    handleLogoClick,
    renderLaser: renderLaserWrapper
  };
};