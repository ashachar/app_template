import React from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { availableLanguages } from './constants';

interface LanguageToggleProps {
  language: string;
  setLanguage: (code: string) => void;
  t: (key: string) => string;
  dir: string;
  isLanguageDropdownOpen: boolean;
  setIsLanguageDropdownOpen: (open: boolean) => void;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({
  language,
  setLanguage,
  t,
  dir,
  isLanguageDropdownOpen,
  setIsLanguageDropdownOpen
}) => {
  return (
    <div className={`fixed bottom-4 ${dir === 'rtl' ? 'left-4' : 'right-4'} z-50 animate-fade-in-up`} style={{ animationDelay: '0.6s' }}>
      <DropdownMenu open={isLanguageDropdownOpen} onOpenChange={setIsLanguageDropdownOpen}>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="outline" 
            className="language-toggle-container flex flex-col items-center justify-center p-2 h-auto w-16 shadow-lg bg-white/80 backdrop-blur-sm hover:bg-white/90"
            onClick={() => setIsLanguageDropdownOpen(prev => !prev)}
          >
            <span className="text-2xl mb-1 leading-none">
              {availableLanguages.find(lang => lang.code === language)?.flag || ''}
            </span>
            <span className="text-xs text-gray-600 font-medium">
              {t('common.language')}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align={dir === 'rtl' ? 'start' : 'end'} side="top" className="w-40 bg-white/90 backdrop-blur-sm shadow-xl rounded-lg">
          {availableLanguages.map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => {
                setLanguage(lang.code);
                setIsLanguageDropdownOpen(false);
              }}
              className={`flex items-center justify-between w-full cursor-pointer hover:bg-gray-100/50 p-2 rounded-md ${language === lang.code ? 'bg-gray-100/70' : ''}`}
            >
              <span className="text-sm text-gray-700">{lang.nativeName}</span>
              <span role="img" aria-label={lang.nativeName}>{lang.flag}</span>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};