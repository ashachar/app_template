import React, { RefObject } from 'react';

interface HeroSectionProps {
  heroContainerRef: RefObject<HTMLDivElement>;
  heroVideoRef: RefObject<HTMLVideoElement>;
  logoPositions: Array<{ id: number; src: string; alt: string; x: number; y: number; delay: number }>;
  positionsCalculated: boolean;
  hitLogos: Set<number>;
  handleLogoClick: (index: number) => void;
  heroCenter: { x: number; y: number } | null;
  isMobile: boolean;
  showLaser: boolean;
  laserTargetIndex: number;
  animationKey: number;
  clickLaser: { targetIndex: number; key: number } | null;
  renderLaser: (targetIndex: number, animationKey: number | string, containerRefElement: HTMLDivElement | null) => React.ReactNode;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  heroContainerRef,
  heroVideoRef,
  logoPositions,
  positionsCalculated,
  hitLogos,
  handleLogoClick,
  heroCenter,
  isMobile,
  showLaser,
  laserTargetIndex,
  animationKey,
  clickLaser,
  renderLaser
}) => {
  return (
    <div className="hero-section-container relative w-full flex justify-center items-center animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
      <div ref={heroContainerRef} className="relative w-full max-w-[800px] h-[70vw] sm:h-[450px] md:h-[500px]">
        <div className="absolute inset-0 flex justify-center items-center">
          <div
            className="relative p-1.5 rounded-full bg-gradient-to-br from-purple-400 via-orange-300 to-pink-400 shadow-lg overflow-hidden hero-container mt-6 mb-6 sm:my-0"
            style={{
              transform: 'translateY(0)',
              width: '70vw',
              height: '70vw',
              maxWidth: '350px',
              maxHeight: '350px'
            }}
          >
            <video
              ref={heroVideoRef}
              className="w-full h-full object-cover rounded-full relative z-10 border-2 border-white/50 hero-video"
              muted playsInline loop autoPlay
            >
              <source src="/swifit_hero.mp4" type="video/mp4" />
            </video>
          </div>
        </div>

        {positionsCalculated && logoPositions.map((logo, index) => (
          <img
            key={logo.id}
            src={logo.src}
            alt={logo.alt}
            onClick={() => handleLogoClick(index)}
            className={`w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 object-contain filter drop-shadow-md logo-subtle-move ${
              (logo.id === 5 || logo.id === 2) ? 'hidden sm:block' : ''
            } ${hitLogos.has(logo.id) ? 'logo-hit' : 'logo-unhit'}`}
            style={{
              left: `${logo.x}px`,
              top: `${logo.y}px`,
              animationDelay: `${logo.delay}s`,
              cursor: 'pointer',
            }}
          />
        ))}

        {positionsCalculated && heroCenter && logoPositions.length > 0 && !isMobile && (
          <svg
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
              zIndex: 10,
              overflow: 'visible'
            }}
          >
            {showLaser && logoPositions[laserTargetIndex] && renderLaser(laserTargetIndex, animationKey, heroContainerRef.current)}
            {clickLaser && logoPositions[clickLaser.targetIndex] && renderLaser(clickLaser.targetIndex, clickLaser.key, heroContainerRef.current)}
          </svg>
        )}
      </div>
    </div>
  );
};