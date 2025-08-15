import { useLayoutEffect } from 'react';
import { MOVEMENT_AMPLITUDE, ANIMATION_DURATION } from './constants';

export const useLandingPageStyles = () => {
  useLayoutEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      /* Hide scrollbar on root page while keeping scrollable */
      html, body {
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* Internet Explorer 10+ */
      }
      html::-webkit-scrollbar, body::-webkit-scrollbar {
        display: none; /* WebKit */
      }
      
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(15px) scale(0.98);
        }
        to {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }
      .animate-fade-in-up {
        opacity: 0;
        animation: fadeInUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
      }

      @keyframes subtleMove {
        0% { transform: translate(-50%, -50%) translate3d(0, 0, 0); }
        25% { transform: translate(-50%, -50%) translate3d(${MOVEMENT_AMPLITUDE * 0.8}px, ${MOVEMENT_AMPLITUDE * 0.4}px, 0); }
        50% { transform: translate(-50%, -50%) translate3d(${-MOVEMENT_AMPLITUDE * 0.5}px, ${-MOVEMENT_AMPLITUDE * 1}px, 0); }
        75% { transform: translate(-50%, -50%) translate3d(${MOVEMENT_AMPLITUDE * 1}px, ${-MOVEMENT_AMPLITUDE * 0.6}px, 0); }
        100% { transform: translate(-50%, -50%) translate3d(0, 0, 0); }
      }
      @keyframes laserGrow {
        0% { stroke-dashoffset: var(--beam-length); }
        100% { stroke-dashoffset: 0; }
      }
      .logo-subtle-move {
        position: absolute;
        transform: translate(-50%, -50%);
        animation: subtleMove ${ANIMATION_DURATION} linear infinite alternate;
        will-change: transform;
        z-index: 1;
        transition: filter 2s ease-out, opacity 2s ease-out;
      }
      .logo-hit {
        filter: grayscale(0) !important;
        opacity: 1 !important;
      }
      .logo-unhit {
        filter: grayscale(1);
        opacity: 0.7;
      }
      .laser-beam {
        stroke-dasharray: var(--beam-length);
        animation: laserGrow 0.6s ease-out forwards;
      }
      .hero-video {
        object-fit: cover;
        object-position: center;
        border-radius: 50%;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.5);
      }
      .hero-container {
        aspect-ratio: 1/1;
        max-width: 100%;
        max-height: 100%;
        overflow: hidden;
        border-radius: 50%;
        position: relative;
      }
      @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
    `;
    document.head.appendChild(style);

    return () => {
      if (document.head.contains(style)) document.head.removeChild(style);
      // Restore scrollbar on other pages
      document.documentElement.style.scrollbarWidth = '';
      (document.documentElement.style as any).msOverflowStyle = '';
      document.body.style.scrollbarWidth = '';
      (document.body.style as any).msOverflowStyle = '';
    };
  }, []);
};