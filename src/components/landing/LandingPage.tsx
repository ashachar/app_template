import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import Footer from '../Footer';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext.hooks';
import ReactConfetti from 'react-confetti';
import { ArrowRight } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';

// Import custom hooks and components
import { useLandingPageStyles } from './LandingPage.styles';
import { useWindowSize } from './useWindowSize';
import { useVideoPlayback } from './useVideoPlayback';
import { useLogoPositioning } from './useLogoPositioning';
import { useLaserAnimation } from './useLaserAnimation';
import { HeroSection } from './HeroSection';
import { LanguageToggle } from './LanguageToggle';
import { SignOutButton } from './SignOutButton';

const LandingPage = () => {
  const { language, setLanguage, t, dir } = useLanguage();
  const { user, loading, signOut } = useAuth();
  const navigate = useNavigate();
  const heroContainerRef = useRef<HTMLDivElement>(null);
  const heroVideoRef = useRef<HTMLVideoElement>(null);

  usePageTitle();
  useLandingPageStyles();

  const [showConfetti, setShowConfetti] = useState(false);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);

  const { windowSize, isMobile } = useWindowSize();
  const { logoPositions, positionsCalculated, heroCenter } = useLogoPositioning(heroContainerRef, heroVideoRef);
  
  useVideoPlayback(heroVideoRef);
  
  const {
    hitLogos,
    showLaser,
    laserTargetIndex,
    animationKey,
    clickLaser,
    handleLogoClick,
    renderLaser
  } = useLaserAnimation(positionsCalculated, heroCenter, logoPositions, isMobile, heroVideoRef);

  const handleMainCTAClick = () => {
    if (user) {
      navigate('/candidate/matches');
    } else {
      navigate('/login');
    }
  };

  const handleQuickSearch = () => {
    const searchPath = language === 'he' ? '/חיפוש' : '/search';
    navigate(searchPath);
  };

  return (
    <div className="landing-page-container relative" dir={dir}>
      {showConfetti && (
        <ReactConfetti
          width={windowSize.width}
          height={windowSize.height}
          recycle={false}
          numberOfPieces={500}
          gravity={0.25}
          colors={['#9333ea', '#a855f7', '#c084fc', '#d8b4fe', '#f97316', '#fb923c', '#fdba74', '#fed7aa']}
          style={{ position: 'fixed', top: 0, left: 0, zIndex: 1000, pointerEvents: 'none' }}
        />
      )}

      <div className="fixed inset-0 bg-gradient-to-br from-purple-100 via-white to-orange-100 -z-10"></div>
      <div className="fixed top-0 right-0 w-1/3 h-1/3 bg-gradient-to-bl from-purple-200/20 to-transparent -z-10 rounded-full blur-3xl transform translate-x-1/4 -translate-y-1/4"></div>
      <div className="fixed bottom-0 left-0 w-1/2 h-1/2 bg-gradient-to-tr from-orange-200/20 to-transparent -z-10 rounded-full blur-3xl transform -translate-x-1/4 translate-y-1/4"></div>

      <main>
        <section className="relative min-h-screen flex flex-col justify-start sm:justify-center items-center pt-10 sm:pt-0">
          <div className="container mx-auto px-4">
            <div className="flex flex-col items-center">
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-brand-purple mb-2 md:mb-6 text-center animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                {t('landingPage.mainHeading')}
              </h1>
              <p className="text-base sm:text-lg md:text-xl text-gray-700 max-w-3xl mb-6 sm:mb-6 text-center animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                {t('landingPage.subHeading')}
              </p>

              <button
                onClick={handleQuickSearch}
                className="text-gray-600 hover:text-orange-400 transition-colors flex items-center text-md group font-medium mb-4 animate-fade-in-up"
                style={{ animationDelay: '0.3s' }}
              >
                {dir === 'rtl' ? (
                  <>
                    <span>{t('appEntry.quickExplore')}</span>
                    <ArrowRight size={20} className="mr-2 transition-transform duration-200 ease-in-out group-hover:-translate-x-1 rotate-180" />
                  </>
                ) : (
                  <>
                    <span>{t('appEntry.quickExplore')}</span>
                    <ArrowRight size={20} className="ml-2 transition-transform duration-200 ease-in-out group-hover:translate-x-1" />
                  </>
                )}
              </button>

              <Button
                onClick={handleMainCTAClick}
                className="flex items-center bg-brand-purple text-white px-8 py-3 rounded-full mb-16 sm:mb-10 hover:bg-brand-purple/90 transition-colors shadow-md z-20 active:scale-95 active:shadow-inner transition-all duration-150 animate-fade-in-up"
                style={{ animationDelay: '0.4s' }}
              >
                <span className="font-medium">
                  {user ? 
                    t('landingPage.viewMatchesButtonText') : 
                    t('landingPage.mainCtaButtonText')
                  }
                </span>
              </Button>

              <HeroSection
                heroContainerRef={heroContainerRef}
                heroVideoRef={heroVideoRef}
                logoPositions={logoPositions}
                positionsCalculated={positionsCalculated}
                hitLogos={hitLogos}
                handleLogoClick={handleLogoClick}
                heroCenter={heroCenter}
                isMobile={isMobile}
                showLaser={showLaser}
                laserTargetIndex={laserTargetIndex}
                animationKey={animationKey}
                clickLaser={clickLaser}
                renderLaser={renderLaser}
              />
            </div>
          </div>
        </section>
      </main>
      <Footer />

      <LanguageToggle
        language={language}
        setLanguage={setLanguage}
        t={t}
        dir={dir}
        isLanguageDropdownOpen={isLanguageDropdownOpen}
        setIsLanguageDropdownOpen={setIsLanguageDropdownOpen}
      />

      <SignOutButton
        user={user}
        loading={loading}
        signOut={signOut}
        t={t}
        dir={dir}
      />
    </div>
  );
};

export default LandingPage;