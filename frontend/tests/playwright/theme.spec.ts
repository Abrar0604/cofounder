import { test, expect } from '@playwright/test';

test.describe('Theme Rules', () => {
  test('all pages enforce strict monochrome CSS', async ({ page }) => {
    // Navigate to the main dashboard
    await page.goto('/dashboard');
    
    // Evaluate in the browser to check for forbidden colors or gradients
    const checkStyles = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const violations: string[] = [];
      
      const isMonochrome = (colorString: string) => {
        // Handle rgba and rgb
        const match = colorString.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (!match) return true; // Could be transparent or something else, but generally we only care about colors
        
        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);
        
        // Monochrome means R=G=B
        // We allow some tolerance (e.g., +/- 5) for rounding in browser color calculations, 
        // though normally R, G, B should be exactly equal for grays.
        return Math.abs(r - g) <= 5 && Math.abs(g - b) <= 5;
      };

      const isTransparent = (colorString: string) => {
        return colorString === 'rgba(0, 0, 0, 0)' || colorString === 'transparent';
      };

      elements.forEach(el => {
        const style = window.getComputedStyle(el);
        
        // Check background color
        if (!isTransparent(style.backgroundColor) && !isMonochrome(style.backgroundColor)) {
          violations.push(`Element <${el.tagName}> has non-monochrome background: ${style.backgroundColor}`);
        }
        
        // Check text color
        if (!isTransparent(style.color) && !isMonochrome(style.color)) {
          violations.push(`Element <${el.tagName}> has non-monochrome text color: ${style.color}`);
        }
        
        // Check border color
        if (style.borderTopWidth !== '0px' && style.borderTopWidth !== '') {
          if (!isTransparent(style.borderColor) && !isMonochrome(style.borderColor)) {
            violations.push(`Element <${el.tagName}> has non-monochrome border color: ${style.borderColor}`);
          }
        }
        
        // Check for gradients in background image
        if (style.backgroundImage && style.backgroundImage.includes('gradient')) {
          violations.push(`Element <${el.tagName}> uses a gradient: ${style.backgroundImage}`);
        }
      });
      
      return violations;
    });

    // If there are any violations, this expect will fail and print them
    expect(checkStyles).toEqual([]);
    
    // Also explicitly check for emojis in the text content
    const pageText = await page.evaluate(() => document.body.innerText);
    // Regex for emojis
    const emojiRegex = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{1FAB0}-\u{1FABF}\u{1FAC0}-\u{1FACF}\u{1FAD0}-\u{1FADF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    expect(emojiRegex.test(pageText)).toBe(false);
  });
});
