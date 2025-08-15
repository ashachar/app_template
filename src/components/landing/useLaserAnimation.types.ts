export interface LogoPosition {
  id: number;
  x: number;
  y: number;
}

export interface ClickLaser {
  targetIndex: number;
  key: number;
}

export interface LaserRenderProps {
  targetIndex: number;
  animationKey: number | string;
  containerRefElement: HTMLDivElement | null;
  heroCenter: { x: number; y: number } | null;
  logoPositions: LogoPosition[];
  heroVideoRef: React.RefObject<HTMLVideoElement>;
}