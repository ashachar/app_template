import { useEffect, RefObject } from 'react';

export const useVideoPlayback = (heroVideoRef: RefObject<HTMLVideoElement>) => {
  useEffect(() => {
    const video = heroVideoRef.current;
    const handleMetadataLoaded = () => {
      if (video) {
        video.playbackRate = 0.7;
      }
    };

    if (video) {
      if (video.readyState >= video.HAVE_METADATA) {
        handleMetadataLoaded();
      } else {
        video.addEventListener('loadedmetadata', handleMetadataLoaded, { once: true });
      }
    }

    return () => {
      // Cleanup if needed
    };
  }, [heroVideoRef]);
};