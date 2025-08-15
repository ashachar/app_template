import React from 'react';
import { LaserRenderProps } from './useLaserAnimation.types';
import { getLaserOriginX, generateLightningPath, calculateBeamLength } from './useLaserAnimation.utils';

export const renderLaser = ({
  targetIndex,
  animationKey,
  containerRefElement,
  heroCenter,
  logoPositions,
  heroVideoRef
}: LaserRenderProps) => {
  if (!heroCenter || !logoPositions[targetIndex]) return null;

  const origin = {
    x: getLaserOriginX(targetIndex, heroCenter.x, containerRefElement, heroVideoRef),
    y: heroCenter.y
  };
  const target = {
    x: logoPositions[targetIndex].x,
    y: logoPositions[targetIndex].y
  };
  const beamLength = calculateBeamLength(origin.x, origin.y, target.x, target.y);

  return (
    <>
      <polyline
        key={`purple-laser-${animationKey}`}
        className="laser-beam"
        points={generateLightningPath(
          origin.x,
          origin.y,
          target.x,
          target.y,
          Math.random()
        )}
        stroke="purple"
        strokeWidth="2"
        style={{
          filter: 'drop-shadow(0 0 4px rgba(128, 0, 128, 0.8))',
          '--beam-length': `${beamLength}px`
        } as React.CSSProperties}
      />
      <polyline
        key={`white-laser-${animationKey}`}
        className="laser-beam"
        points={generateLightningPath(
          origin.x,
          origin.y,
          target.x,
          target.y,
          Math.random()
        )}
        stroke="white"
        strokeWidth="1"
        style={{
          filter: 'drop-shadow(0 0 2px rgba(255, 255, 255, 0.9))',
          '--beam-length': `${beamLength}px`
        } as React.CSSProperties}
      />
    </>
  );
};