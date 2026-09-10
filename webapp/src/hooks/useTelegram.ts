import { useEffect, useCallback } from 'react';

// Declaration for Telegram WebApp
declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        close: () => void;
        sendData: (data: string) => void;
        initDataUnsafe?: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
          };
        };
        themeParams?: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
          secondary_bg_color?: string;
        };
        HapticFeedback?: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
          selectionChanged: () => void;
        };
      };
    };
  }
}

export function useTelegram() {
  const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : undefined;

  useEffect(() => {
    if (tg) {
      tg.ready();
      try {
        tg.expand();
      } catch (e) {
        console.warn('Could not expand WebApp:', e);
      }
    }
  }, [tg]);

  const haptic = useCallback(
    (type: 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning' = 'light') => {
      if (!tg?.HapticFeedback) return;
      if (type === 'light' || type === 'medium' || type === 'heavy') {
        tg.HapticFeedback.impactOccurred(type);
      } else if (type === 'success' || type === 'error' || type === 'warning') {
        tg.HapticFeedback.notificationOccurred(type);
      }
    },
    [tg]
  );

  const sendData = useCallback(
    (data: any) => {
      if (tg?.sendData) {
        tg.sendData(typeof data === 'string' ? data : JSON.stringify(data));
      }
    },
    [tg]
  );

  return {
    tg,
    haptic,
    sendData,
    close: () => tg?.close(),
    isTelegramWebApp: Boolean(tg),
    user: tg?.initDataUnsafe?.user,
    themeParams: tg?.themeParams,
  };
}
