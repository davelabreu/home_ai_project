import React, { useEffect } from 'react';

// Import the SVG logos
import DesktopIcon from '/desktop_icon.svg'; 
import NvidiaLogo from '/nvidia_logo.svg';

interface FaviconChangerProps {
  isJetsonApp: boolean;
  configLoading: boolean;
}

const FaviconChanger: React.FC<FaviconChangerProps> = ({ isJetsonApp, configLoading }) => {
  useEffect(() => {
    if (!configLoading) {
      // Dynamically set favicon
      let link: HTMLLinkElement | null = document.querySelector("link[rel~='icon']");
      if (!link) {
        link = document.createElement('link');
        link.rel = 'icon';
        document.getElementsByTagName('head')[0].appendChild(link);
      }
      link.href = isJetsonApp ? NvidiaLogo : DesktopIcon;
      link.type = 'image/svg+xml';

      // Dynamically set document title
      document.title = isJetsonApp ? "Jetson Dashboard" : "PC Dashboard";
    }
  }, [isJetsonApp, configLoading]);

  return null; // This component doesn't render anything itself
};

export default FaviconChanger;
