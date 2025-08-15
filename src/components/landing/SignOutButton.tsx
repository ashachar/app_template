import React from 'react';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SignOutButtonProps {
  user: any;
  loading: boolean;
  signOut: () => Promise<void>;
  t: (key: string) => string;
  dir: string;
}

export const SignOutButton: React.FC<SignOutButtonProps> = ({
  user,
  loading,
  signOut,
  t,
  dir
}) => {
  const navigate = useNavigate();

  if (!user || loading) return null;

  return (
    <div className={`fixed bottom-4 ${dir === 'rtl' ? 'right-4' : 'left-4'} z-50 animate-fade-in-up`} style={{ animationDelay: '0.6s' }}>
      <Button 
        variant="outline" 
        className="sign-out-button-container flex flex-col items-center justify-center p-2 h-auto w-16 shadow-lg bg-white/80 backdrop-blur-sm hover:bg-white/90"
        onClick={async () => {
          await signOut();
          navigate('/');
        }}
      >
        <LogOut className="h-5 w-5 mb-1 text-gray-600" />
        <span className="text-xs text-gray-600 font-medium">
          {t('common.signOut')}
        </span>
      </Button>
    </div>
  );
};